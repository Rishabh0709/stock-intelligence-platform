# Phase 1B installation

This release upgrades the Phase 1A foundation. It does not contain a database
file and does not delete existing application data.

## Apply

1. Stop Streamlit.
2. Back up `database/stock_data.db` once.
3. Extract the release into the project root and replace included files.
4. Install the cleaned dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Apply migrations explicitly:

   ```powershell
   python scripts\migrate_database.py
   ```

   Application startup also applies pending migrations automatically. The
   explicit command makes any migration error visible before Streamlit starts.

6. Run the complete quality gate:

   ```powershell
   python scripts\quality_gate.py
   ```

7. Start the dashboard:

   ```powershell
   python -m streamlit run dashboard/app.py
   ```

## What changes

- Existing candles in the sync buffer are reconciled through SQLite upsert.
- Sync results distinguish inserted, corrected and unchanged candles.
- Candle provider and verification timestamps are recorded.
- Alembic owns database schema evolution and safely adopts existing tables.
- Runtime and development dependencies are separated and stored as UTF-8.
- The quality gate runs the complete isolated test suite.
- Legacy print scripts are replaced with portable assertion-based tests.
