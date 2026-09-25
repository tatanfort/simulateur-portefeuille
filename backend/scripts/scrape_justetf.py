"""Refresh backend/etf_metadata.json from justETF's fund database.

Run this by hand whenever you want to refresh PEA eligibility / distribution
policy / currency / domicile / replication data for the catalogue in
etfs.py. It is NOT called automatically by the app - re-run it yourself
periodically (fund line-ups and PEA eligibility do change over time).

    cd backend
    python3 scripts/scrape_justetf.py

What this does and why it's built this way
--------------------------------------------
justETF's search/filter tool (the only place PEA eligibility is exposed) is
entirely driven by an internal AJAX endpoint under /search.html - every
single result row, for every filter combination, comes from a POST to a URL
containing `_wicket=1`. Their own robots.txt explicitly disallows crawling
that exact pattern (`Disallow: /*/search.html*_wicket=1*`), and individual
fund profile pages (which ARE crawlable) don't expose PEA eligibility as a
structured field at all - only whatever happens to appear in the fund's own
name.

So getting real PEA-eligibility data at all means using that AJAX endpoint
directly, same as the justETF web page itself does when you click their
"PEA" filter checkbox in a browser - this script is not exploring hidden or
authenticated data, or bypassing any access control, just replicating one
public, unauthenticated interaction their own site performs continuously.
It is meant to be run occasionally, by hand, for personal portfolio
analysis - not on a tight automated schedule and not to redistribute
justETF's data. Consider this a personal-use exception to the disallow
rule, made deliberately and knowingly - if that's not a trade-off you're
comfortable with, don't run this script; the app works fine without it,
just with PEA eligibility left unset for anything not already known.

Matching a justETF row to a catalogue ticker is done by base ticker (before
any Yahoo-style exchange suffix) plus a name-token-overlap sanity check,
since bare ticker mnemonics can collide across exchanges (verified during
development - e.g. our GOVT.AX or CEMA.L tickers happen to collide with
unrelated European funds sharing the same mnemonic). A candidate is only
accepted if it shares enough meaningful words with our own catalogue name;
otherwise it's left unmatched rather than guessed.
"""

import json
import re
import sys
import time
import unicodedata
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from etfs import ALL_FEES, ALL_TICKERS  # noqa: E402

OUTPUT_FILE = Path(__file__).resolve().parent.parent / "etf_metadata.json"
BASE_URL = "https://www.justetf.com/fr/search.html"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

STOPWORDS = {
    "ucits", "etf", "etfs", "the", "of", "fund", "trust", "acc", "dist", "eur", "usd", "gbp",
    "hedged", "hedge", "swap", "physical", "physique", "core", "1c", "1d", "a", "de", "en",
    # index/provider families: shared by dozens of otherwise-unrelated funds,
    # so they'd otherwise inflate the overlap score without meaning anything
    # (this is what let "iShares MSCI EM Asia" wrongly match "iShares MSCI
    # World Swap" during development - both share only "ishares"+"msci")
    "ishares", "msci", "amundi", "vanguard", "spdr", "invesco", "xtrackers", "lyxor",
    "wisdomtree", "globalx", "global", "ftse", "stoxx", "s&p", "sp", "russell", "select",
    "sector", "index", "select", "screened", "esg", "solutions",
}


def _tokens(name):
    norm = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    words = re.findall(r"[a-z0-9]+", norm.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def _names_match(a, b):
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return False
    overlap = ta & tb
    return len(overlap) >= 2 or len(overlap) / min(len(ta), len(tb)) >= 0.6


def _fetch_rows(session, fetch_url, etfs_params):
    payload = {
        "draw": 1, "start": 0, "length": -1,
        "lang": "fr", "country": "FR", "universeType": "private", "defaultCurrency": "EUR",
        "etfsParams": etfs_params,
    }
    resp = session.post(fetch_url, data=payload, timeout=30)
    resp.raise_for_status()
    return resp.json().get("data", [])


def _parse_pct(s):
    if not s:
        return None
    try:
        return float(s.replace("%", "").replace(",", ".").strip())
    except ValueError:
        return None


def _parse_size(s):
    if not s:
        return None
    # thousands separator is often a narrow no-break space (U+202F), not a
    # plain space - strip everything but digits/comma/minus to be safe
    cleaned = re.sub(r"[^\d,.-]", "", s).replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _parse_date(s):
    if not s or "/" not in s:
        return None
    d, m, y = s.split("/")
    return f"{y}-{m}-{d}"


def _clean_html(s):
    return re.sub(r"<[^>]+>", " ", s or "").strip()


def main():
    print(f"Catalogue: {len(ALL_TICKERS)} tickers to match against justETF.\n")
    session = requests.Session()
    session.headers.update({"User-Agent": UA})

    print("Fetching search page to discover the AJAX endpoint...")
    initial = session.get(BASE_URL, params={"search": "ETFS"}, timeout=30)
    initial.raise_for_status()
    m = re.search(r"fetchCallbackUrl = '([^']+)'", initial.text)
    if not m:
        print("Could not find the AJAX endpoint URL - justETF likely changed their page structure.")
        sys.exit(1)
    fetch_url = "https://www.justetf.com" + m.group(1)

    print("Fetching the full ETF universe (one request, ~4000+ funds)...")
    universe = _fetch_rows(session, fetch_url, "search=ETFS&query=")
    print(f"  -> {len(universe)} funds")
    time.sleep(1)

    print("Fetching the PEA-eligible fund list...")
    pea_rows = _fetch_rows(session, fetch_url, "search=ETFS&pea=true&query=")
    pea_isins = {r["isin"] for r in pea_rows}
    print(f"  -> {len(pea_isins)} PEA-eligible funds\n")

    by_base_ticker = {}
    for row in universe:
        by_base_ticker.setdefault(row["ticker"].upper(), []).append(row)

    matched, unmatched = {}, []
    for ticker, name in ALL_TICKERS.items():
        if "." not in ticker:
            # A bare ticker (no exchange suffix) in our catalogue always means
            # the US-listed share class - justETF is a European-fund-centric
            # database, so any same-mnemonic hit there is a different, foreign
            # sibling fund (verified during development: our bare "SMH" - the
            # US VanEck Semiconductor ETF - matched a same-named but
            # Irish-domiciled UCITS share class with its own ISIN). US-listed
            # '40 Act funds are never PEA-eligible anyway, so nothing of value
            # would come from looking this up.
            unmatched.append(ticker)
            continue
        base = ticker.split(".")[0].upper()
        candidates = by_base_ticker.get(base, [])
        best = next((c for c in candidates if _names_match(c["name"], name)), None)
        if not best:
            unmatched.append(ticker)
            continue

        fund_currency = _clean_html(best["fundCurrency"])
        hedged = "couvert" in fund_currency.lower() or "hedged" in fund_currency.lower()
        currency = re.sub(r"\s*(couvert|hedged)\s*", "", fund_currency, flags=re.IGNORECASE).strip()

        dist_raw = (best.get("distributionPolicy") or "").lower()
        distribution = "Capitalisant" if "capitalisation" in dist_raw else (
            "Distribuant" if "distribution" in dist_raw else None
        )

        matched[ticker] = {
            "isin": best["isin"],
            "pea": best["isin"] in pea_isins,
            "distribution": distribution,
            "currency": currency or None,
            "hedged": hedged,
            "domicile": best.get("domicileCountry") or None,
            "replication": _clean_html(best.get("replicationMethod", "")) or None,
            "inception_date": _parse_date(best.get("inceptionDate")),
            "fund_size_mln": _parse_size(best.get("fundSize")),
            "ter_justetf": _parse_pct(best.get("ter")),
            "matched_name": best["name"],
        }

    payload = {
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "justetf.com",
        "etfs": matched,
    }
    OUTPUT_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    n_pea = sum(1 for m in matched.values() if m["pea"])
    print(f"Matched {len(matched)}/{len(ALL_TICKERS)} catalogue tickers ({n_pea} PEA-eligible).")
    print(f"Written to {OUTPUT_FILE}")
    if unmatched:
        print(f"\n{len(unmatched)} tickers not found on justETF (likely US-listed funds, absent from")
        print("their mostly-European database, or a ticker/name mismatch worth checking by hand):")
        print("  " + ", ".join(sorted(unmatched)))


if __name__ == "__main__":
    main()
