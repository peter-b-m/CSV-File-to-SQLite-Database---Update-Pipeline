# run_raw_layer_update.py

import logging
from utils.data_loader import load_csvs_to_table
from utils.schema_diff import diff_schema
from utils.utils_db import connect_to_db, table_exists, get_table_schema, get_tables_from_db
from utils.utils_manifest import load_manifest, validate_job
from utils.utils_schema import load_table_schema
from utils.utils_sql import generate_create_table_sql

def run_raw_layer_update(script_dir: str, dry_run: bool, env: str, db_path: str, manifest_path: str, drop_orphans: bool, verbose: bool, log_to_file: bool, use_sample: bool):

    logging.info(f"\n[UPDATE] Updating Raw Layer")

    jobs = load_manifest(script_dir, env, manifest_path, use_sample)

    with connect_to_db(db_path) as conn:

        db_raw_tables = get_tables_from_db(conn, "raw")
        manifest_tables = set(job.name for job in jobs)
        extra_raw_tables = db_raw_tables - manifest_tables
        for table in sorted(extra_raw_tables):
            logging.warning(f"\n[WARNING] DB has raw table not declared in manifest: {table}")
            if drop_orphans:
                if dry_run:
                    logging.info(f"[DRY-RUN] Would execute: DROP TABLE IF EXISTS {table};")
                else:
                    try:
                        conn.execute(f"DROP TABLE IF EXISTS {table};")
                        conn.commit()
                        logging.info(f"✅ Dropped orphan table: {table}")
                    except Exception as e:
                        logging.error(f"Failed to drop orphan table '{table}': {e}")

        skipped_jobs = []
        loaded_count = 0

        for job in jobs:
            logging.info(f"\n[UPDATE] Processing table: {job.name}")
            logging.info(f"[JOB] {job.name} — required: {job.required}, load: {job.load}, allow_schema_change: {job.allow_schema_change}")

            if not validate_job(job):
                skipped_jobs.append(job.name)
                logging.info(f"[SKIP] Job skipped due to validation: {job.name}")
                continue

            does_table_exist = table_exists(conn, job.name)

            if not job.required:
                if does_table_exist:
                    logging.info(f"[DROP] Dropping unused table: {job.name}")
                    if dry_run:
                        logging.info(f"[DRY-RUN] Would execute: DROP TABLE IF EXISTS {job.name};")
                    else:
                        try:
                            conn.execute(f"DROP TABLE IF EXISTS {job.name};")
                            conn.commit()
                        except Exception as e:
                            logging.error(f"Failed to run: DROP TABLE IF EXISTS {job.name}: {e}")
                else:
                    logging.info(f"[SKIP] Table: {job.name} not required and does not exist in database")
                continue

            schema = load_table_schema(job.schema_path)

            if not does_table_exist:
                logging.info(f"[CREATE] Table '{job.name}' does NOT exist. Creating...")
                sql = generate_create_table_sql(job.name, schema)
                if dry_run:
                    logging.info(f"[DRY-RUN] Would execute: {sql}")
                else:
                    try:
                        conn.execute(sql)
                    except Exception as e:
                        logging.error(f"Failed to run: CREATE TABLE {job.name}: {e}")

                logging.info(f"✅ Created table '{job.name}'")
            else:
                db_schema = get_table_schema(conn, job.name)
                diffs = diff_schema(schema, db_schema)
                if not diffs:
                    logging.info(f"✅ Table '{job.name}' matches schema. No action needed")
                elif job.allow_schema_change:
                    logging.warning(f"⚠️ Schema drift detected in '{job.name}'. Recreating table...")
                    if dry_run:
                        logging.info(f"[DRY-RUN] Would execute: DROP TABLE IF EXISTS {job.name};")
                    else:
                        try:
                            conn.execute(f"DROP TABLE IF EXISTS {job.name};")
                        except Exception as e:
                            logging.error(f"Failed to run: DROP TABLE IF EXISTS {job.name}: {e}")
                    sql = generate_create_table_sql(job.name, schema)
                    if dry_run:
                        logging.info(f"[DRY-RUN] Would execute: {sql}")
                    else:
                        try:
                            conn.execute(sql)
                        except Exception as e:
                            logging.error(f"Failed to run: CREATE TABLE {job.name}: {e}")
                    logging.info(f"✅ Recreated table '{job.name}'")
                else:
                    logging.error(f"❌ Schema drift detected in '{job.name}', but schema change not allowed")
                    for d in diffs:
                        logging.error(f" - {d}")
                    continue

            if job.load:
                load_csvs_to_table(conn, job.name, schema, job.data_path, dry_run, log_to_file, verbose)
                loaded_count += 1

        if dry_run:
            logging.info(f"\n[DRY-RUN] Manifest contained {len(jobs)} jobs. Would have skipped {len(skipped_jobs)} jobs and loaded {loaded_count} tables")
        else:
            logging.info(f"\n[SUMMARY] Manifest contained {len(jobs)} jobs. Skipped {len(skipped_jobs)} jobs and loaded {loaded_count} tables")
            if skipped_jobs:
                logging.info(f"[SKIPPED JOBS] {', '.join(skipped_jobs)}")
            if drop_orphans:
                logging.info(f"[ORPHANS] Dropped {len(extra_raw_tables)} orphan tables")

        logging.info(f"[COMPLETE] Raw layer update finished in '{env}' environment")

    return {
        "jobs_processed": len(jobs),
        "jobs_skipped": len(skipped_jobs),
        "tables_loaded": loaded_count,
        "orphans_dropped": len(extra_raw_tables) if drop_orphans else 0
    }
