import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SODA_DIR = Path(__file__).resolve().parent
TABLES = ("orders_clean", "revenue_by_country")


def project_python():
    candidates = (
        ROOT / ".venv" / "Scripts" / "python.exe",
        ROOT / ".venv" / "bin" / "python",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "Project Python not found. Create .venv or update soda/refresh_database.py."
    )


def main():
    source_db = ROOT / "warehouse.duckdb"
    if not source_db.is_file():
        raise FileNotFoundError(
            f"{source_db} does not exist. Run dbt build before refreshing Soda data."
        )

    output_db = SODA_DIR / "warehouse-soda.duckdb"
    project_code = """
import sys
import duckdb
from pathlib import Path

source_db, output_dir = sys.argv[1:]
connection = duckdb.connect(source_db, read_only=True)
try:
    for table in ("orders_clean", "revenue_by_country"):
        output_file = (
            Path(output_dir) / f"{table}.parquet"
        ).as_posix().replace("'", "''")
        connection.execute(
            f"COPY (SELECT * FROM {table}) TO '{output_file}' (FORMAT PARQUET)"
        )
finally:
    connection.close()
"""
    soda_code = """
import sys
import duckdb
from pathlib import Path

output_db, *parquet_files = sys.argv[1:]
connection = duckdb.connect(output_db)
try:
    for table, parquet_file in zip(
        ("orders_clean", "revenue_by_country"), parquet_files, strict=True
    ):
        parquet_file = Path(parquet_file).as_posix().replace("'", "''")
        connection.execute(
            f"CREATE TABLE {table} AS SELECT * FROM read_parquet('{parquet_file}')"
        )
    for table in ("orders_clean", "revenue_by_country"):
        connection.execute(f"SELECT count(*) FROM {table}").fetchone()
finally:
    connection.close()
"""

    with tempfile.TemporaryDirectory(prefix=".soda-refresh-", dir=SODA_DIR) as temp:
        temp_dir = Path(temp)
        parquet_files = [temp_dir / f"{table}.parquet" for table in TABLES]
        candidate_db = temp_dir / output_db.name

        subprocess.run(
            [
                str(project_python()),
                "-c",
                project_code,
                str(source_db),
                str(temp_dir),
            ],
            check=True,
        )
        subprocess.run(
            [
                sys.executable,
                "-c",
                soda_code,
                str(candidate_db),
                *(str(path) for path in parquet_files),
            ],
            check=True,
        )
        candidate_db.replace(output_db)

    print(f"Prepared Soda-compatible database: {output_db}")


if __name__ == "__main__":
    main()
