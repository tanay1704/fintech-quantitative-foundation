from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import logging
import sys
import time
from typing import Any, Dict, List, Optional
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class StructuredJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


logger = logging.getLogger("market_pipeline")
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(StructuredJsonFormatter())
logger.handlers = [stream_handler]


@dataclass(frozen=True)
class MarketAsset:
    rank: int
    name: str
    symbol: str
    current_price_usd: float
    market_cap_usd: float
    volume_24h_usd: float
    high_24h_usd: float
    low_24h_usd: float
    price_change_percentage_24h: float
    circulating_supply: float
    last_updated: str


class MarketDataPipeline:
    COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
    BINANCE_URL = "https://api.binance.com/api/v3/ticker/24hr"

    def __init__(self, timeout: int = 15, max_retries: int = 4, backoff_factor: float = 1.5):
        self.timeout = timeout
        self.session = self._create_resilient_session(max_retries, backoff_factor)

    def _create_resilient_session(self, max_retries: int, backoff_factor: float) -> requests.Session:
        session = requests.Session()
        retries = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.headers.update({
            "User-Agent": "EnterpriseMarketIngestion/2.0 (Financial Analytics Pipeline)",
            "Accept": "application/json",
        })
        return session

    def fetch_primary_coingecko(self, limit: int = 25) -> List[MarketAsset]:
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": "false",
        }
        logger.info(f"Initiating request to primary endpoint: {self.COINGECKO_URL}")
        response = self.session.get(self.COINGECKO_URL, params=params, timeout=self.timeout)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            logger.warning(f"Rate limited by primary endpoint. Backing off for {retry_after} seconds.")
            time.sleep(retry_after)
            response = self.session.get(self.COINGECKO_URL, params=params, timeout=self.timeout)

        response.raise_for_status()
        payload: List[Dict[str, Any]] = response.json()

        assets: List[MarketAsset] = []
        for item in payload:
            try:
                asset = MarketAsset(
                    rank=int(item.get("market_cap_rank") or 0),
                    name=str(item.get("name") or "Unknown"),
                    symbol=str(item.get("symbol") or "").upper(),
                    current_price_usd=float(item.get("current_price") or 0.0),
                    market_cap_usd=float(item.get("market_cap") or 0.0),
                    volume_24h_usd=float(item.get("total_volume") or 0.0),
                    high_24h_usd=float(item.get("high_24h") or 0.0),
                    low_24h_usd=float(item.get("low_24h") or 0.0),
                    price_change_percentage_24h=float(item.get("price_change_percentage_24h") or 0.0),
                    circulating_supply=float(item.get("circulating_supply") or 0.0),
                    last_updated=str(item.get("last_updated") or datetime.now(timezone.utc).isoformat()),
                )
                assets.append(asset)
            except (ValueError, TypeError) as err:
                logger.warning(f"Skipping malformed asset record: {err}")
                continue

        logger.info(f"Successfully processed {len(assets)} assets from primary endpoint.")
        return assets

    def fetch_fallback_binance(self, limit: int = 25) -> List[MarketAsset]:
        logger.info(f"Initiating failover request to secondary endpoint: {self.BINANCE_URL}")
        response = self.session.get(self.BINANCE_URL, timeout=self.timeout)
        response.raise_for_status()
        payload: List[Dict[str, Any]] = response.json()

        usdt_tickers = [
            t for t in payload
            if isinstance(t, dict) and t.get("symbol", "").endswith("USDT")
        ]
        sorted_tickers = sorted(
            usdt_tickers,
            key=lambda x: float(x.get("quoteVolume", 0.0)),
            reverse=True,
        )[:limit]

        now_timestamp = datetime.now(timezone.utc).isoformat()
        assets: List[MarketAsset] = []
        for idx, item in enumerate(sorted_tickers, start=1):
            raw_symbol = item.get("symbol", "").replace("USDT", "")
            asset = MarketAsset(
                rank=idx,
                name=raw_symbol,
                symbol=raw_symbol,
                current_price_usd=float(item.get("lastPrice") or 0.0),
                market_cap_usd=0.0,
                volume_24h_usd=float(item.get("quoteVolume") or 0.0),
                high_24h_usd=float(item.get("highPrice") or 0.0),
                low_24h_usd=float(item.get("lowPrice") or 0.0),
                price_change_percentage_24h=float(item.get("priceChangePercent") or 0.0),
                circulating_supply=0.0,
                last_updated=now_timestamp,
            )
            assets.append(asset)

        logger.info(f"Successfully processed {len(assets)} assets from failover endpoint.")
        return assets

    def execute_pipeline(self, limit: int = 25) -> List[MarketAsset]:
        try:
            return self.fetch_primary_coingecko(limit=limit)
        except Exception as primary_error:
            logger.error(f"Primary endpoint execution failed: {primary_error}. Attempting fallback.")
            try:
                return self.fetch_fallback_binance(limit=limit)
            except Exception as fallback_error:
                logger.critical(f"Both primary and fallback endpoints failed: {fallback_error}")
                raise RuntimeError("All public financial endpoints exhausted.") from fallback_error

    @staticmethod
    def export_to_csv(assets: List[MarketAsset], destination_path: str = "api_data_extract.csv") -> None:
        if not assets:
            raise ValueError("Cannot export empty asset payload to CSV.")

        records = [asdict(a) for a in assets]
        df = pd.DataFrame.from_records(records)
        df.to_csv(destination_path, index=False, encoding="utf-8")
        logger.info(f"Exported {len(df)} validated records to {destination_path}")


def main() -> None:
    output_filename = "api_data_extract.csv"
    pipeline = MarketDataPipeline(timeout=15, max_retries=4, backoff_factor=1.5)
    data = pipeline.execute_pipeline(limit=25)
    pipeline.export_to_csv(data, destination_path=output_filename)


if __name__ == "__main__":
    main()
