import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from streamlit_option_menu import option_menu

# Page configuration
st.set_page_config(
    page_title="TMDB Movie Insights",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>

/* Import fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@400;500;600;700;800&display=swap');

/* Main application */
.stApp {
    background-color: #0E1117;
    color: #F5F5F5;
    font-family: 'Inter', sans-serif;
}

/* Headings */
h1, h2, h3 {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 700 !important;
    color: #FFFFFF !important;
}

/* Body text */
p, label, li {
    font-family: 'Inter', sans-serif !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #191B23;
    font-family: 'Inter', sans-serif;
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: #1C1F26;
    padding: 20px;
    border-radius: 12px;
    border-left: 4px solid #E50914;
}

[data-testid="stMetricValue"] {
    color: #E50914;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 700 !important;
}

/* Buttons */
.stButton > button {
    background-color: #E50914;
    color: white;
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    font-family: 'Inter', sans-serif;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# Load movie data
@st.cache_data
def load_data():
    movies = pd.read_csv("cleaned_data/movies.csv")
    genres = pd.read_csv("cleaned_data/genres.csv")
    movie_genres = pd.read_csv("cleaned_data/movie_genres.csv")

    movies["release_date"] = pd.to_datetime(
        movies["release_date"], errors="coerce"
    )

    return movies, genres, movie_genres

movies_df, genres_df, movie_genres_df = load_data()


# Sidebar navigation and global filters

# Prepare release year
movies_df["release_year"] = movies_df["release_date"].dt.year

# Filter options
genre_options = sorted(genres_df["genre_name"].dropna().unique())

min_year = int(movies_df["release_year"].min())
max_year = int(movies_df["release_year"].max())

max_popularity = float(movies_df["popularity"].max())

with st.sidebar:

    st.title("🎬 TMDB Insights")

    selected = option_menu(
        menu_title="Main Menu",
        options=["Filters", "Dashboard", "Query Explorer"],
        icons=["funnel", "bar-chart", "database"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical"
    )

    st.markdown("---")
    st.subheader("🎛️ Global Movie Filters")

    selected_genres_filter = st.multiselect(
        "Select Genre",
        options=genre_options,
        default=[],
        key="global_genres"
    )

    selected_years = st.slider(
        "Release Year",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        key="global_years"
    )

    min_rating = st.slider(
        "Minimum Rating",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.5,
        key="global_rating"
    )

    selected_popularity = st.slider(
        "Popularity Range",
        min_value=0.0,
        max_value=max_popularity,
        value=(0.0, max_popularity),
        key="global_popularity"
    )

# Apply Global Filters to Movie Dataset

filtered_movies = movies_df.copy()

# Genre filter
if selected_genres_filter:

    selected_genre_ids = genres_df[
        genres_df["genre_name"].isin(selected_genres_filter)
    ]["genre_id"]

    matching_movie_ids = movie_genres_df[
        movie_genres_df["genre_id"].isin(selected_genre_ids)
    ]["movie_id"].unique()

    filtered_movies = filtered_movies[
        filtered_movies["movie_id"].isin(matching_movie_ids)
    ]

# Release year filter
filtered_movies = filtered_movies[
    filtered_movies["release_year"].between(
        selected_years[0],
        selected_years[1]
    )
]

# Rating filter
filtered_movies = filtered_movies[
    filtered_movies["vote_average"] >= min_rating
]

# Popularity filter
filtered_movies = filtered_movies[
    filtered_movies["popularity"].between(
        selected_popularity[0],
        selected_popularity[1]
    )
]

# Saved SQL Analysis Queries
sql_queries = {
    "1. Action Movies Released After 2015": """
        SELECT DISTINCT m.title, m.release_date
        FROM movies m
        JOIN movie_genres mg ON m.movie_id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.genre_id
        WHERE g.genre_name = 'Action'
          AND CAST(strftime('%Y', m.release_date) AS INTEGER) > 2015
        ORDER BY m.release_date;
    """,

    "2. Top 10 Highest-Grossing Movies by Genre": """
        SELECT m.title, m.revenue, g.genre_name
        FROM movies m
        JOIN movie_genres mg ON m.movie_id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.genre_id
        WHERE m.revenue > 0
        ORDER BY m.revenue DESC
        LIMIT 10;
    """,

    "3. Average Budget and Revenue by Genre": """
        SELECT g.genre_name,
               ROUND(AVG(m.budget), 2) AS average_budget,
               ROUND(AVG(m.revenue), 2) AS average_revenue
        FROM movies m
        JOIN movie_genres mg ON m.movie_id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.genre_id
        GROUP BY g.genre_name
        ORDER BY average_revenue DESC;
    """,

    "4. Top 10 Actors by Movie Count": """
        SELECT actor_name,
               COUNT(DISTINCT movie_id) AS movie_count
        FROM "cast"
        GROUP BY person_id, actor_name
        ORDER BY movie_count DESC
        LIMIT 10;
    """,

    "5. Directors with More Than 3 Movies": """
        SELECT person_name AS director,
               COUNT(DISTINCT movie_id) AS movie_count
        FROM crew
        WHERE job = 'Director'
        GROUP BY person_id, person_name
        HAVING COUNT(DISTINCT movie_id) > 3
        ORDER BY movie_count DESC;
    """,

    "6. Top 10 Most Frequently Used Keywords": """
        SELECT keyword_name,
               COUNT(DISTINCT movie_id) AS usage_count
        FROM movie_keywords
        GROUP BY keyword_id, keyword_name
        ORDER BY usage_count DESC
        LIMIT 10;
    """,

    "7. Movies with Above-Average Budget and Below-Average Revenue": """
        SELECT title, budget, revenue
        FROM movies
        WHERE budget > (SELECT AVG(budget) FROM movies)
          AND revenue < (SELECT AVG(revenue) FROM movies)
        ORDER BY budget DESC;
    """,

    "8. Actors in Christopher Nolan Movies": """
        SELECT c.actor_name,
           COUNT(DISTINCT c.movie_id) AS movie_count
        FROM "cast" c
        JOIN crew cr ON c.movie_id = cr.movie_id
        WHERE cr.job = 'Director'
          AND cr.person_name = 'Christopher Nolan'
        GROUP BY c.person_id, c.actor_name
        ORDER BY movie_count DESC;
    """,

    "9. Highest-Rated Genre (At Least 20 Movies)": """
        SELECT g.genre_name,
               ROUND(AVG(m.vote_average), 2) AS average_rating,
               COUNT(DISTINCT m.movie_id) AS movie_count
        FROM movies m
        JOIN movie_genres mg ON m.movie_id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.genre_id
        GROUP BY g.genre_name
        HAVING COUNT(DISTINCT m.movie_id) >= 20
        ORDER BY average_rating DESC
        LIMIT 1;
    """,

    "10. Top 10 Movies by Keyword Count": """
        SELECT m.title,
               COUNT(mk.keyword_id) AS keyword_count
        FROM movies m
        JOIN movie_keywords mk ON m.movie_id = mk.movie_id
        GROUP BY m.movie_id, m.title
        ORDER BY keyword_count DESC
        LIMIT 10;
    """
}

# Page routing
# Page 1 - Filters
if selected == "Filters":


    # Display results
    st.markdown("""
<h2 style='color:#FFFFFF; font-size:25px;'>
    🎬 Filtered Movie Results
</h2>
""", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Movies",
            len(filtered_movies)
        )

    with col2:
        st.metric(
            "Average Rating",
            round(filtered_movies["vote_average"].mean(), 2)
            if not filtered_movies.empty else "N/A"
        )

    st.dataframe(
        filtered_movies[
            [
                "movie_id",
                "title",
                "release_year",
                "runtime",
                "vote_average",
                "popularity",
                "budget",
                "revenue"
            ]
        ].sort_values(
            by="popularity",
            ascending=False
        ),
        use_container_width=True,
        hide_index=True
    )

# Page 2 - Dashboard
elif selected == "Dashboard":

    # Dashboard heading
    st.markdown("""
    <h1 style="font-family:'Poppins';">
        📊 Movie <span style="color:#E50914;">Dashboard</span>
    </h1>
    <p style="color:#A7A9B4;">
        Explore movie trends, ratings, genres and financial performance.
    </p>
    <hr>
    """, unsafe_allow_html=True)

    # Prepare data
    dashboard_df = filtered_movies.copy()

    dashboard_df["release_year"] = (
        dashboard_df["release_date"].dt.year
    )

    # Original financial data: avoid median-imputed values
    financial_df = pd.read_csv("data/movies.csv")

    financial_df = financial_df[
        (financial_df["budget"] > 0) &
        (financial_df["revenue"] > 0)
    ].copy()
    # Apply global filters to financial data
    financial_df = financial_df[
    financial_df["movie_id"].isin(filtered_movies["movie_id"])
].copy()

    # Primary genre for each movie
    primary_genres = movie_genres_df.drop_duplicates(
        subset="movie_id",
        keep="first"
    )

    primary_genres = primary_genres.merge(
        genres_df,
        on="genre_id",
        how="left"
    )

    genre_movies = dashboard_df.merge(
        primary_genres[["movie_id", "genre_name"]],
        on="movie_id",
        how="inner"
    )

    # KPI section
    st.subheader("🎬 Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Movies",
        f"{dashboard_df['movie_id'].nunique():,}"
    )

    col2.metric(
        "Average Rating",
        f"{dashboard_df['vote_average'].mean():.2f}/10"
    )

    col3.metric(
        "Average Popularity",
        f"{dashboard_df['popularity'].mean():.2f}"
    )

    col4.metric(
        "Total Genres",
        genres_df["genre_name"].nunique()
    )

    st.markdown("---")

   
    # 1. INTERACTIVE PIE CHART - Genre distribution
    st.subheader("🎭 Interactive Movie Distribution by Genre")

    genre_counts = (
        genre_movies.groupby("genre_name")["movie_id"]
        .nunique()
        .reset_index(name="movie_count")
    )

    # Select genre to highlight
    selected_pie_genre = st.selectbox(
        "Highlight a Genre",
        ["All"] + sorted(genre_counts["genre_name"].tolist())
    )

    # Highlight selected genre
    pull_values = [
        0.12 if genre == selected_pie_genre else 0
        for genre in genre_counts["genre_name"]
    ]

    fig_pie = px.pie(
        genre_counts,
        names="genre_name",
        values="movie_count",
        hole=0.45,
        title="Movie Distribution Across Genres",
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig_pie.update_traces(
        pull=pull_values,
        textinfo="percent+label",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Movies: %{value}<br>"
            "Share: %{percent}"
            "<extra></extra>"
        )
    )

    fig_pie.update_layout(
        template="plotly_dark",
        height=550,
        legend_title="Movie Genres"
    )

    st.plotly_chart(fig_pie, use_container_width=True)


    # 2. LINE CHART - Release trends
    st.subheader("📅 Movie Release Trends")

    yearly_movies = (
        dashboard_df.dropna(subset=["release_year"])
        .groupby("release_year")["movie_id"]
        .nunique()
        .reset_index(name="movie_count")
    )

    fig_line = px.line(
        yearly_movies,
        x="release_year",
        y="movie_count",
        markers=True,
        title="Number of Movies Released per Year",
        color_discrete_sequence=["#E50914"]
    )

    fig_line.update_layout(
        template="plotly_dark",
        height=450,
        xaxis_title="Release Year",
        yaxis_title="Number of Movies"
    )

    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("---")

    
    
    # 3. INTERACTIVE HEATMAP - Correlation Analysis
    st.subheader("🔥 Interactive Movie Attribute Correlation")

    correlation_columns = [
        "budget",
        "revenue",
        "runtime",
        "popularity",
        "vote_average",
        "vote_count"
    ]

    correlation_data = dashboard_df[
        correlation_columns
    ].dropna()

    # Select correlation method
    correlation_method = st.selectbox(
        "Choose Correlation Method",
        ["Pearson", "Spearman"]
    )

    method = correlation_method.lower()

    correlation_matrix = correlation_data.corr(
        method=method
    )

    fig_heatmap = px.imshow(
        correlation_matrix,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
        title=f"{correlation_method} Correlation Between Movie Attributes"
    )

    fig_heatmap.update_layout(
        template="plotly_dark",
        height=600
    )

    st.plotly_chart(
        fig_heatmap,
        use_container_width=True
    )

    # 4. HISTOGRAM - Rating distribution
    st.subheader("⭐ Movie Rating Distribution")

    fig_hist = px.histogram(
        dashboard_df,
        x="vote_average",
        nbins=25,
        title="Distribution of Movie Ratings",
        color_discrete_sequence=["#E50914"]
    )

    fig_hist.update_layout(
        template="plotly_dark",
        height=450,
        xaxis_title="Average Rating",
        yaxis_title="Number of Movies"
    )

    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")


    
    # 5. INTERACTIVE BOX PLOT - Ratings Across Genres
    st.subheader("📦 Interactive Movie Ratings by Genre")

    available_genres = sorted(
        genre_movies["genre_name"].dropna().unique().tolist()
    )

    selected_genres = st.multiselect(
        "Select Genres to Compare",
        options=available_genres,
        default=available_genres[:5]
    )

    filtered_genres = genre_movies[
        genre_movies["genre_name"].isin(selected_genres)
    ]

    if not filtered_genres.empty:

        fig_box = px.box(
            filtered_genres,
            x="genre_name",
            y="vote_average",
            color="genre_name",
            points="all",
            hover_data=["title", "vote_count"],
            title="Movie Rating Distribution Across Selected Genres"
        )

        fig_box.update_layout(
            template="plotly_dark",
            height=600,
            showlegend=False,
            xaxis_title="Genre",
            yaxis_title="Average Rating",
            xaxis_tickangle=-35
        )

        st.plotly_chart(
            fig_box,
            use_container_width=True
        )

    else:
        st.info("Please select at least one genre.")

    # 6. INTERACTIVE SCATTER PLOT - Budget vs Revenue
    st.subheader("💰 Interactive Budget vs Revenue Analysis")

    # Add primary genre to financial data
    scatter_df = financial_df.merge(
        primary_genres[["movie_id", "genre_name"]],
        on="movie_id",
        how="left"
    )

    # Chart controls
    col1, col2 = st.columns(2)

    with col1:
        color_option = st.selectbox(
            "Colour Points By",
            ["vote_average", "genre_name", "popularity"]
        )

    with col2:
        minimum_budget = st.slider(
            "Minimum Movie Budget ($)",
            min_value=0,
            max_value=int(scatter_df["budget"].max()),
            value=0,
            step=10_000_000
        )

    # Apply budget filter
    filtered_scatter = scatter_df[
        scatter_df["budget"] >= minimum_budget
    ]

    fig_scatter = px.scatter(
        filtered_scatter,
        x="budget",
        y="revenue",
        size="vote_count",
        color=color_option,
        hover_name="title",
        hover_data=[
            "release_date",
            "budget",
            "revenue",
            "vote_average",
            "vote_count"
        ],
        color_continuous_scale="Turbo"
        if color_option != "genre_name"
        else None,
        color_discrete_sequence=px.colors.qualitative.Bold
        if color_option == "genre_name"
        else None,
        title="Movie Budget vs Revenue"
    )

    fig_scatter.update_layout(
        template="plotly_dark",
        height=650,
        xaxis_title="Budget ($)",
        yaxis_title="Revenue ($)"
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )


    # 7. TREEMAP - Genre distribution
    st.subheader("🗺️ Genre Distribution Treemap")

    fig_tree = px.treemap(
        genre_counts,
        path=["genre_name"],
        values="movie_count",
        color="movie_count",
        color_continuous_scale="Plasma",
        title="Movie Collection by Primary Genre"
    )

    fig_tree.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("---")

    # 8. BAR CHART - Top popular movies
    st.subheader("🔥 Top 10 Most Popular Movies")

    top_movies = dashboard_df.nlargest(
        10, "popularity"
    ).sort_values("popularity", ascending=True)

    fig_top = px.bar(
        top_movies,
        x="popularity",
        y="title",
        orientation="h",
        color="popularity",
        color_continuous_scale="Magma",
        title="Top 10 Movies by Popularity"
    )

    fig_top.update_layout(
        template="plotly_dark",
        height=500,
        xaxis_title="Popularity Score",
        yaxis_title="Movie"
    )

    st.plotly_chart(fig_top, use_container_width=True)



# Page 3 - Query Explorer
elif selected == "Query Explorer":

    st.title("🗄️ SQL Query Explorer")
    st.write(
        "Explore the TMDB database through interactive SQL analysis. "
        "Select a question to view its query results and visualization."
    )

    st.markdown("---")

    # SQL Query Selection Box
    selected_query = st.selectbox(
        "🎯 Select an SQL Analysis Question",
        options=list(sql_queries.keys())
    )

    # Display selected SQL query
    st.subheader("📝 SQL Query")

    st.code(
        sql_queries[selected_query],
        language="sql"
    )

    # Execute selected SQL query
    try:
        conn = sqlite3.connect("tmdb_movies.db")

        result_df = pd.read_sql_query(
            sql_queries[selected_query],
            conn
        )

        conn.close()

        # Display query results
        st.markdown("---")
        st.subheader("📊 Query Results")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Records", len(result_df))

        with col2:
            st.metric("Total Columns", len(result_df.columns))

        st.dataframe(
            result_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Dynamic Visualization Section
        st.markdown("---")
        st.subheader("📈 Data Visualization")

        # 1. Action Movies Released After 2015
        if selected_query.startswith("1."):

            yearly_movies = (
                result_df.assign(
                    release_year=pd.to_datetime(
                        result_df["release_date"]
                    ).dt.year
                )
                .groupby("release_year")
                .size()
                .reset_index(name="movie_count")
            )

            fig = px.bar(
                yearly_movies,
                x="release_year",
                y="movie_count",
                title="Action Movies Released by Year",
                color="movie_count",
                color_continuous_scale="Reds"
            )

        # 2. Top Grossing Movies
        elif selected_query.startswith("2."):

            chart_df = result_df.sort_values(
                "revenue", ascending=True
            )

            fig = px.bar(
                chart_df,
                x="revenue",
                y="title",
                orientation="h",
                title="Top 10 Highest-Grossing Movies",
                color="revenue",
                color_continuous_scale="Reds"
            )

        # 3. Average Budget and Revenue by Genre
        elif selected_query.startswith("3."):

            chart_df = result_df.melt(
                id_vars="genre_name",
                value_vars=[
                    "average_budget",
                    "average_revenue"
                ],
                var_name="financial_metric",
                value_name="amount"
            )

            fig = px.bar(
                chart_df,
                x="genre_name",
                y="amount",
                color="financial_metric",
                barmode="group",
                title="Average Budget vs Revenue by Genre",
                color_discrete_sequence=["#E50914", "#F5A623"]
            )

        # 4. Top Actors
        elif selected_query.startswith("4."):

            fig = px.bar(
                result_df.sort_values(
                    "movie_count", ascending=True
                ),
                x="movie_count",
                y="actor_name",
                orientation="h",
                title="Top 10 Actors by Movie Count",
                color="movie_count",
                color_continuous_scale="Reds"
            )

        # 5. Directors with More Than 3 Movies
        elif selected_query.startswith("5."):

            fig = px.bar(
                result_df.sort_values(
                    "movie_count", ascending=True
                ),
                x="movie_count",
                y="director",
                orientation="h",
                title="Movies Directed by Each Director",
                color="movie_count",
                color_continuous_scale="Reds"
            )

        # 6. Most Frequently Used Keywords
        elif selected_query.startswith("6."):

            fig = px.bar(
                result_df.sort_values(
                    "usage_count", ascending=True
                ),
                x="usage_count",
                y="keyword_name",
                orientation="h",
                title="Top 10 Most Used Movie Keywords",
                color="usage_count",
                color_continuous_scale="Reds"
            )

        # 7. Above-Average Budget and Below-Average Revenue
        elif selected_query.startswith("7."):

            fig = px.scatter(
                result_df,
                x="budget",
                y="revenue",
                hover_name="title",
                title="Budget vs Revenue of Selected Movies",
                color="budget",
                color_continuous_scale="Reds"
            )

       
        # 8. Actors in Christopher Nolan Movies
        elif selected_query.startswith("8."):

            chart_df = result_df.sort_values(
                "movie_count",
                ascending=True
            ).tail(10)

            fig = px.bar(
                chart_df,
                x="movie_count",
                y="actor_name",
                orientation="h",
                title="Top Actors in Christopher Nolan Movies",
                color="movie_count",
                color_continuous_scale="Reds"
            )

        # 9. Highest-Rated Genre
        elif selected_query.startswith("9."):

            fig = px.bar(
                result_df,
                x="genre_name",
                y="average_rating",
                title="Highest Average-Rated Genre",
                color="average_rating",
                color_continuous_scale="Reds"
            )

        # 10. Movies with the Most Keywords
        elif selected_query.startswith("10."):

            chart_df = result_df.sort_values(
                "keyword_count", ascending=True
            )

            fig = px.bar(
                chart_df,
                x="keyword_count",
                y="title",
                orientation="h",
                title="Top 10 Movies by Keyword Count",
                color="keyword_count",
                color_continuous_scale="Reds"
            )

        # Apply common chart styling
        fig.update_layout(
            template="plotly_dark",
            height=550,
            title_x=0.5,
            font=dict(
                family="Inter",
                size=12
            ),
            margin=dict(
                l=20,
                r=20,
                t=70,
                b=40
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    except Exception as e:
        st.error(f"Error executing query: {e}")
