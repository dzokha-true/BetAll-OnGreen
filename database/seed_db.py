"""
seed_db.py
----------
Reads CSV files for our tech/semi watchlist and populates a SQLite database
with 4 tables:
  - stock_prices   : raw OHLCV data
  - stock_signals  : derived indicators (pct_change, volume ratio, RSI, 52w high/low)
  - clients        : mock client portfolio data
  - reports        : placeholder for generated morning briefs

Usage:
  python seed_db.py --csv_dir /path/to/csv/folder

The CSV files are expected to have columns:
  date, open, high, low, close, adj_close, volume
"""

import os
import sqlite3
import argparse
import pandas as pd
from datetime import datetime, timedelta

# ── Config ────────────────────────────────────────────────────────────────────

DB_PATH = "market_brief.db"

# Our tech/semi watchlist — make sure these CSVs exist in your csv_dir
WATCHLIST = [
    "NVDA", "AMD", "INTC", "ASML", "QCOM",
    "AVGO", "MSFT", "AAPL", "GOOGL",
    "CRM",  "ADBE", "SNPS", "KLAC", "AMAT"
]

# Mock clients with realistic semi/tech holdings
MOCK_CLIENTS = [
    {"name": "Sarah Chen",      "email": "schen@hedgeco.com",      "holdings": "NVDA,AMD,ASML"},
    {"name": "James Hartley",   "email": "jhartley@alphafund.com", "holdings": "MSFT,AAPL,GOOGL"},
    {"name": "Priya Patel",     "email": "ppatel@meridian.com",    "holdings": "NVDA,QCOM,AVGO"},
    {"name": "Tom Walsh",       "email": "twalsh@bluerock.com",    "holdings": "INTC,AMD,AMAT"},
    {"name": "Lisa Monroe",     "email": "lmonroe@crestview.com",  "holdings": "MSFT,CRM,ADBE"},
    {"name": "David Kim",       "email": "dkim@quantedge.com",     "holdings": "NVDA,ASML,KLAC"},
    {"name": "Rachel Torres",   "email": "rtorres@veritas.com",    "holdings": "AAPL,GOOGL,META"},
    {"name": "Michael Osei",    "email": "mosei@pinnacle.com",     "holdings": "AVGO,QCOM,SNPS"},
    {"name": "Emma Schulz",     "email": "eschulz@northpoint.com", "holdings": "AMD,NVDA,MSFT"},
    {"name": "Carlos Rivera",   "email": "crivera@stonegate.com",  "holdings": "KLAC,AMAT,ASML"},
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Compute RSI for a price series."""
    delta = series.diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs  = avg_gain / avg_loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def load_ticker(csv_dir: str, ticker: str) -> pd.DataFrame | None:
    """Load a single ticker CSV and return a cleaned DataFrame."""
    path = os.path.join(csv_dir, f"{ticker}.csv")
    if not os.path.exists(path):
        print(f"  ⚠  {ticker}.csv not found — skipping")
        return None

    df = pd.read_csv(path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Normalise the date column
    date_col = next((c for c in df.columns if "date" in c), None)
    if date_col is None:
        print(f"  ⚠  {ticker}: no date column found — skipping")
        return None
    df.rename(columns={date_col: "date"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"]).dt.date

    # Normalise price/volume columns
    rename_map = {}
    for col in df.columns:
        if "adj" in col and "close" in col:
            rename_map[col] = "adj_close"
        elif col == "close":
            rename_map[col] = "close"
        elif col == "open":
            rename_map[col] = "open"
        elif col == "high":
            rename_map[col] = "high"
        elif col == "low":
            rename_map[col] = "low"
        elif col == "volume":
            rename_map[col] = "volume"
    df.rename(columns=rename_map, inplace=True)

    required = ["date", "open", "high", "low", "close", "volume"]
    for col in required:
        if col not in df.columns:
            print(f"  ⚠  {ticker}: missing column '{col}' — skipping")
            return None

    df["ticker"] = ticker
    df = df.sort_values("date").reset_index(drop=True)
    return df


# ── Database setup ────────────────────────────────────────────────────────────

def create_tables(conn: sqlite3.Connection):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker      TEXT    NOT NULL,
            date        DATE    NOT NULL,
            open        REAL,
            high        REAL,
            low         REAL,
            close       REAL,
            adj_close   REAL,
            volume      INTEGER,
            pct_change  REAL,
            UNIQUE(ticker, date)
        );

        CREATE TABLE IF NOT EXISTS stock_signals (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker              TEXT    NOT NULL,
            date                DATE    NOT NULL,
            avg_volume_30d      REAL,
            volume_ratio        REAL,
            rsi_14              REAL,
            price_52w_high      REAL,
            price_52w_low       REAL,
            pct_from_52w_high   REAL,
            UNIQUE(ticker, date)
        );

        CREATE TABLE IF NOT EXISTS clients (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            email    TEXT NOT NULL,
            holdings TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS reports (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            generated_at    TEXT NOT NULL,
            brief_text      TEXT,
            call_list       TEXT,
            email_drafts    TEXT
        );
    """)
    conn.commit()


# ── Seeding ───────────────────────────────────────────────────────────────────

def seed_ticker(conn: sqlite3.Connection, df: pd.DataFrame, ticker: str):
    """Insert price rows and compute + insert signal rows for one ticker."""

    # ── stock_prices ──────────────────────────────────────────────────────────
    df["pct_change"] = df["close"].pct_change() * 100

    price_rows = []
    for _, row in df.iterrows():
        price_rows.append((
            ticker,
            str(row["date"]),
            float(row["open"])      if pd.notna(row["open"])      else None,
            float(row["high"])      if pd.notna(row["high"])      else None,
            float(row["low"])       if pd.notna(row["low"])       else None,
            float(row["close"])     if pd.notna(row["close"])     else None,
            float(row.get("adj_close", row["close"])) if pd.notna(row.get("adj_close", row["close"])) else None,
            int(row["volume"])      if pd.notna(row["volume"])    else None,
            float(row["pct_change"]) if pd.notna(row["pct_change"]) else None,
        ))

    conn.executemany("""
        INSERT OR IGNORE INTO stock_prices
            (ticker, date, open, high, low, close, adj_close, volume, pct_change)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, price_rows)

    # ── stock_signals ─────────────────────────────────────────────────────────
    df["avg_volume_30d"]    = df["volume"].rolling(30, min_periods=1).mean()
    df["volume_ratio"]      = df["volume"] / df["avg_volume_30d"].replace(0, 1)
    df["rsi_14"]            = compute_rsi(df["close"])
    df["price_52w_high"]    = df["close"].rolling(252, min_periods=1).max()
    df["price_52w_low"]     = df["close"].rolling(252, min_periods=1).min()
    df["pct_from_52w_high"] = ((df["close"] - df["price_52w_high"]) / df["price_52w_high"]) * 100

    signal_rows = []
    for _, row in df.iterrows():
        signal_rows.append((
            ticker,
            str(row["date"]),
            float(row["avg_volume_30d"])    if pd.notna(row["avg_volume_30d"])    else None,
            float(row["volume_ratio"])      if pd.notna(row["volume_ratio"])      else None,
            float(row["rsi_14"])            if pd.notna(row["rsi_14"])            else None,
            float(row["price_52w_high"])    if pd.notna(row["price_52w_high"])    else None,
            float(row["price_52w_low"])     if pd.notna(row["price_52w_low"])     else None,
            float(row["pct_from_52w_high"]) if pd.notna(row["pct_from_52w_high"]) else None,
        ))

    conn.executemany("""
        INSERT OR IGNORE INTO stock_signals
            (ticker, date, avg_volume_30d, volume_ratio, rsi_14,
             price_52w_high, price_52w_low, pct_from_52w_high)
        VALUES (?,?,?,?,?,?,?,?)
    """, signal_rows)

    conn.commit()
    print(f"  ✓  {ticker}: {len(df)} rows inserted")


def seed_clients(conn: sqlite3.Connection):
    conn.executemany(
        "INSERT INTO clients (name, email, holdings) VALUES (?,?,?)",
        [(c["name"], c["email"], c["holdings"]) for c in MOCK_CLIENTS]
    )
    conn.commit()
    print(f"  ✓  {len(MOCK_CLIENTS)} mock clients inserted")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Seed the market brief SQLite database")
    parser.add_argument("--csv_dir", required=True, help="Path to folder containing ticker CSVs")
    parser.add_argument("--db",      default=DB_PATH, help="SQLite DB path (default: market_brief.db)")
    args = parser.parse_args()

    print(f"\n🗄  Creating database at: {args.db}")
    conn = sqlite3.connect(args.db)
    create_tables(conn)

    print(f"\n📈 Seeding {len(WATCHLIST)} tickers from: {args.csv_dir}")
    for ticker in WATCHLIST:
        df = load_ticker(args.csv_dir, ticker)
        if df is not None:
            seed_ticker(conn, df, ticker)

    print(f"\n👥 Seeding mock clients...")
    seed_clients(conn)

    conn.close()
    print(f"\n✅ Done! Database ready at: {args.db}")
    print(f"\nExample Snow Leopard queries you can now ask:")
    print(f"  → 'Which stocks moved more than 2% yesterday?'")
    print(f"  → 'Which stocks had volume more than 2x their 30-day average?'")
    print(f"  → 'Which clients hold NVDA?'")
    print(f"  → 'What is the RSI for NVDA and AMD today?'")
    print(f"  → 'Which stocks are within 5% of their 52-week high?'")


if __name__ == "__main__":
    main()