# Description of the logic of cleaning

# Data 1
## Books
1) The Books df was in .yaml format. Its column names were broken, with leading ":".
2) Check for duplicates, delete of nulls
3) Identification of invalid characters in year column by str.contains method and regular expressions
4) Checks for other columns as well
5) Replacing invalid puclisher values with Unknown

## Orders

### timestamp
1) Convert timestampt column to datetime with format = mixed
2) Got NaT rows, and identifyed issues
3) Constructed cleaning function to replace invalid chars, and converted to datetime properly

### unit_price
1) Identifyed the pattern of dollars and euros
2) Saved indexes for prices in euros
3) Cleaned prices for dollars from dollar and cent signs
4) Cleaned prices for euros from euro and cent signs
5) By euro indexes converted them to dollar prices