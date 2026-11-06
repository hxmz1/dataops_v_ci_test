import sys
import duckdb

WAREHOUSE = "warehouse.duckdb"

def main(path):
    con = duckdb.connect(WAREHOUSE)
    try:
        con.execute("CREATE SCHEMA IF NOT EXISTS raw")

        con.execute("""
            CREATE OR REPLACE TABLE raw.orders AS
            SELECT *,
                   row_number() OVER () AS _row_number,
                   ? AS _source_file,
                   current_timestamp AS _loaded_at
            FROM read_csv(
                ?,
                delim = ',',
                header = true,
                auto_detect = false,
                columns = {
                    'order_id': 'VARCHAR',
                    'order_date': 'VARCHAR',
                    'customer_id': 'VARCHAR',
                    'country': 'VARCHAR',
                    'product': 'VARCHAR',
                    'quantity': 'VARCHAR',
                    'unit_price': 'VARCHAR'
                }
            )
        """, [path, path])

        print("Actual columns:")
        print([r[0] for r in con.execute(
            "DESCRIBE raw.orders"
        ).fetchall()])

        n = con.execute(
            "SELECT COUNT(*) FROM raw.orders"
        ).fetchone()[0]
        print(f"Loaded {n} rows from {path} into raw.orders")
    finally:
        con.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python load_raw.py <csv_file>")
    main(sys.argv[1])
