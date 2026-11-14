# 🎬 Reel Insights: An End-to-End Exploratory Data Analysis of the Global Movie Industry (TMDB)

## 📌 Project Overview

Reel Insights is an end-to-end data analytics project focused on exploring the global movie industry using The Movie Database (TMDB) dataset.

The project analyzes approximately 2,500 movies across six relational datasets to uncover insights about movie genres, budgets, revenues, ratings, popularity, cast, crew, and keywords.

It combines data cleaning, SQL analysis, Python-based exploratory data analysis, interactive visualizations, and a Streamlit application into one complete analytics workflow.

## 🎯 Project Objectives

- Clean and preprocess multiple related datasets.
- Build a relational SQLite database.
- Perform analytical queries using SQL.
- Conduct exploratory data analysis using Pandas.
- Identify trends and relationships through visualizations.
- Develop an interactive Streamlit dashboard for exploring movie industry insights.

## 🛠️ Technologies Used

| Category          | Tools                       |
| ----------------- | --------------------------- |
| Programming       | Python                      |
| Data Manipulation | Pandas, NumPy               |
| Database          | SQLite, SQL                 |
| Visualization     | Matplotlib, Seaborn, Plotly |
| Dashboard         | Streamlit                   |
| Development       | Jupyter Notebook, VS Code   |
| Version Control   | Git, GitHub                 |

## 📂 Project Structure

```text
TMDB-Project/
│
├── 01_data_cleaning.ipynb
├── 02_sql_analysis.ipynb
├── 03_pandas_analysis.ipynb
├── 04_visualizations.ipynb
│
├── app.py
├── README.md
├── tmdb_movies.db
├── .gitignore
│
├── data/
│   ├── movies.csv
│   ├── genres.csv
│   ├── movie_genres.csv
│   ├── cast.csv
│   ├── crew.csv
│   └── movie_keywords.csv
│
└── cleaned_data/
    ├── movies.csv
    ├── genres.csv
    ├── movie_genres.csv
    ├── cast.csv
    ├── crew.csv
    └── movie_keywords.csv
```

## 🔄 Project Workflow

### 1. Data Cleaning and Preprocessing

- Loaded and inspected six CSV datasets.
- Handled missing values and duplicate records.
- Converted columns into appropriate data types.
- Performed data validation and referential integrity checks.
- Exported cleaned datasets into `cleaned_data/`.

### 2. SQL Analysis

- Created a relational SQLite database.
- Imported all six cleaned datasets.
- Used SQL joins, aggregations, subqueries, and filtering.
- Answered 10 analytical business questions.

### 3. Pandas Analysis

- Conducted exploratory data analysis using Pandas.
- Analyzed movie profitability, ROI, release trends, runtime, genres, actors, and popularity.
- Answered 10 analytical questions.

### 4. Data Visualization

Created 15 visualizations using Matplotlib, Seaborn, and Plotly to explore:

- Budget and revenue distributions.
- Movie ratings and popularity.
- Genre performance.
- Release trends.
- Budget versus revenue relationships.
- ROI comparisons.
- Correlations between movie attributes.

### 5. Interactive Streamlit Application

Developed an interactive dashboard featuring:

- Movie filters.
- Key performance indicators.
- Genre distribution.
- Movie release trends.
- Rating analysis.
- Budget and revenue analysis.
- Popular movies.
- SQL Query Explorer.

## 📊 Key Project Outcomes

- Analyzed six related datasets containing over 83,000 records.
- Removed 59 duplicate records during data cleaning.
- Built a SQLite database containing six relational tables.
- Completed 10 SQL analytical questions.
- Completed 10 Pandas analytical questions.
- Developed 15 data visualizations.
- Built an interactive Streamlit dashboard.

## 🚀 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Sharuk0026/TMDB-Project-.git
cd TMDB-Project-
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install pandas numpy matplotlib seaborn plotly sqlalchemy streamlit streamlit-option-menu jupyter
```

### 4. Run the Streamlit application

```bash
streamlit run app.py
```

## 📁 Dataset Information

The project uses six relational datasets:

| Dataset            | Description                                                 |
| ------------------ | ----------------------------------------------------------- |
| movies.csv         | Movie information, ratings, budget, revenue, and popularity |
| genres.csv         | Movie genre reference data                                  |
| movie_genres.csv   | Relationship between movies and genres                      |
| cast.csv           | Movie cast information                                      |
| crew.csv           | Movie crew information                                      |
| movie_keywords.csv | Keywords associated with movies                             |

## ⚠️ Data Considerations

- Zero budget and revenue values were treated as missing and median-imputed in the cleaned dataset.
- Financial visualizations use original records with valid positive budget and revenue values to avoid relying on imputed financial figures.
- ROI is calculated using production budget and gross revenue only. Marketing, distribution, and other costs are not included.
- Some analyses may be affected by dataset coverage and the availability of movie information.

## 👨‍💻 Author

**Sharukesh M**

B.Tech – Computer Science and Engineering

GitHub: [Sharuk0026](https://github.com/Sharuk0026)

---

⭐ If you find this project interesting, feel free to explore the notebooks and interactive application!
