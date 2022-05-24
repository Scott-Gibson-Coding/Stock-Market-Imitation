# Using top 20 S&P 500 companies for now while testing
# https://www.slickcharts.com/sp500
def preset_companies():
    return dict(
        companies={
            '^GSPC': 'S&P 500', 'AAPL': 'Apple Inc.', 'MSFT': 'Microsoft Corporation', 'AMZN': 'Amazon.com Inc.',
            'GOOGL': 'Alphabet Inc. Class A', 'GOOG': 'Alphabet Inc. Class C', 'TSLA': 'Tesla Inc',
            'BRK.B': 'Berkshire Hathaway Inc. Class B', 'JNJ': 'Johnson & Johnson',
            'UNH': 'UnitedHealth Group Incorporated', 'FB': 'Meta Platforms Inc. Class A', 'NVDA': 'NVIDIA Corporation',
            'XOM': 'Exxon Mobil Corporation', 'JPM': 'JPMorgan Chase & Co.', 'PG': 'Procter & Gamble Company',
            'V': 'Visa Inc. Class A', 'CVX': 'Chevron Corporation', 'HD': 'Home Depot Inc.',
            'MA': 'Mastercard Incorporated Class A', 'PFE': 'Pfizer Inc.', 'ABBV': 'AbbVie Inc.',
        },
        values={
            '^GSPC': 3901.36, 'AAPL': 137.60, 'MSFT': 252.94, 'AMZN': 2159.37, 'GOOGL': 2180.08, 'GOOG': 2187.00,
            'TSLA': 665.40, 'BRK.B': 304.05, 'JNJ': 177.25, 'UNH': 485.73, 'FB': 193.81, 'NVDA': 166.94, 'XOM': 92.25,
            'JPM': 117.37, 'PG': 141.88, 'V': 200.00, 'CVX': 168.50, 'HD': 287.80, 'MA': 336.00, 'PFE': 52.51,
            'ABBV': 151.01,
        },
        changes={
            '^GSPC': 0.57, 'AAPL': 0.01, 'MSFT': 0.38, 'AMZN': 7.55, 'GOOGL': 1.92, 'GOOG': 0.74, 'TSLA': 1.50,
            'BRK.B': 0.00, 'JNJ': 0.27, 'UNH': 0.00, 'FB': 0.27, 'NVDA': 0.00, 'XOM': 0.39, 'JPM': 0.03,
            'PG': 0.09, 'V': 0.97, 'CVX': 0.68, 'HD': 0.61, 'MA': -0.18, 'PFE': 0.04, 'ABBV': 0.00,
        }
    )