import streamlit as st
import pickle
import pandas as pd
import requests
import time

# ✅ TMDB API Key
API_KEY = "10d6be6edf92c4a4bcc24d72da0e76bc"

# ✅ Fetch Poster with Retry + Timeout + Error Handling
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    for attempt in range(3):  # retry 3 times
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if 'poster_path' in data and data['poster_path']:
                return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
            else:
                return "https://via.placeholder.com/500x750?text=No+Image"
        except requests.exceptions.RequestException as e:
            print(f"Error fetching poster (attempt {attempt+1}): {e}")
            time.sleep(2)  # wait before retry
    return "https://via.placeholder.com/500x750?text=No+Image"

# ✅ Recommend Function
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]]['id']
        recommended_movies.append(movies.iloc[i[0]]['title'])
        recommended_movies_posters.append(fetch_poster(movie_id))
        time.sleep(0.3)  # small delay to avoid rate limit
    return recommended_movies, recommended_movies_posters

# ✅ Load Data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# ✅ Streamlit UI
st.title('🍿 Movie Recommender System')

selected_movie_name = st.selectbox("Search for a movie:", movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)

    for i, col in enumerate(cols):
        with col:
            st.image(posters[i], width=200)  # fixed size
            st.markdown(
                f"<p style='text-align:center; font-size:14px; font-weight:bold;'>{names[i]}</p>",
                unsafe_allow_html=True
            )
