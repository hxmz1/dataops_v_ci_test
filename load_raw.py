
import sys

import duckdb

WAREHOUSE = "warehouse.duckdb"


def main(path):
    """Extract + Load: copy the raw file into the warehouse, exactly as it is."""

    con = duckdb.connect(WAREHOUSE)

    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw")

        con.execute("""
            CREATE OR REPLACE TABLE raw.orders AS
            SELECT
                *,
                row_number() OVER () AS _row_number,
                ? AS _source_file,
                current_timestamp AS _loaded_at
            FROM read_csv(
                ?,
                header = true,
                delim = ',',
                all_varchar = true
            )
        """, [path, path])

        n = con.execute(
            "SELECT COUNT(*) FROM raw.orders"
        ).fetchone()[0]

        print(f"Loaded {n} rows from {path} into raw.orders")

    finally:
        con.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python load_raw.py <csv_file>")
        sys.exit(1)

    main(sys.argv[1])
