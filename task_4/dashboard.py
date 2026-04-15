import streamlit as st
import plotly.express as px
import pandas as pd
from pathlib import Path

from analysis import load_data, compute_metrics

st.set_page_config(page_title="Book Sales Dashboard", layout="wide")

TASK4_DIR = Path(__file__).resolve().parent
DATASETS = [
    ("Dataset 1 (Cleaned)", TASK4_DIR / 'data' / 'DATA1_cleaned'),
    ("Dataset 2 (Cleaned)", TASK4_DIR / 'data' / 'DATA2_cleaned'),
    ("Dataset 3 (Cleaned)", TASK4_DIR / 'data' / 'DATA3_cleaned'),
]

def _popular_author_label(popular_author: dict) -> str:
    author_set = popular_author.get('author_set', [])
    if not author_set:
        return "N/A"
    return ", ".join(author_set)

def _render_dataset_tab(dataset_name: str, dataset_path: Path) -> None:
    users_df, orders_df, books_df = load_data(dataset_path)
    metrics = compute_metrics(users_df, orders_df, books_df)

    top5_df = metrics['top5'].rename('revenue').reset_index()
    top5_df.columns = ['date', 'revenue']
    top5_df['date'] = pd.to_datetime(top5_df['date']).dt.strftime('%Y-%m-%d')

    daily_revenue_df = metrics['daily_revenue'].rename('revenue').reset_index()
    daily_revenue_df.columns = ['date', 'revenue']
    daily_revenue_df['date'] = pd.to_datetime(daily_revenue_df['date'])

    st.header(dataset_name)

    col1, col2, col3 = st.columns(3)
    col1.metric("Number of unique users", int(metrics['unique_users']))
    col2.metric("Number of unique sets of authors", int(metrics['author_sets']))
    col3.metric("Most popular author(s)", _popular_author_label(metrics['popular_author']))

    st.subheader("Top 5 days by revenue")
    st.dataframe(top5_df, use_container_width=True, hide_index=True)

    st.subheader("Best buyer (with aliases) as IDs")
    st.json(metrics['best_buyer']['user_ids'])

    st.subheader("Daily revenue chart")
    fig = px.line(
        daily_revenue_df,
        x='date',
        y='revenue',
        markers=True,
        title='Daily Revenue',
    )
    fig.update_layout(xaxis_title='Date', yaxis_title='Revenue')
    st.plotly_chart(fig, use_container_width=True)

tabs = st.tabs([label for label, _ in DATASETS])

for tab, (label, path) in zip(tabs, DATASETS):
    with tab:
        _render_dataset_tab(label, path)