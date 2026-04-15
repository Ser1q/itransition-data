import pandas as pd
import yaml
import re 

# Books
with open('./data/DATA1/books.yaml', 'r') as f:
    data = yaml.safe_load(f)

books_df = pd.DataFrame(data)

books_df.columns = books_df.columns.str.lstrip(':')

# year cleaning
invalid_chars = [' ', '', '\t', '-', 'NULL', '0', 0]

books_df = books_df.dropna(subset=['id', 'title', 'author']) 
books_df=books_df[~books_df['year'].isin(invalid_chars)]

books_df['year'] = pd.to_datetime(books_df['year'], format='%Y').dt.to_period('Y')

books_df['title'] = books_df['title'].str.strip()

# Search for invalid chars in other columns
for col in books_df.columns:
    count = books_df[col].isin(invalid_chars).sum()
    if count > 0:
            print(f"{col}: {count} invalid values")

invalid_mask = books_df['publisher'].isin(invalid_chars)
books_df.loc[invalid_mask, 'publisher'] = 'Unknown'

# Save
books_df.to_csv('./data/DATA1_cleaned/books.csv', index=False)


# Orders
orders_df = pd.read_parquet('./data/DATA1/orders.parquet')

# dtype to datetime
def clean_dt(value):
    return value.replace('A.M.', 'AM').replace('P.M.', 'PM').replace(',', ' ')

orders_df['timestamp'] = pd.to_datetime(orders_df['timestamp'].apply(clean_dt), format='mixed', errors='coerce', utc=True)

orders_df.info()

# extract dates
orders_df['year'] = orders_df['timestamp'].dt.year
orders_df['month'] = orders_df['timestamp'].dt.month
orders_df['day'] = orders_df['timestamp'].dt.day



# convert unit_price from € to $
euro_indexes = orders_df[orders_df['unit_price'].str.contains(r'€|EUR')].index
dollar_indexes = orders_df[orders_df['unit_price'].str.contains(r'\$|USD')].index 
# 3532 prices in euros + 7705 prices in dollars -> 11237 in total


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
orders_df.loc[euro_indexes, 'unit_price'] = orders_df.loc[euro_indexes, 'unit_price'] * 1.2
orders_df['unit_price'] = orders_df['unit_price'].round(2)

orders_df['paid_price'] = orders_df['unit_price'] * orders_df['quantity']

orders_df.to_csv('./data/DATA1_cleaned/orders.csv', index=False)

# Users
users_df = pd.read_csv('./data/DATA1/users.csv')
users_df.head()
users_df.info()

users_df['phone'] = users_df['phone'].apply(lambda x: '+1' + re.sub(r'\D', '', x))

users_df.duplicated(subset=['name', 'email']).sum()

phone_map = users_df.groupby('phone')['id'].transform('max')
email_map = users_df.groupby('email')['id'].transform('max')

users_df['canonical_id'] = users_df[['id']].assign(
    p=phone_map, e=email_map
).max(axis=1).astype(int)

id_map = dict(zip(users_df['id'], users_df['canonical_id']))

users_df = users_df[users_df['id'] == users_df['canonical_id']]

users_df['name'] = users_df['name'].str.strip().str.replace(r'\s+', ' ', regex=True)

users_df['name'] = users_df['name'].str.title()

company_keywords = ['LLC', 'Inc', 'Ltd', 'Corp', 'LLD', 'Company', 'Co.', 'Esq.', 'Ret.']
pattern = '|'.join(company_keywords)
users_df['is_company'] = users_df['name'].str.contains(pattern, case=False, na=False)

users_df['name'] = users_df['name'].str.replace(r"[^a-zA-Z\s\.\-\']", '', regex=True)

users_df.to_csv('./data/DATA1_cleaned/users.csv', index=False)