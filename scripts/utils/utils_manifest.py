# utils_manifest.py

import os
import logging
import yaml
from dataclasses import dataclass
from typing import List
from utils.utils_paths import resolve_path

@dataclass
class TableJob:
    name: str
    schema: str
    data_folder: str
    required: bool
    load: bool
    allow_schema_change: bool
    schema_path: str = ""
    data_path: str = ""

def load_manifest(script_dir: str, env: str, manifest_path: str, use_sample: bool) -> list[TableJob]:
    """Load and parse a manifest YAML file into a list of TableJob objects."""
    with open(manifest_path, 'r') as f:
        config = yaml.safe_load(f)
    jobs = []
    for entry in config.get("tables", []):
        try:
            schema_path = resolve_path(script_dir, use_sample, "schemas", env, entry["schema"])
            data_path = resolve_path(script_dir, use_sample, "data", entry["data_folder"])
            job = TableJob(
                name=entry["name"],
                schema=entry["schema"],
                data_folder=entry["data_folder"],
                required=entry.get("required", False),
                load=entry.get("load", False),
                allow_schema_change=entry.get("allow_schema_change", False),
                schema_path=schema_path,
                data_path=data_path
            )
            jobs.append(job)
            logging.info(f"[LOAD] Loaded job: {job.name}")
        except KeyError as e:
            logging.error(f"[ERROR] Missing key in manifest entry: {e}")
    return jobs

def validate_job(job: TableJob) -> bool:
    """Validate a TableJob for consistency and file existence."""
    # Manifest-only validation: checks for internal consistency
    if job.schema and not job.schema.lower().endswith((".yaml", ".yml")):
        logging.warning(f"[WARN] {job.name}: schema file does not have a .yaml/.yml extension.")
        # logging.error(f"[SKIP] {job.name}: schema file must end with .yaml or .yml.")
        # return False
    if not job.schema and (job.required or job.load):
        logging.error(f"[SKIP] {job.name}: schema file missing but required/load is true.")
        return False
    if job.load:
        if not job.data_folder:
            logging.error(f"[SKIP] {job.name}: load=true but no data_folder specified.")
            return False
        if not job.required:
            logging.error(f"[SKIP] {job.name}: load=true but required=false — inconsistent settings.")
            return False
    if job.allow_schema_change and not job.required:
        logging.error(f"[SKIP] {job.name}: allow_schema_change=true but required=false — inconsistent settings.")
        return False
    # File existence checks
    if job.schema_path and not os.path.isfile(job.schema_path):
        logging.error(f"[SKIP] {job.name}: schema file '{job.schema}' not found.")
        return False
    if job.load and job.data_folder:
        if not os.path.isdir(job.data_path):
            logging.error(f"[SKIP] {job.name}: data folder '{job.data_folder}' not found.")
            return False
        csv_files = [f for f in os.listdir(job.data_path) if f.lower().endswith(".csv")]
        if not csv_files:
            logging.error(f"[SKIP] {job.name}: data folder has no CSV files.")
            return False
    return True
