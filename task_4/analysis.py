import pandas as pd
from pathlib import Path

def _build_user_components(users_df: pd.DataFrame) -> dict[int, list[int]]:
    identity_fields = ['name', 'address', 'phone', 'email']

    normalized = users_df[identity_fields].copy()
    for field in identity_fields:
        normalized[field] = normalized[field].astype('string').str.strip().str.lower()

    n = len(normalized)
    parent = list(range(n))
    rank = [0] * n

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            parent[ra] = rb
        elif rank[ra] > rank[rb]:
            parent[rb] = ra
        else:
            parent[rb] = ra
            rank[ra] += 1

    signature_owner = {}
    for idx, row in enumerate(normalized.itertuples(index=False, name=None)):
        row_values = dict(zip(identity_fields, row))
        for skipped in identity_fields:
            signature = (skipped,) + tuple(row_values[field] for field in identity_fields if field != skipped)
            owner = signature_owner.get(signature)
            if owner is None:
                signature_owner[signature] = idx
            else:
                union(owner, idx)

    components = {}
    for i in range(n):
        root = find(i)
        components.setdefault(root, []).append(i)

    return components

def count_real_unique_users(users_df: pd.DataFrame) -> int:
    return len(_build_user_components(users_df))

def load_data(path):
    users_df = pd.read_csv(f"{path}/users.csv", dtype={
        'id':           'Int64',
        'canonical_id': 'Int64',
        'name':         'str',
        'address':      'str',
        'phone':        'str',
        'email':        'str',
        'is_company':   'bool',
    })

    orders_df = pd.read_csv(f"{path}/orders.csv", dtype={
        'id':           'Int64',
        'user_id':      'Int64',
        'book_id':      'Int64',
        'quantity':     'Int64',
        'unit_price':   'float64',
        'paid_price':   'float64',
        'shipping':     'str',
        'year':         'Int64',
        'month':        'Int64',
        'day':          'Int64',
    })
    
    orders_df['timestamp'] = pd.to_datetime(orders_df['timestamp'], format='ISO8601', utc=True)
    orders_df['date'] = orders_df['timestamp'].dt.date

    books_df = pd.read_csv(f"{path}/books.csv", dtype={
        'id':        'Int64',
        'title':     'str',
        'author':    'str',
        'genre':     'str',
        'publisher': 'str',
        'year':      'Int64',
    })

    return users_df, orders_df, books_df

def parse_author_set(author_value: str) -> tuple[str, ...]:
    if pd.isna(author_value):
        return tuple()

    authors = [part.strip() for part in str(author_value).split(',') if part.strip()]
    return tuple(sorted(authors))

def count_unique_author_sets(books_df: pd.DataFrame) -> int:
    return books_df['author'].map(parse_author_set).nunique()

def most_popular_author_set(orders_df: pd.DataFrame, books_df: pd.DataFrame) -> dict:
    order_books = orders_df.merge(
        books_df[['id', 'author']],
        left_on='book_id',
        right_on='id',
        how='left',
        suffixes=('', '_book'),
    )
    order_books['author_set'] = order_books['author'].map(parse_author_set)

    order_books = order_books[order_books['author_set'].map(len) > 0]
    if order_books.empty:
        return {
            'author_set': [],
            'sold_book_count': 0,
        }

    sold_by_set = order_books.groupby('author_set', dropna=False)['quantity'].sum().sort_values(ascending=False)
    best_set = sold_by_set.index[0]

    return {
        'author_set': list(best_set),
        'sold_book_count': int(sold_by_set.iloc[0]),
    }

def top_customer_by_total_spending(users_df: pd.DataFrame, orders_df: pd.DataFrame) -> dict:
    user_totals = orders_df.groupby('user_id', dropna=True)['paid_price'].sum().to_dict()
    components = _build_user_components(users_df)

    best_group_ids: list[int] = []
    best_spending = -1.0

    for row_indexes in components.values():
        ids = users_df.iloc[row_indexes]['id'].dropna().astype(int).tolist()
        group_spending = sum(float(user_totals.get(user_id, 0.0)) for user_id in ids)

        if (
            group_spending > best_spending
            or (group_spending == best_spending and ids and (not best_group_ids or min(ids) < min(best_group_ids)))
        ):
            best_spending = group_spending
            best_group_ids = sorted(ids)

    return {
        'user_ids': best_group_ids,
        'total_spending': round(best_spending, 2),
    }

_TASK4_DIR = Path(__file__).resolve().parent
users_df, orders_df, books_df = load_data(_TASK4_DIR / 'data' / 'DATA1_cleaned')

def compute_metrics(users_df: pd.DataFrame, orders_df: pd.DataFrame, books_df: pd.DataFrame):
    daily_revenue = orders_df.groupby(orders_df['timestamp'].dt.date)['paid_price'].sum().sort_index()
    top5 = daily_revenue.sort_values(ascending=False).head(5)
    unique_users = count_real_unique_users(users_df)
    author_sets = count_unique_author_sets(books_df)
    popular_author = most_popular_author_set(orders_df, books_df)
    best_buyer = top_customer_by_total_spending(users_df, orders_df)
    
    return {
        "top5": top5,
        "unique_users": unique_users,
        "author_sets": author_sets,
        "popular_author": popular_author,
        "best_buyer": best_buyer,
        "daily_revenue": daily_revenue,
    }