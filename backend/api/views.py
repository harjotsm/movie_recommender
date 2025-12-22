from django.shortcuts import render
import os
import pickle
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings

BASE_DIR = settings.BASE_DIR
ML_DIR = os.path.join(BASE_DIR, 'api', 'ml')

print(f"--- Load ML Model from: {ML_DIR} ---")

try:
    movies = pickle.load(open(os.path.join(ML_DIR, 'movies.pkl'), 'rb'))
    count_matrix = pickle.load(open(os.path.join(ML_DIR, 'similarity_matrix.pkl'), 'rb'))
    vectorizer = pickle.load(open(os.path.join(ML_DIR, 'vectorizer.pkl'), 'rb'))
    print("Success: Model loaded successfully.")
except FileNotFoundError:
    print("Error: .pkl File not found! Please ensure the model files are in the correct path.")
    movies, count_matrix, vectorizer = None, None, None

MOOD_MAPPING = {
    "Funny": "comedy spoof parody fun",
    "Dark": "crime murder noir thriller horror",
    "Exciting": "action adventure chase explosion war",
    "Emotional": "romance drama love crying wedding",
    "Brainy": "mystery puzzle psychology philosophy"
}


@api_view(['GET'])
def get_options(request):
    genres = ["Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama", "Family", "Fantasy",
              "History", "Horror", "Music", "Mystery", "Romance", "Science Fiction", "Thriller", "War", "Western"]

    moods = list(MOOD_MAPPING.keys())

    return Response({
        "genres": genres,
        "moods": moods
    })


@api_view(['POST'])
def recommend_movies(request):
    if movies is None:
        return Response({"error": "Model not loaded"}, status=500)

    data = request.data

    genre = data.get('genre', '')
    mood_key = data.get('mood', '')
    content = data.get('content', '')
    element = data.get('element', '')

    mood_keywords = MOOD_MAPPING.get(mood_key, "")

    search_query = f"{genre} {genre} {genre} {mood_keywords} {content} {element}"
    print(f"User Query Vector: {search_query}")

    try:
        user_vec = vectorizer.transform([search_query])
        similarity = cosine_similarity(user_vec, count_matrix)

        scores = list(enumerate(similarity[0]))
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

        results = []
        for i, (index, score) in enumerate(sorted_scores[:5]):
            results.append({
                "id": int(movies.iloc[index].name),
                "title": movies.iloc[index]['title'],
                "overview": movies.iloc[index]['overview'],
                "score": round(score, 2),
            })

        return Response(results)

    except Exception as e:
        print(f"Error during recommendation: {e}")
        return Response({"ERROR": "error during calculation"}, status=500)
