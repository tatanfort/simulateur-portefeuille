"""Fetches historical ETF prices from Yahoo Finance, aligns them into a
common EUR-denominated monthly series, and runs the backtest + Monte Carlo
simulations that back the report. Also maintains a background-refreshed,
disk-cached table of quick return/volatility stats for every ETF in the
curated catalogue, used to sort the picker in the frontend.
"""

import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from scipy.optimize import minimize

from etfs import ALL_FEES, DEFAULT_TER

USER_AGENT = "Mozilla/5.0"
CACHE_TTL_SECONDS = 6 * 3600
_cache = {}

MIN_OVERLAP_MONTHS = 6
MIN_MONTHS_FOR_OPTIMIZATION = 24  # a covariance matrix estimated on less is mostly noise
DEFAULT_BLOCK_MONTHS = 6
N_SIMS = 5000
MAX_MISSING_WEIGHT_FOR_EXTENSION = 0.25
MC_EXCLUDE_MAX_WEIGHT = 0.10
MC_EXCLUDE_MIN_YEARS = 5

RISK_FREE_RATE = 0.02  # annualized, EUR — rough proxy for Sharpe/Sortino, not a live rate

# well-known stress windows used for the crisis stress-test — calendar-month
# ranges, deliberately simple (peak-to-trough / acute-shock spans) rather
# than debated exact start/end dates
CRISIS_PERIODS = [
    {
        "key": "gfc2008",
        "label": "Crise financiere 2008",
        "category": "financiere",
        "start": "2007-10",
        "end": "2009-02",
    },
    {
        "key": "covid2020",
        "label": "Crise sanitaire (COVID-19)",
        "category": "sanitaire",
        "start": "2020-02",
        "end": "2020-03",
    },
    {
        "key": "ukraine2022",
        "label": "Crise geopolitique (guerre en Ukraine)",
        "category": "geopolitique",
        "start": "2022-02",
        "end": "2022-06",
    },
]

# tried in order, without a dot in the typed symbol, so "EXCS" resolves to
# "EXCS.L" the way a user typing a bare US-style ticker would expect
TICKER_SUFFIX_CANDIDATES = [".L", ".AS", ".DE", ".PA", ".MI", ".SW", ".TO"]

STATS_CACHE_FILE = Path(__file__).resolve().parent / "etf_stats_cache.json"
STATS_TTL_SECONDS = 24 * 3600
STATS_LOOKBACK_YEARS = 10
STATS_MAX_WORKERS = 16


class SimulationError(Exception):
    pass


def _fetch_yahoo_chart(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    resp = requests.get(
        url,
        params={"range": "max", "interval": "1mo"},
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    resp.raise_for_status()
    payload = resp.json()
    result = payload.get("chart", {}).get("result")
    if not result:
        err = payload.get("chart", {}).get("error")
        message = err.get("description") if isinstance(err, dict) else "no data"
        raise SimulationError(f"{ticker}: {message}")
    return result[0]


def resolve_ticker(raw_ticker):
    """Validates a manually-typed ticker, trying common exchange suffixes
    (.L, .AS, .DE, ...) when the bare symbol doesn't resolve on its own —
    e.g. "EXCS" alone 404s on Yahoo Finance, but "EXCS.L" is the real LSE
    listing. Successful lookups are cached under their resolved key so the
    simulation that follows doesn't re-fetch the same data.
    """
    raw_ticker = raw_ticker.strip().upper()
    if not raw_ticker:
        raise SimulationError("Ticker vide.")
    candidates = (
        [raw_ticker]
        if "." in raw_ticker
        else [raw_ticker] + [raw_ticker + suffix for suffix in TICKER_SUFFIX_CANDIDATES]
    )

    tried = []
    for candidate in candidates:
        try:
            result = _fetch_yahoo_chart(candidate)
        except Exception:
            tried.append(candidate)
            continue
        meta = result.get("meta", {})
        currency = meta.get("currency", "USD")
        series = _to_monthly_series(result)
        _cache[f"ticker:{candidate}"] = (time.time(), (series, currency))
        name = meta.get("longName") or meta.get("shortName") or candidate

        fee = ALL_FEES.get(candidate, DEFAULT_TER)
        response = {"valid": True, "ticker": candidate, "name": name, "currency": currency, "ter": fee}
        try:
            eur_series = _to_eur_series(candidate)
            ann_return, ann_vol, years_used = compute_ann_stats(eur_series, fee_annual_pct=fee)
            response["ann_return"] = round(ann_return * 100, 2)
            response["ann_vol"] = round(ann_vol * 100, 2)
            response["years"] = round(years_used, 1)
        except Exception:
            pass  # stats are a nice-to-have; the ticker is still valid without them
        return response

    raise SimulationError(f"Aucun ticker Yahoo Finance valide trouvé (essayé : {', '.join(tried)})")


def _to_monthly_series(result):
    """Timestamps are bucketed to the exchange's local trading day, so a
    naive UTC .date() truncation mislabels months for GMT/BST-style
    exchanges near DST transitions. A 12h buffer absorbs any timezone
    offset before truncating to the calendar month.
    """
    timestamps = result["timestamp"]
    indicators = result["indicators"]
    if indicators.get("adjclose") and indicators["adjclose"][0].get("adjclose"):
        prices = indicators["adjclose"][0]["adjclose"]
    else:
        prices = indicators["quote"][0]["close"]
    dates = [
        (datetime.fromtimestamp(t, timezone.utc) + timedelta(hours=12)).date()
        for t in timestamps
    ]
    s = pd.Series(prices, index=pd.to_datetime(dates)).dropna()
    s.index = s.index.to_period("M")
    return s[~s.index.duplicated(keep="last")]


def _get_series_cached(key, fetch_fn):
    now = time.time()
    cached = _cache.get(key)
    if cached and now - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]
    value = fetch_fn()
    _cache[key] = (now, value)
    return value


def _get_ticker_series(ticker):
    def fetch():
        result = _fetch_yahoo_chart(ticker)
        currency = result.get("meta", {}).get("currency", "USD")
        series = _to_monthly_series(result)
        return series, currency

    return _get_series_cached(f"ticker:{ticker}", fetch)


def _get_eur_fx_series(currency):
    """Monthly units of `currency` per 1 EUR, so local_price / fx = EUR price."""
    pair = f"EUR{currency}=X"

    def fetch():
        result = _fetch_yahoo_chart(pair)
        return _to_monthly_series(result)

    return _get_series_cached(f"fx:{pair}", fetch)


def _to_eur_series(ticker):
    series, currency = _get_ticker_series(ticker)
    if currency == "EUR":
        return series
    fx = _get_eur_fx_series(currency)
    aligned = pd.concat([series, fx], axis=1, join="inner")
    return aligned.iloc[:, 0] / aligned.iloc[:, 1]


def _fetch_all_eur_series(tickers):
    """Fetches each ticker's own EUR-converted price series independently,
    with NO cross-asset alignment — callers decide how to combine series
    with different start dates (see _determine_extended_start below).
    """
    eur_series = {}
    failed = []
    for ticker in tickers:
        try:
            eur_series[ticker] = _to_eur_series(ticker)
        except Exception as exc:
            failed.append({"ticker": ticker, "reason": f"téléchargement impossible ({exc})"})
    return eur_series, failed


def _determine_extended_start(rets_df, weights_by_ticker):
    """A single very-recent, small-weight ETF shouldn't truncate the whole
    backtest to its own short inception date. Starting from the newest
    asset's inception and walking backwards through assets ordered by start
    date (most recent first), this finds the earliest date at which the
    assets still missing never exceed MAX_MISSING_WEIGHT_FOR_EXTENSION of
    total portfolio weight — i.e. how far back we can extend the period
    while only ever "missing" an acceptably small slice of the portfolio.
    """
    first_valid = {t: rets_df[t].first_valid_index() for t in rets_df.columns}
    order = sorted(rets_df.columns, key=lambda t: first_valid[t], reverse=True)
    extended_start = first_valid[order[0]]
    cum_excluded = 0.0
    for i, ticker in enumerate(order):
        cum_excluded += weights_by_ticker[ticker]
        if cum_excluded > MAX_MISSING_WEIGHT_FOR_EXTENSION:
            break
        extended_start = first_valid[order[i + 1]] if i + 1 < len(order) else rets_df.index.min()
    return extended_start


def _max_drawdown_pct(returns):
    if len(returns) == 0:
        return 0.0
    wealth = np.cumprod(1 + returns.values)
    peak = np.maximum.accumulate(wealth)
    drawdown = wealth / peak - 1
    return float(drawdown.min()) * 100


def compute_risk_metrics(returns, risk_free=RISK_FREE_RATE):
    """returns: pandas Series of monthly returns (fractions, not %)."""
    if returns is None or len(returns) < 2:
        return None
    ann_return = float((1 + returns.mean()) ** 12 - 1)
    ann_vol = float(returns.std() * np.sqrt(12))
    max_dd_pct = _max_drawdown_pct(returns)
    sharpe = (ann_return - risk_free) / ann_vol if ann_vol > 1e-9 else None
    downside = returns[returns < 0]
    downside_dev = float(downside.std() * np.sqrt(12)) if len(downside) >= 2 else 0.0
    sortino = (ann_return - risk_free) / downside_dev if downside_dev > 1e-9 else None
    var95 = float(np.percentile(returns.values, 5))
    tail = returns.values[returns.values <= var95]
    cvar95 = float(tail.mean()) if len(tail) else var95
    return {
        "max_drawdown": round(max_dd_pct, 2),
        "sharpe": round(sharpe, 2) if sharpe is not None else None,
        "sortino": round(sortino, 2) if sortino is not None else None,
        "var_95_monthly": round(var95 * 100, 2),
        "cvar_95_monthly": round(cvar95 * 100, 2),
    }


def _crisis_return(returns, start, end):
    start_p, end_p = pd.Period(start, freq="M"), pd.Period(end, freq="M")
    if returns is None or len(returns) == 0:
        return None
    if returns.index.min() > start_p or returns.index.max() < end_p:
        return None
    window = returns.loc[start_p:end_p]
    if len(window) == 0:
        return None
    return float(np.prod(1 + window.values) - 1)


def compute_crisis_table(returns):
    out = []
    for crisis in CRISIS_PERIODS:
        r = _crisis_return(returns, crisis["start"], crisis["end"])
        out.append(
            {
                "key": crisis["key"],
                "label": crisis["label"],
                "category": crisis["category"],
                "start": crisis["start"],
                "end": crisis["end"],
                "available": r is not None,
                "return_pct": round(r * 100, 2) if r is not None else None,
            }
        )
    return out


def _clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def _score_from_range(value, worst, best):
    """Linear map: value==worst -> 0, value==best -> 100, clamped either side."""
    if best == worst:
        return 50.0
    return _clamp((value - worst) / (best - worst) * 100)


def compute_resilience_score(ann_vol_pct, max_dd_pct, sharpe, avg_corr, crisis_table, n_assets):
    """A transparent, explainable heuristic composite (not a scientific
    absolute): five 0-100 sub-scores blended into one headline number, with
    the full breakdown returned alongside so the number is never a black box.
    """
    vol_score = _score_from_range(ann_vol_pct, 35, 5)
    dd_score = _score_from_range(abs(max_dd_pct), 60, 5)
    sharpe_score = _score_from_range(sharpe if sharpe is not None else 0, -0.5, 2.0)
    div_score = 0.0 if (n_assets <= 1 or avg_corr is None) else _score_from_range(avg_corr, 1.0, -0.2)

    available = [c for c in crisis_table if c["available"]]
    crisis_score = (
        float(np.mean([_score_from_range(c["return_pct"], -50, 5) for c in available]))
        if available
        else None
    )

    components = {
        "volatility": {"score": round(vol_score, 1), "value_pct": round(ann_vol_pct, 2)},
        "drawdown": {"score": round(dd_score, 1), "value_pct": round(max_dd_pct, 2)},
        "sharpe": {"score": round(sharpe_score, 1), "value": round(sharpe, 2) if sharpe is not None else None},
        "diversification": {
            "score": round(div_score, 1),
            "avg_correlation": round(avg_corr, 2) if avg_corr is not None else None,
        },
        "crisis": {
            "score": round(crisis_score, 1) if crisis_score is not None else None,
            "n_available": len(available),
        },
    }

    base_weights = {"volatility": 0.25, "drawdown": 0.25, "sharpe": 0.15, "diversification": 0.20, "crisis": 0.15}
    if crisis_score is None:
        remaining = {k: v for k, v in base_weights.items() if k != "crisis"}
        total = sum(remaining.values())
        weights_map = {k: v / total for k, v in remaining.items()}
        weights_map["crisis"] = 0.0
    else:
        weights_map = base_weights

    total_score = sum(
        components[k]["score"] * weights_map[k] for k in weights_map if components[k]["score"] is not None
    )

    if total_score >= 80:
        label = "Tres resilient"
    elif total_score >= 65:
        label = "Resilient"
    elif total_score >= 50:
        label = "Modere"
    elif total_score >= 35:
        label = "Fragile"
    else:
        label = "Tres fragile"

    return {"score": round(total_score, 1), "label": label, "components": components, "weights": weights_map}


def _block_bootstrap_path(returns_matrix, horizon_months, block_months, rng):
    n_hist = returns_matrix.shape[0]
    months = []
    while len(months) < horizon_months:
        start = rng.integers(0, n_hist)
        months.extend([(start + i) % n_hist for i in range(block_months)])
    return returns_matrix[months[:horizon_months]]


def run_simulation(portfolio, years, window_months=DEFAULT_BLOCK_MONTHS):
    """portfolio: list of {"ticker": str, "weight": float (percent)}.
    years: Monte-Carlo horizon in years for the N-year performance simulation.
    window_months: length (in months) of the rolling window used for the
    best/worst-window backtest, its Monte-Carlo distribution, and the
    bootstrap block size.
    """
    if not portfolio:
        raise SimulationError("Le portefeuille est vide.")
    if not (1 <= years <= 50):
        raise SimulationError("N doit être compris entre 1 et 50 ans.")
    if not (1 <= window_months <= 24):
        raise SimulationError("La fenêtre glissante doit être comprise entre 1 et 24 mois.")

    merged_weights = {}
    fee_overrides = {}
    for row in portfolio:
        ticker = str(row["ticker"]).strip().upper()
        weight = float(row["weight"])
        if not ticker or weight <= 0:
            continue
        merged_weights[ticker] = merged_weights.get(ticker, 0.0) + weight
        if row.get("fee") is not None:
            fee_overrides[ticker] = float(row["fee"])
    if not merged_weights:
        raise SimulationError("Aucune pondération positive fournie.")

    tickers = list(merged_weights.keys())
    eur_series, failed = _fetch_all_eur_series(tickers)

    used_tickers = [t for t in tickers if t in eur_series]
    if not used_tickers:
        raise SimulationError("Aucun des tickers fournis n'a pu être récupéré.")

    raw_w = np.array([merged_weights[t] for t in used_tickers], dtype=float)
    weights = raw_w / raw_w.sum()
    weights_by_ticker = dict(zip(used_tickers, weights))

    # annual expense ratio (TER, %) per asset — user-supplied override if given,
    # else the catalogue default, else a generic estimate for unknown tickers.
    # Deducted from every monthly return BEFORE any other calculation, so
    # fees flow through the whole report (returns, risk metrics, crisis
    # analysis, Monte Carlo, optimization) rather than being a cosmetic label.
    fee_by_ticker = {
        t: fee_overrides[t] if t in fee_overrides else ALL_FEES.get(t, DEFAULT_TER)
        for t in used_tickers
    }

    price_df = pd.DataFrame({t: eur_series[t] for t in used_tickers})
    rets_df = price_df.pct_change()  # outer-joined: NaN before a ticker's own inception
    fee_monthly = pd.Series({t: fee_by_ticker[t] / 100.0 / 12.0 for t in used_tickers})
    rets_df = rets_df.sub(fee_monthly, axis=1)

    extended_start = _determine_extended_start(rets_df, weights_by_ticker)
    common_end = min(rets_df[t].last_valid_index() for t in used_tickers)
    window_df = rets_df.loc[extended_start:common_end, used_tickers]

    if len(window_df) < MIN_OVERLAP_MONTHS:
        raise SimulationError(
            f"Historique disponible trop court ({len(window_df)} mois) pour ces actifs "
            f"— {MIN_OVERLAP_MONTHS} mois minimum requis."
        )

    # blend/prorate: months where one or more (collectively <=25% weight)
    # assets are missing get their return computed over the assets that ARE
    # present, reweighted back up to 100% of target weight.
    avail = window_df.notna()
    weight_row = weights.reshape(1, -1)
    weight_matrix = avail.values.astype(float) * weight_row
    coverage = weight_matrix.sum(axis=1)
    normalized_w = weight_matrix / coverage.reshape(-1, 1)
    port_ret = pd.Series(
        (normalized_w * window_df.fillna(0.0).values).sum(axis=1), index=window_df.index
    )
    coverage_series = pd.Series(coverage, index=window_df.index)
    missing_by_date = {
        d: [used_tickers[j] for j in range(len(used_tickers)) if not avail.values[i, j]]
        for i, d in enumerate(window_df.index)
    }

    # per-asset stats over each asset's own available data within the window
    ann_ret = {t: (1 + window_df[t].dropna().mean()) ** 12 - 1 for t in used_tickers}
    ann_vol = {t: window_df[t].dropna().std() * np.sqrt(12) for t in used_tickers}
    port_ann_ret = (1 + port_ret.mean()) ** 12 - 1
    port_ann_vol = port_ret.std() * np.sqrt(12)
    corr = window_df.corr()  # pandas uses pairwise-complete observations by default

    roll_window = (1 + port_ret).rolling(window_months).apply(np.prod, raw=True) - 1
    roll_window = roll_window.dropna()
    if len(roll_window) == 0:
        raise SimulationError(
            f"Historique trop court ({len(window_df)} mois) pour une fenêtre de {window_months} mois."
        )
    roll_coverage = coverage_series.rolling(window_months).min().reindex(roll_window.index)

    def missing_over_span(end_date, span_months):
        span = pd.period_range(end=end_date, periods=span_months, freq="M")
        merged = set()
        for d in span:
            merged.update(missing_by_date.get(d, []))
        return sorted(merged)

    roll_missing = [missing_over_span(d, window_months) for d in roll_window.index]
    best_idx = roll_window.idxmax()
    worst_idx = roll_window.idxmin()
    best_pos = roll_window.index.get_loc(best_idx)
    worst_pos = roll_window.index.get_loc(worst_idx)

    # calendar-year returns, for the annual-performance bar chart
    year_groups = (1 + port_ret).groupby(port_ret.index.year)
    coverage_by_year = coverage_series.groupby(coverage_series.index.year)
    annual_returns = []
    for year, group in year_groups:
        cov_min = float(coverage_by_year.get_group(year).min())
        year_missing = missing_over_span(group.index.max(), len(group))
        annual_returns.append(
            {
                "year": int(year),
                "return": round(float(np.prod(group.values) - 1) * 100, 2),
                "months": int(len(group)),
                "partial": bool(len(group) < 12 or cov_min < 0.999),
                "missing": year_missing,
                "coverage_pct": round(cov_min * 100, 1),
            }
        )

    # same two charts (rolling window + calendar-year returns) computed per
    # individual asset, so the frontend can let the user filter the "backtest
    # réel" section to a single product instead of the blended portfolio
    asset_series = {}
    for t in used_tickers:
        s = window_df[t].dropna()
        entry = {"roll_window": {"dates": [], "values": []}, "annual_returns": []}
        if len(s) >= window_months:
            a_roll = (1 + s).rolling(window_months).apply(np.prod, raw=True) - 1
            a_roll = a_roll.dropna()
            if len(a_roll):
                a_best_idx = a_roll.idxmax()
                a_worst_idx = a_roll.idxmin()
                entry["roll_window"] = {
                    "dates": [str(d) for d in a_roll.index],
                    "values": [round(float(v) * 100, 2) for v in a_roll.values],
                    "median": round(float(a_roll.median()) * 100, 2),
                    "std": round(float(a_roll.std()) * 100, 2),
                    "best": {
                        "date": str(a_best_idx),
                        "start": str(a_best_idx - (window_months - 1)),
                        "value": round(float(a_roll[a_best_idx]) * 100, 2),
                    },
                    "worst": {
                        "date": str(a_worst_idx),
                        "start": str(a_worst_idx - (window_months - 1)),
                        "value": round(float(a_roll[a_worst_idx]) * 100, 2),
                    },
                }
        a_year_groups = (1 + s).groupby(s.index.year)
        entry["annual_returns"] = [
            {
                "year": int(year),
                "return": round(float(np.prod(group.values) - 1) * 100, 2),
                "months": int(len(group)),
                "partial": bool(len(group) < 12),
            }
            for year, group in a_year_groups
        ]
        asset_series[t] = entry

    # risk metrics + crisis stress-test + resilience score. Per-asset risk
    # metrics reuse the same window as the return/vol table above (for a
    # consistent comparison); per-asset crisis returns instead use each
    # asset's own FULL history (rets_df, pre-truncation) since a stress test
    # is specifically about looking as far back as each asset allows, even
    # if a shorter-lived portfolio member limited the main backtest window.
    portfolio_risk = compute_risk_metrics(port_ret)
    asset_risk = {t: compute_risk_metrics(window_df[t].dropna()) for t in used_tickers}
    portfolio_crisis = compute_crisis_table(port_ret)
    asset_crisis = {t: compute_crisis_table(rets_df[t].dropna()) for t in used_tickers}

    n = len(used_tickers)
    if n > 1:
        corr_values = corr.values
        w_outer = np.outer(weights, weights)
        off_diag = ~np.eye(n, dtype=bool)
        vals, wts = corr_values[off_diag], w_outer[off_diag]
        valid = ~np.isnan(vals)
        avg_corr = float(np.sum(vals[valid] * wts[valid]) / np.sum(wts[valid])) if valid.any() else None
    else:
        avg_corr = None

    resilience = compute_resilience_score(
        ann_vol_pct=float(port_ann_vol) * 100,
        max_dd_pct=portfolio_risk["max_drawdown"] if portfolio_risk else 0.0,
        sharpe=portfolio_risk["sharpe"] if portfolio_risk else None,
        avg_corr=avg_corr,
        crisis_table=portfolio_crisis,
        n_assets=n,
    )

    def hist(data, nbins=22):
        counts, edges = np.histogram(data, bins=nbins)
        return {"counts": counts.tolist(), "edges": edges.tolist()}

    def pct_summary(arr):
        return {
            "mean": round(float(np.mean(arr)) * 100, 2),
            "median": round(float(np.median(arr)) * 100, 2),
            "p5": round(float(np.percentile(arr, 5)) * 100, 2),
            "p25": round(float(np.percentile(arr, 25)) * 100, 2),
            "p75": round(float(np.percentile(arr, 75)) * 100, 2),
            "p95": round(float(np.percentile(arr, 95)) * 100, 2),
            "min": round(float(np.min(arr)) * 100, 2),
            "max": round(float(np.max(arr)) * 100, 2),
        }

    # Monte Carlo needs a clean, NaN-free joint-asset return matrix (it
    # resamples whole months across all assets at once to preserve their
    # real correlations) — so unlike the real backtest above, it can only
    # use the sub-period where every included asset actually has data. A
    # small (<10% weight), recently-launched (<5 years of its own history)
    # asset is dropped from Monte Carlo entirely rather than letting it
    # squeeze that shared window down to its own short lifetime — its own
    # weight is redistributed proportionally among the remaining assets.
    own_years = {t: rets_df[t].dropna().shape[0] / 12.0 for t in used_tickers}
    mc_excluded = [
        t
        for t in used_tickers
        if weights_by_ticker[t] < MC_EXCLUDE_MAX_WEIGHT and own_years[t] < MC_EXCLUDE_MIN_YEARS
    ]
    mc_tickers = [t for t in used_tickers if t not in mc_excluded]

    if mc_tickers:
        mc_raw_w = np.array([weights_by_ticker[t] for t in mc_tickers], dtype=float)
        mc_weights = mc_raw_w / mc_raw_w.sum()
        full_coverage_df = window_df[mc_tickers].dropna()
    else:
        mc_weights = np.array([])
        full_coverage_df = pd.DataFrame()

    mc_available = len(mc_tickers) > 0 and len(full_coverage_df) >= MIN_OVERLAP_MONTHS
    full_coverage_period = {
        "start": str(full_coverage_df.index.min()) if len(full_coverage_df) else None,
        "end": str(full_coverage_df.index.max()) if len(full_coverage_df) else None,
        "n_months": len(full_coverage_df),
        "n_years": round(len(full_coverage_df) / 12, 1),
    }

    mc_window_payload = None
    mc_nyear_payload = None
    mc_unavailable_reason = None

    if mc_available:
        rng = np.random.default_rng()
        R = full_coverage_df.values
        horizon_months = years * 12

        mc_win_best = np.empty(N_SIMS)
        mc_win_worst = np.empty(N_SIMS)
        fan_paths = np.empty((N_SIMS, horizon_months))

        for i in range(N_SIMS):
            path = _block_bootstrap_path(R, horizon_months, window_months, rng)
            port = path.dot(mc_weights)
            wealth = np.cumprod(1 + port)
            fan_paths[i] = wealth
            w_full = np.concatenate(([1.0], wealth))
            if horizon_months >= window_months:
                rw = w_full[window_months:] / w_full[:-window_months] - 1
                mc_win_best[i] = rw.max()
                mc_win_worst[i] = rw.min()
            else:
                mc_win_best[i] = wealth[-1] - 1
                mc_win_worst[i] = wealth[-1] - 1

        final_wealth = fan_paths[:, -1]
        cagr = final_wealth ** (12 / horizon_months) - 1
        fan_wealth = np.concatenate([np.ones((N_SIMS, 1)), fan_paths], axis=1)
        fan_pct = np.percentile(fan_wealth, [5, 25, 50, 75, 95], axis=0)

        mc_window_payload = {
            "n_sims": N_SIMS,
            "horizon_years": years,
            "window_months": window_months,
            "best": {**pct_summary(mc_win_best), "hist": hist(mc_win_best * 100)},
            "worst": {**pct_summary(mc_win_worst), "hist": hist(mc_win_worst * 100)},
        }
        mc_nyear_payload = {
            "n_sims": N_SIMS,
            "years": years,
            "total_return": pct_summary(final_wealth - 1),
            "cagr": pct_summary(cagr),
            "fan": {
                "months": list(range(horizon_months + 1)),
                "p5": [round(float(v), 4) for v in fan_pct[0]],
                "p25": [round(float(v), 4) for v in fan_pct[1]],
                "median": [round(float(v), 4) for v in fan_pct[2]],
                "p75": [round(float(v), 4) for v in fan_pct[3]],
                "p95": [round(float(v), 4) for v in fan_pct[4]],
            },
        }
    elif not mc_tickers:
        mc_unavailable_reason = (
            "Tous les actifs sélectionnés pèsent moins de "
            f"{MC_EXCLUDE_MAX_WEIGHT*100:.0f}% et ont moins de {MC_EXCLUDE_MIN_YEARS} ans "
            "d'historique — Monte Carlo indisponible."
        )
    else:
        mc_unavailable_reason = (
            f"Seuls {len(full_coverage_df)} mois couvrent simultanément les actifs retenus "
            f"pour Monte Carlo (minimum {MIN_OVERLAP_MONTHS}) — Monte Carlo indisponible."
        )

    return {
        "used_tickers": used_tickers,
        "weights_pct": {t: round(float(w) * 100, 2) for t, w in zip(used_tickers, weights)},
        "fees_pct": {t: round(fee_by_ticker[t], 3) for t in used_tickers},
        "failed": failed,
        "window_months": window_months,
        "backtest_period": {
            "start": str(window_df.index.min()),
            "end": str(window_df.index.max()),
            "n_months": len(window_df),
            "n_years": round(len(window_df) / 12, 1),
        },
        "full_coverage_period": full_coverage_period,
        "assets": {
            t: {
                "ann_return": round(float(ann_ret[t]) * 100, 2),
                "ann_vol": round(float(ann_vol[t]) * 100, 2),
            }
            for t in used_tickers
        },
        "portfolio": {
            "ann_return": round(float(port_ann_ret) * 100, 2),
            "ann_vol": round(float(port_ann_vol) * 100, 2),
        },
        "correlation": {
            r: {c: round(float(corr.loc[r, c]), 2) for c in corr.columns} for r in corr.index
        },
        "annual_returns": annual_returns,
        "asset_series": asset_series,
        "risk_metrics": {"portfolio": portfolio_risk, "assets": asset_risk},
        "crisis_analysis": {"portfolio": portfolio_crisis, "assets": asset_crisis},
        "resilience": resilience,
        "roll_window": {
            "window_months": window_months,
            "dates": [str(d) for d in roll_window.index],
            "values": [round(float(v) * 100, 2) for v in roll_window.values],
            "coverage_pct": [round(float(v) * 100, 1) for v in roll_coverage.values],
            "partial": [bool(v < 0.999) for v in roll_coverage.values],
            "missing": roll_missing,
            "median": round(float(roll_window.median()) * 100, 2),
            "std": round(float(roll_window.std()) * 100, 2),
            "best": {
                "date": str(best_idx),
                "start": str(best_idx - (window_months - 1)),
                "value": round(float(roll_window[best_idx]) * 100, 2),
                "partial": bool(roll_coverage.iloc[best_pos] < 0.999),
                "missing": roll_missing[best_pos],
            },
            "worst": {
                "date": str(worst_idx),
                "start": str(worst_idx - (window_months - 1)),
                "value": round(float(roll_window[worst_idx]) * 100, 2),
                "partial": bool(roll_coverage.iloc[worst_pos] < 0.999),
                "missing": roll_missing[worst_pos],
            },
        },
        "mc_available": mc_available,
        "mc_unavailable_reason": mc_unavailable_reason,
        "mc_excluded": mc_excluded,
        "mc_tickers": mc_tickers,
        "mc_window": mc_window_payload,
        "mc_nyear": mc_nyear_payload,
    }


# ---------------------------------------------------------------------------
# Portfolio optimization — for a fixed set of tickers, suggests long-only
# weights that either minimize historical variance or maximize the
# historical Sharpe ratio, using SLSQP against the sample covariance matrix.
# ---------------------------------------------------------------------------


def optimize_portfolio(portfolio, risk_free=RISK_FREE_RATE, fees=None, max_deviation_pct=15.0):
    """portfolio: list of {"ticker": str, "weight": float (percent)}. Suggested
    portfolios stay within `max_deviation_pct` percentage points of each
    asset's current weight, so the result is a tilt of the portfolio the user
    actually built rather than an unrelated allocation that happens to share
    the same tickers (a pure unconstrained optimum can — and often does —
    zero out a large existing position, which defeats the point of asking
    "how could *this* portfolio be improved").
    """
    merged_weights = {}
    for row in portfolio:
        ticker = str(row["ticker"]).strip().upper()
        weight = float(row.get("weight", 0))
        if not ticker or weight <= 0:
            continue
        merged_weights[ticker] = merged_weights.get(ticker, 0.0) + weight
    if len(merged_weights) < 2:
        raise SimulationError("Il faut au moins 2 actifs valides pour optimiser un portefeuille.")

    tickers = list(merged_weights.keys())
    eur_series, failed = _fetch_all_eur_series(tickers)
    used = [t for t in tickers if t in eur_series]
    if len(used) < 2:
        raise SimulationError("Au moins 2 des actifs sélectionnés doivent être valides pour optimiser.")

    raw_w = np.array([merged_weights[t] for t in used], dtype=float)
    current_weights = raw_w / raw_w.sum()

    fees = fees or {}
    fee_by_ticker = {t: fees[t] if t in fees else ALL_FEES.get(t, DEFAULT_TER) for t in used}

    price_df = pd.DataFrame({t: eur_series[t] for t in used})
    rets_raw = price_df.pct_change()
    rets = rets_raw.dropna()
    fee_monthly = pd.Series({t: fee_by_ticker[t] / 100.0 / 12.0 for t in used})
    rets = rets.sub(fee_monthly, axis=1)
    if len(rets) < MIN_MONTHS_FOR_OPTIMIZATION:
        # name the actual bottleneck(s) so the message is actionable, not just a number
        first_valid = {t: rets_raw[t].first_valid_index() for t in used}
        latest_start = max(first_valid.values())
        bottlenecks = sorted(t for t, d in first_valid.items() if d == latest_start)
        raise SimulationError(
            f"Historique commun trop court ({len(rets)} mois) pour une optimisation fiable "
            f"— {MIN_MONTHS_FOR_OPTIMIZATION} mois (2 ans) minimum requis, sans quoi la matrice de "
            f"corrélations n'est que du bruit statistique. {', '.join(bottlenecks)} limite{'nt' if len(bottlenecks)>1 else ''} "
            f"la période commune depuis {latest_start}. Retirez-le/les de l'optimisation ou attendez davantage d'historique."
        )

    mu = rets.mean().values * 12
    cov = rets.cov().values * 12
    n = len(used)

    deviation = max_deviation_pct / 100.0
    lower = np.clip(current_weights - deviation, 0.0, 1.0)
    upper = np.clip(current_weights + deviation, 0.0, 1.0)
    if lower.sum() > 1.0 + 1e-9:
        raise SimulationError(
            "Écart maximal autorisé trop faible pour ces pondérations de départ — augmentez-le."
        )
    if upper.sum() < 1.0 - 1e-9:
        raise SimulationError(
            "Écart maximal autorisé trop faible pour atteindre 100% du portefeuille — augmentez-le."
        )
    bounds = list(zip(lower.tolist(), upper.tolist()))
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    x0 = np.clip(current_weights, lower, upper)
    x0 = x0 / x0.sum()

    def port_vol(w):
        return float(np.sqrt(w @ cov @ w))

    def neg_sharpe(w):
        v = port_vol(w)
        if v < 1e-9:
            return 1e9
        return -((w @ mu) - risk_free) / v

    min_var_res = minimize(port_vol, x0, method="SLSQP", bounds=bounds, constraints=constraints)
    max_sharpe_res = minimize(neg_sharpe, x0, method="SLSQP", bounds=bounds, constraints=constraints)

    def summarize(w):
        w = np.clip(w, 0, None)
        total = w.sum()
        w = w / total if total > 1e-9 else current_weights
        # geometric annualization from the actual monthly portfolio-return
        # series — matches run_simulation's methodology exactly, so this
        # figure is directly comparable to the main report's. (w @ mu, the
        # linear/arithmetic annualization used inside the optimizer's own
        # objective, systematically overstates the compounded return an
        # investor would actually realize.)
        port_ret_series = rets.values @ w
        r = float((1 + port_ret_series.mean()) ** 12 - 1)
        v = port_vol(w)
        sharpe = (r - risk_free) / v if v > 1e-9 else None
        return {
            "weights_pct": {t: round(float(wi) * 100, 2) for t, wi in zip(used, w)},
            "ann_return": round(r * 100, 2),
            "ann_vol": round(v * 100, 2),
            "sharpe": round(sharpe, 2) if sharpe is not None else None,
        }

    return {
        "used_tickers": used,
        "failed": failed,
        "max_deviation_pct": max_deviation_pct,
        "period": {
            "start": str(rets.index.min()),
            "end": str(rets.index.max()),
            "n_months": len(rets),
            "n_years": round(len(rets) / 12, 1),
        },
        "current": summarize(current_weights),
        "min_variance": summarize(min_var_res.x),
        "max_sharpe": summarize(max_sharpe_res.x),
    }


# ---------------------------------------------------------------------------
# ETF picker stats (return/volatility) — computed for the whole catalogue in
# the background, cached to disk, refreshed lazily so page loads never block
# on a 60-ticker scrape.
# ---------------------------------------------------------------------------


def compute_ann_stats(series, years=STATS_LOOKBACK_YEARS, fee_annual_pct=0.0):
    rets = series.pct_change().dropna()
    if len(rets) == 0:
        raise SimulationError("historique insuffisant")
    rets = rets - fee_annual_pct / 100.0 / 12.0
    window = years * 12
    used = rets.tail(window) if len(rets) > window else rets
    ann_return = (1 + used.mean()) ** 12 - 1
    ann_vol = used.std() * np.sqrt(12)
    return float(ann_return), float(ann_vol), float(len(used) / 12)


def _compute_one_etf_stats(ticker):
    try:
        series = _to_eur_series(ticker)
        fee = ALL_FEES.get(ticker, DEFAULT_TER)
        ann_return, ann_vol, years_used = compute_ann_stats(series, fee_annual_pct=fee)
        return ticker, {
            "ann_return": round(ann_return * 100, 2),
            "ann_vol": round(ann_vol * 100, 2),
            "years": round(years_used, 1),
            "ter": fee,
        }
    except Exception as exc:
        return ticker, {"error": str(exc)}


def _compute_all_etf_stats(tickers):
    results = {}
    with ThreadPoolExecutor(max_workers=STATS_MAX_WORKERS) as pool:
        futures = [pool.submit(_compute_one_etf_stats, t) for t in tickers]
        for future in as_completed(futures):
            ticker, stat = future.result()
            results[ticker] = stat
    return results


def _load_stats_cache():
    if STATS_CACHE_FILE.exists():
        try:
            return json.loads(STATS_CACHE_FILE.read_text())
        except Exception:
            return None
    return None


def _save_stats_cache(payload):
    STATS_CACHE_FILE.write_text(json.dumps(payload))


_stats_refresh_lock = threading.Lock()
_stats_refreshing = False


def _refresh_stats_async(tickers):
    global _stats_refreshing
    with _stats_refresh_lock:
        if _stats_refreshing:
            return
        _stats_refreshing = True

    def _run():
        global _stats_refreshing
        try:
            stats = _compute_all_etf_stats(tickers)
            _save_stats_cache({"computed_at": time.time(), "stats": stats})
        finally:
            with _stats_refresh_lock:
                _stats_refreshing = False

    threading.Thread(target=_run, daemon=True).start()


def get_etf_stats(tickers):
    """Stale-while-revalidate: always return instantly if a cache exists
    (even if stale), kicking off a non-blocking background refresh; only
    the very first call ever (no disk cache yet) has to compute inline.
    """
    cached = _load_stats_cache()
    now = time.time()
    if cached is None:
        stats = _compute_all_etf_stats(tickers)
        payload = {"computed_at": now, "stats": stats}
        _save_stats_cache(payload)
        return payload
    if now - cached.get("computed_at", 0) > STATS_TTL_SECONDS:
        _refresh_stats_async(tickers)
    return cached
