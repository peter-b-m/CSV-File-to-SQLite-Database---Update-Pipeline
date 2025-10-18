# data_loader.py

import csv
import logging
import os
import sqlite3
from utils.utils_db import table_exists
from utils.utils_schema import TableSchema

def load_csvs_to_table(conn: sqlite3.Connection, table_name: str, schema: TableSchema, folder_path: str, dry_run: bool = False, log_to_file: bool = True, verbose: bool = False):

    total_inserted = 0
    total_skipped = 0

    csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]
    cursor = conn.cursor()

    schema_headers = [col.name for col in schema.columns]

    logging.info(f"[CLEAR] Deleting existing data from '{table_name}'")
    if dry_run:
        logging.info(f"[DRY-RUN] Would execute: DELETE FROM {table_name};")
    else:
        try:
            cursor.execute(f"DELETE FROM {table_name};")
            conn.commit()
        except Exception as e:
            logging.error(f"Failed to run: DELETE FROM {table_name}: {e}")

    for file in csv_files:

        inserted_rows = 0
        skipped_rows = 0

        path = os.path.join(folder_path, file)
        logging.info(f"[LOAD] Inserting data from '{file}' into '{table_name}'")

        with open(path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                logging.error(f"[SKIP FILE] '{file}' is empty or malformed.")
                continue

            csv_headers = [h.strip() for h in reader.fieldnames]
            # Check for exact match
            missing = set(schema_headers) - set(csv_headers)
            extra = set(csv_headers) - set(schema_headers)
            if csv_headers != schema_headers or missing or extra:
                logging.error(f"[SKIP FILE] Header mismatch in '{file}'")
                logging.error(f"  CSV headers   : {csv_headers}")
                logging.error(f"  Schema headers: {schema_headers}")
                logging.error(f"  Missing headers: {missing}")
                logging.error(f"  Unexpected headers: {extra}")
                continue

            columns = [col.name for col in schema.columns]

            for i, row in enumerate(reader, start=1):
                # Validate required fields
                missing_required = [
                    col.name for col in schema.columns
                    if col.not_null and (row.get(col.name) is None or row.get(col.name).strip() == "")
                ]
                if missing_required:
                    logging.error(f"[SKIP ROW {i} in '{file}'] Missing required fields: {missing_required}")
                    skipped_rows += 1
                    continue

                # Prepare values
                values = [row.get(col.name, None) for col in schema.columns]
                placeholders = ", ".join(["?"] * len(values))
                sql = f"INSERT INTO {table_name} ({', '.join(schema_headers)}) VALUES ({placeholders})"
                if dry_run:
                    if verbose and inserted_rows < 3:
                        logging.info(f"[DRY-RUN] Sample insert: {values}")
                else:
                    try:
                        cursor.execute(sql, values)
                    except Exception as e:
                        logging.error(f"Failed to insert row into '{table_name}': {e}")

                inserted_rows += 1

            if dry_run:
                logging.info(f"[DRY-RUN] '{file}' would insert {inserted_rows} rows, skip {skipped_rows} rows.")
            else:
                logging.info(f"'{file}' inserted {inserted_rows} rows, skipped {skipped_rows} rows.")

            total_inserted += inserted_rows
            total_skipped += skipped_rows

    if not dry_run:
        conn.commit()
    logging.info(f"✅ Loaded {len(csv_files)} file(s) into '{table_name}'")

    if dry_run:
        logging.info(f"[DRY-RUN] Total rows that would be inserted: {total_inserted}")
        logging.info(f"[DRY-RUN] Total rows that would be skipped: {total_skipped}")
    else:
        logging.info(f"📊 Total rows inserted: {total_inserted}")
        logging.info(f"📉 Total rows skipped : {total_skipped}")

    return {
        "files_processed": len(csv_files),
        "rows_inserted": total_inserted,
        "rows_skipped": total_skipped
    }
