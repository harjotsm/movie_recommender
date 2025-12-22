import pickle
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity

print("Load DB...")
movies = pickle.load(open('../api/ml/movies.pkl', 'rb'))
count_matrix = pickle.load(open('../api/ml/similarity_matrix.pkl', 'rb'))
vectorizer = pickle.load(open('../api/ml/vectorizer.pkl', 'rb'))

all_genres = []
for genres_str in movies['genres']:
    if isinstance(genres_str, str):
        all_genres.extend(genres_str.split())


top_genres = [g[0] for g in Counter(all_genres).most_common(10)]

mood_mapping = {
    "1": ("Zum Lachen (Funny)", "comedy spoof parody fun"),
    "2": ("Düster & Ernst (Dark)", "crime murder noir thriller horror"),
    "3": ("Adrenalin (Exciting)", "action adventure chase explosion war"),
    "4": ("Fürs Herz (Emotional)", "romance drama love crying wedding"),
    "5": ("Mind-Bending (Brainy)", "mystery puzzle psychology philosophy")
}

top_elements = ["future", "alien", "magic", "police", "high school", "robot", "zombie"]


def ask_user(question, options):
    print(f"\n{question}")
    for i, opt in enumerate(options):
        print(f"[{i + 1}] {opt}")

    while True:
        try:
            choice = int(input("Your choice (Nummer): "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
        except ValueError:
            pass
        print("False entry, only the number please")


def run_wizard():
    print("\n--- MOVIE WIZARD (Selection-Mode) ---")

    # FRAGE 1: GENRE (Dynamisch aus DB)
    selected_genre = ask_user("Which Genre?", top_genres)

    # FRAGE 2: STIMMUNG (Hardcoded Map)
    print("\nWhich mood?")
    for key, val in mood_mapping.items():
        print(f"[{key}] {val[0]}")

    mood_choice = input("Your choice (Nummer): ")
    selected_mood_keywords = mood_mapping.get(mood_choice, mood_mapping["1"])[1]


    selected_element = ask_user("Which element must appear?", top_elements)

    search_query = f"{selected_genre} {selected_genre} {selected_genre} {selected_mood_keywords} {selected_element}"

    print(f"\nInternal Search-Vector: '{search_query}'")

    user_vec = vectorizer.transform([search_query])
    similarity = cosine_similarity(user_vec, count_matrix)

    scores = list(enumerate(similarity[0]))
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)

    print("\n--- Results ---")
    for i, (index, score) in enumerate(sorted_scores[:5]):
        title = movies.iloc[index]['title']
        genres = movies.iloc[index]['genres']
        print(f"{i + 1}. {title} ({genres})")


if __name__ == "__main__":
    run_wizard()