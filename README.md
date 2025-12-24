# Movie Recommender

A content-based movie recommendation system that suggests films based on user preferences.

## What It Does

The app asks users about their movie preferences (genre, mood, content themes, and specific elements) and recommends 6 similar movies using content similarity analysis.

## How It Works

**Backend (Django + ML)**
- Processes TMDB 5000 Movies dataset
- Uses CountVectorizer to create feature vectors from movie metadata (genres, keywords, overview)
- Combines user preferences into a query vector
- Computes cosine similarity between user query and all movies
- Returns top 6 matches with relevance scores

**Frontend (React + TypeScript)**
- Interactive wizard-style interface for preference selection
- Displays recommendations with movie details (title, year, rating, runtime, overview)
- Real-time API communication with Django backend

## Tech Stack

- **Backend:** Django, scikit-learn, pandas
- **Frontend:** React, TypeScript, Axios
- **ML:** TF-IDF vectorization, cosine similarity
- **Data:** TMDB 5000 Movies dataset

## Setup

**Option 1: Docker (Recommended)**
```bash
docker-compose up --build
```

**Option 2: Manual Setup**

Backend:
```bash
cd backend
pip install -r requirements.txt # this is only necessary once
python scripts/build_sbert_model.py  # Generate ML model
python manage.py runserver
```

Frontend:
```bash
cd frontend
npm install
npm start
```

Access at `http://localhost:3000`
