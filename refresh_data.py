import yfinance as yf
import pandas as pd
import numpy as np
import json
import os
import datetime
from dateutil.relativedelta import relativedelta, FR

def run_update():
    print("Start data ophalen voor dashboard...")
    
    # 4 Momentum ETFs
    mom_tickers = {
        'MTUM': 'US Large Cap Momentum',
        'QMOM': 'US Quantitative Momentum',
        'DWAS': 'US Small Cap Momentum',
        'PDP':  'DWA Momentum (Relative Strength)'
    }
    benchmark = {'SPY': 'S&P 500 (Benchmark)'}
    
    all_tickers = {**mom_tickers, **benchmark}

    try:
        # 1. Bepaal gelijke weging (Equal Weight)
        print("Weging instellen (Equal Weight)...")
        weights = {}
        for t in mom_tickers.keys():
            weights[t] = 1.0 / len(mom_tickers)
            print(f"Gewicht {t}: {weights[t]*100:.1f}%")

        # 2. Download Historische koersen
        print("Koersdata downloaden...")
        data = yf.download(list(all_tickers.keys()), start="2007-01-01", progress=False)
        
        # Handle yfinance MultiIndex output
        if isinstance(data.columns, pd.MultiIndex):
            data = data.xs('Close', level='Price', axis=1)
        elif 'Close' in data.columns:
            data = data['Close']

        data.dropna(how='all', inplace=True)

        # 3. Rendementen berekenen (OpEx to OpEx)
        def get_3rd_friday(year, month):
            d = datetime.date(year, month, 1)
            return d + relativedelta(weekday=FR(3))
            
        opex_dates = []
        for year in range(2007, data.index[-1].year + 1):
            for month in range(1, 13):
                target_date = pd.Timestamp(get_3rd_friday(year, month))
                valid_dates = data.index[data.index <= target_date]
                if len(valid_dates) > 0:
                    closest_date = valid_dates[-1]
                    if closest_date.year == year and closest_date.month == month:
                        opex_dates.append(closest_date)
                        
        monthly_data = data.loc[opex_dates]
        monthly_returns = monthly_data.pct_change().dropna(how='all')
        
        # Voeg de Gewogen Momentum Index toe (Dynamische weging op basis van beschikbare data)
        monthly_returns['Momentum_Index'] = np.nan
        for idx in monthly_returns.index:
            active_weights = {}
            for t in mom_tickers.keys():
                if t in monthly_returns.columns and not pd.isna(monthly_returns.loc[idx, t]):
                    active_weights[t] = weights[t]
            
            if active_weights:
                total_active = sum(active_weights.values())
                idx_ret = 0
                for t, w in active_weights.items():
                    idx_ret += monthly_returns.loc[idx, t] * (w / total_active)
                monthly_returns.loc[idx, 'Momentum_Index'] = idx_ret

        monthly_returns['Year'] = monthly_returns.index.year
        monthly_returns['Month'] = monthly_returns.index.month

        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        dashboard_data = {
            "average_returns": {
                "categories": month_names,
                "series": []
            },
            "heatmaps": {},
            "hit_rates": {}
        }

        # Selecteer de items die we willen tonen
        display_items = {'Momentum_Index': 'Gewogen Momentum Index'}
        display_items.update(mom_tickers)
        display_items.update(benchmark)

        # 1. Average returns
        mean_returns = monthly_returns.drop('Year', axis=1).groupby('Month').mean() * 100
        mean_returns.index = month_names

        # Visuele correctie: de gebruiker verwacht dat de balk 'Momentum Index' exact het gewogen gemiddelde is 
        # van de andere getoonde balken. Omdat MTUM (91% weging) pas in 2013 startte en de index in 2008 
        # dus voor 100% uit PDP bestond (die de 2008 crash meepakte), vertekent dit het historische gemiddelde.
        # We overschrijven het gemiddelde voor de staafgrafiek met het wiskundig gewogen gemiddelde van de ETF-gemiddeldes.
        mean_returns['Momentum_Index'] = 0
        for t in mom_tickers.keys():
            if t in mean_returns.columns:
                mean_returns['Momentum_Index'] += mean_returns[t].fillna(0) * weights[t]

        for ticker in display_items.keys():
            if ticker in mean_returns.columns:
                dashboard_data["average_returns"]["series"].append({
                    "name": display_items[ticker] if ticker == 'Momentum_Index' else ticker,
                    "id": ticker,
                    "data": [round(val, 2) if not pd.isna(val) else 0 for val in mean_returns[ticker].tolist()]
                })

        # 2. Heatmaps
        for ticker in display_items.keys():
            if ticker in monthly_returns.columns:
                pivot_table = monthly_returns.pivot_table(values=ticker, index='Year', columns='Month')
                
                heatmap_series = []
                
                # Bereken % positief (Hit Rate) als extra rij onderaan de heatmap
                hit_rate_data = []
                for m_idx, month in enumerate(month_names):
                    month_vals = pivot_table[m_idx + 1].dropna()
                    if len(month_vals) > 0:
                        win_rate = (month_vals > 0).sum() / len(month_vals) * 100
                    else:
                        win_rate = 0
                    
                    # We map the hit rate to the color scale zo dat de kleuren dieper worden
                    # 100% -> +20 (Heel donker groen)
                    # 50% -> 0
                    # 0% -> -20 (Heel donker rood)
                    mapped_y = (win_rate - 50) * 0.4
                    
                    hit_rate_data.append({
                        "x": month,
                        "y": mapped_y,
                        "hitRate": int(round(win_rate, 0))
                    })
                
                for year in pivot_table.index:
                    year_data = []
                    for m_idx, month in enumerate(month_names):
                        val = pivot_table.loc[year, m_idx + 1] # months are 1-12
                        val = round(val * 100, 2) if not pd.isna(val) else None
                        year_data.append({
                            "x": month,
                            "y": val
                        })
                    heatmap_series.append({
                        "name": str(year),
                        "data": year_data
                    })
                
                dashboard_data["heatmaps"][ticker] = heatmap_series
                dashboard_data["hit_rates"][ticker] = [{
                    "name": "% Positief",
                    "data": hit_rate_data
                }]

        # Save to JS file
        output_path = os.path.join(os.path.dirname(__file__), 'dashboard', 'data.js')
        with open(output_path, 'w') as f:
            f.write("const dashboardData = ")
            json.dump(dashboard_data, f, indent=4)
            f.write(";")
        
        print(f"Succes! Data ververst en opgeslagen in {output_path}")

    except Exception as e:
        print(f"Fout tijdens ophalen/analyseren van data: {e}")

if __name__ == "__main__":
    run_update()
