from pytrends.request import TrendReq
import pandas as pd

# --- Proxy configuration (as list of URLs) ---
proxies = [
    'http://10.240.16.4:8080',   # HTTP
    'https://10.240.16.4:8080'   # HTTPS
]

# --- Initialize Google Trends connection ---
pytrends = TrendReq(
    hl='en-US',
    tz=360,                  # UTC+6; adjust if needed
    timeout=(10, 25),
    retries=2,
    backoff_factor=0.1,
    proxies=proxies          # <-- list, not dict
)

# --- Keywords to track ---
keywords = [
    "BTC",
    "AVAX",
    "SOLANA",
    "ETH",
    "BITTENSOR"
]

# --- Build payload ---
pytrends.build_payload(
    kw_list=keywords,
    timeframe='today 5-y',
    geo='',
    gprop=''
)

# --- Download interest over time ---
data = pytrends.interest_over_time()

# --- Remove partial data column if exists ---
if 'isPartial' in data.columns:
    data = data.drop(columns=['isPartial'])

# --- Save to CSV ---
data.to_csv("google_trends_data.csv")

print("Google Trends data downloaded successfully.")
print(data.head())
