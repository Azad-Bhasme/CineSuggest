import os
import streamlit as st
import pickle
import pandas as pd
import requests
from dotenv import load_dotenv

# Load environment variables from .env file (optional, for local development)
load_dotenv()

# Placeholder image for missing posters
PLACEHOLDER_POSTER = "https://via.placeholder.com/300x450?text=No+Image"

# Fetch movie poster using TMDb API
def fetch_poster(movie_id):
    api_key = os.environ.get("TMDB_API_KEY")  # Access API key securely
    if not api_key:
        st.error("TMDB API key not found in environment variables.")
        return PLACEHOLDER_POSTER

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"

    try:
        response = requests.get(url)
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            return PLACEHOLDER_POSTER
    except:
        return PLACEHOLDER_POSTER

# Recommend similar movies
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movie_indices:
        movie_row = movies.iloc[i[0]]
        title = movie_row['title']
        movie_id = movie_row.get('movie_id')

        if pd.isna(movie_id):
            poster = PLACEHOLDER_POSTER
        else:
            poster = fetch_poster(movie_id)

        recommended_movies.append(title)
        recommended_movies_posters.append(poster)

    return recommended_movies, recommended_movies_posters

# Load data
movies_list = pickle.load(open('movies.pkl', 'rb'))
movies = pd.DataFrame(movies_list)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit UI
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations:',
    movies['title'].values
)

if st.button('Recommend Movies'):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(len(names))
    for idx, (name, poster) in enumerate(zip(names, posters)):
        with cols[idx]:
            st.text(name)
            st.image(poster)
