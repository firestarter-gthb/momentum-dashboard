import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("Start data ophalen...")
tickers = {
    'MTUM': 'US Large Cap Momentum',
    'QMOM': 'US Quantitative Momentum',
    'DWAS': 'US Small Cap Momentum',
    'SPY': 'S&P 500 (Benchmark)'
}

try:
    data = yf.download(list(tickers.keys()), start="2015-01-01", progress=False)
    
    if isinstance(data.columns, pd.MultiIndex):
        data = data.xs('Close', level='Price', axis=1)
    elif 'Close' in data.columns:
        data = data['Close']

    data.dropna(how='all', inplace=True)

    monthly_data = data.resample('ME').last()
    monthly_returns = monthly_data.pct_change().dropna(how='all')

    monthly_returns['Year'] = monthly_returns.index.year
    monthly_returns['Month'] = monthly_returns.index.month

    # Generate Heatmaps
    sns.set_theme(style="whitegrid")
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    for ticker in tickers.keys():
        if ticker in monthly_returns.columns:
            pivot_table = monthly_returns.pivot_table(values=ticker, index='Year', columns='Month')
            pivot_table.columns = month_names[:len(pivot_table.columns)]
            
            plt.figure(figsize=(10, 5))
            sns.heatmap(pivot_table * 100, annot=True, fmt=".1f", cmap="RdYlGn", center=0, 
                        cbar_kws={'label': 'Rendement (%)'}, linewidths=.5)
            plt.title(f'Seasonality Heatmap: {tickers[ticker]} ({ticker})')
            plt.yticks(rotation=0)
            plt.tight_layout()
            plt.savefig(f"{ticker}_heatmap.png")
            plt.close()

    # Calculate and save mean returns
    mean_returns = monthly_returns.drop('Year', axis=1).groupby('Month').mean() * 100
    mean_returns.index = month_names

    plt.figure(figsize=(12, 6))
    mean_returns[[t for t in tickers.keys() if t in mean_returns.columns]].plot(kind='bar', figsize=(14, 7), width=0.8)
    plt.title('Gemiddeld Maandrendement per ETF (2015 - Heden)')
    plt.ylabel('Gemiddeld Rendement (%)')
    plt.xlabel('Maand')
    plt.axhline(0, color='black', linewidth=1)
    plt.legend(title='ETF')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig("gemiddeld_maandrendement.png")
    plt.close()

    print("\n--- Analyse Succesvol ---")
    print("Gemiddelde maandelijkse rendementen (%):")
    print(mean_returns.round(2).to_string())
    print("\nAlle grafieken zijn opgeslagen als PNG-bestanden in je workspace.")

except Exception as e:
    print(f"Fout tijdens ophalen/analyseren van data: {e}")
