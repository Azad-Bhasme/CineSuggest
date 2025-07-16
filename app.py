import os
import pickle
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
import gdown

# Load environment variables
load_dotenv()

# Download similarity.pkl from Google Drive if not exists
SIMILARITY_PATH = "similarity.pkl"
if not os.path.exists(SIMILARITY_PATH):
    file_id = "1Yzi3ElfOW9rHbbPMRAKo57GPRGonjvre"
    gdown.download(f"https://drive.google.com/uc?id={file_id}", SIMILARITY_PATH, quiet=False)

# Load data
movies = pd.DataFrame(pickle.load(open("movies.pkl", "rb")))
similarity = pickle.load(open("similarity.pkl", "rb"))

# Constants
PLACEHOLDER_POSTER = "https://via.placeholder.com/300x450?text=No+Image"
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")

# Fetch poster from TMDB
def fetch_poster(movie_id):
    if not TMDB_API_KEY:
        return PLACEHOLDER_POSTER
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url)
        data = response.json()
        return f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get("poster_path") else PLACEHOLDER_POSTER
    except:
        return PLACEHOLDER_POSTER

# Recommendation logic
def recommend(movie):
    idx = movies[movies['title'] == movie].index[0]
    dists = similarity[idx]
    movie_indices = sorted(list(enumerate(dists)), key=lambda x: x[1], reverse=True)[1:6]
    titles, posters = [], []
    for i in movie_indices:
        titles.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movies.iloc[i[0]].movie_id))
    return titles, posters

# UI Config
st.set_page_config(page_title="CineSuggest", page_icon="🍿", layout="wide")

# Sidebar Navigation
page = st.sidebar.radio("📂 Navigate", ["Home", "About"])

# === Home Page ===
if page == "Home":
    st.markdown("<h1 style='text-align: center;'>🍿 Movie Recommender System</h1>", unsafe_allow_html=True)

    selected_movie = st.selectbox("🎥 Select a movie to get recommendations:", movies['title'].values)

    if st.button("Recommend Movies"):
        names, posters = recommend(selected_movie)
        cols = st.columns(5)
        for idx, (title, poster) in enumerate(zip(names, posters)):
            with cols[idx]:
                st.image(poster, width=150)
                st.markdown(f"**{title}**")

    st.markdown(
        "<div style='text-align: center; margin-top: 3rem;'>"
        "Made with <span style='color:red; animation: blink 1.5s infinite;'>❤️</span> by <strong>Azad Bhasme</strong>"
        "</div><style>@keyframes blink {0%{opacity:1;}50%{opacity:0.3;}100%{opacity:1;}}</style>",
        unsafe_allow_html=True,
    )

# === About Page ===
elif page == "About":
    st.markdown("<h1 style='text-align: center;'>🎬 About CineSuggest</h1>", unsafe_allow_html=True)
    st.write("""
    **CineSuggest** is a content-based movie recommendation system that suggests similar films based on the one you select.
    
    🔍 It uses cosine similarity and metadata (genre, keywords, overview) to find the closest matches.

    📡 Movie posters are fetched using the [TMDB API](https://www.themoviedb.org/).

    🛠 Built with:
    - Python
    - Pandas
    - Streamlit
    - TMDB API
    - Google Drive integration for large files

    💡 Designed and developed with ❤️ by **Azad Bhasme**
    """)

