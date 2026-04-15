import re
from pathlib import Path

import pandas as pd
import yaml


TASK4_DIR = Path(__file__).resolve().parent
DATA_DIR = TASK4_DIR / 'data'
INVALID_MARKERS = {'', ' ', '\t', '-', 'NULL', 'NAN'}


def _normalize_text(value: object) -> str:
    if pd.isna(value):
        return ''
    return re.sub(r'\s+', ' ', str(value)).strip()


def clean_books(dataset_dir: Path, output_dir: Path) -> None:
    with open(dataset_dir / 'books.yaml', 'r', encoding='utf-8') as file:
        books_df = pd.DataFrame(yaml.safe_load(file))

    books_df.columns = books_df.columns.str.lstrip(':')
    books_df = books_df.dropna(subset=['id', 'title', 'author']).copy()

    for col in ['title', 'author', 'genre', 'publisher']:
        books_df[col] = books_df[col].apply(_normalize_text)

    books_df['publisher'] = books_df['publisher'].replace(list(INVALID_MARKERS), 'Unknown')
    books_df.loc[books_df['publisher'] == '', 'publisher'] = 'Unknown'

    year_str = books_df['year'].astype('string').str.strip()
    books_df['year'] = pd.to_numeric(year_str, errors='coerce').astype('Int64')
    books_df = books_df.dropna(subset=['year'])

    books_df['id'] = pd.to_numeric(books_df['id'], errors='coerce').astype('Int64')
    books_df = books_df.dropna(subset=['id']).drop_duplicates(subset=['id'])

    books_df.to_csv(output_dir / 'books.csv', index=False)


def _clean_timestamp(value: object) -> str:
    text = str(value)
    return text.replace('A.M.', 'AM').replace('P.M.', 'PM').replace(',', ' ')


def _parse_unit_price(value: object) -> float | None:
    text = _normalize_text(value).replace(' ', '')
    text_upper = text.upper()

    is_euro = '€' in text or 'EUR' in text_upper

    if '¢' in text:
        nums = re.findall(r'\d+', text)
        if len(nums) >= 2:
            dollars = int(nums[0])
            cents = int(nums[1][:2].ljust(2, '0'))
            amount = dollars + cents / 100
        elif len(nums) == 1:
            amount = int(nums[0]) / 100
        else:
            return None
    else:
        match = re.search(r'\d+(?:[\.,]\d+)?', text)
        if not match:
            return None
        amount = float(match.group().replace(',', '.'))

    if is_euro:
        amount *= 1.2

    return round(amount, 2)


def clean_orders(dataset_dir: Path, output_dir: Path) -> None:
    orders_df = pd.read_parquet(dataset_dir / 'orders.parquet').copy()

    orders_df['timestamp'] = pd.to_datetime(
        orders_df['timestamp'].map(_clean_timestamp),
        format='mixed',
        errors='coerce',
        utc=True,
    )
    orders_df = orders_df.dropna(subset=['timestamp'])

    orders_df['unit_price'] = orders_df['unit_price'].map(_parse_unit_price)
    orders_df = orders_df.dropna(subset=['unit_price'])

    orders_df['quantity'] = pd.to_numeric(orders_df['quantity'], errors='coerce').astype('Int64')
    orders_df = orders_df.dropna(subset=['quantity'])

    orders_df['paid_price'] = (orders_df['unit_price'] * orders_df['quantity']).round(2)
    orders_df['year'] = orders_df['timestamp'].dt.year.astype('Int64')
    orders_df['month'] = orders_df['timestamp'].dt.month.astype('Int64')
    orders_df['day'] = orders_df['timestamp'].dt.day.astype('Int64')

    orders_df['shipping'] = orders_df['shipping'].fillna('')
    orders_df['shipping'] = orders_df['shipping'].apply(_normalize_text)
    orders_df.loc[orders_df['shipping'].isin(INVALID_MARKERS), 'shipping'] = 'Unknown'

    for col in ['id', 'user_id', 'book_id']:
        orders_df[col] = pd.to_numeric(orders_df[col], errors='coerce').astype('Int64')

    orders_df = orders_df.dropna(subset=['id', 'user_id', 'book_id'])
    orders_df.to_csv(output_dir / 'orders.csv', index=False)


def clean_users(dataset_dir: Path, output_dir: Path) -> None:
    users_df = pd.read_csv(dataset_dir / 'users.csv').copy()

    for col in ['name', 'address', 'phone', 'email']:
        users_df[col] = users_df[col].apply(_normalize_text)

    users_df['phone'] = users_df['phone'].map(lambda x: '+1' + re.sub(r'\D', '', x) if x else '')
    users_df['email'] = users_df['email'].str.lower()
    users_df['name'] = users_df['name'].str.title()

    company_keywords = ['LLC', 'Lld', 'Inc', 'Ltd', 'Corp', 'LLP', 'Company', 'Co.', 'Esq.', 'Ret.']
    users_df['is_company'] = users_df['name'].str.contains('|'.join(company_keywords), case=False, na=False)

    users_df['name'] = users_df['name'].str.replace(r"[^a-zA-Z\s\.\-\']", '', regex=True)
    users_df['address'] = users_df['address'].replace(list(INVALID_MARKERS), 'Unknown')

    users_df['id'] = pd.to_numeric(users_df['id'], errors='coerce').astype('Int64')
    users_df = users_df.dropna(subset=['id'])

    phone_map = users_df.groupby('phone', dropna=False)['id'].transform('max')
    email_map = users_df.groupby('email', dropna=False)['id'].transform('max')
    address_map = users_df.groupby('address', dropna=False)['id'].transform('max')

    users_df['canonical_id'] = users_df[['id']].assign(
        phone=phone_map,
        email=email_map,
        address=address_map,
    ).max(axis=1).astype('Int64')

    users_df = users_df[users_df['id'] == users_df['canonical_id']].copy()
    users_df.to_csv(output_dir / 'users.csv', index=False)


def clean_dataset(dataset_name: str) -> None:
    dataset_dir = DATA_DIR / dataset_name
    output_dir = DATA_DIR / f'{dataset_name}_cleaned'
    output_dir.mkdir(parents=True, exist_ok=True)

    clean_books(dataset_dir, output_dir)
    clean_orders(dataset_dir, output_dir)
    clean_users(dataset_dir, output_dir)

    print(f'Cleaned {dataset_name} -> {output_dir}')


for dataset in ['DATA1', 'DATA2', 'DATA3']:
        clean_dataset(dataset)