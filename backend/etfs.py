"""Curated list of major, liquid ETFs available for the portfolio builder.

Not exhaustive (there are thousands of ETFs) - this covers the major
building blocks across regions, factors, sectors, themes, fixed income and
commodities that a retail investor would realistically combine.

Each entry carries "ter" - its annual expense ratio (Total Expense Ratio,
in percent) - sourced from provider fact sheets where known, or a
reasonable category-typical estimate otherwise. It is only a starting
point: the frontend lets the user override it per position, and that
user-supplied value is what actually feeds every calculation server-side.
"""

DEFAULT_TER = 0.20  # fallback used for manually-typed tickers not in this catalogue

CATEGORIES = [
    {
        "name": "Actions US - large cap",
        "etfs": [
            {"ticker": "SPY", "name": "SPDR S&P 500 ETF Trust", "ter": 0.09},
            {"ticker": "VOO", "name": "Vanguard S&P 500 ETF", "ter": 0.03},
            {"ticker": "IVV", "name": "iShares Core S&P 500 ETF", "ter": 0.03},
            {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF", "ter": 0.03},
            {"ticker": "QQQ", "name": "Invesco QQQ Trust (Nasdaq 100)", "ter": 0.20},
            {"ticker": "DIA", "name": "SPDR Dow Jones Industrial Average ETF", "ter": 0.16},
            {"ticker": "IWM", "name": "iShares Russell 2000 ETF (small cap)", "ter": 0.19},
        ],
    },
    {
        "name": "Actions US - facteurs / styles",
        "etfs": [
            {"ticker": "SPMO", "name": "Invesco S&P 500 Momentum ETF", "ter": 0.13},
            {"ticker": "MTUM", "name": "iShares MSCI USA Momentum Factor ETF", "ter": 0.15},
            {"ticker": "VLUE", "name": "iShares MSCI USA Value Factor ETF", "ter": 0.15},
            {"ticker": "QUAL", "name": "iShares MSCI USA Quality Factor ETF", "ter": 0.15},
            {"ticker": "USMV", "name": "iShares MSCI USA Min Vol Factor ETF", "ter": 0.15},
            {"ticker": "VYM", "name": "Vanguard High Dividend Yield ETF", "ter": 0.06},
            {"ticker": "SCHD", "name": "Schwab US Dividend Equity ETF", "ter": 0.06},
        ],
    },
    {
        "name": "Actions US - secteurs",
        "etfs": [
            {"ticker": "XLK", "name": "Technology Select Sector SPDR", "ter": 0.09},
            {"ticker": "SMH", "name": "VanEck Semiconductor ETF", "ter": 0.35},
            {"ticker": "XLF", "name": "Financial Select Sector SPDR", "ter": 0.09},
            {"ticker": "XLE", "name": "Energy Select Sector SPDR", "ter": 0.09},
            {"ticker": "XLY", "name": "Consumer Discretionary Select SPDR", "ter": 0.09},
            {"ticker": "XLP", "name": "Consumer Staples Select SPDR", "ter": 0.09},
            {"ticker": "XLI", "name": "Industrial Select Sector SPDR", "ter": 0.09},
            {"ticker": "XLU", "name": "Utilities Select Sector SPDR", "ter": 0.09},
            {"ticker": "XLRE", "name": "Real Estate Select Sector SPDR", "ter": 0.09},
        ],
    },
    {
        "name": "Actions internationales - large",
        "etfs": [
            {"ticker": "EFA", "name": "iShares MSCI EAFE ETF", "ter": 0.32},
            {"ticker": "VEA", "name": "Vanguard FTSE Developed Markets ETF", "ter": 0.05},
            {"ticker": "EEM", "name": "iShares MSCI Emerging Markets ETF", "ter": 0.68},
            {"ticker": "VWO", "name": "Vanguard FTSE Emerging Markets ETF", "ter": 0.07},
            {"ticker": "IEMG", "name": "iShares Core MSCI Emerging Markets ETF", "ter": 0.09},
            {"ticker": "EXCS.L", "name": "iShares MSCI EM ex China UCITS ETF", "ter": 0.20},
        ],
    },
    {
        "name": "Actions Europe",
        "etfs": [
            {"ticker": "VGK", "name": "Vanguard FTSE Europe ETF", "ter": 0.08},
            {"ticker": "EZU", "name": "iShares MSCI Eurozone ETF", "ter": 0.50},
            {"ticker": "FEZ", "name": "SPDR EURO STOXX 50 ETF", "ter": 0.29},
            {"ticker": "IEUR", "name": "iShares Core MSCI Europe ETF", "ter": 0.09},
            {"ticker": "EWG", "name": "iShares MSCI Germany ETF", "ter": 0.50},
            {"ticker": "EWQ", "name": "iShares MSCI France ETF", "ter": 0.50},
            {"ticker": "EWU", "name": "iShares MSCI United Kingdom ETF", "ter": 0.50},
            {"ticker": "EWI", "name": "iShares MSCI Italy ETF", "ter": 0.50},
            {"ticker": "EWP", "name": "iShares MSCI Spain ETF", "ter": 0.50},
            {"ticker": "EWL", "name": "iShares MSCI Switzerland ETF", "ter": 0.50},
        ],
    },
    {
        "name": "Actions Asie",
        "etfs": [
            {"ticker": "AAXJ", "name": "iShares MSCI All Country Asia ex Japan ETF", "ter": 0.68},
            {"ticker": "CEMA.L", "name": "iShares MSCI EM Asia UCITS ETF", "ter": 0.65},
            {"ticker": "VPL", "name": "Vanguard FTSE Pacific ETF", "ter": 0.08},
            {"ticker": "AIA", "name": "iShares Asia 50 ETF", "ter": 0.50},
            {"ticker": "GMF", "name": "SPDR S&P Emerging Asia Pacific ETF", "ter": 0.49},
            {"ticker": "EPP", "name": "iShares MSCI Pacific ex Japan ETF", "ter": 0.49},
            {"ticker": "EWJ", "name": "iShares MSCI Japan ETF", "ter": 0.50},
            {"ticker": "DXJ", "name": "WisdomTree Japan Hedged Equity ETF (USD hedged)", "ter": 0.48},
            {"ticker": "IJPE.L", "name": "iShares MSCI Japan EUR Hedged UCITS ETF", "ter": 0.64},
            {"ticker": "EWT", "name": "iShares MSCI Taiwan ETF", "ter": 0.59},
            {"ticker": "INDA", "name": "iShares MSCI India ETF", "ter": 0.65},
            {"ticker": "MCHI", "name": "iShares MSCI China ETF", "ter": 0.58},
            {"ticker": "FXI", "name": "iShares China Large-Cap ETF", "ter": 0.74},
            {"ticker": "EWY", "name": "iShares MSCI South Korea ETF", "ter": 0.59},
        ],
    },
    {
        "name": "Actions par pays - Ameriques / Oceanie",
        "etfs": [
            {"ticker": "EWC", "name": "iShares MSCI Canada ETF", "ter": 0.50},
            {"ticker": "EWA", "name": "iShares MSCI Australia ETF", "ter": 0.50},
            {"ticker": "EWZ", "name": "iShares MSCI Brazil ETF", "ter": 0.58},
            {"ticker": "EWW", "name": "iShares MSCI Mexico ETF", "ter": 0.50},
        ],
    },
    {
        "name": "Thematique - Robotique & IA",
        "etfs": [
            {"ticker": "ROBO", "name": "ROBO Global Robotics and Automation ETF", "ter": 0.95},
            {"ticker": "BOTZ", "name": "Global X Robotics & Artificial Intelligence ETF", "ter": 0.68},
            {"ticker": "QTUM", "name": "Defiance Quantum ETF", "ter": 0.40},
        ],
    },
    {
        "name": "Thematique - Tech & Innovation",
        "etfs": [
            {"ticker": "ARKK", "name": "ARK Innovation ETF", "ter": 0.75},
            {"ticker": "HACK", "name": "ETFMG Prime Cyber Security ETF", "ter": 0.60},
            {"ticker": "CIBR", "name": "First Trust NASDAQ Cybersecurity ETF", "ter": 0.59},
            {"ticker": "BLOK", "name": "Amplify Transformational Data Sharing ETF (blockchain)", "ter": 0.71},
        ],
    },
    {
        "name": "Thematique - Energie renouvelable",
        "etfs": [
            {"ticker": "ICLN", "name": "iShares Global Clean Energy ETF", "ter": 0.41},
            {"ticker": "TAN", "name": "Invesco Solar ETF", "ter": 0.66},
            {"ticker": "FAN", "name": "First Trust Global Wind Energy ETF", "ter": 0.60},
        ],
    },
    {
        "name": "Thematique - Eau",
        "etfs": [
            {"ticker": "WATC.PA", "name": "Amundi MSCI Water UCITS ETF Acc", "ter": 0.60},
            {"ticker": "WAT.PA", "name": "Amundi MSCI Water UCITS ETF Dist", "ter": 0.60},
            {"ticker": "AWAT.PA", "name": "Amundi PEA Eau (MSCI Water) UCITS ETF Capi (eligible PEA)", "ter": 0.60},
            {"ticker": "DH2O.L", "name": "iShares Global Water UCITS ETF", "ter": 0.65},
            {"ticker": "GLUG.L", "name": "L&G Clean Water UCITS ETF", "ter": 0.49},
        ],
    },
    {
        "name": "Thematique - Vehicules electriques & Batteries",
        "etfs": [
            {"ticker": "LIT", "name": "Global X Lithium & Battery Tech ETF", "ter": 0.75},
            {"ticker": "DRIV", "name": "Global X Autonomous & Electric Vehicles ETF", "ter": 0.68},
        ],
    },
    {
        "name": "Thematique - Sante & Pharma",
        "etfs": [
            {"ticker": "WHCA.AS", "name": "iShares MSCI World Health Care Sector UCITS ETF", "ter": 0.18},
            {"ticker": "XLV", "name": "Health Care Select Sector SPDR", "ter": 0.09},
            {"ticker": "VHT", "name": "Vanguard Health Care ETF", "ter": 0.10},
            {"ticker": "IXJ", "name": "iShares Global Healthcare ETF", "ter": 0.40},
            {"ticker": "XBI", "name": "SPDR S&P Biotech ETF", "ter": 0.35},
            {"ticker": "IBB", "name": "iShares Biotechnology ETF", "ter": 0.45},
            {"ticker": "XPH", "name": "SPDR S&P Pharmaceuticals ETF", "ter": 0.35},
            {"ticker": "IHE", "name": "iShares U.S. Pharmaceuticals ETF", "ter": 0.39},
            {"ticker": "IHF", "name": "iShares U.S. Healthcare Providers ETF", "ter": 0.39},
            {"ticker": "ARKG", "name": "ARK Genomic Revolution ETF", "ter": 0.75},
        ],
    },
    {
        "name": "Thematique - Defense",
        "etfs": [
            {"ticker": "ITA", "name": "iShares U.S. Aerospace & Defense ETF", "ter": 0.40},
            {"ticker": "XAR", "name": "SPDR S&P Aerospace & Defense ETF", "ter": 0.35},
            {"ticker": "PPA", "name": "Invesco Aerospace & Defense ETF", "ter": 0.58},
            {"ticker": "EUAD", "name": "VanEck Defense UCITS ETF (defense europeenne)", "ter": 0.55},
            {"ticker": "SHLD", "name": "Global X Defense Tech ETF", "ter": 0.50},
        ],
    },
    {
        "name": "Thematique - Aerospatial & Spatial",
        "etfs": [
            {"ticker": "ARKX", "name": "ARK Space Exploration & Innovation ETF", "ter": 0.75},
            {"ticker": "UFO", "name": "Procure Space ETF", "ter": 0.75},
            {"ticker": "ROKT", "name": "SPDR S&P Kensho Final Frontiers ETF (espace)", "ter": 0.45},
        ],
    },
    {
        "name": "Obligations d'Etat par pays (notation de credit)",
        "etfs": [
            {"ticker": "IS0L.DE", "name": "iShares Germany Govt Bond UCITS ETF (Allemagne, notation AAA)", "ter": 0.20},
            {"ticker": "GOVT.AX", "name": "SPDR S&P/ASX Australian Govt Bond ETF (Australie, notation AAA)", "ter": 0.22},
            {"ticker": "IGLT.L", "name": "iShares Core UK Gilts UCITS ETF (Royaume-Uni, notation AA)", "ter": 0.07},
            {"ticker": "IFRB.AS", "name": "iShares France Govt Bond UCITS ETF (France, notation AA-)", "ter": 0.20},
            {"ticker": "CEB2.DE", "name": "iShares Japan Govt Bond ETF EUR Hedged (Japon, notation A+)", "ter": 0.20},
            {"ticker": "IS0P.DE", "name": "iShares Spain Govt Bond UCITS ETF (Espagne, notation A)", "ter": 0.20},
            {"ticker": "IITB.MI", "name": "iShares Italy Govt Bond UCITS ETF (Italie, notation BBB)", "ter": 0.20},
            {"ticker": "EMB", "name": "iShares JP Morgan USD EM Bond ETF (marches emergents, notation BB moyenne)", "ter": 0.39},
            {"ticker": "2B7H.MU", "name": "iShares Global Govt Bond UCITS ETF (mondial diversifie AAA-A, inclut Norvege/Danemark/Pays-Bas/Suede en petite part)", "ter": 0.20},
        ],
    },
    {
        "name": "Obligations",
        "etfs": [
            {"ticker": "AGG", "name": "iShares Core US Aggregate Bond ETF", "ter": 0.03},
            {"ticker": "BND", "name": "Vanguard Total Bond Market ETF", "ter": 0.03},
            {"ticker": "TLT", "name": "iShares 20+ Year Treasury Bond ETF", "ter": 0.15},
            {"ticker": "IEF", "name": "iShares 7-10 Year Treasury Bond ETF", "ter": 0.15},
            {"ticker": "SHY", "name": "iShares 1-3 Year Treasury Bond ETF", "ter": 0.15},
            {"ticker": "LQD", "name": "iShares iBoxx Investment Grade Corp Bond ETF", "ter": 0.14},
            {"ticker": "HYG", "name": "iShares iBoxx High Yield Corp Bond ETF", "ter": 0.48},
            {"ticker": "TIP", "name": "iShares TIPS Bond ETF", "ter": 0.19},
        ],
    },
    {
        "name": "Matieres premieres / Metaux precieux",
        "etfs": [
            {"ticker": "GLD", "name": "SPDR Gold Shares (or physique)", "ter": 0.40},
            {"ticker": "IAU", "name": "iShares Gold Trust (or physique)", "ter": 0.25},
            {"ticker": "SLV", "name": "iShares Silver Trust (argent physique)", "ter": 0.50},
            {"ticker": "PPLT", "name": "abrdn Physical Platinum Shares ETF (platine physique)", "ter": 0.60},
            {"ticker": "DBC", "name": "Invesco DB Commodity Index Tracking Fund", "ter": 0.87},
            {"ticker": "USO", "name": "United States Oil Fund", "ter": 0.60},
        ],
    },
    {
        "name": "Immobilier",
        "etfs": [
            {"ticker": "VNQ", "name": "Vanguard Real Estate ETF", "ter": 0.13},
            {"ticker": "IYR", "name": "iShares US Real Estate ETF", "ter": 0.39},
        ],
    },
]

ALL_TICKERS = {etf["ticker"]: etf["name"] for cat in CATEGORIES for etf in cat["etfs"]}
ALL_FEES = {etf["ticker"]: etf["ter"] for cat in CATEGORIES for etf in cat["etfs"]}
