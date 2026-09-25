import json
import re
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from auth import (
    RESET_TOKEN_TTL,
    VERIFICATION_TOKEN_TTL,
    create_token,
    generate_token,
    get_current_user,
    hash_password,
    utcnow,
    verify_password,
)
from compute import SimulationError, get_etf_stats, optimize_portfolio, resolve_ticker, run_simulation
from db import Base, engine, get_db, run_lightweight_migrations
from email_service import send_reset_email, send_verification_email
from etfs import (
    ALL_META,
    ALL_TICKERS,
    CATEGORIES,
    DEFAULT_TER,
    GEO_REGIONS_ORDER,
    GEO_ZONE_OF,
    GEO_ZONES_ORDER,
    METADATA_SCRAPED_AT,
)
from pdf_render import render_pdf, start_browser, stop_browser

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

app = FastAPI(title="Portfolio Simulator")


@app.on_event("startup")
async def on_startup():
    Base.metadata.create_all(bind=engine)
    run_lightweight_migrations()
    await start_browser()


@app.on_event("shutdown")
async def on_shutdown():
    await stop_browser()


class SyntheticSpec(BaseModel):
    ann_return: float = Field(ge=-50, le=100)
    ann_vol: float = Field(ge=0, le=100)


class PortfolioRow(BaseModel):
    ticker: str
    weight: float = Field(gt=0)
    fee: float | None = Field(default=None, ge=0, le=10)
    synthetic: SyntheticSpec | None = None


class SimulateRequest(BaseModel):
    portfolio: list[PortfolioRow]
    years: int = Field(ge=1, le=50)
    window_months: int = Field(ge=1, le=24, default=6)
    annual_rebalance: bool = False


class OptimizeRequest(BaseModel):
    portfolio: list[PortfolioRow]
    max_deviation_pct: float = Field(default=15.0, ge=1, le=100)


class RenderPdfRequest(BaseModel):
    html: str = Field(min_length=1, max_length=5_000_000)


class SignupRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=200)


class LoginRequest(BaseModel):
    email: str
    password: str


class VerifyEmailRequest(BaseModel):
    token: str


class RequestPasswordResetRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=200)


class SavePortfolioRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    portfolio: list[PortfolioRow]
    years: int = Field(ge=1, le=50)
    window_months: int = Field(ge=1, le=24, default=6)
    annual_rebalance: bool = False


@app.get("/api/etfs")
def get_etfs():
    return {
        "categories": CATEGORIES,
        "default_ter": DEFAULT_TER,
        "geo_regions_order": GEO_REGIONS_ORDER,
        "geo_zones_order": GEO_ZONES_ORDER,
        "geo_zone_of": GEO_ZONE_OF,
        "meta": ALL_META,
        "meta_scraped_at": METADATA_SCRAPED_AT,
    }


@app.get("/api/etf-stats")
def api_etf_stats():
    return get_etf_stats(list(ALL_TICKERS.keys()))


@app.get("/api/resolve-ticker")
def api_resolve_ticker(ticker: str):
    try:
        return resolve_ticker(ticker)
    except SimulationError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/api/simulate")
def post_simulate(req: SimulateRequest):
    try:
        return run_simulation(
            [row.model_dump() for row in req.portfolio],
            req.years,
            req.window_months,
            rebalance_mode="annual" if req.annual_rebalance else "monthly",
        )
    except SimulationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/optimize")
def post_optimize(req: OptimizeRequest):
    try:
        portfolio = [row.model_dump() for row in req.portfolio]
        fees = {row["ticker"].upper(): row["fee"] for row in portfolio if row.get("fee") is not None}
        return optimize_portfolio(portfolio, fees=fees, max_deviation_pct=req.max_deviation_pct)
    except SimulationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/render-pdf")
async def api_render_pdf(req: RenderPdfRequest):
    try:
        pdf_bytes = await render_pdf(req.html)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération du PDF : {exc}")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="rapport-portefeuille.pdf"'},
    )


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


@app.post("/api/auth/signup")
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=400, detail="Adresse email invalide.")
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=400, detail="Un compte existe déjà avec cet email.")
    token = generate_token()
    user = models.User(
        email=email,
        hashed_password=hash_password(req.password),
        email_verified=False,
        verification_token=token,
        verification_token_expires=utcnow() + VERIFICATION_TOKEN_TTL,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    send_verification_email(user.email, token)
    return {"token": create_token(user.id), "email": user.email, "email_verified": False}


@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")
    return {"token": create_token(user.id), "email": user.email, "email_verified": user.email_verified}


@app.get("/api/auth/me")
def me(user: models.User = Depends(get_current_user)):
    return {"email": user.email, "email_verified": user.email_verified}


@app.post("/api/auth/resend-verification")
def resend_verification(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.email_verified:
        return {"ok": True}
    token = generate_token()
    user.verification_token = token
    user.verification_token_expires = utcnow() + VERIFICATION_TOKEN_TTL
    db.commit()
    send_verification_email(user.email, token)
    return {"ok": True}


@app.post("/api/auth/verify-email")
def verify_email(req: VerifyEmailRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.verification_token == req.token).first()
    if not user or not user.verification_token_expires:
        raise HTTPException(status_code=400, detail="Lien de vérification invalide.")
    expires = user.verification_token_expires
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=utcnow().tzinfo)
    if expires < utcnow():
        raise HTTPException(status_code=400, detail="Ce lien de vérification a expiré.")
    user.email_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    db.commit()
    return {"ok": True, "email": user.email}


@app.post("/api/auth/request-password-reset")
def request_password_reset(req: RequestPasswordResetRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    # always the same response, whether or not the account exists - otherwise
    # this endpoint would let anyone check which emails are registered
    if user:
        token = generate_token()
        user.reset_token = token
        user.reset_token_expires = utcnow() + RESET_TOKEN_TTL
        db.commit()
        send_reset_email(user.email, token)
    return {"ok": True}


@app.post("/api/auth/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.reset_token == req.token).first()
    if not user or not user.reset_token_expires:
        raise HTTPException(status_code=400, detail="Lien de réinitialisation invalide.")
    expires = user.reset_token_expires
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=utcnow().tzinfo)
    if expires < utcnow():
        raise HTTPException(status_code=400, detail="Ce lien de réinitialisation a expiré.")
    user.hashed_password = hash_password(req.password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    return {"token": create_token(user.id), "email": user.email, "email_verified": user.email_verified}


# ---------------------------------------------------------------------------
# Saved portfolios (requires an account)
# ---------------------------------------------------------------------------


def _serialize_portfolio(row: models.SavedPortfolio) -> dict:
    payload = json.loads(row.data)
    return {
        "id": row.id,
        "name": row.name,
        "portfolio": payload.get("portfolio", []),
        "years": payload.get("years"),
        "window_months": payload.get("window_months"),
        "annual_rebalance": payload.get("annual_rebalance", False),
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


@app.get("/api/portfolios")
def list_portfolios(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = (
        db.query(models.SavedPortfolio)
        .filter(models.SavedPortfolio.user_id == user.id)
        .order_by(models.SavedPortfolio.updated_at.desc())
        .all()
    )
    return [_serialize_portfolio(r) for r in rows]


@app.post("/api/portfolios")
def create_portfolio(
    req: SavePortfolioRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = json.dumps(
        {
            "portfolio": [row.model_dump() for row in req.portfolio],
            "years": req.years,
            "window_months": req.window_months,
            "annual_rebalance": req.annual_rebalance,
        }
    )
    row = models.SavedPortfolio(user_id=user.id, name=req.name, data=data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return _serialize_portfolio(row)


@app.put("/api/portfolios/{portfolio_id}")
def update_portfolio(
    portfolio_id: int,
    req: SavePortfolioRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.get(models.SavedPortfolio, portfolio_id)
    if not row or row.user_id != user.id:
        raise HTTPException(status_code=404, detail="Portefeuille introuvable.")
    row.name = req.name
    row.data = json.dumps(
        {
            "portfolio": [r.model_dump() for r in req.portfolio],
            "years": req.years,
            "window_months": req.window_months,
            "annual_rebalance": req.annual_rebalance,
        }
    )
    db.commit()
    db.refresh(row)
    return _serialize_portfolio(row)


@app.delete("/api/portfolios/{portfolio_id}")
def delete_portfolio(
    portfolio_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.get(models.SavedPortfolio, portfolio_id)
    if not row or row.user_id != user.id:
        raise HTTPException(status_code=404, detail="Portefeuille introuvable.")
    db.delete(row)
    db.commit()
    return {"ok": True}


app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
