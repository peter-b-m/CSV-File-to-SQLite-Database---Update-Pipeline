# update_database.py

import argparse
import datetime
import logging
import os
from run_raw_layer_update import run_raw_layer_update
# from run_base_layer_update import run_base_layer_update
from utils.utils_paths import resolve_path

# Configure logging
def configure_logging(log_to_file: bool, log_dir: str, log_path: str):
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    if log_to_file:
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

def main():
    parser = argparse.ArgumentParser(description="Update database from manifest")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode (no changes applied)")
    parser.add_argument("--env", type=str, choices=["dev", "staging", "prod"], default="dev", help="Environment name")
    # parser.add_argument("--database", type=str, required=True, help="SQLite database")
    parser.add_argument("--database", type=str, default="astrology.db", help="SQLite database")
    # parser.add_argument("--manifest", type=str, required=True, help="Manifest file")
    parser.add_argument("--manifest", type=str, default="manifest.yaml", help="Manifest file")
    # parser.add_argument("--log-file", type=str, required=True, help="Log file")
    parser.add_argument("--log-file", type=str, default="update_database.log", help="Log file")
    parser.add_argument("--layer", type=str, choices=["all", "raw", "base"], default="all", help="DB layer you want to update (all, raw, base)")
    # parser.add_argument("--strict", action="store_true", help="Enable strict validation mode")# haven't done anything with this yet
    parser.add_argument("--drop-orphans", action="store_true", help="Drop Orphans")
    parser.add_argument("--vl", action="store_true", help="Verbose logging")
    parser.add_argument("--ltf", action="store_true", help="Log to file")
    parser.add_argument("--use-sample", action="store_true", help="Use sample folder structure")

    args = parser.parse_args()

    dry_run = args.dry_run
    env = args.env
    database = args.database
    manifest = args.manifest
    log_file = args.log_file
    layer = args.layer
    # strict = args.strict
    drop_orphans = args.drop_orphans
    verbose_logging = args.vl
    log_to_file = args.ltf
    use_sample = args.use_sample

    script_dir = os.path.dirname(os.path.abspath(__file__))

    db_path = resolve_path(script_dir, use_sample, "db", env, database)
    manifest_path = resolve_path(script_dir, use_sample, "configs", env, manifest)
    log_dir = resolve_path(script_dir, use_sample, "logs", env)

    log_path = os.path.join(log_dir, log_file)

    configure_logging(log_to_file, log_dir, log_path)
    logging.info(f"\n[NEW RUN] {datetime.datetime.now().isoformat()} — Starting database update")
    logging.info(f"\n[ENVIRONMENT] Running in '{args.env}' environment")
    logging.info(f"\n[CONFIG] DB: {db_path}, Manifest: {manifest_path}, Log: {log_path}")

    if layer in ["all", "raw"]:
        run_raw_layer_update(script_dir, dry_run, env, db_path, manifest_path, drop_orphans, verbose_logging, log_to_file, use_sample)

    if layer in ["all", "base"]:
        # run_base_layer_update(...)
        logging.info("[SKIP] Base layer update not yet implemented")

if __name__ == "__main__":
    main()
