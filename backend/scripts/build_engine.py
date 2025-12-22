import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from ast import literal_eval

print("1. load dataset...")
try:
    df = pd.read_csv('/Users/harjot/Desktop/movie_recommender/backend/scripts/tmdb_5000_movies.csv')
except FileNotFoundError:
    print("Error, please ensure the dataset 'tmdb_5000_movies.csv' is in the correct path.")
    exit()

features = ['keywords', 'genres', 'overview', 'title', 'release_date', 'vote_average', 'runtime']
df_clean = df[features].copy()

print("2. Cleaned Data")


def parse_features(x):
    try:
        data = literal_eval(x)
        if isinstance(data, list):
            return " ".join([i['name'] for i in data])
        return ""
    except:
        return ""


df_clean['genres'] = df_clean['genres'].apply(parse_features)
df_clean['keywords'] = df_clean['keywords'].apply(parse_features)
df_clean['overview'] = df_clean['overview'].fillna('')
df_clean['release_date'] = df_clean['release_date'].fillna('')
df_clean['runtime'] = df_clean['runtime'].fillna(0)
df_clean['vote_average'] = df_clean['vote_average'].fillna(0)
print("   Example genre (cleaned):", df_clean['genres'].iloc[0])


def combine_features(row):
    try:
        return row['keywords'] + " " + row['genres'] + " " + row['overview']
    except:
        print("Error:", row)
        return ""


print("3. creating combined features...")
df_clean['combined_features'] = df_clean.apply(combine_features, axis=1)

print("4. train vectorizer (das dauert kurz)...")
cv = CountVectorizer(max_features=5000, stop_words='english')
count_matrix = cv.fit_transform(df_clean['combined_features'])

print("5. store .pkl files...")
pickle.dump(df_clean, open('../api/ml/movies.pkl', 'wb'))
pickle.dump(count_matrix, open('../api/ml/similarity_matrix.pkl', 'wb'))
pickle.dump(cv, open('../api/ml/vectorizer.pkl', 'wb'))
print("DONE.")
