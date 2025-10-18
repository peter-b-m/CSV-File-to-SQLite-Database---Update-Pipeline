```markdown
# 🌌 CSV File to SQLite Database - Update Pipeline

A modular Python pipeline for ingesting and transforming CSV files into an SQLite database. Designed for flexibility, clarity, and future extensibility—including base layer transformations.

## 📦 Features

- Upload CSV files into raw SQLite database tables via manifest-driven configuration
- Environment-aware setup (`dev` and `prod`)
- Sample data and configs included for easy testing
- Modular utilities for path resolution, schema validation, and logging

## 🗂️ Folder Structure

```text
my_project/
├── sample/         # Public examples: configs, data, db, logs, schemas, views
├── scripts/        # Upload logic, utilities, and CLI entry points
├── README.md       # You're reading it!
├── .gitignore      # Excludes sensitive and bulky folders
```

## 🚀 Getting Started

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the upload script
```bash
python3 update_database.py --vl --ltf --use-sample
```

#### Run the following to get help

Running the script with -h will display available options:
```bash
python3 update_database.py -h    
```

Running the above should bring back:

```text
usage: update_database.py [-h] [--dry-run] [--env {dev,staging,prod}]
                          [--database DATABASE] [--manifest MANIFEST]
                          [--log-file LOG_FILE] [--layer {all,raw,base}]
                          [--drop-orphans] [--vl] [--ltf] [--use-sample]

Update database from manifest

options:
  -h, --help            show this help message and exit
  --dry-run             Run in dry-run mode (no changes applied)
  --env {dev,staging,prod}
                        Environment name
  --database DATABASE   SQLite database
  --manifest MANIFEST   Manifest file
  --log-file LOG_FILE   Log file
  --layer {all,raw,base}
                        DB layer you want to update (all, raw, base)
  --drop-orphans        Drop Orphans
  --vl                  Verbose logging
  --ltf                 Log to file
  --use-sample          Use sample folder structure
```

### 3. Explore the database
Use any SQLite database browser to inspect `sample/db/dev/astrology.db` and query views like:
```sql
SELECT * FROM vw_birthdays_of_famous_people;
```

## 🧪 Testing

Unit tests are planned but not yet implemented.

## 🛣️ Roadmap

- Base layer transformations (cleaning, deduping, normalization)
- Public API ingestion
- Mobile app development (React Native or Flutter)
- GitHub Actions for CI/CD
- Packaging for PyPI

## 🙌 Credits

Built with Python, SQLite, and a lot of curiosity.
```
