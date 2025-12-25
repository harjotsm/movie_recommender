from django.shortcuts import render
import os
import pickle
import numpy as np
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings
from sentence_transformers import SentenceTransformer

BASE_DIR = settings.BASE_DIR
ML_DIR = os.path.join(BASE_DIR, 'api', 'ml')

print(f"--- INIT: Loading S-BERT Model from: {ML_DIR} ---")


movies_df = None
movie_embeddings = None
model = None

try:

    movies_path = os.path.join(ML_DIR, 'movies.pkl')
    movies_df = pickle.load(open(movies_path, 'rb'))
    emb_path = os.path.join(ML_DIR, 'movie_embeddings.pkl')
    movie_embeddings = pickle.load(open(emb_path, 'rb'))

    print("Loading SentenceTransformer (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print(" Model & Data loaded.")
except FileNotFoundError as e:
    print(f" Error: .pkl File not found! {e}")
    print("   Please run 'python scripts/build_engine.py' first.")
except Exception as e:
    print(f" Critical Error loading model: {e}")

MOOD_MAPPING = {
    "Funny": "comedy, funny, hilarious, parody, spoof, laughing, happy",
    "Dark": "crime, murder, thriller, horror, noir, dark, tense, gritty",
    "Exciting": "action, adventure, war, explosion, chase, fast-paced, adrenaline",
    "Emotional": "drama, romance, love, sad, crying, touching, sentimental, wedding",
    "Brainy": "mystery, puzzle, psychology, philosophy, mind-bending, complex, sci-fi"
}

@api_view(['GET'])
def get_options(request):
    genres = ["Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama",
              "Family", "Fantasy", "History", "Horror", "Music", "Mystery", "Romance",
              "Science Fiction", "Thriller", "War", "Western"]
    moods = list(MOOD_MAPPING.keys())
    return Response({"genres": genres, "moods": moods})


@api_view(['POST'])
def recommend_movies(request):
    if model is None:
        return Response({"error": "ML Model not ready."}, status=500)

    data = request.data
    genre = data.get('genre', '')
    mood_key = data.get('mood', '')
    content = data.get('content', '')
    element = data.get('element', '')

    mood_keywords = MOOD_MAPPING.get(mood_key, "")

    # SBERT Query Construction
    user_query = f"A {genre} movie. Mood: {mood_keywords}. About: {content}. Contains: {element}."
    print(f"🔍 AI Search Query: {user_query}")

    try:
        #  Encode
        query_embedding = model.encode([user_query])

        #  Similarity
        similarities = cosine_similarity(query_embedding, movie_embeddings)

        #  Sort + Return Top 6
        scores = list(enumerate(similarities[0]))
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

        results = []
        for index, score in sorted_scores[:6]:
            row = movies_df.iloc[index]

            release_date = str(row['release_date'])
            year = release_date.split("-")[0] if "-" in release_date else "N/A"

            results.append({
                "id": int(row['id']),
                "title": row['title'],
                "overview": row['overview'],
                "score": round(float(score), 2),
                "genres": row['genres_str'],
                "year": year,
                "rating": float(row['vote_average']),
                "runtime": int(row['runtime'])
            })

        return Response(results)

    except Exception as e:
        print(f"Error: {e}")
        return Response({"error": str(e)}, status=500)