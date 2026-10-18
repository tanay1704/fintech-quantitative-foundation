import csv
import sys
from datetime import datetime
import requests


def fetch_coingecko_data(limit=25):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": "false",
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, params=params, headers=headers, timeout=15)
    response.raise_for_status()
    raw_data = response.json()

    records = []
    for coin in raw_data:
        records.append({
            "rank": coin.get("market_cap_rank"),
            "name": coin.get("name"),
            "symbol": str(coin.get("symbol", "")).upper(),
            "current_price_usd": coin.get("current_price"),
            "market_cap_usd": coin.get("market_cap"),
            "volume_24h_usd": coin.get("total_volume"),
            "high_24h_usd": coin.get("high_24h"),
            "low_24h_usd": coin.get("low_24h"),
            "price_change_percentage_24h": coin.get("price_change_percentage_24h"),
            "circulating_supply": coin.get("circulating_supply"),
            "last_updated": coin.get("last_updated"),
        })
    return records


def fetch_binance_fallback(limit=25):
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    raw_data = response.json()

    usdt_pairs = [item for item in raw_data if item.get("symbol", "").endswith("USDT")]
    sorted_pairs = sorted(usdt_pairs, key=lambda x: float(x.get("quoteVolume", 0)), reverse=True)[:limit]

    records = []
    now_iso = datetime.utcnow().isoformat() + "Z"
    for idx, item in enumerate(sorted_pairs, start=1):
        symbol = item.get("symbol", "").replace("USDT", "")
        records.append({
            "rank": idx,
            "name": symbol,
            "symbol": symbol,
            "current_price_usd": float(item.get("lastPrice", 0)),
            "market_cap_usd": None,
            "volume_24h_usd": float(item.get("quoteVolume", 0)),
            "high_24h_usd": float(item.get("highPrice", 0)),
            "low_24h_usd": float(item.get("lowPrice", 0)),
            "price_change_percentage_24h": float(item.get("priceChangePercent", 0)),
            "circulating_supply": None,
            "last_updated": now_iso,
        })
    return records


def export_to_csv(records, output_file="api_data_extract.csv"):
    if not records:
        raise ValueError("No records available to export.")

    fieldnames = [
        "rank",
        "name",
        "symbol",
        "current_price_usd",
        "market_cap_usd",
        "volume_24h_usd",
        "high_24h_usd",
        "low_24h_usd",
        "price_change_percentage_24h",
        "circulating_supply",
        "last_updated",
    ]

    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main():
    target_csv = "api_data_extract.csv"
    try:
        data = fetch_coingecko_data(limit=25)
    except Exception:
        data = fetch_binance_fallback(limit=25)

    export_to_csv(data, output_file=target_csv)
    print(f"Successfully exported {len(data)} records to {target_csv}")


if __name__ == "__main__":
    main()
