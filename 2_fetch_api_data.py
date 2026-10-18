import concurrent.futures
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
class EquityConstituent:
    symbol: str
    company_name: str
    sector: str
    shares_outstanding_cr: float
    ttm_eps_inr: float


@dataclass(frozen=True)
class EquityMarketRecord:
    symbol: str
    company_name: str
    sector: str
    current_price_inr: float
    previous_close_inr: float
    price_change_pct: float
    day_high_inr: float
    day_low_inr: float
    fifty_two_week_high_inr: float
    fifty_two_week_low_inr: float
    trading_volume: int
    turnover_inr_cr: float
    market_cap_inr_cr: float
    trailing_pe: float
    exchange: str
    timestamp: str


class NiftyDataPipeline:
    ENDPOINT_TEMPLATE = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"

    CONSTITUENTS: List[EquityConstituent] = [
        EquityConstituent("RELIANCE.NS", "Reliance Industries Ltd", "Energy & Conglomerate", 676.5, 41.2),
        EquityConstituent("TCS.NS", "Tata Consultancy Services Ltd", "Information Technology", 361.8, 88.5),
        EquityConstituent("HDFCBANK.NS", "HDFC Bank Ltd", "Financial Services", 762.3, 45.6),
        EquityConstituent("ICICIBANK.NS", "ICICI Bank Ltd", "Financial Services", 704.5, 35.8),
        EquityConstituent("BHARTIARTL.NS", "Bharti Airtel Ltd", "Telecommunications", 600.2, 24.1),
        EquityConstituent("INFY.NS", "Infosys Ltd", "Information Technology", 415.1, 42.3),
        EquityConstituent("SBIN.NS", "State Bank of India", "Financial Services", 892.5, 48.2),
        EquityConstituent("ITC.NS", "ITC Ltd", "Fast Moving Consumer Goods", 1248.0, 13.2),
        EquityConstituent("HINDUNILVR.NS", "Hindustan Unilever Ltd", "Fast Moving Consumer Goods", 235.0, 32.4),
        EquityConstituent("LT.NS", "Larsen & Toubro Ltd", "Construction & Engineering", 137.5, 65.0),
        EquityConstituent("BAJFINANCE.NS", "Bajaj Finance Ltd", "Financial Services", 61.8, 145.2),
        EquityConstituent("HCLTECH.NS", "HCL Technologies Ltd", "Information Technology", 271.4, 40.5),
        EquityConstituent("MARUTI.NS", "Maruti Suzuki India Ltd", "Automobiles & Components", 31.4, 275.4),
        EquityConstituent("SUNPHARMA.NS", "Sun Pharmaceutical Industries Ltd", "Healthcare & Pharmaceuticals", 239.9, 31.5),
        EquityConstituent("ADANIENT.NS", "Adani Enterprises Ltd", "Metals & Mining", 114.0, 21.4),
        EquityConstituent("KOTAKBANK.NS", "Kotak Mahindra Bank Ltd", "Financial Services", 198.8, 42.8),
        EquityConstituent("TITAN.NS", "Titan Company Ltd", "Consumer Durables", 88.8, 29.6),
        EquityConstituent("ONGC.NS", "Oil & Natural Gas Corporation Ltd", "Energy - Oil & Gas", 1258.0, 23.4),
        EquityConstituent("TMCV.NS", "Tata Motors Limited", "Automobiles & Components", 368.1, 42.1),
        EquityConstituent("NTPC.NS", "NTPC Ltd", "Power & Utilities", 969.7, 15.8),
        EquityConstituent("AXISBANK.NS", "Axis Bank Ltd", "Financial Services", 309.2, 52.3),
        EquityConstituent("ADANIPORTS.NS", "Adani Ports and SEZ Ltd", "Services - Shipping & Logistics", 216.0, 24.6),
        EquityConstituent("POWERGRID.NS", "Power Grid Corporation of India Ltd", "Power & Utilities", 930.1, 12.4),
        EquityConstituent("COALINDIA.NS", "Coal India Ltd", "Energy - Coal", 616.3, 38.6),
        EquityConstituent("BAJAJFINSV.NS", "Bajaj Finserv Ltd", "Financial Services", 159.5, 32.1),
        EquityConstituent("M%26M.NS", "Mahindra & Mahindra Ltd", "Automobiles & Components", 124.3, 64.2),
        EquityConstituent("ULTRACEMCO.NS", "UltraTech Cement Ltd", "Construction Materials", 28.9, 195.4),
        EquityConstituent("ASIANPAINT.NS", "Asian Paints Ltd", "Consumer Durables", 95.9, 39.5),
        EquityConstituent("TATASTEEL.NS", "Tata Steel Ltd", "Metals & Mining", 1248.4, 4.8),
        EquityConstituent("SIEMENS.NS", "Siemens Ltd", "Capital Goods", 35.6, 54.2),
        EquityConstituent("BAJAJ-AUTO.NS", "Bajaj Auto Ltd", "Automobiles & Components", 27.9, 198.5),
        EquityConstituent("DMART.NS", "Avenue Supermarts Ltd", "Consumer Services", 65.1, 28.4),
        EquityConstituent("IOC.NS", "Indian Oil Corporation Ltd", "Energy - Refining & Marketing", 1412.1, 18.2),
        EquityConstituent("HAL.NS", "Hindustan Aeronautics Ltd", "Aerospace & Defence", 66.9, 78.4),
        EquityConstituent("VBL.NS", "Varun Beverages Ltd", "Fast Moving Consumer Goods", 129.9, 12.8),
        EquityConstituent("DLF.NS", "DLF Ltd", "Real Estate", 247.5, 9.4),
        EquityConstituent("BEL.NS", "Bharat Electronics Ltd", "Aerospace & Defence", 731.0, 4.2),
        EquityConstituent("GRASIM.NS", "Grasim Industries Ltd", "Construction Materials", 68.3, 54.6),
        EquityConstituent("SBILIFE.NS", "SBI Life Insurance Company Ltd", "Financial Services", 100.2, 15.2),
        EquityConstituent("ETERNAL.NS", "Eternal Ltd (Zomato)", "Consumer Services - Internet", 882.5, 0.85),
        EquityConstituent("TRENT.NS", "Trent Ltd", "Consumer Services - Retail", 35.5, 22.8),
        EquityConstituent("TECHM.NS", "Tech Mahindra Ltd", "Information Technology", 97.9, 32.4),
        EquityConstituent("PIDILITIND.NS", "Pidilite Industries Ltd", "Chemicals", 50.8, 28.6),
        EquityConstituent("HINDALCO.NS", "Hindalco Industries Ltd", "Metals & Mining", 222.4, 34.2),
        EquityConstituent("JIOFIN.NS", "Jio Financial Services Ltd", "Financial Services", 635.3, 2.1),
        EquityConstituent("VEDL.NS", "Vedanta Ltd", "Metals & Mining", 371.7, 28.4),
        EquityConstituent("CHOLAFIN.NS", "Cholamandalam Investment & Finance", "Financial Services", 83.9, 32.4),
        EquityConstituent("ADANIPOWER.NS", "Adani Power Ltd", "Power & Utilities", 385.7, 18.5),
        EquityConstituent("GAIL.NS", "GAIL (India) Ltd", "Energy - Utilities", 657.5, 11.6),
        EquityConstituent("PNB.NS", "Punjab National Bank", "Financial Services", 1101.1, 7.2),
        EquityConstituent("INDUSINDBK.NS", "IndusInd Bank Ltd", "Financial Services", 77.8, 82.4),
        EquityConstituent("BANKBARODA.NS", "Bank of Baroda", "Financial Services", 517.1, 28.5),
        EquityConstituent("SHREECEM.NS", "Shree Cement Ltd", "Construction Materials", 3.6, 520.0),
        EquityConstituent("INDIGO.NS", "InterGlobe Aviation Ltd", "Aviation & Logistics", 38.6, 135.2),
        EquityConstituent("BPCL.NS", "Bharat Petroleum Corporation Ltd", "Energy - Refining & Marketing", 216.9, 38.4),
        EquityConstituent("TVSMOTOR.NS", "TVS Motor Company Ltd", "Automobiles & Components", 47.5, 34.2),
        EquityConstituent("DIVISLAB.NS", "Divis Laboratories Ltd", "Healthcare & Pharmaceuticals", 26.5, 48.6),
        EquityConstituent("CIPLA.NS", "Cipla Ltd", "Healthcare & Pharmaceuticals", 80.7, 38.4),
        EquityConstituent("EICHERMOT.NS", "Eicher Motors Ltd", "Automobiles & Components", 27.4, 118.5),
        EquityConstituent("AMBUJACEM.NS", "Ambuja Cements Ltd", "Construction Materials", 246.3, 14.2),
        EquityConstituent("TATACONSUM.NS", "Tata Consumer Products Ltd", "Fast Moving Consumer Goods", 95.3, 10.8),
        EquityConstituent("POLYCAB.NS", "Polycab India Ltd", "Capital Goods - Cables", 15.0, 98.4),
        EquityConstituent("DRREDDY.NS", "Dr. Reddys Laboratories Ltd", "Healthcare & Pharmaceuticals", 16.7, 215.0),
        EquityConstituent("ABB.NS", "ABB India Ltd", "Capital Goods", 21.2, 45.2),
        EquityConstituent("DABUR.NS", "Dabur India Ltd", "Fast Moving Consumer Goods", 177.2, 8.4),
        EquityConstituent("HAVELLS.NS", "Havells India Ltd", "Consumer Durables", 62.7, 15.6),
        EquityConstituent("HEROMOTOCO.NS", "Hero MotoCorp Ltd", "Automobiles & Components", 20.0, 155.0),
        EquityConstituent("JSWENERGY.NS", "JSW Energy Ltd", "Power & Utilities", 164.5, 7.8),
        EquityConstituent("JSWSTEEL.NS", "JSW Steel Ltd", "Metals & Mining", 244.5, 24.5),
        EquityConstituent("TATAPOWER.NS", "Tata Power Company Ltd", "Power & Utilities", 319.5, 11.2),
        EquityConstituent("MOTHERSON.NS", "Samvardhana Motherson International", "Automobiles & Components", 676.6, 3.2),
        EquityConstituent("BOSCHLTD.NS", "Bosch Ltd", "Automobiles & Components", 2.95, 480.0),
        EquityConstituent("GODREJCP.NS", "Godrej Consumer Products Ltd", "Fast Moving Consumer Goods", 102.3, 14.8),
        EquityConstituent("TORNTPOWER.NS", "Torrent Power Ltd", "Power & Utilities", 48.1, 32.4),
        EquityConstituent("TORNTPHARM.NS", "Torrent Pharmaceuticals Ltd", "Healthcare & Pharmaceuticals", 33.8, 38.5),
        EquityConstituent("BDL.NS", "Bharat Dynamics Ltd", "Aerospace & Defence", 18.3, 18.2),
        EquityConstituent("CANBK.NS", "Canara Bank", "Financial Services", 907.1, 12.4),
        EquityConstituent("CGPOWER.NS", "CG Power & Industrial Solutions", "Capital Goods", 152.7, 4.8),
        EquityConstituent("CUMMINSIND.NS", "Cummins India Ltd", "Capital Goods", 27.7, 38.6),
        EquityConstituent("MAXHEALTH.NS", "Max Healthcare Institute Ltd", "Healthcare Services", 97.1, 9.2),
        EquityConstituent("PERSISTENT.NS", "Persistent Systems Ltd", "Information Technology", 15.4, 62.5),
        EquityConstituent("PFC.NS", "Power Finance Corporation Ltd", "Financial Services", 330.0, 42.5),
        EquityConstituent("RECLTD.NS", "REC Ltd", "Financial Services", 263.3, 39.8),
        EquityConstituent("SHRIRAMFIN.NS", "Shriram Finance Ltd", "Financial Services", 37.6, 142.0),
        EquityConstituent("SUPREMEIND.NS", "Supreme Industries Ltd", "Capital Goods - Plastics", 12.7, 68.4),
        EquityConstituent("TATACOMM.NS", "Tata Communications Ltd", "Telecommunications", 28.5, 32.1),
        EquityConstituent("TATAELXSI.NS", "Tata Elxsi Ltd", "Information Technology", 6.23, 98.5),
        EquityConstituent("TIINDIA.NS", "Tube Investments of India Ltd", "Automobiles & Components", 19.3, 24.8),
        EquityConstituent("UNIONBANK.NS", "Union Bank of India", "Financial Services", 763.4, 14.5),
        EquityConstituent("UNITDSPR.NS", "United Spirits Ltd", "Fast Moving Consumer Goods", 72.7, 14.2),
        EquityConstituent("UPL.NS", "UPL Ltd", "Chemicals & Agro", 75.1, 12.0),
        EquityConstituent("YESBANK.NS", "Yes Bank Ltd", "Financial Services", 3134.0, 0.45),
        EquityConstituent("IRFC.NS", "Indian Railway Finance Corporation", "Financial Services", 1306.9, 3.8),
        EquityConstituent("RVNL.NS", "Rail Vikas Nigam Ltd", "Construction & Engineering", 208.5, 5.6),
        EquityConstituent("NHPC.NS", "NHPC Ltd", "Power & Utilities", 1004.5, 2.9),
        EquityConstituent("SUZLON.NS", "Suzlon Energy Ltd", "Capital Goods - Renewable", 1364.0, 0.62),
        EquityConstituent("MAZDOCK.NS", "Mazagon Dock Shipbuilders Ltd", "Aerospace & Defence", 20.2, 68.4),
        EquityConstituent("HUDCO.NS", "Housing & Urban Development Corp", "Financial Services", 200.2, 8.5),
        EquityConstituent("BHEL.NS", "Bharat Heavy Electricals Ltd", "Capital Goods", 348.2, 2.8),
        EquityConstituent("APOLLOHOSP.NS", "Apollo Hospitals Enterprise Ltd", "Healthcare Services", 14.4, 68.5),
        EquityConstituent("HINDZINC.NS", "Hindustan Zinc Ltd", "Metals & Mining", 422.5, 18.5),
        EquityConstituent("COLPAL.NS", "Colgate-Palmolive (India) Ltd", "Fast Moving Consumer Goods", 27.2, 48.6),
        EquityConstituent("MARICO.NS", "Marico Ltd", "Fast Moving Consumer Goods", 129.5, 10.8),
        EquityConstituent("BERGEPAINT.NS", "Berger Paints India Ltd", "Consumer Durables", 116.6, 9.5),
        EquityConstituent("NAUKRI.NS", "Info Edge (India) Ltd", "Consumer Services - Internet", 13.0, 48.2),
    ]

    def __init__(self, timeout: int = 12, max_workers: int = 8, max_retries: int = 3, backoff_factor: float = 1.0):
        self.timeout = timeout
        self.max_workers = max_workers
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
        adapter = HTTPAdapter(max_retries=retries, pool_connections=self.max_workers, pool_maxsize=self.max_workers)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        })
        return session

    def fetch_equity_record(self, constituent: EquityConstituent) -> Optional[EquityMarketRecord]:
        url = self.ENDPOINT_TEMPLATE.format(symbol=constituent.symbol)
        clean_symbol = constituent.symbol.replace(".NS", "").replace("%26", "&")
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 2))
                time.sleep(retry_after)
                response = self.session.get(url, timeout=self.timeout)

            if response.status_code != 200:
                logger.warning(f"Failed to fetch {clean_symbol} (HTTP {response.status_code})")
                return None

            payload = response.json()
            result = payload.get("chart", {}).get("result", [])
            if not result:
                return None

            meta: Dict[str, Any] = result[0].get("meta", {})
            current_price = float(meta.get("regularMarketPrice") or 0.0)
            prev_close = float(meta.get("chartPreviousClose") or current_price)
            if prev_close > 0:
                price_change_pct = round(((current_price - prev_close) / prev_close) * 100.0, 2)
            else:
                price_change_pct = round(float(meta.get("regularMarketChangePercent") or 0.0), 2)

            day_high = float(meta.get("regularMarketDayHigh") or current_price)
            day_low = float(meta.get("regularMarketDayLow") or current_price)
            fifty_two_week_high = float(meta.get("fiftyTwoWeekHigh") or day_high)
            fifty_two_week_low = float(meta.get("fiftyTwoWeekLow") or day_low)
            volume = int(meta.get("regularMarketVolume") or 0)

            turnover_inr_cr = round((current_price * volume) / 10000000.0, 2)
            market_cap_inr_cr = round(current_price * constituent.shares_outstanding_cr, 2)
            trailing_pe = round(current_price / constituent.ttm_eps_inr, 2) if constituent.ttm_eps_inr > 0 else 0.0

            raw_time = meta.get("regularMarketTime")
            if raw_time:
                timestamp = datetime.fromtimestamp(raw_time, tz=timezone.utc).isoformat()
            else:
                timestamp = datetime.now(timezone.utc).isoformat()

            return EquityMarketRecord(
                symbol=clean_symbol,
                company_name=constituent.company_name,
                sector=constituent.sector,
                current_price_inr=current_price,
                previous_close_inr=prev_close,
                price_change_pct=price_change_pct,
                day_high_inr=day_high,
                day_low_inr=day_low,
                fifty_two_week_high_inr=fifty_two_week_high,
                fifty_two_week_low_inr=fifty_two_week_low,
                trading_volume=volume,
                turnover_inr_cr=turnover_inr_cr,
                market_cap_inr_cr=market_cap_inr_cr,
                trailing_pe=trailing_pe,
                exchange="NSE",
                timestamp=timestamp,
            )
        except Exception as error:
            logger.error(f"Error extracting metrics for {clean_symbol}: {error}")
            return None

    def execute_pipeline(self) -> List[EquityMarketRecord]:
        logger.info(f"Initiating concurrent extraction for {len(self.CONSTITUENTS)} Nifty constituents.")
        records: List[EquityMarketRecord] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_constituent = {
                executor.submit(self.fetch_equity_record, c): c for c in self.CONSTITUENTS
            }
            for future in concurrent.futures.as_completed(future_to_constituent):
                record = future.result()
                if record is not None:
                    records.append(record)

        records.sort(key=lambda x: x.market_cap_inr_cr, reverse=True)
        logger.info(f"Extraction pipeline completed. Successfully processed {len(records)} records.")
        return records

    @staticmethod
    def export_to_csv(records: List[EquityMarketRecord], destination_path: str = "api_data_extract.csv") -> None:
        if not records:
            raise ValueError("Cannot export empty equity dataset to CSV.")

        serialized = [asdict(r) for r in records]
        df = pd.DataFrame.from_records(serialized)
        df.to_csv(destination_path, index=False, encoding="utf-8")
        logger.info(f"Persisted {len(df)} validated equity records to {destination_path}")


def main() -> None:
    output_destination = "api_data_extract.csv"
    pipeline = NiftyDataPipeline(timeout=12, max_workers=8, max_retries=3, backoff_factor=1.0)
    dataset = pipeline.execute_pipeline()
    pipeline.export_to_csv(dataset, destination_path=output_destination)


if __name__ == "__main__":
    main()
