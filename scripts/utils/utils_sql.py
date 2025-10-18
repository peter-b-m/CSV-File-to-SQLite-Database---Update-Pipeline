# utils_sql.py

from utils.utils_schema import TableSchema

def generate_create_table_sql(table_name: str, schema: TableSchema) -> str:
    """Generate a SQLite CREATE TABLE statement from a TableSchema object."""
    column_lines = []
    for col in schema.columns:
        line = f'"{col.name}" {col.type}'
        if col.not_null:
            line += " NOT NULL"
        column_lines.append(line)

    constraints = []

    if schema.primary_key:
        pk = ", ".join(schema.primary_key)
        constraints.append(f"PRIMARY KEY ({pk})")

    if schema.checks:
        for expr in schema.checks:
            constraints.append(f"CHECK ({expr})")

    all_lines = column_lines + constraints
    joined = ",\n  ".join(all_lines)

    sql = f'CREATE TABLE "{table_name}" (\n  {joined}\n);'
    return sql
