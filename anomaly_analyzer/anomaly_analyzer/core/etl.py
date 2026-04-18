from typing import Any

import polars as pl


def process_quotes(quotes_data: list[dict[str, Any]]) -> pl.DataFrame:
    """Process raw J-Quants quotes data into a Polars DataFrame with derived features.

    Args:
        quotes_data: List of dictionaries containing daily quotes from the API.

    Returns:
        Polars DataFrame with calculated returns and datetime features.
    """
    if not quotes_data:
        return pl.DataFrame()

    # Create initial DataFrame
    df = pl.DataFrame(quotes_data)

    # Convert and cast types
    df = df.with_columns([
        pl.col("Date").str.strptime(pl.Date, "%Y-%m-%d"),
        pl.col("Code").cast(pl.Utf8),
        pl.col("Open").cast(pl.Float32),
        pl.col("High").cast(pl.Float32),
        pl.col("Low").cast(pl.Float32),
        pl.col("Close").cast(pl.Float32),
        pl.col("Volume").cast(pl.Float32),
    ])

    # Sort by Code and Date to ensure proper shifting
    df = df.sort(["Code", "Date"])

    # Forward fill 0.0 or null values in OHLC columns based on previous valid Close
    # Since prices cannot naturally be 0.0, we treat 0.0 as missing data (e.g., no trades)
    for col_name in ["Open", "High", "Low", "Close"]:
        df = df.with_columns(
            pl.when((pl.col(col_name) == 0.0) | pl.col(col_name).is_null())
            .then(None)
            .otherwise(pl.col(col_name))
            .alias(col_name)
        )

    # Apply forward fill within each Code group
    df = df.with_columns([
        pl.col(c).forward_fill().over("Code")
        for c in ["Open", "High", "Low", "Close"]
    ])

    # Feature Engineering
    # Calculate returns and date features
    df = df.with_columns([
        # Previous day's close
        pl.col("Close").shift(1).over("Code").alias("Prev_Close"),

        # Day of week (1=Monday, 7=Sunday according to Polars dt.weekday())
        pl.col("Date").dt.weekday().alias("DayOfWeek"),

        # Is Month End (simplified: compare month of current date with next date's month)
        (pl.col("Date").dt.month() != pl.col("Date").shift(-1).over("Code").dt.month()).alias("Is_MonthEnd")
    ])

    # Calculate various returns
    df = df.with_columns([
        # Return_Daily: (Close - Prev_Close) / Prev_Close
        ((pl.col("Close") - pl.col("Prev_Close")) / pl.col("Prev_Close")).alias("Return_Daily"),

        # Return_Intraday: (Close - Open) / Open
        ((pl.col("Close") - pl.col("Open")) / pl.col("Open")).alias("Return_Intraday"),

        # Return_Overnight: (Open - Prev_Close) / Prev_Close
        ((pl.col("Open") - pl.col("Prev_Close")) / pl.col("Prev_Close")).alias("Return_Overnight"),
    ])

    # Drop intermediate column if not needed, but Prev_Close is often useful.
    # df = df.drop("Prev_Close")

    # Drop any remaining rows with nulls in critical columns (like first row of each group due to shift)
    return df.drop_nulls(subset=["Return_Daily", "Return_Intraday", "Return_Overnight"])
