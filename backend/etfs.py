"""Curated list of major, liquid ETFs available for the portfolio builder.

Not exhaustive (there are thousands of ETFs) - this covers the major
building blocks across regions, factors, sectors, themes, fixed income and
commodities that a retail investor would realistically combine.

Each entry carries "ter" - its annual expense ratio (Total Expense Ratio,
in percent) - sourced from provider fact sheets where known, or a
reasonable category-typical estimate otherwise. It is only a starting
point: the frontend lets the user override it per position, and that
user-supplied value is what actually feeds every calculation server-side.

Each entry also carries "geo" - an approximate country/region breakdown
(percent, summing to ~100) used for the portfolio's geographic-exposure
analysis. These are typical/representative allocations for well-known
index families (MSCI, FTSE, S&P...) or, for single-country/sector funds,
simply 100% of that country - not live holdings data, since none of the
data sources this app already uses (Yahoo Finance price history) expose
fund holdings. Commodity funds have no equity-country exposure and are
bucketed under "Matieres premieres" instead of a country.
"""

DEFAULT_TER = 0.20  # fallback used for manually-typed tickers not in this catalogue

# Canonical display/color order for the geographic-exposure chart - anything
# encountered that isn't listed here (a typo-guard, not expected in practice)
# just sorts after these, alphabetically.
GEO_REGIONS_ORDER = [
    "Etats-Unis",
    "Zone euro (diversifie)",
    "France",
    "Allemagne",
    "Royaume-Uni",
    "Italie",
    "Espagne",
    "Suisse",
    "Pays-Bas",
    "Europe (autres)",
    "Japon",
    "Chine",
    "Taiwan",
    "Inde",
    "Coree du Sud",
    "Hong Kong",
    "Singapour",
    "Asie (autres)",
    "Australie",
    "Nouvelle-Zelande",
    "Canada",
    "Bresil",
    "Mexique",
    "Israel",
    "Marches emergents (diversifie)",
    "Monde developpe (diversifie)",
    "Monde (diversifie)",
    "Matieres premieres",
    "Fonds a taux fixe",
    "Non classe",
]

# The country/region labels above are mutually exclusive at the COUNTRY
# level, but a flat list of ~30 of them mixes countries, sub-regions and
# "diversified" catch-alls at the same visual level - e.g. "France" and
# "Europe (autres)" both belong under the same "Europe" umbrella, but a flat
# bar chart shows them as unrelated slices. GEO_ZONE_OF rolls every label
# above up into one of a handful of mutually-exclusive, non-overlapping
# macro-zones (continent-scale, the level at which "is my portfolio
# geographically diversified?" is actually answered at a glance); the
# country-level labels remain available as a drill-down within each zone.
GEO_ZONES_ORDER = [
    "Amerique du Nord",
    "Europe",
    "Asie-Pacifique",
    "Amerique latine",
    "Moyen-Orient",
    "Marches emergents / Monde (non detaille)",
    "Matieres premieres",
    "Fonds a taux fixe",
    "Non classe",
]

GEO_ZONE_OF = {
    "Etats-Unis": "Amerique du Nord",
    "Canada": "Amerique du Nord",
    "France": "Europe",
    "Allemagne": "Europe",
    "Royaume-Uni": "Europe",
    "Italie": "Europe",
    "Espagne": "Europe",
    "Suisse": "Europe",
    "Pays-Bas": "Europe",
    "Europe (autres)": "Europe",
    "Zone euro (diversifie)": "Europe",
    "Japon": "Asie-Pacifique",
    "Chine": "Asie-Pacifique",
    "Taiwan": "Asie-Pacifique",
    "Inde": "Asie-Pacifique",
    "Coree du Sud": "Asie-Pacifique",
    "Hong Kong": "Asie-Pacifique",
    "Singapour": "Asie-Pacifique",
    "Asie (autres)": "Asie-Pacifique",
    "Australie": "Asie-Pacifique",
    "Nouvelle-Zelande": "Asie-Pacifique",
    "Bresil": "Amerique latine",
    "Mexique": "Amerique latine",
    "Israel": "Moyen-Orient",
    "Marches emergents (diversifie)": "Marches emergents / Monde (non detaille)",
    "Monde developpe (diversifie)": "Marches emergents / Monde (non detaille)",
    "Monde (diversifie)": "Marches emergents / Monde (non detaille)",
    "Matieres premieres": "Matieres premieres",
    "Fonds a taux fixe": "Fonds a taux fixe",
    "Non classe": "Non classe",
}

CATEGORIES = [
    {
        "name": "Actions US - large cap",
        "etfs": [
            {"ticker": "SPY", "name": "SPDR S&P 500 ETF Trust", "ter": 0.09, "geo": {"Etats-Unis": 100}},
            {"ticker": "VOO", "name": "Vanguard S&P 500 ETF", "ter": 0.03, "geo": {"Etats-Unis": 100}},
            {"ticker": "IVV", "name": "iShares Core S&P 500 ETF", "ter": 0.03, "geo": {"Etats-Unis": 100}},
            {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF", "ter": 0.03, "geo": {"Etats-Unis": 100}},
            {"ticker": "QQQ", "name": "Invesco QQQ Trust (Nasdaq 100)", "ter": 0.20, "geo": {"Etats-Unis": 100}},
            {"ticker": "DIA", "name": "SPDR Dow Jones Industrial Average ETF", "ter": 0.16, "geo": {"Etats-Unis": 100}},
            {"ticker": "IWM", "name": "iShares Russell 2000 ETF (small cap)", "ter": 0.19, "geo": {"Etats-Unis": 100}},
            {"ticker": "PSP5.PA", "name": "Amundi PEA S&P 500 UCITS ETF Acc", "ter": 0.12, "geo": {"Etats-Unis": 100}},
            {"ticker": "PUST.PA", "name": "Amundi PEA Nasdaq-100 UCITS ETF Acc", "ter": 0.30, "geo": {"Etats-Unis": 100}},
            {"ticker": "CU2.PA", "name": "Amundi PEA MSCI USA ESG Selection UCITS ETF Acc", "ter": 0.35, "geo": {"Etats-Unis": 100}},
            {"ticker": "AHYI.DE", "name": "Amundi PEA Dow Jones Industrial Average UCITS ETF Dist", "ter": 0.45, "geo": {"Etats-Unis": 100}},
            {"ticker": "ESD.PA", "name": "BNP Paribas Easy S&P 500 UCITS ETF USD (Acc)", "ter": 0.14, "geo": {"Etats-Unis": 100}},
            {"ticker": "ESE.PA", "name": "BNP Paribas Easy S&P 500 UCITS ETF EUR", "ter": 0.14, "geo": {"Etats-Unis": 100}},
            {"ticker": "ESEA.DE", "name": "BNP Paribas Easy S&P 500 UCITS ETF", "ter": 0.14, "geo": {"Etats-Unis": 100}},
            {"ticker": "ESEH.PA", "name": "BNP Paribas Easy S&P 500 UCITS ETF EUR Hedged", "ter": 0.14, "geo": {"Etats-Unis": 100}},
            {"ticker": "P500H.PA", "name": "Amundi PEA S&P 500 Screened UCITS ETF EUR Hedged Acc", "ter": 0.28, "geo": {"Etats-Unis": 100}},
            {"ticker": "PANX.PA", "name": "Amundi PEA US Tech Screened UCITS ETF Acc", "ter": 0.3, "geo": {"Etats-Unis": 100}},
            {"ticker": "PE500.PA", "name": "Amundi PEA S&P 500 Screened UCITS ETF Acc", "ter": 0.25, "geo": {"Etats-Unis": 100}},
            {"ticker": "PNAS.PA", "name": "Amundi PEA Nasdaq-100 UCITS ETF UCITS ETF S Acc", "ter": 0.3, "geo": {"Etats-Unis": 100}},
            {"ticker": "PSPH.PA", "name": "Amundi PEA S&P 500 UCITS ETF EUR Hedged Acc", "ter": 0.12, "geo": {"Etats-Unis": 100}},
            {"ticker": "PSPS.PA", "name": "Amundi PEA S&P 500 Screened UCITS ETF S Acc", "ter": 0.25, "geo": {"Etats-Unis": 100}},
            {"ticker": "RS2K.PA", "name": "Amundi Russell 2000 UCITS ETF EUR (C)", "ter": 0.35, "geo": {"Etats-Unis": 100}},
            {"ticker": "SPEA.PA", "name": "iShares S&P 500 Swap PEA UCITS ETF EUR (Acc)", "ter": 0.1, "geo": {"Etats-Unis": 100}},
        ],
    },
    {
        "name": "Actions Monde",
        "etfs": [
            {"ticker": "CW8.PA", "name": "Amundi MSCI World UCITS ETF Acc", "ter": 0.38, "geo": {"Etats-Unis": 72, "Japon": 6, "Royaume-Uni": 4, "France": 3, "Canada": 3, "Suisse": 2.5, "Allemagne": 2.5, "Australie": 2, "Pays-Bas": 1.3, "Europe (autres)": 2.2, "Asie (autres)": 1.5}},
            {"ticker": "DCAM.PA", "name": "Amundi PEA Monde (MSCI World) UCITS ETF Acc", "ter": 0.2, "geo": {"Etats-Unis": 72, "Japon": 6, "Royaume-Uni": 4, "France": 3, "Canada": 3, "Suisse": 2.5, "Allemagne": 2.5, "Australie": 2, "Pays-Bas": 1.3, "Europe (autres)": 2.2, "Asie (autres)": 1.5}},
            {"ticker": "EWLD.PA", "name": "Amundi MSCI World Swap UCITS ETF EUR Dist", "ter": 0.38, "geo": {"Etats-Unis": 72, "Japon": 6, "Royaume-Uni": 4, "France": 3, "Canada": 3, "Suisse": 2.5, "Allemagne": 2.5, "Australie": 2, "Pays-Bas": 1.3, "Europe (autres)": 2.2, "Asie (autres)": 1.5}},
            {"ticker": "GPEA.PA", "name": "Amundi PEA Global (MSCI ACWI) UCITS ETF Acc", "ter": 0.3, "geo": {"Etats-Unis": 72, "Japon": 6, "Royaume-Uni": 4, "France": 3, "Canada": 3, "Suisse": 2.5, "Allemagne": 2.5, "Australie": 2, "Pays-Bas": 1.3, "Europe (autres)": 2.2, "Asie (autres)": 1.5}},
            {"ticker": "MLUX.PA", "name": "Amundi PEA Luxe Monde UCITS ETF Acc", "ter": 0.3, "geo": {"France": 35, "Italie": 15, "Etats-Unis": 20, "Europe (autres)": 20, "Asie (autres)": 10}},
            {"ticker": "WPEA.PA", "name": "iShares MSCI World Swap PEA UCITS ETF EUR (Acc)", "ter": 0.2, "geo": {"Etats-Unis": 72, "Japon": 6, "Royaume-Uni": 4, "France": 3, "Canada": 3, "Suisse": 2.5, "Allemagne": 2.5, "Australie": 2, "Pays-Bas": 1.3, "Europe (autres)": 2.2, "Asie (autres)": 1.5}},
            {"ticker": "WPEH.PA", "name": "iShares MSCI World Swap PEA UCITS ETF EUR Hedged (Acc)", "ter": 0.2, "geo": {"Etats-Unis": 72, "Japon": 6, "Royaume-Uni": 4, "France": 3, "Canada": 3, "Suisse": 2.5, "Allemagne": 2.5, "Australie": 2, "Pays-Bas": 1.3, "Europe (autres)": 2.2, "Asie (autres)": 1.5}},
        ],
    },
    {
        "name": "Actions US - facteurs / styles",
        "etfs": [
            {"ticker": "SPMO", "name": "Invesco S&P 500 Momentum ETF", "ter": 0.13, "geo": {"Etats-Unis": 100}},
            {"ticker": "MTUM", "name": "iShares MSCI USA Momentum Factor ETF", "ter": 0.15, "geo": {"Etats-Unis": 100}},
            {"ticker": "VLUE", "name": "iShares MSCI USA Value Factor ETF", "ter": 0.15, "geo": {"Etats-Unis": 100}},
            {"ticker": "QUAL", "name": "iShares MSCI USA Quality Factor ETF", "ter": 0.15, "geo": {"Etats-Unis": 100}},
            {"ticker": "USMV", "name": "iShares MSCI USA Min Vol Factor ETF", "ter": 0.15, "geo": {"Etats-Unis": 100}},
            {"ticker": "VYM", "name": "Vanguard High Dividend Yield ETF", "ter": 0.06, "geo": {"Etats-Unis": 100}},
            {"ticker": "SCHD", "name": "Schwab US Dividend Equity ETF", "ter": 0.06, "geo": {"Etats-Unis": 100}},
            {"ticker": "USVE.PA", "name": "Amundi PEA MSCI USA Value Advanced UCITS ETF Acc", "ter": 0.5, "geo": {"Etats-Unis": 100}},
        ],
    },
    {
        "name": "Actions US - secteurs",
        "etfs": [
            {"ticker": "XLK", "name": "Technology Select Sector SPDR", "ter": 0.09, "geo": {"Etats-Unis": 100}},
            {"ticker": "SMH", "name": "VanEck Semiconductor ETF", "ter": 0.35, "geo": {"Etats-Unis": 65, "Taiwan": 20, "Pays-Bas": 10, "Asie (autres)": 5}},
            {"ticker": "XLF", "name": "Financial Select Sector SPDR", "ter": 0.09, "geo": {"Etats-Unis": 100}},
            {"ticker": "XLE", "name": "Energy Select Sector SPDR", "ter": 0.09, "geo": {"Etats-Unis": 100}},
            {"ticker": "XLY", "name": "Consumer Discretionary Select SPDR", "ter": 0.09, "geo": {"Etats-Unis": 100}},
            {"ticker": "XLP", "name": "Consumer Staples Select SPDR", "ter": 0.09, "geo": {"Etats-Unis": 100}},
            {"ticker": "XLI", "name": "Industrial Select Sector SPDR", "ter": 0.09, "geo": {"Etats-Unis": 100}},
            {"ticker": "XLU", "name": "Utilities Select Sector SPDR", "ter": 0.09, "geo": {"Etats-Unis": 100}},
            {"ticker": "XLRE", "name": "Real Estate Select Sector SPDR", "ter": 0.09, "geo": {"Etats-Unis": 100}},
            {"ticker": "COSE.PA", "name": "Amundi PEA S&P US Consumer Staples Screened UCITS ETF Acc", "ter": 0.5, "geo": {"Etats-Unis": 100}},
            {"ticker": "PDJE.PA", "name": "Amundi PEA S&P US Industrials Screened UCITS ETF Acc", "ter": 0.5, "geo": {"Etats-Unis": 100}},
        ],
    },
    {
        "name": "Actions internationales - large",
        "etfs": [
            {"ticker": "EFA", "name": "iShares MSCI EAFE ETF", "ter": 0.32, "geo": {"Japon": 22, "Royaume-Uni": 14, "France": 11, "Suisse": 10, "Allemagne": 8, "Australie": 7, "Pays-Bas": 4, "Europe (autres)": 24}},
            {"ticker": "VEA", "name": "Vanguard FTSE Developed Markets ETF", "ter": 0.05, "geo": {"Japon": 21, "Royaume-Uni": 13, "Canada": 7, "France": 8, "Suisse": 7, "Allemagne": 7, "Australie": 6, "Europe (autres)": 31}},
            {"ticker": "EEM", "name": "iShares MSCI Emerging Markets ETF", "ter": 0.68, "geo": {"Chine": 26, "Taiwan": 18, "Inde": 18, "Coree du Sud": 12, "Bresil": 5, "Marches emergents (diversifie)": 21}},
            {"ticker": "VWO", "name": "Vanguard FTSE Emerging Markets ETF", "ter": 0.07, "geo": {"Chine": 26, "Taiwan": 18, "Inde": 18, "Coree du Sud": 12, "Bresil": 5, "Marches emergents (diversifie)": 21}},
            {"ticker": "IEMG", "name": "iShares Core MSCI Emerging Markets ETF", "ter": 0.09, "geo": {"Chine": 26, "Taiwan": 18, "Inde": 18, "Coree du Sud": 12, "Bresil": 5, "Marches emergents (diversifie)": 21}},
            {"ticker": "PAEEM.PA", "name": "Amundi PEA Emergent (MSCI Emerging) ESG Transition UCITS ETF Acc", "ter": 0.30, "geo": {"Chine": 26, "Taiwan": 18, "Inde": 18, "Coree du Sud": 12, "Bresil": 5, "Marches emergents (diversifie)": 21}},
            {"ticker": "EXCS.L", "name": "iShares MSCI EM ex China UCITS ETF", "ter": 0.20, "geo": {"Taiwan": 22, "Inde": 22, "Coree du Sud": 15, "Bresil": 7, "Marches emergents (diversifie)": 34}},
            {"ticker": "PAASI.PA", "name": "Amundi PEA Asie Emergente (MSCI Emerging Asia) Screened UCITS ETF EUR (C/D)", "ter": 0.3, "geo": {"Chine": 40, "Inde": 25, "Taiwan": 20, "Coree du Sud": 15}},
            {"ticker": "PEMS.PA", "name": "Amundi PEA Emergent (MSCI Emerging) ESG Transition UCITS ETF S - Acc", "ter": 0.3, "geo": {"Chine": 26, "Taiwan": 18, "Inde": 18, "Coree du Sud": 12, "Bresil": 5, "Marches emergents (diversifie)": 21}},
            {"ticker": "PLEM.PA", "name": "Amundi PEA Emergent EMEA (MSCI Emerging EMEA) ESG Transition UCITS ETF Acc", "ter": 0.55, "geo": {"Europe (autres)": 40, "Moyen-Orient": 30, "Marches emergents (diversifie)": 30}},
        ],
    },
    {
        "name": "Actions Europe",
        "etfs": [
            {"ticker": "VGK", "name": "Vanguard FTSE Europe ETF", "ter": 0.08, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "EZU", "name": "iShares MSCI Eurozone ETF", "ter": 0.50, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "FEZ", "name": "SPDR EURO STOXX 50 ETF", "ter": 0.29, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "IEUR", "name": "iShares Core MSCI Europe ETF", "ter": 0.09, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "SXR7.DE", "name": "iShares Core MSCI EMU UCITS ETF EUR Acc", "ter": 0.12, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "CAC.PA", "name": "Amundi CAC 40 UCITS ETF Dist", "ter": 0.25, "geo": {"France": 100}},
            {"ticker": "EWG", "name": "iShares MSCI Germany ETF", "ter": 0.50, "geo": {"Allemagne": 100}},
            {"ticker": "EWQ", "name": "iShares MSCI France ETF", "ter": 0.50, "geo": {"France": 100}},
            {"ticker": "EWU", "name": "iShares MSCI United Kingdom ETF", "ter": 0.50, "geo": {"Royaume-Uni": 100}},
            {"ticker": "EWI", "name": "iShares MSCI Italy ETF", "ter": 0.50, "geo": {"Italie": 100}},
            {"ticker": "EWP", "name": "iShares MSCI Spain ETF", "ter": 0.50, "geo": {"Espagne": 100}},
            {"ticker": "EWL", "name": "iShares MSCI Switzerland ETF", "ter": 0.50, "geo": {"Suisse": 100}},
            {"ticker": "0CAC.PA", "name": "Ossiam CAC 40 NR UCITS ETF 1C/A (EUR)", "ter": 0.18, "geo": {"France": 100}},
            {"ticker": "0EMU.PA", "name": "Ossiam MSCI EMU UCITS ETF 1C", "ter": 0.12, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "50E.PA", "name": "HSBC EURO STOXX 50 UCITS ETF EUR", "ter": 0.05, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "AEMUS.PA", "name": "BNP Paribas Easy ESG Enhanced EMU UCITS ETF Acc", "ter": 0.1, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "AEXX.PA", "name": "Amundi Euro Stoxx UCITS ETF Dist", "ter": 0.1, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "B41J.DE", "name": "Global X European Infrastructure Development UCITS ETF EUR Accumulating", "ter": 0.47, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "BNKE.PA", "name": "Amundi Euro Stoxx Banks UCITS ETF Acc", "ter": 0.3, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "C007.DE", "name": "Amundi MDAX ESG UCITS ETF UCITS ETF Dist", "ter": 0.3, "geo": {"Allemagne": 100}},
            {"ticker": "C40.PA", "name": "Amundi CAC 40 ESG UCITS ETF Acc", "ter": 0.25, "geo": {"France": 100}},
            {"ticker": "C4D.PA", "name": "Amundi CAC 40 ESG UCITS ETF Dist", "ter": 0.25, "geo": {"France": 100}},
            {"ticker": "C50.PA", "name": "Amundi Core EURO STOXX 50 UCITS ETF EUR Acc", "ter": 0.09, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "CA40.PA", "name": "Amundi CAC 40 UCITS ETF S - Acc", "ter": 0.25, "geo": {"France": 100}},
            {"ticker": "CACC.PA", "name": "Amundi CAC 40 UCITS ETF Acc", "ter": 0.25, "geo": {"France": 100}},
            {"ticker": "CD5.PA", "name": "Amundi Core EURO STOXX 50 UCITS ETF EUR Dist", "ter": 0.09, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "CEUD.MI", "name": "iShares Core MSCI EMU UCITS ETF EUR (Dist)", "ter": 0.12, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "CF1.PA", "name": "Amundi CAC Transition Climat UCITS ETF", "ter": 0.25, "geo": {"France": 100}},
            {"ticker": "CG1.PA", "name": "Amundi ETF DAX UCITS ETF DR", "ter": 0.1, "geo": {"Allemagne": 100}},
            {"ticker": "CM5E.PA", "name": "CM-AM Euro Stoxx 50 UCITS ETF ", "ter": 0.09, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "CMU.PA", "name": "Amundi MSCI EMU ESG Selection UCITS ETF EUR Acc", "ter": 0.25, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "CMUD.PA", "name": "Amundi MSCI EMU ESG Selection UCITS ETF EUR Dist", "ter": 0.25, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "CS1.PA", "name": "Amundi IBEX 35 UCITS ETF Acc", "ter": 0.3, "geo": {"Espagne": 100}},
            {"ticker": "DAX.PA", "name": "Amundi DAX II UCITS ETF Acc", "ter": 0.15, "geo": {"Allemagne": 100}},
            {"ticker": "DBXD.DE", "name": "Xtrackers DAX UCITS ETF 1C", "ter": 0.09, "geo": {"Allemagne": 100}},
            {"ticker": "DECD.DE", "name": "Amundi MSCI EMU Screened UCITS ETF EUR Acc", "ter": 0.12, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "DX2G.DE", "name": "Xtrackers CAC 40 UCITS ETF 1D", "ter": 0.2, "geo": {"France": 100}},
            {"ticker": "E40.PA", "name": "BNP Paribas Easy CAC 40 ESG UCITS ETF", "ter": 0.25, "geo": {"France": 100}},
            {"ticker": "EDM4.DE", "name": "iShares MSCI EMU CTB Enhanced ESG UCITS ETF EUR (Acc)", "ter": 0.12, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EEMU.PA", "name": "BNP Paribas Easy MSCI EMU Min TE UCITS ETF", "ter": 0.15, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EESG.PA", "name": "Amundi MSCI EMU SRI Climate Paris Aligned UCITS ETF Acc", "ter": 0.18, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EMNE.DE", "name": "iShares MSCI EMU CTB Enhanced ESG UCITS ETF EUR (Dist)", "ter": 0.12, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EMUSRI.MI", "name": "UBS MSCI EMU Socially Responsible UCITS ETF EUR acc", "ter": 0.2, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EPAB.PA", "name": "Amundi S&P Eurozone Climate Paris Aligned UCITS ETF Acc", "ter": 0.2, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EPAZ.DE", "name": "Amundi S&P Eurozone Climate Paris Aligned UCITS ETF Dist", "ter": 0.14, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "ESIT.DE", "name": "iShares MSCI Europe Information Technology Sector UCITS ETF EUR (Acc)", "ter": 0.18, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "ETBB.PA", "name": "BNP Paribas Easy EURO STOXX 50 UCITS ETF", "ter": 0.1, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "ETDD.PA", "name": "BNP Paribas Easy EURO STOXX 50 UCITS ETF", "ter": 0.1, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "ETZ.PA", "name": "BNP Paribas Easy STOXX Europe 600 UCITS ETF", "ter": 0.19, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "ETZD.PA", "name": "BNP Paribas Easy STOXX Europe 600 UCITS ETF", "ter": 0.19, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "EUDV.PA", "name": "State Street SPDR S&P Euro Dividend Aristocrats UCITS ETF EUR", "ter": 0.3, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EUN2.DE", "name": "iShares Core EURO STOXX 50 UCITS ETF EUR (Dist)", "ter": 0.1, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "EUSR.L", "name": "UBS MSCI EMU Socially Responsible UCITS ETF hGBP dis", "ter": 0.23, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EUSRS.SW", "name": "UBS MSCI EMU Socially Responsible UCITS ETF hCHF acc", "ter": 0.23, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EUSRT.SW", "name": "UBS MSCI EMU Socially Responsible UCITS ETF hCHF dis", "ter": 0.23, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EUSRU.SW", "name": "UBS MSCI EMU Socially Responsible UCITS ETF hUSD acc", "ter": 0.23, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EUZON.PA", "name": "BNP Paribas Easy MSCI EMU UCITS ETF Acc", "ter": 0.06, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EXIB.DE", "name": "iShares TecDAX® UCITS ETF (DE) EUR (Dist)", "ter": 0.51, "geo": {"Allemagne": 100}},
            {"ticker": "EXIC.DE", "name": "iShares Core DAX® UCITS ETF (DE) EUR (Dist)", "ter": 0.16, "geo": {"Allemagne": 100}},
            {"ticker": "EXID.DE", "name": "iShares MDAX® UCITS ETF (DE) EUR (Dist)", "ter": 0.51, "geo": {"Allemagne": 100}},
            {"ticker": "EXS1.DE", "name": "iShares Core DAX® UCITS ETF (DE) EUR (Acc)", "ter": 0.16, "geo": {"Allemagne": 100}},
            {"ticker": "EXS2.DE", "name": "iShares TecDAX UCITS ETF (DE)", "ter": 0.51, "geo": {"Allemagne": 100}},
            {"ticker": "EXS3.DE", "name": "iShares MDAX UCITS ETF (DE)", "ter": 0.51, "geo": {"Allemagne": 100}},
            {"ticker": "EXSB.DE", "name": "iShares DivDAX UCITS ETF (DE)", "ter": 0.31, "geo": {"Allemagne": 100}},
            {"ticker": "EXSI.DE", "name": "iShares EURO STOXX UCITS ETF (DE)", "ter": 0.2, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EXW1.DE", "name": "iShares EURO STOXX 50 UCITS ETF (DE)", "ter": 0.09, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "EXX1.DE", "name": "iShares EURO STOXX Banks 30-15 UCITS ETF (DE)", "ter": 0.52, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EXXV.DE", "name": "iShares Dow Jones Eurozone Sustainability Screened UCITS ETF (DE)", "ter": 0.43, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "FEUD.L", "name": "First Trust Eurozone AlphaDEX UCITS ETF B Dist", "ter": 0.65, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "FGZI.DE", "name": "UBS Core EURO STOXX 50 UCITS ETF EUR acc", "ter": 0.06, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "FMI.PA", "name": "Amundi Italy MIB ESG UCITS ETF", "ter": 0.18, "geo": {"Italie": 100}},
            {"ticker": "FTGE.DE", "name": "First Trust Eurozone AlphaDEX UCITS ETF Acc", "ter": 0.65, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "FTGG.DE", "name": "First Trust Germany AlphaDEX UCITS ETF Dist", "ter": 0.65, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "GRE.PA", "name": "Amundi MSCI Greece UCITS ETF Dist", "ter": 0.55, "geo": {"Europe (autres)": 100}},
            {"ticker": "H4ZZ.DE", "name": "HSBC Euro Stoxx 50 UCITS ETF EUR (Acc)", "ter": 0.05, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "INDEP.PA", "name": "Amundi European Strategic Autonomy UCITS ETF Acc", "ter": 0.4, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "IQQA.DE", "name": "iShares Euro Dividend UCITS ETF", "ter": 0.4, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "IQQG.DE", "name": "iShares Euro Total Market Growth Large UCITS ETF", "ter": 0.4, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "IS3U.DE", "name": "iShares MSCI France UCITS ETF", "ter": 0.25, "geo": {"France": 100}},
            {"ticker": "LDAX.DE", "name": "Amundi DAX II UCITS ETF Dist", "ter": 0.15, "geo": {"Allemagne": 100}},
            {"ticker": "MD4C.DE", "name": "Amundi MDAX UCITS ETF Acc", "ter": 0.2, "geo": {"Allemagne": 100}},
            {"ticker": "MDX.PA", "name": "Amundi MDAX UCITS ETF Dist", "ter": 0.2, "geo": {"Allemagne": 100}},
            {"ticker": "MEUR.PA", "name": "Ossiam MSCI Europe UCITS ETF 1C/A (EUR)", "ter": 0.12, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "MFDD.MI", "name": "Amundi MSCI EMU ESG Broad Transition UCITS ETF Dist", "ter": 0.12, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "MFE.PA", "name": "Amundi Core MSCI EMU UCITS ETF Dist", "ter": 0.12, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "MFEC.PA", "name": "Amundi Core MSCI EMU UCITS ETF Acc", "ter": 0.12, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "MFED.PA", "name": "Amundi MSCI EMU ESG Broad Transition UCITS ETF Acc", "ter": 0.12, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "MIB.PA", "name": "Amundi FTSE MIB UCITS ETF Dist", "ter": 0.35, "geo": {"Italie": 100}},
            {"ticker": "MIBA.MI", "name": "Amundi FTSE MIB UCITS ETF Acc", "ter": 0.35, "geo": {"Italie": 100}},
            {"ticker": "MSE.PA", "name": "Amundi EURO STOXX 50 II UCITS ETF Acc", "ter": 0.2, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "MSEC.SW", "name": "Amundi EURO STOXX 50 II UCITS ETF CHF Hedged Acc", "ter": 0.2, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "MSES.PA", "name": "Amundi EURO STOXX 50 II UCITS ETF S Acc", "ter": 0.2, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "MUSRI.PA", "name": "BNP Paribas Easy MSCI EMU SRI S-Series PAB 5% Capped UCITS ETF", "ter": 0.25, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "NTSZ.DE", "name": "WisdomTree Eurozone Efficient Core UCITS ETF EUR Unhedged Acc", "ter": 0.2, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "OFIEU.PA", "name": "Ofi Invest EMU Equity Active UCITS ETF Acc", "ter": 0.25, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "OP2E.PA", "name": "Ossiam Bloomberg Eurozone PAB NR UCITS ETF 1C (EUR)", "ter": 0.17, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "OSX4.DE", "name": "Ossiam Europe ESG Machine Learning UCITS ETF 1C (EUR)", "ter": 0.65, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "PABZ.PA", "name": "Amundi MSCI EMU Climate Paris Aligned UCITS ETF Acc", "ter": 0.15, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "PCEU.PA", "name": "Amundi PEA MSCI Europe UCITS ETF Acc", "ter": 0.15, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "PR1Z.DE", "name": "Amundi Prime Eurozone UCITS ETF DR (D)", "ter": 0.05, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "PRAZ.DE", "name": "Amundi Prime Eurozone UCITS ETF DR (C)", "ter": 0.05, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "SEZA.MI", "name": "State Street EMU Screened Equity Fund UCITS ETF", "ter": 0.6, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "SLMA.DE", "name": "iShares MSCI EMU Screened UCITS ETF EUR (Acc)", "ter": 0.12, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "SLMB.DE", "name": "iShares MSCI EMU Screened UCITS ETF EUR (Dist)", "ter": 0.12, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "SXRT.DE", "name": "iShares Core EURO STOXX 50 UCITS ETF EUR (Acc)", "ter": 0.1, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "UIM1.DE", "name": "UBS Core EURO STOXX 50 UCITS ETF EUR dis", "ter": 0.06, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "UIMR.DE", "name": "UBS MSCI EMU Socially Responsible UCITS ETF EUR dis", "ter": 0.2, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "VERE.DE", "name": "Vanguard FTSE Developed Europe ex UK UCITS ETF (EUR) Accumulating", "ter": 0.1, "geo": {"France": 20, "Suisse": 18, "Allemagne": 16, "Pays-Bas": 10, "Europe (autres)": 36}},
            {"ticker": "VERX.DE", "name": "Vanguard FTSE Developed Europe ex UK UCITS ETF (EUR) Distributing", "ter": 0.1, "geo": {"France": 20, "Suisse": 18, "Allemagne": 16, "Pays-Bas": 10, "Europe (autres)": 36}},
            {"ticker": "VEXA.DE", "name": "Vanguard FTSE Eurozone UCITS ETF EUR Acc", "ter": 0.07, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "VEXD.DE", "name": "Vanguard FTSE Eurozone UCITS ETF EUR Dist", "ter": 0.07, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "VGER.DE", "name": "Vanguard Germany All Cap UCITS ETF (EUR) Distributing", "ter": 0.07, "geo": {"Allemagne": 100}},
            {"ticker": "XD5D.L", "name": "Xtrackers MSCI EMU UCITS ETF 1C - USD Hedged", "ter": 0.17, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "XD5E.DE", "name": "Xtrackers MSCI EMU UCITS ETF 1D", "ter": 0.09, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "XD5S.L", "name": "Xtrackers MSCI EMU UCITS ETF 2C - GBP Hedged", "ter": 0.12, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "XDCH.SW", "name": "Xtrackers DAX ESG Screened UCITS ETF 4C CHF Hedged", "ter": 0.19, "geo": {"Allemagne": 100}},
            {"ticker": "XDDA.DE", "name": "Xtrackers DAX UCITS ETF 1D", "ter": 0.09, "geo": {"Allemagne": 100}},
            {"ticker": "XDDX.DE", "name": "Xtrackers DAX ESG Screened UCITS ETF 1D", "ter": 0.09, "geo": {"Allemagne": 100}},
            {"ticker": "XDGM.DE", "name": "Xtrackers MDAX ESG Screened UCITS ETF 1D", "ter": 0.4, "geo": {"Allemagne": 100}},
            {"ticker": "XDUD.SW", "name": "Xtrackers DAX ESG Screened UCITS ETF 2C USD Hedged", "ter": 0.19, "geo": {"Allemagne": 100}},
            {"ticker": "XDUE.SW", "name": "Xtrackers MSCI EMU UCITS ETF 3C CHF hedged", "ter": 0.17, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "XEMU.DE", "name": "Xtrackers MSCI EMU UCITS ETF 4C", "ter": 0.09, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "XESC.DE", "name": "Xtrackers EURO STOXX 50 UCITS ETF 1C", "ter": 0.09, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "XESX.DE", "name": "Xtrackers EURO STOXX 50 UCITS ETF 1D", "ter": 0.09, "geo": {"France": 33, "Allemagne": 30, "Pays-Bas": 15, "Espagne": 10, "Italie": 6, "Zone euro (diversifie)": 6}},
            {"ticker": "XZEZ.DE", "name": "Xtrackers MSCI EMU ESG UCITS ETF 1C", "ter": 0.2, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "ZPRE.DE", "name": "State Street SPDR MSCI EMU UCITS ETF EUR", "ter": 0.08, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
        ],
    },
    {
        "name": "Actions Europe - facteurs / styles",
        "etfs": [
            {"ticker": "CAPE.PA", "name": "Ossiam Shiller Barclays CAPE® Europe Sector Value TR UCITS ETF 1C (EUR)", "ter": 0.65, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "CD8.PA", "name": "Amundi MSCI EMU High Dividend UCITS ETF UCITS ETF Acc", "ter": 0.3, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "DXSA.DE", "name": "Xtrackers Euro Stoxx Quality Dividend UCITS ETF 1D", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "EDEU.PA", "name": "BNP Paribas Easy Dividend Europe UCITS ETF", "ter": 0.31, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "EDHE.DE", "name": "Amundi MSCI EMU High Dividend UCITS ETF Dist", "ter": 0.3, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EGRA.PA", "name": "WisdomTree Eurozone Quality Dividend Growth UCITS ETF EUR Acc", "ter": 0.29, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "EGRO.PA", "name": "BNP Paribas Easy Growth Europe UCITS ETF Acc", "ter": 0.31, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "EHDV.DE", "name": "Invesco EURO STOXX High Dividend Low Volatility UCITS ETF", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "EQUA.PA", "name": "BNP Paribas Easy Quality Europe UCITS ETF", "ter": 0.31, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "EVAE.PA", "name": "BNP Paribas Easy Value Europe UCITS ETF", "ter": 0.31, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "EVOE.PA", "name": "BNP Paribas Easy Low Volatility Europe UCITS ETF", "ter": 0.31, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "EXSG.DE", "name": "iShares EURO STOXX Select Dividend 30 UCITS ETF (DE)", "ter": 0.32, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "MMS.PA", "name": "Amundi MSCI EMU Small Cap ESG Broad Transition UCITS ETF Dist", "ter": 0.4, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "QUED.PA", "name": "BNP Paribas Easy Quality Europe UCITS ETF", "ter": 0.31, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "SEL.PA", "name": "Amundi Stoxx Europe Select Dividend 30 UCITS ETF Dist", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "VAL.PA", "name": "Amundi MSCI EMU Value Factor UCITS ETF Dist", "ter": 0.4, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "VALD.PA", "name": "BNP Paribas Easy Value Europe UCITS ETF", "ter": 0.31, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "VLED.PA", "name": "BNP Paribas Easy Low Volatility Europe UCITS ETF", "ter": 0.31, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "XZDZ.DE", "name": "Xtrackers MSCI EMU High Dividend Yield ESG UCITS ETF 1D", "ter": 0.25, "geo": {"France": 20, "Allemagne": 20, "Pays-Bas": 12, "Espagne": 8, "Italie": 8, "Zone euro (diversifie)": 32}},
            {"ticker": "ZPRL.DE", "name": "State Street SPDR EURO STOXX Low Volatility UCITS ETF EUR", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
        ],
    },
    {
        "name": "Actions Europe - secteurs",
        "etfs": [
            {"ticker": "6TVL.DE", "name": "Amundi STOXX Europe 600 Consumer Discretionary UCITS ETF Dist", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "BNK.PA", "name": "Amundi STOXX Europe 600 Banks UCITS ETF Acc", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "BRES.PA", "name": "Amundi STOXX Europe 600 Basic Resources UCITS ETF Acc", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "CHM.PA", "name": "Amundi STOXX Europe 600 Basic Materials UCITS ETF Acc", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "CSTA.DE", "name": "Amundi STOXX Europe 600 Technology UCITS ETF Dist", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "DFOP.DE", "name": "Amundi STOXX Europe 600 Consumer Staples UCITS ETF Dist", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "E6BR.DE", "name": "Amundi STOXX Europe 600 Basic Resources UCITS ETF Dist", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "EGV1.DE", "name": "Amundi STOXX Europe 600 Insurance UCITS ETF Dist", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "EHLT.DE", "name": "Amundi STOXX Europe 600 Healthcare UCITS ETF Dist", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "EXHG.DE", "name": "iShares STOXX Europe 600 Automobiles & Parts UCITS ETF (DE) EUR (Acc)", "ter": 0.41, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "EXV3.DE", "name": "iShares STOXX Europe 600 Technology UCITS ETF (DE) EUR (Dist)", "ter": 0.46, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "EXV5.DE", "name": "iShares STOXX Europe 600 Automobiles & Parts UCITS ETF (DE) EUR (Dist)", "ter": 0.46, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "FOO.PA", "name": "Amundi STOXX Europe 600 Consumer Staples UCITS ETF Acc", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "HLT.PA", "name": "Amundi STOXX Europe 600 Healthcare UCITS ETF Acc", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "IND.PA", "name": "Amundi STOXX Europe 600 Industrials UCITS ETF Acc", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "INDA.DE", "name": "Amundi STOXX Europe 600 Banks UCITS ETF Dist", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "INDB.DE", "name": "Amundi STOXX Europe 600 Telecommunications UCITS ETF Dist", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "INDU.DE", "name": "Amundi STOXX Europe 600 Industrials UCITS ETF Dist", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "INS.PA", "name": "Amundi STOXX Europe 600 Insurance UCITS ETF Acc", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "LUTL.DE", "name": "Amundi STOXX Europe 600 Utilities UCITS ETF Dist", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "LYX4.DE", "name": "Amundi STOXX Europe 600 Basic Materials UCITS ETF Dist", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "TELE.PA", "name": "Amundi STOXX Europe 600 Telecommunications UCITS ETF Acc", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "TNO.PA", "name": "Amundi STOXX Europe 600 Technology UCITS ETF Acc", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "TRV.PA", "name": "Amundi STOXX Europe 600 Consumer Discretionary UCITS ETF Acc", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "UTI.PA", "name": "Amundi STOXX Europe 600 Utilities UCITS ETF Acc", "ter": 0.3, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
        ],
    },
    {
        "name": "Actions Asie",
        "etfs": [
            {"ticker": "AAXJ", "name": "iShares MSCI All Country Asia ex Japan ETF", "ter": 0.68, "geo": {"Chine": 30, "Inde": 20, "Taiwan": 18, "Coree du Sud": 14, "Asie (autres)": 18}},
            {"ticker": "PAEJ.PA", "name": "Amundi PEA Asie Pacifique (MSCI AC Asia Pacific Ex Japan) UCITS ETF Acc", "ter": 0.60, "geo": {"Chine": 30, "Inde": 20, "Taiwan": 18, "Coree du Sud": 14, "Asie (autres)": 18}},
            {"ticker": "CEMA.L", "name": "iShares MSCI EM Asia UCITS ETF", "ter": 0.65, "geo": {"Chine": 32, "Inde": 20, "Taiwan": 18, "Coree du Sud": 14, "Asie (autres)": 16}},
            {"ticker": "VPL", "name": "Vanguard FTSE Pacific ETF", "ter": 0.08, "geo": {"Japon": 65, "Australie": 16, "Hong Kong": 8, "Singapour": 6, "Asie (autres)": 5}},
            {"ticker": "AIA", "name": "iShares Asia 50 ETF", "ter": 0.50, "geo": {"Chine": 30, "Taiwan": 20, "Inde": 20, "Coree du Sud": 15, "Asie (autres)": 15}},
            {"ticker": "GMF", "name": "SPDR S&P Emerging Asia Pacific ETF", "ter": 0.49, "geo": {"Chine": 30, "Taiwan": 20, "Inde": 20, "Coree du Sud": 15, "Asie (autres)": 15}},
            {"ticker": "EPP", "name": "iShares MSCI Pacific ex Japan ETF", "ter": 0.49, "geo": {"Australie": 55, "Hong Kong": 20, "Singapour": 15, "Nouvelle-Zelande": 5, "Asie (autres)": 5}},
            {"ticker": "EWJ", "name": "iShares MSCI Japan ETF", "ter": 0.50, "geo": {"Japon": 100}},
            {"ticker": "DXJ", "name": "WisdomTree Japan Hedged Equity ETF (USD hedged)", "ter": 0.48, "geo": {"Japon": 100}},
            {"ticker": "IJPE.L", "name": "iShares MSCI Japan EUR Hedged UCITS ETF", "ter": 0.64, "geo": {"Japon": 100}},
            {"ticker": "EWT", "name": "iShares MSCI Taiwan ETF", "ter": 0.59, "geo": {"Taiwan": 100}},
            {"ticker": "INDA", "name": "iShares MSCI India ETF", "ter": 0.65, "geo": {"Inde": 100}},
            {"ticker": "PINR.PA", "name": "Amundi PEA Inde (MSCI India) UCITS ETF Acc", "ter": 0.85, "geo": {"Inde": 100}},
            {"ticker": "MCHI", "name": "iShares MSCI China ETF", "ter": 0.58, "geo": {"Chine": 100}},
            {"ticker": "FXI", "name": "iShares China Large-Cap ETF", "ter": 0.74, "geo": {"Chine": 100}},
            {"ticker": "PASI.PA", "name": "Amundi PEA Chine (MSCI China) Screened UCITS ETF Acc", "ter": 0.65, "geo": {"Chine": 100}},
            {"ticker": "EWY", "name": "iShares MSCI South Korea ETF", "ter": 0.59, "geo": {"Coree du Sud": 100}},
            {"ticker": "PTPXE.PA", "name": "Amundi PEA Japon (TOPIX) UCITS ETF EUR Acc", "ter": 0.2, "geo": {"Japon": 100}},
            {"ticker": "PTPXH.PA", "name": "Amundi PEA Japan (TOPIX) UCITS ETF EUR Hedged", "ter": 0.48, "geo": {"Japon": 100}},
        ],
    },
    {
        "name": "Actions par pays - Ameriques / Oceanie",
        "etfs": [
            {"ticker": "EWC", "name": "iShares MSCI Canada ETF", "ter": 0.50, "geo": {"Canada": 100}},
            {"ticker": "EWA", "name": "iShares MSCI Australia ETF", "ter": 0.50, "geo": {"Australie": 100}},
            {"ticker": "EWZ", "name": "iShares MSCI Brazil ETF", "ter": 0.58, "geo": {"Bresil": 100}},
            {"ticker": "EWW", "name": "iShares MSCI Mexico ETF", "ter": 0.50, "geo": {"Mexique": 100}},
            {"ticker": "PALAT.PA", "name": "Amundi PEA MSCI Emerging Latin America Selection UCITS ETF Acc", "ter": 0.30, "geo": {"Bresil": 65, "Mexique": 35}},
        ],
    },
    {
        "name": "Thematique - Robotique & IA",
        "etfs": [
            {"ticker": "ROBO", "name": "ROBO Global Robotics and Automation ETF", "ter": 0.95, "geo": {"Etats-Unis": 35, "Japon": 30, "Monde (diversifie)": 35}},
            {"ticker": "BOTZ", "name": "Global X Robotics & Artificial Intelligence ETF", "ter": 0.68, "geo": {"Etats-Unis": 47, "Japon": 53}},
            {"ticker": "QTUM", "name": "Defiance Quantum ETF", "ter": 0.40, "geo": {"Etats-Unis": 88, "Japon": 12}},
        ],
    },
    {
        "name": "Thematique - Tech & Innovation",
        "etfs": [
            {"ticker": "ARKK", "name": "ARK Innovation ETF", "ter": 0.75, "geo": {"Etats-Unis": 100}},
            {"ticker": "HACK", "name": "ETFMG Prime Cyber Security ETF", "ter": 0.60, "geo": {"Etats-Unis": 88, "Israel": 12}},
            {"ticker": "CIBR", "name": "First Trust NASDAQ Cybersecurity ETF", "ter": 0.59, "geo": {"Etats-Unis": 100}},
            {"ticker": "BLOK", "name": "Amplify Transformational Data Sharing ETF (blockchain)", "ter": 0.71, "geo": {"Etats-Unis": 60, "Monde (diversifie)": 40}},
        ],
    },
    {
        "name": "Thematique - Energie renouvelable",
        "etfs": [
            {"ticker": "ICLN", "name": "iShares Global Clean Energy ETF", "ter": 0.41, "geo": {"Etats-Unis": 35, "Chine": 15, "Monde (diversifie)": 50}},
            {"ticker": "TAN", "name": "Invesco Solar ETF", "ter": 0.66, "geo": {"Etats-Unis": 40, "Chine": 25, "Monde (diversifie)": 35}},
            {"ticker": "FAN", "name": "First Trust Global Wind Energy ETF", "ter": 0.60, "geo": {"Etats-Unis": 15, "Monde (diversifie)": 85}},
        ],
    },
    {
        "name": "Thematique - Eau",
        "etfs": [
            {"ticker": "WATC.PA", "name": "Amundi MSCI Water UCITS ETF Acc", "ter": 0.60, "geo": {"Etats-Unis": 45, "Royaume-Uni": 10, "Monde (diversifie)": 45}},
            {"ticker": "WAT.PA", "name": "Amundi MSCI Water UCITS ETF Dist", "ter": 0.60, "geo": {"Etats-Unis": 45, "Royaume-Uni": 10, "Monde (diversifie)": 45}},
            {"ticker": "AWAT.PA", "name": "Amundi PEA Eau (MSCI Water) UCITS ETF Capi", "ter": 0.60, "geo": {"Etats-Unis": 45, "Royaume-Uni": 10, "Monde (diversifie)": 45}},
            {"ticker": "DH2O.L", "name": "iShares Global Water UCITS ETF", "ter": 0.65, "geo": {"Etats-Unis": 45, "Royaume-Uni": 10, "Monde (diversifie)": 45}},
            {"ticker": "GLUG.L", "name": "L&G Clean Water UCITS ETF", "ter": 0.49, "geo": {"Etats-Unis": 45, "Royaume-Uni": 10, "Monde (diversifie)": 45}},
        ],
    },
    {
        "name": "Thematique - Vehicules electriques & Batteries",
        "etfs": [
            {"ticker": "LIT", "name": "Global X Lithium & Battery Tech ETF", "ter": 0.75, "geo": {"Chine": 40, "Etats-Unis": 20, "Monde (diversifie)": 40}},
            {"ticker": "DRIV", "name": "Global X Autonomous & Electric Vehicles ETF", "ter": 0.68, "geo": {"Etats-Unis": 45, "Chine": 15, "Japon": 10, "Monde (diversifie)": 30}},
        ],
    },
    {
        "name": "Thematique - Sante & Pharma",
        "etfs": [
            {"ticker": "WHCA.AS", "name": "iShares MSCI World Health Care Sector UCITS ETF", "ter": 0.18, "geo": {"Etats-Unis": 70, "Monde (diversifie)": 30}},
            {"ticker": "XLV", "name": "Health Care Select Sector SPDR", "ter": 0.09, "geo": {"Etats-Unis": 100}},
            {"ticker": "VHT", "name": "Vanguard Health Care ETF", "ter": 0.10, "geo": {"Etats-Unis": 100}},
            {"ticker": "IXJ", "name": "iShares Global Healthcare ETF", "ter": 0.40, "geo": {"Etats-Unis": 65, "Monde (diversifie)": 35}},
            {"ticker": "XBI", "name": "SPDR S&P Biotech ETF", "ter": 0.35, "geo": {"Etats-Unis": 100}},
            {"ticker": "IBB", "name": "iShares Biotechnology ETF", "ter": 0.45, "geo": {"Etats-Unis": 100}},
            {"ticker": "XPH", "name": "SPDR S&P Pharmaceuticals ETF", "ter": 0.35, "geo": {"Etats-Unis": 100}},
            {"ticker": "IHE", "name": "iShares U.S. Pharmaceuticals ETF", "ter": 0.39, "geo": {"Etats-Unis": 100}},
            {"ticker": "IHF", "name": "iShares U.S. Healthcare Providers ETF", "ter": 0.39, "geo": {"Etats-Unis": 100}},
            {"ticker": "ARKG", "name": "ARK Genomic Revolution ETF", "ter": 0.75, "geo": {"Etats-Unis": 100}},
        ],
    },
    {
        "name": "Thematique - Defense",
        "etfs": [
            {"ticker": "ITA", "name": "iShares U.S. Aerospace & Defense ETF", "ter": 0.40, "geo": {"Etats-Unis": 100}},
            {"ticker": "XAR", "name": "SPDR S&P Aerospace & Defense ETF", "ter": 0.35, "geo": {"Etats-Unis": 100}},
            {"ticker": "PPA", "name": "Invesco Aerospace & Defense ETF", "ter": 0.58, "geo": {"Etats-Unis": 100}},
            {"ticker": "EUAD", "name": "VanEck Defense UCITS ETF (defense europeenne)", "ter": 0.55, "geo": {"France": 25, "Allemagne": 20, "Royaume-Uni": 20, "Italie": 15, "Europe (autres)": 20}},
            {"ticker": "SHLD", "name": "Global X Defense Tech ETF", "ter": 0.50, "geo": {"Etats-Unis": 60, "Monde (diversifie)": 40}},
            {"ticker": "EDEF.DE", "name": "BNP Paribas Easy Bloomberg Europe Defense UCITS ETF Dist", "ter": 0.35, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
            {"ticker": "GUARD.PA", "name": "BNP Paribas Easy Bloomberg Europe Defense UCITS ETF Acc", "ter": 0.35, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
        ],
    },
    {
        "name": "Thematique - Aerospatial & Spatial",
        "etfs": [
            {"ticker": "ARKX", "name": "ARK Space Exploration & Innovation ETF", "ter": 0.75, "geo": {"Etats-Unis": 100}},
            {"ticker": "UFO", "name": "Procure Space ETF", "ter": 0.75, "geo": {"Etats-Unis": 73, "Europe (autres)": 27}},
            {"ticker": "ROKT", "name": "SPDR S&P Kensho Final Frontiers ETF (espace)", "ter": 0.45, "geo": {"Etats-Unis": 100}},
        ],
    },
    {
        "name": "Obligations d'Etat par pays (notation de credit)",
        "etfs": [
            {"ticker": "IS0L.DE", "name": "iShares Germany Govt Bond UCITS ETF (Allemagne, notation AAA)", "ter": 0.20, "geo": {"Allemagne": 100}},
            {"ticker": "GOVT.AX", "name": "SPDR S&P/ASX Australian Govt Bond ETF (Australie, notation AAA)", "ter": 0.22, "geo": {"Australie": 100}},
            {"ticker": "IGLT.L", "name": "iShares Core UK Gilts UCITS ETF (Royaume-Uni, notation AA)", "ter": 0.07, "geo": {"Royaume-Uni": 100}},
            {"ticker": "IFRB.AS", "name": "iShares France Govt Bond UCITS ETF (France, notation AA-)", "ter": 0.20, "geo": {"France": 100}},
            {"ticker": "CEB2.DE", "name": "iShares Japan Govt Bond ETF EUR Hedged (Japon, notation A+)", "ter": 0.20, "geo": {"Japon": 100}},
            {"ticker": "IS0P.DE", "name": "iShares Spain Govt Bond UCITS ETF (Espagne, notation A)", "ter": 0.20, "geo": {"Espagne": 100}},
            {"ticker": "IITB.MI", "name": "iShares Italy Govt Bond UCITS ETF (Italie, notation BBB)", "ter": 0.20, "geo": {"Italie": 100}},
            {"ticker": "EMB", "name": "iShares JP Morgan USD EM Bond ETF (marches emergents, notation BB moyenne)", "ter": 0.39, "geo": {"Marches emergents (diversifie)": 100}},
            {"ticker": "2B7H.MU", "name": "iShares Global Govt Bond UCITS ETF (mondial diversifie AAA-A, inclut Norvege/Danemark/Pays-Bas/Suede en petite part)", "ter": 0.20, "geo": {"Monde developpe (diversifie)": 100}},
        ],
    },
    {
        "name": "Obligations",
        "etfs": [
            {"ticker": "AGG", "name": "iShares Core US Aggregate Bond ETF", "ter": 0.03, "geo": {"Etats-Unis": 100}},
            {"ticker": "BND", "name": "Vanguard Total Bond Market ETF", "ter": 0.03, "geo": {"Etats-Unis": 100}},
            {"ticker": "TLT", "name": "iShares 20+ Year Treasury Bond ETF", "ter": 0.15, "geo": {"Etats-Unis": 100}},
            {"ticker": "IEF", "name": "iShares 7-10 Year Treasury Bond ETF", "ter": 0.15, "geo": {"Etats-Unis": 100}},
            {"ticker": "SHY", "name": "iShares 1-3 Year Treasury Bond ETF", "ter": 0.15, "geo": {"Etats-Unis": 100}},
            {"ticker": "LQD", "name": "iShares iBoxx Investment Grade Corp Bond ETF", "ter": 0.14, "geo": {"Etats-Unis": 100}},
            {"ticker": "HYG", "name": "iShares iBoxx High Yield Corp Bond ETF", "ter": 0.48, "geo": {"Etats-Unis": 100}},
            {"ticker": "TIP", "name": "iShares TIPS Bond ETF", "ter": 0.19, "geo": {"Etats-Unis": 100}},
            {"ticker": "OBLI.PA", "name": "Amundi PEA Euro Court Terme UCITS ETF Acc", "ter": 0.25, "geo": {"Fonds a taux fixe": 100}},
            {"ticker": "OVNI.PA", "name": "BNP Paribas Easy EUR Overnight PEA UCITS ETF Acc", "ter": 0.05, "geo": {"Fonds a taux fixe": 100}},
        ],
    },
    {
        "name": "Matieres premieres / Metaux precieux",
        "etfs": [
            {"ticker": "GLD", "name": "SPDR Gold Shares (or physique)", "ter": 0.40, "geo": {"Matieres premieres": 100}},
            {"ticker": "IAU", "name": "iShares Gold Trust (or physique)", "ter": 0.25, "geo": {"Matieres premieres": 100}},
            {"ticker": "SLV", "name": "iShares Silver Trust (argent physique)", "ter": 0.50, "geo": {"Matieres premieres": 100}},
            {"ticker": "PPLT", "name": "abrdn Physical Platinum Shares ETF (platine physique)", "ter": 0.60, "geo": {"Matieres premieres": 100}},
            {"ticker": "DBC", "name": "Invesco DB Commodity Index Tracking Fund", "ter": 0.87, "geo": {"Matieres premieres": 100}},
            {"ticker": "USO", "name": "United States Oil Fund", "ter": 0.60, "geo": {"Matieres premieres": 100}},
            {"ticker": "CMSE.PA", "name": "iShares Diversified Commodity Swap UCITS ETF (DE)", "ter": 0.46, "geo": {"Matieres premieres": 100}},
        ],
    },
    {
        "name": "Immobilier",
        "etfs": [
            {"ticker": "VNQ", "name": "Vanguard Real Estate ETF", "ter": 0.13, "geo": {"Etats-Unis": 100}},
            {"ticker": "IYR", "name": "iShares US Real Estate ETF", "ter": 0.39, "geo": {"Etats-Unis": 100}},
            {"ticker": "PMEH.PA", "name": "Amundi PEA Immobilier Europe (FTSE EPRA/NAREIT) UCITS ETF Acc", "ter": 0.4, "geo": {"Royaume-Uni": 22, "France": 15, "Suisse": 14, "Allemagne": 13, "Europe (autres)": 36}},
        ],
    },
]

ALL_TICKERS = {etf["ticker"]: etf["name"] for cat in CATEGORIES for etf in cat["etfs"]}
ALL_FEES = {etf["ticker"]: etf["ter"] for cat in CATEGORIES for etf in cat["etfs"]}
ALL_GEO = {etf["ticker"]: etf["geo"] for cat in CATEGORIES for etf in cat["etfs"]}
ALL_CATEGORY = {etf["ticker"]: cat["name"] for cat in CATEGORIES for etf in cat["etfs"]}


# ---------------------------------------------------------------------------
# Extra per-ETF metadata for the search/filter picker: PEA eligibility,
# distribution policy (capitalisant/distribuant) and quotation currency.
#
# These aren't derivable from price history the way return/volatility are, so
# they're sourced two ways:
#   1. A best-effort mechanical default computed right here from the ticker
#      itself (exchange suffix -> currency; US-domiciled '40 Act funds are
#      always distributing, that's a structural fact not a per-fund guess).
#   2. An override from `etf_metadata.json`, produced by
#      `scripts/scrape_justetf.py` against justETF's fund database (PEA
#      eligibility in particular can't be inferred at all - only that scrape
#      has it). Re-run that script periodically; nothing here calls it
#      automatically.
# Anything not covered by either source is simply left unset (None) rather
# than guessed, since a wrong PEA flag has real tax-wrapper consequences.
# ---------------------------------------------------------------------------

import json
import re
from pathlib import Path

_METADATA_FILE = Path(__file__).resolve().parent / "etf_metadata.json"

_SUFFIX_CURRENCY = {
    "PA": "EUR", "DE": "EUR", "AS": "EUR", "MI": "EUR", "MU": "EUR", "MC": "EUR", "BR": "EUR",
    "L": "GBP", "AX": "AUD", "SW": "CHF", "TO": "CAD",
}


def _default_currency(ticker):
    if "." in ticker:
        return _SUFFIX_CURRENCY.get(ticker.rsplit(".", 1)[1].upper(), "EUR")
    return "USD"


def _default_distribution(ticker, name):
    if "." not in ticker:
        return "Distribuant"  # US-listed '40 Act funds cannot have an accumulating share class
    low = name.lower()
    if re.search(r"\bacc\b|capitalisant|\bcapi\b", low):
        return "Capitalisant"
    if re.search(r"\bdist\b|distribuant|distribution", low):
        return "Distribuant"
    return None


def _load_scraped_metadata():
    if _METADATA_FILE.exists():
        try:
            return json.loads(_METADATA_FILE.read_text()).get("etfs", {})
        except Exception:
            return {}
    return {}


_SCRAPED_METADATA = _load_scraped_metadata()


def _build_meta(ticker, name):
    scraped = _SCRAPED_METADATA.get(ticker, {})
    return {
        "currency": scraped.get("currency") or _default_currency(ticker),
        "hedged": scraped.get("hedged", False),
        "distribution": scraped.get("distribution") or _default_distribution(ticker, name),
        "pea": scraped.get("pea", False),
        "pea_source": "justetf" if "pea" in scraped else None,
        "domicile": scraped.get("domicile"),
        "replication": scraped.get("replication"),
        "inception_date": scraped.get("inception_date"),
        "fund_size_mln": scraped.get("fund_size_mln"),
    }


ALL_META = {ticker: _build_meta(ticker, name) for ticker, name in ALL_TICKERS.items()}
METADATA_SCRAPED_AT = None
if _METADATA_FILE.exists():
    try:
        METADATA_SCRAPED_AT = json.loads(_METADATA_FILE.read_text()).get("scraped_at")
    except Exception:
        pass
