import os
import pickle
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv
import gdown

# Load TMDB API key
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Download similarity.pkl from Google Drive if not exists
SIMILARITY_FILE = "similarity.pkl"
if not os.path.exists(SIMILARITY_FILE):
    gdown.download(
        "https://drive.google.com/uc?id=1Yzi3ElfOW9rHbbPMRAKo57GPRGonjvre",
        SIMILARITY_FILE,
        quiet=False
    )

# Load movie data and similarity matrix
movies = pd.DataFrame(pickle.load(open('movies.pkl', 'rb')))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Poster fetch helper
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url)
        data = response.json()
        poster_path = data.get('poster_path')
        return f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/300x450?text=No+Image"
    except:
        return "https://via.placeholder.com/300x450?text=No+Image"

# Recommendation logic
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_indices:
        movie_id = movies.iloc[i[0]]['movie_id']
        recommended_movies.append(movies.iloc[i[0]]['title'])
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters

# UI Layout
st.set_page_config(page_title="CineSuggest", layout="wide")
st.markdown("<h1 style='text-align: center; color: white;'>🍿 Movie Recommender System</h1>", unsafe_allow_html=True)
selected_movie_name = st.selectbox("🎥 Select a movie to get recommendations:", movies['title'].values)

if st.button("Recommend Movies"):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.image(posters[idx])
            st.markdown(f"**{names[idx]}**", unsafe_allow_html=True)

# Animated Footer
st.markdown("""
    <style>
        .footer {
            position: fixed;
            bottom: 10px;
            width: 100%;
            text-align: center;
            color: white;
            font-weight: bold;
            font-size: 18px;
        }
        .heartbeat {
            display: inline-block;
            animation: beat 1.2s infinite;
        }
        @keyframes beat {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.3); }
        }
    </style>
    <div class="footer">
        Made with <span class="heartbeat">❤️</span> by Azad Bhasme
    </div>
""", unsafe_allow_html=True)
