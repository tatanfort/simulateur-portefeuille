import json
import re
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from auth import create_token, get_current_user, hash_password, verify_password
from compute import SimulationError, get_etf_stats, optimize_portfolio, resolve_ticker, run_simulation
from db import Base, engine, get_db
from etfs import ALL_TICKERS, CATEGORIES, DEFAULT_TER

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

app = FastAPI(title="Portfolio Simulator")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


class PortfolioRow(BaseModel):
    ticker: str
    weight: float = Field(gt=0)
    fee: float | None = Field(default=None, ge=0, le=10)


class SimulateRequest(BaseModel):
    portfolio: list[PortfolioRow]
    years: int = Field(ge=1, le=50)
    window_months: int = Field(ge=1, le=24, default=6)


class OptimizeRequest(BaseModel):
    portfolio: list[PortfolioRow]
    max_deviation_pct: float = Field(default=15.0, ge=1, le=100)


class SignupRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=200)


class LoginRequest(BaseModel):
    email: str
    password: str


class SavePortfolioRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    portfolio: list[PortfolioRow]
    years: int = Field(ge=1, le=50)
    window_months: int = Field(ge=1, le=24, default=6)


@app.get("/api/etfs")
def get_etfs():
    return {"categories": CATEGORIES, "default_ter": DEFAULT_TER}


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
            [row.model_dump() for row in req.portfolio], req.years, req.window_months
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
    user = models.User(email=email, hashed_password=hash_password(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"token": create_token(user.id), "email": user.email}


@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect.")
    return {"token": create_token(user.id), "email": user.email}


@app.get("/api/auth/me")
def me(user: models.User = Depends(get_current_user)):
    return {"email": user.email}


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
