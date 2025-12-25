import os
import pandas as pd
import pickle

from sklearn.feature_extraction.text import CountVectorizer
from ast import literal_eval
from sentence_transformers import SentenceTransformer

CURRENT_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_SCRIPT_DIR)
CSV_PATH = os.path.join(CURRENT_SCRIPT_DIR, 'tmdb_5000_movies.csv')
ML_DIR = os.path.join(BACKEND_DIR, 'api', 'ml')
MODEL_NAME = 'all-MiniLM-L6-v2'

print("1. load dataset...")

if not os.path.exists(CSV_PATH):
    print(f"Error: Dataset not found at {CSV_PATH}")
    exit()

df = pd.read_csv(CSV_PATH)

#features = ['keywords', 'genres', 'overview', 'title', 'release_date', 'vote_average', 'runtime']
#df_clean = df[features].copy()

df = df[['id', 'title', 'genres', 'overview', 'keywords', 'release_date', 'vote_average', 'runtime']].copy()


print("2. Cleaning Data")
df['overview'] = df['overview'].fillna('')
df['genres'] = df['genres'].fillna('[]')
df['keywords'] = df['keywords'].fillna('[]')


def parse_json_col(x):
    try:
        items = literal_eval(x)
        if isinstance(items, list):
            return " ".join([i['name'] for i in items])
        return ""
    except:
        return str(x)

df['genres_str'] = df['genres'].apply(parse_json_col)
df['keywords_str'] = df['keywords'].apply(parse_json_col)

#  "Rich Context String", that the transformer reads
df['semantic_text'] = df.apply(
    lambda row: f"Title: {row['title']}. Genre: {row['genres_str']}. Plot: {row['overview']}",
    axis=1
)

print(f"   Sample Input: {df['semantic_text'].iloc[0][:80]}...")

print(f"3. Loading Model {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)

print("4. Encoding Movie Overviews")
embeddings = model.encode(df['semantic_text'].tolist(), show_progress_bar=True)



#df_clean['genres'] = df_clean['genres'].apply(parse_features)
#df_clean['keywords'] = df_clean['keywords'].apply(parse_features)
#df_clean['overview'] = df_clean['overview'].fillna('')
#df_clean['release_date'] = df_clean['release_date'].fillna('')
#df_clean['runtime'] = df_clean['runtime'].fillna(0)
#df_clean['vote_average'] = df_clean['vote_average'].fillna(0)
#print("   Example genre (cleaned):", df_clean['genres'].iloc[0])


def combine_features(row):
    try:
        return row['keywords'] + " " + row['genres'] + " " + row['overview']
    except:
        print("Error:", row)
        return ""


#print("3. creating combined features...")
#df_clean['combined_features'] = df_clean.apply(combine_features, axis=1)

#print("4. train vectorizer (das dauert kurz)...")
#cv = CountVectorizer(max_features=5000, stop_words='english')
#count_matrix = cv.fit_transform(df_clean['combined_features'])

print("5. store .pkl files...")

if not os.path.exists(ML_DIR):
    os.makedirs(ML_DIR)
    print(f"  Created directory: {ML_DIR}")

#pickle.dump(df_clean, open(os.path.join(ML_DIR, 'movies.pkl'), 'wb'))
#pickle.dump(count_matrix, open(os.path.join(ML_DIR, 'similarity_matrix.pkl'), 'wb'))
#pickle.dump(cv, open(os.path.join(ML_DIR, 'vectorizer.pkl'), 'wb'))

pickle.dump(df, open(os.path.join(ML_DIR, 'movies.pkl'), 'wb'))

# Embeddings speichern (Die "Intelligenz" des Modells)
pickle.dump(embeddings, open(os.path.join(ML_DIR, 'movie_embeddings.pkl'), 'wb'))

print(f"DONE. Saved SBERT models to {ML_DIR}")
