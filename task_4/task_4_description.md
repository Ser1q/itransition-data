TASK 4_DATA

Load data from DATA1 folder into pandas and clean it – ensure proper types, for example, make dates are parsed as dates, handle any duplicated, missing or malformed values.

Add a column paid_price = quantity * unit_price to orders (convert everything to dollars and cents, €1 = $1.2).

Extract date (year, month and day) from timestamp.

Compute daily revenue (sum of paid_price grouped by date) and find top 5 days by revenue.

Find how many real unique users there are. Note that user can change address or change phone or even provide alias instead of a real name; you need to reconciliate data. You may assume that only one field is changed.

Find how how many unique sets of authors there are. For example, if John and Paul wrote a book together and wrote several books separately, it means that there are 3 different sets.

Find the most popular (by sold book count) author (or author set).

Identify the top customer by total spending (list all user_id values for the possible different addresses, phones, e-mails, or aliases).

Plot a simple line chart of daily revenue using matplotlib.

Repeat for the data from DATA2 and DATA3 folders separately.

Send to me (p.lebedev@itransition.com) a link to code repository as well as a link to any kind of dashboard accessible online via browser (even static page is OK) containing three tabs/views/anything with the following:
Top 5 days by revenue using the format "YYYY-MM-dd".
Number of unique users.
Number of unique sets of authors.
The name of most popular author(s).
Best buyer (with aliases) as an array of ids ([id1, id2, ...])
Daily revenue chart

Make sure the information is presented neatly and professionally, resembling a BI dashboard rather than plain text. The use of any ready-made templates or engines is highly recommended.

Plan to submit the solution not later than Wednesday 15.04.26.
