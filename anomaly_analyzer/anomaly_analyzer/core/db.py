from pathlib import Path

import duckdb
import polars as pl

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
PARQUET_FILE = DATA_DIR / "quotes.parquet"

def save_quotes(df: pl.DataFrame) -> None:
    """Save quotes data to parquet, appending and deduplicating if it exists.

    Args:
        df: Polars DataFrame containing new quotes data.
    """
    if not PARQUET_FILE.exists():
        df.write_parquet(PARQUET_FILE)
        return

    # Load existing data
    existing_df = pl.read_parquet(PARQUET_FILE)

    # Combine and deduplicate
    combined_df = pl.concat([existing_df, df])
    deduplicated_df = combined_df.unique(subset=["Date", "Code"], keep="last")

    # Write back
    deduplicated_df.write_parquet(PARQUET_FILE)

def load_quotes(codes: list[str]) -> pl.DataFrame:
    """Load quotes data for specific codes from parquet using DuckDB.

    Args:
        codes: List of stock codes to filter.

    Returns:
        Polars DataFrame containing the filtered quotes.
    """
    if not PARQUET_FILE.exists():
        return pl.DataFrame()

    codes_str = ", ".join(f"'{code}'" for code in codes)

    # Use DuckDB to efficiently query the parquet file
    query = f"""
        SELECT *
        FROM read_parquet('{PARQUET_FILE}')
        WHERE Code IN ({codes_str})
        ORDER BY Code, Date
    """

    # Execute query and convert to Polars DataFrame
    return duckdb.query(query).pl()
