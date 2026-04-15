import pandas as pd
import yaml

# Books
with open('./data/DATA1/books.yaml', 'r') as f:
    data = yaml.safe_load(f)

books_df = pd.DataFrame(data)

books_df = books_df.rename(columns={':id': 'id', ':title': 'title', ':author': 'author', ':genre': 'genre', ':publisher': 'publisher', ':year': 'year'})

# year cleaning
invalid_chars = [' ', '', '\t', '-', 'NULL', '0', 0]

books_df = books_df.dropna()
books_df=books_df[~books_df['year'].isin(invalid_chars)]

books_df['year'] = pd.to_datetime(books_df['year'], format='%Y').dt.to_period('Y')

books_df['title'] = books_df['title'].str.strip()

# Search for invalid chars in other columns
for col in books_df.columns:
    print(f'Col: {col}')
    print(books_df[books_df[f'{col}'].isin(invalid_chars)])

invalid_mask = books_df['publisher'].isin(invalid_chars)
books_df.loc[invalid_mask, 'publisher'] = 'Unknown'

# Save
books_df.to_csv('./data/DATA1_cleaned/books.csv')

# Check
print(books_df['publisher'].value_counts().to_string())


# Orders
orders_df = pd.read_parquet('./data/DATA1/orders.parquet')

# dtype to datetime
def clean_dt(value):
    return value.replace('A.M.', 'AM').replace('P.M.', 'PM').replace(',', ' ')

orders_df['timestamp'] = pd.to_datetime(orders_df['timestamp'].apply(clean_dt), format='mixed', errors='coerce', utc=True)

orders_df.info()

# convert unit_price from € to $
euro_indexes = orders_df[orders_df['unit_price'].str.contains(r'€|EUR')].index
dollar_indexes = orders_df[orders_df['unit_price'].str.contains(r'\$|USD')].index # 3532 prices in euros + 7705 prices in dollars -> 11237 in total


# work with dollars
orders_df['unit_price'] = orders_df['unit_price'].str.replace('USD', '$')

mask = orders_df['unit_price'].str.contains(r'^\$|\$$')

orders_df.loc[mask, 'unit_price'] = orders_df.loc[mask, 'unit_price'].apply(lambda x: x.replace('$', '').strip())

orders_df['unit_price'] = orders_df['unit_price'].str.replace('$', '.').str.replace(r'¢$', '', regex=True)

# work with euros
orders_df['unit_price'] = orders_df['unit_price'].str.replace('EUR', '€')

mask = orders_df['unit_price'].str.contains(r'^€|€$')

orders_df.loc[mask, 'unit_price'] = orders_df.loc[mask, 'unit_price'].apply(lambda x: x.replace('€', '').strip())

orders_df['unit_price'] = orders_df['unit_price'].str.replace('€', '.').str.replace('¢', '.')

orders_df['unit_price'] = orders_df['unit_price'].astype(float)

orders_df.info()

orders_df.loc[euro_indexes, 'unit_price'] = orders_df.loc[euro_indexes, 'unit_price'] * 1.2

orders_df['unit_price'] = orders_df['unit_price'].round(2)

orders_df