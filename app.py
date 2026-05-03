import pickle
from flask import Flask, render_template, request
import requests
import os


def download_file(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename}...")
        r = requests.get(url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
movies_url = "https://github.com/yugkayasth05/movie-recommendation-system/releases/download/v1.0/movies.pkl"
similarity_url = "https://github.com/yugkayasth05/movie-recommendation-system/releases/download/v1.0/similarity.pkl"

if os.path.exists("movies.pkl"):
    os.remove("movies.pkl")

if os.path.exists("similarity.pkl"):
    os.remove("similarity.pkl")

download_file(movies_url, "movies.pkl")
download_file(similarity_url, "similarity.pkl")

movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

app = Flask(__name__)

# Load data
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

#fetch poster
# import requests
# import urllib.parse

def fetch_poster(movie_id):
    import requests

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=76ee6355cf31688510e64302f0404fc5"
        data = requests.get(url).json()

        poster_path = data.get('poster_path')

        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path

        # fallback if no poster
        return "https://via.placeholder.com/200x300?text=No+Poster"

    except Exception as e:
        print("Error:", e)
        return "https://via.placeholder.com/200x300?text=Error"
# Recommendation function
def recommend(movie):
    movie = movie.strip()

    if movie not in movies['title'].values:
        return [], []   # 👈 return empty safely

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))

    return recommended_movies, posters


@app.route('/',methods=['post','get'])
def index():
    recommended=[]
    posters=[]
    error=""
    selected_movie=""

    if request.method=='POST':
        selected_movie=request.form['movie']
        recommended,posters=recommend(selected_movie)

        if not recommended:
          error = "Movie not found. Please select from suggestions."

    return render_template('index.html',movies=list(movies['title'].values),recommended=recommended,posters=posters,selected_movie=selected_movie)
    posters = [p if p else "https://via.placeholder.com/200x300?text=No+Image" for p in posters]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)