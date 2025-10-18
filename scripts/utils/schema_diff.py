# schema_diff.py

from utils.utils_schema import TableSchema

def diff_schema(yaml_schema: TableSchema, db_schema: list[dict]) -> list[str]:
    """Compare YAML schema with DB schema and return list of differences."""
    diffs = []

    # Compare column count
    if len(yaml_schema.columns) != len(db_schema):
        diffs.append(f"Column count mismatch: YAML has {len(yaml_schema.columns)}, DB has {len(db_schema)}")

    # Compare column-by-column
    for i, yaml_col in enumerate(yaml_schema.columns):
        if i >= len(db_schema):
            diffs.append(f"Missing column in DB: {yaml_col.name}")
            continue

        db_col = db_schema[i]

        # Name
        if yaml_col.name.strip().lower() != db_col["name"].strip().lower():
            diffs.append(f"Column {i} name mismatch: YAML='{yaml_col.name}', DB='{db_col['name']}'")

        # Type
        if yaml_col.type.strip().upper() != db_col["type"].strip().upper():
            diffs.append(f"Column {yaml_col.name} type mismatch: YAML='{yaml_col.type}', DB='{db_col['type']}'")

        # Nullability
        if yaml_col.not_null != db_col["notnull"]:
            diffs.append(f"Column {yaml_col.name} nullability mismatch: YAML={'NOT NULL' if yaml_col.not_null else 'NULLABLE'}, DB={'NOT NULL' if db_col['notnull'] else 'NULLABLE'}")

    yaml_col_names = set(col.name for col in yaml_schema.columns)
    db_col_names = set(col["name"] for col in db_schema)

    extra_in_db = db_col_names - yaml_col_names
    for col in sorted(extra_in_db):
        diffs.append(f"Extra column in DB not declared in YAML: {col}")

    # Compare primary key
    yaml_pk = set(yaml_schema.primary_key or [])
    db_pk = set(col["name"] for col in db_schema if col["pk"])
    if yaml_pk != db_pk:
        diffs.append(f"Primary key mismatch: YAML={sorted(yaml_pk)}, DB={sorted(db_pk)}")

    return diffs
