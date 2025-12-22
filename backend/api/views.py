from django.shortcuts import render
import os
import pickle
from rest_framework.decorators import api_view
from rest_framework.response import Response
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings

# --- 1. SETUP & MODEL LOADING ---
# Wir bauen den Pfad dynamisch, damit es auf jedem PC funktioniert
# Base Dir ist backend/, wir gehen nach api/ml/
BASE_DIR = settings.BASE_DIR
ML_DIR = os.path.join(BASE_DIR, 'api', 'ml')

print(f"--- Lade ML-Modelle aus: {ML_DIR} ---")

# Laden der .pkl Dateien (nur einmal beim Server-Start!)
try:
    movies = pickle.load(open(os.path.join(ML_DIR, 'movies.pkl'), 'rb'))
    count_matrix = pickle.load(open(os.path.join(ML_DIR, 'similarity_matrix.pkl'), 'rb'))
    vectorizer = pickle.load(open(os.path.join(ML_DIR, 'vectorizer.pkl'), 'rb'))
    print("ERFOLG: Modelle geladen.")
except FileNotFoundError:
    print("FEHLER: .pkl Dateien nicht gefunden! Hast du sie nach backend/api/ml/ verschoben?")
    # Wir setzen Platzhalter, damit der Server nicht abstürzt, aber die API wird Fehler werfen
    movies, count_matrix, vectorizer = None, None, None

# Statische Mapping-Daten für die Fragen (Könnte man auch aus DB laden)
MOOD_MAPPING = {
    "Funny": "comedy spoof parody fun",
    "Dark": "crime murder noir thriller horror",
    "Exciting": "action adventure chase explosion war",
    "Emotional": "romance drama love crying wedding",
    "Brainy": "mystery puzzle psychology philosophy"
}


# --- 2. API ENDPOINTS ---

@api_view(['GET'])
def get_options(request):
    """
    Liefert die Auswahlmöglichkeiten für das Frontend (Dropdowns).
    """
    # Wir holen uns einfache Listen
    # 1. Genres (Wir nehmen die Top-Genres aus unserer Analyse oder hardcoden die wichtigsten)
    # Hier eine kuratierte Liste für bessere UX:
    genres = ["Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama", "Family", "Fantasy",
              "History", "Horror", "Music", "Mystery", "Romance", "Science Fiction", "Thriller", "War", "Western"]

    # 2. Moods (Keys aus unserem Mapping)
    moods = list(MOOD_MAPPING.keys())

    return Response({
        "genres": genres,
        "moods": moods
    })


@api_view(['POST'])
def recommend_movies(request):
    """
    Nimmt User-Antworten entgegen und berechnet Empfehlungen.
    Erwartet JSON: { "genre": "...", "mood": "...", "content": "...", "element": "..." }
    """
    if movies is None:
        return Response({"error": "Modelle nicht geladen"}, status=500)

    data = request.data

    # 1. Inputs auslesen
    genre = data.get('genre', '')
    mood_key = data.get('mood', '')  # z.B. "Dark"
    content = data.get('content', '')  # z.B. "Space"
    element = data.get('element', '')  # z.B. "Robot"

    # 2. Mood in Keywords übersetzen
    mood_keywords = MOOD_MAPPING.get(mood_key, "")

    # 3. Such-Vektor bauen (Gewichtung: Genre x3)
    search_query = f"{genre} {genre} {genre} {mood_keywords} {content} {element}"
    print(f"User Query Vector: {search_query}")

    # 4. ML-Berechnung
    try:
        user_vec = vectorizer.transform([search_query])
        similarity = cosine_similarity(user_vec, count_matrix)

        # Sortieren
        scores = list(enumerate(similarity[0]))
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

        # Top 5 Ergebnisse formatieren
        results = []
        for i, (index, score) in enumerate(sorted_scores[:5]):
            # Optional: Filtere Ergebnisse mit zu niedrigem Score (Rauschen)
            # if score < 0.1: continue

            results.append({
                "id": int(movies.iloc[index].name),  # oder eine ID Spalte
                "title": movies.iloc[index]['title'],
                "overview": movies.iloc[index]['overview'],
                "score": round(score, 2),
                # "genres": movies.iloc[index]['genres'] # Falls du das anzeigen willst
            })

        return Response(results)

    except Exception as e:
        print(f"Error during recommendation: {e}")
        return Response({"error": "Fehler bei der Berechnung"}, status=500)
# Create your views here.
