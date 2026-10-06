# Momentum Seasonality Dashboard

Een opvallend, datagedreven webdashboard dat de seizoenspatronen (seasonality) van toonaangevende Amerikaanse Momentum ETF's in kaart brengt. Het dashboard helpt bij het identificeren van sterke en zwakke beursmaanden, gemeten in optie-expiratie cycli (OpEx).

## 🚀 Over het project

Het volgen van kalendermaanden voor seizoensinvloeden kan misleidend zijn. Grote institutionele kapitaalstromen en rebalancing gebeuren vaak rondom de maandelijkse optie-expiratiedatum (OpEx), die altijd op de 3e vrijdag van de maand valt. 

Dit dashboard verzamelt de koersdata van 4 bekende Momentum ETF's en de S&P 500, en berekent de historische winstkansen ("Hit Rate") en gemiddelde rendementen **van OpEx tot OpEx**. Dit geeft een veel nauwkeuriger inzicht in de daadwerkelijke markt-cycli.

### Gemonitorde Assets
- **MTUM**: iShares MSCI USA Momentum Factor ETF
- **QMOM**: Alpha Architect U.S. Quantitative Momentum ETF
- **DWAS**: Invesco DWA SmallCap Momentum ETF
- **PDP**: Invesco DWA Momentum ETF
- **SPY**: SPDR S&P 500 ETF Trust (Benchmark)

De gecombineerde **Momentum Index (Equal Weight)** geeft elke ETF een vaste weging van 25%, wat zorgt voor een stabiel en gebalanceerd inzicht in de totale momentum factor.

## 🎨 Design System

Het dashboard maakt gebruik van een **Neo-Brutalist** design stijl (afgeleid van DataSente). Kenmerken zijn onder andere:
- Harde randen en vierkante hoeken (`border-radius: 0`).
- Duidelijke contrasten met dikke, zwarte randen (`border: 3px solid var(--ink)`).
- Opvallend en vibrant kleurenpalet (`--lime`, `--violet`, `--coral`).
- Typografie gefocust op leesbaarheid (`Space Grotesk` voor headers, `Space Mono` voor datalabels).
- ApexCharts voor strakke en dynamische heatmaps en staafgrafieken.

## ⚙️ Hoe werkt het?

De infrastructuur is verdeeld in een Python back-end (voor data verzameling en analyse) en een puur HTML/JS front-end. 

### Structuur
- `refresh_data.py`: Het zware werk. Dit script downloadt actuele koersen via `yfinance`, zoekt de OpEx data (3e vrijdag) op, berekent de rendementen en slaat dit alles op in `dashboard/data.js`.
- `refresh.bat`: Een handige snelkoppeling om het Python script in één klik te runnen.
- `dashboard/`: Map met alle frontend code (`momentum_dashboard.html`, `style.css`, `script.js`).

### Data Verversen
Om het dashboard te voorzien van de meest recente beurskoersen:
1. Zorg dat je Python hebt geïnstalleerd met de benodigde packages (`pip install yfinance pandas numpy`).
2. Dubbelklik op `refresh.bat`.
3. Open `dashboard/momentum_dashboard.html` in je browser. Klaar!

## 🌍 Talen
Het dashboard is beschikbaar in twee weergaves:
- `momentum_dashboard.html` (Nederlands)
- `momentum_dashboard_en.html` (Engels)

## 🛡️ Licentie
Gemaakt voor privé/intern gebruik, analyse en educatieve doeleinden. Bevat data van Yahoo Finance (via `yfinance`). 
