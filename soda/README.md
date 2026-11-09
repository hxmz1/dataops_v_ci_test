# Soda checks

Soda Core 3.5.6 requires DuckDB `<1.1`, while the dbt project uses a newer
DuckDB that writes an incompatible warehouse format. Refresh a compatible copy
of the two tables used by the checks before scanning:

```powershell
python soda\refresh_database.py
soda scan -d shop -c soda\configuration.yml soda\checks.yml
```

Run the refresh command from the Soda environment after rebuilding the dbt
warehouse. It reads the dbt database without modifying it and stages the data
through Parquet into `soda\warehouse-soda.duckdb`.
