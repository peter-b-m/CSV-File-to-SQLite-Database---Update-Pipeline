# utils_schema.py

import yaml
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ColumnDefinition:
    """Represents a column in a table schema."""
    name: str
    type: str
    not_null: bool = False

@dataclass
class TableSchema:
    columns: List[ColumnDefinition]
    primary_key: Optional[List[str]] = None
    checks: Optional[List[str]] = None

def load_table_schema(schema_path: str) -> TableSchema:
    """Load a table schema from a YAML file and return a TableSchema object."""
    try:
        with open(schema_path, 'r') as f:
            schema_yaml = yaml.safe_load(f)
    except Exception as e:
        raise ValueError(f"Failed to load schema from {schema_path}: {e}")

    columns_raw = schema_yaml.get("columns")
    if not isinstance(columns_raw, list) or not columns_raw:
        raise ValueError(f"Schema file '{schema_path}' must contain a non-empty 'columns' list.")

    columns = []
    for col in columns_raw:
        columns.append(ColumnDefinition(
            name=col["name"],
            type=col["type"],
            not_null=col.get("not_null", False)
        ))

    primary_key = schema_yaml.get("primary_key")
    checks = [check["expression"] if isinstance(check, dict) else check
              for check in schema_yaml.get("checks", [])]

    return TableSchema(columns=columns, primary_key=primary_key, checks=checks)
