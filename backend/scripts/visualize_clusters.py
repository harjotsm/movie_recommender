import pickle
import os
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.manifold import TSNE

# Pfade
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML_DIR = os.path.join(BASE_DIR, 'api', 'ml')

def plot_clusters():
    print(" load Daten...")
    try:
        movies = pickle.load(open(os.path.join(ML_DIR, 'movies.pkl'), 'rb'))
        embeddings = pickle.load(open(os.path.join(ML_DIR, 'movie_embeddings.pkl'), 'rb'))
    except FileNotFoundError:
        print("firstly run build_sbert_model.py!")
        return

    # only take first 1000 movies for plotting, else plot will be too big and slow
    limit = 1000
    subset_embeddings = embeddings[:limit]
    subset_movies = movies.iloc[:limit].copy()

    # main-genre for all movies
    def get_main_genre(genre_str):
        if not genre_str: return "Unknown"
        return genre_str.split(" ")[0] # Das erste Wort ist meist das Hauptgenre

    subset_movies['main_genre'] = subset_movies['genres_str'].apply(get_main_genre)

    print("2. calc 2D-Projection (t-SNE)...")
    # t-SNE reduces 384 dimension to 2
    tsne = TSNE(n_components=2, random_state=42, perplexity=30, init='pca', learning_rate='auto')
    vis_dims = tsne.fit_transform(subset_embeddings)

    x = [x for x,y in vis_dims]
    y = [y for x,y in vis_dims]

    plt.figure(figsize=(16, 10))
    sns.scatterplot(x=x, y=y, hue=subset_movies['main_genre'], palette="tab10", s=60, alpha=0.8)

    plt.title("SBERT Movie Embeddings", fontsize=20)
    plt.xlabel("Semantic dimension 1")
    plt.ylabel("Semantic dimension 2")
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_clusters()