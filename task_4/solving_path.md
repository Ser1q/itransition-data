# Cleaning Pipeline (cleaning.py)

The script cleans three datasets separately: DATA1, DATA2, DATA3.
For each dataset it creates an output folder:
- data/DATA1_cleaned
- data/DATA2_cleaned
- data/DATA3_cleaned

It runs the same 3-stage pipeline for every dataset:
1. clean_books(...)
2. clean_orders(...)
3. clean_users(...)

## 1) Shared helpers

1. _normalize_text(value)
- Converts NaN/null to empty string.
- Trims spaces and compresses repeated whitespace into single spaces.

2. INVALID_MARKERS
- Treats these values as invalid placeholders:
  - ''
  - ' '
  - '\t'
  - '-'
  - 'NULL'
  - 'NAN'

## 2) Books cleaning (clean_books)

Input: books.yaml

Steps:
1. Load YAML into pandas DataFrame.
2. Fix broken column names by removing leading ':' from each column.
3. Drop rows where id, title, or author is missing.
4. Normalize text fields: title, author, genre, publisher.
5. Replace invalid publisher values with 'Unknown'.
6. Convert year to numeric (Int64); invalid year values become NaN and are dropped.
7. Convert id to numeric (Int64); invalid ids are dropped.
8. Remove duplicate books by id.
9. Save cleaned file to books.csv.

## 3) Orders cleaning (clean_orders)

Input: orders.parquet

### 3.1 Timestamp cleaning
1. Normalize timestamp strings:
	- Replace A.M./P.M. with AM/PM
	- Replace commas with spaces
2. Parse with pd.to_datetime(format='mixed', utc=True, errors='coerce').
3. Drop rows where timestamp parsing failed.

### 3.2 Unit price cleaning and currency conversion
1. Parse unit_price with _parse_unit_price(value):
	- Supports USD/$ and EUR/€ formats.
	- Supports cent-notation values (examples: $22¢50, €61¢99, 70€99¢).
	- Extracts numeric amount robustly from mixed symbols/positions.
2. Convert euro prices to dollars using €1 = $1.2.
3. Round final unit_price to 2 decimals.
4. Drop rows where unit_price could not be parsed.

### 3.3 Derived fields and validation
1. Convert quantity to Int64; drop invalid quantity rows.
2. Compute paid_price = unit_price * quantity (rounded to 2 decimals).
3. Extract year, month, day from timestamp.
4. Clean shipping:
	- Fill null with empty string.
	- Normalize spaces.
	- Replace invalid markers with 'Unknown'.
5. Convert id, user_id, book_id to Int64; drop rows where any are invalid.
6. Save cleaned file to orders.csv.

## 4) Users cleaning (clean_users)

Input: users.csv

Steps:
1. Normalize text fields: name, address, phone, email.
2. Normalize phone to digits-only US format: +1XXXXXXXXXX.
3. Normalize email to lowercase.
4. Convert name to title case.
5. Detect companies in name and create boolean is_company using keywords:
	- LLC, Lld, Inc, Ltd, Corp, LLP, Company, Co., Esq., Ret.
6. Remove non-name symbols from name (keep letters, spaces, dot, apostrophe, hyphen).
7. Replace invalid address values with 'Unknown'.
8. Convert id to Int64 and drop invalid rows.

### Canonical user reconciliation
1. Build max-id maps by phone, email, and address.
2. Compute canonical_id as max(id, phone_map, email_map, address_map) per row.
3. Keep only rows where id == canonical_id.
4. Save cleaned file to users.csv.

## 5) Execution flow

1. clean_dataset(dataset_name) creates output directory if missing.
2. Runs books, orders, users cleaning in sequence.
3. Main loop executes for DATA1, DATA2, DATA3.
4. Prints completion message for each dataset.
