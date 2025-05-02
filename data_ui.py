import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="YouTube Title Trends", page_icon=":bar_chart:", layout="wide")

# ---- READ FINAL CSV ----
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_youtube_data.csv")
    return df

df = load_data()

# ---- SIDEBAR ----
st.sidebar.header("Filter by Category:")
category = st.sidebar.multiselect(
    "Select Categories:",
    options=df["category"].unique(),
    default=df["category"].unique()
)

df_selection = df[df["category"].isin(category)]

if df_selection.empty:
    st.warning("No data based on current filter!")
    st.stop()

# ---- MAINPAGE ----
st.title(":bar_chart: YouTube Title Trends")
st.markdown("##")

# KPIs
total_videos = df_selection.shape[0]
avg_title_len = round(df_selection["title_len"].mean(), 2)
avg_views = round(df_selection["view_count"].mean(), 2)

left_column, mid_column, right_column = st.columns(3)
with left_column:
    st.subheader("Total Videos:")
    st.subheader(f"{total_videos}")
with mid_column:
    st.subheader("Average Title Length:")
    st.subheader(f"{avg_title_len} words")
with right_column:
    st.subheader("Average Views:")
    st.subheader(f"{avg_views:,}")

st.markdown("""---""")

# ---- PLOTS ----

# Most Common Words
top_words_df = pd.read_csv("top_words.csv").sort_values(by=['word_count'])
fig_words = px.bar(
    top_words_df,
    x="word_count",
    y="word",
    orientation="h",
    title="<b>Top 15 Used Words</b>",
    color_discrete_sequence=["#0083B8"] * 15,
    template="plotly_white",
)
fig_words.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False))

# Top Bigrams
top_bigrams_df = pd.read_csv("top_bigrams.csv").sort_values(by=['bigram_count'])
fig_bigrams = px.bar(
    top_bigrams_df,
    x="bigram_count",
    y="bigram",
    orientation="h",
    title="<b>Top Bigrams</b>",
    color_discrete_sequence=["#0083B8"] * 15,
    template="plotly_white",
)
fig_bigrams.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False))


# Title Length vs. Views
fig_len_views = px.scatter(
    df_selection,
    x="title_len",
    y="view_count",
    title="<b>Title Length vs. Views</b>",
    template="plotly_white",
    trendline="ols"
)


# Views by Category
views_by_cat = df_selection.groupby("category")["view_count"].mean().reset_index().sort_values(by=['view_count'])
fig_views_cat = px.bar(
    views_by_cat,
    x="category",
    y="view_count",
    title="<b>Average Views per Category</b>",
    color_discrete_sequence=["#0083B8"] * len(views_by_cat),
    template="plotly_white"
)

# ---- Additional Charts ----
# Metrics Ratio
st.markdown("## Engagement Analysis")
engagement_metric = st.selectbox(
    "Select Engagement Metric:",
    options=["Likes to Views Ratio", "Comments to Views Ratio", "Comments to Likes Ratio"]
)

df_selection["likes_views_ratio"] = df_selection["like_count"] / df_selection["view_count"]
df_selection["comments_views_ratio"] = df_selection["comment_count"] / df_selection["view_count"]
df_selection["comments_likes_ratio"] = df_selection["comment_count"] / df_selection["like_count"]

if engagement_metric == "Likes to Views Ratio":
    metric_col = "likes_views_ratio"
    y_title = "Likes to Views Ratio"
elif engagement_metric == "Comments to Views Ratio":
    metric_col = "comments_views_ratio"
    y_title = "Comments to Views Ratio"
else:
    metric_col = "comments_likes_ratio"
    y_title = "Comments to Likes Ratio"

engagement_by_cat = df_selection.groupby("category")[metric_col].mean().reset_index().sort_values(by=[metric_col])
fig_engagement = px.bar(
    engagement_by_cat,
    x="category",
    y=metric_col,
    title=f"<b>Average {y_title} by Category</b>",
    color="category",
    template="plotly_white"
)
fig_engagement.update_layout(xaxis_title="Category", yaxis_title=y_title)
st.plotly_chart(fig_engagement, use_container_width=True)


# Layout

col1, col2 = st.columns(2)
col1.plotly_chart(fig_words, use_container_width=True)
col2.plotly_chart(fig_len_views, use_container_width=True)

col3, col4 = st.columns(2)
col3.plotly_chart(fig_bigrams, use_container_width=True)
col4.plotly_chart(fig_views_cat, use_container_width=True)

# ---- HIDE STREAMLIT STYLE ----
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

