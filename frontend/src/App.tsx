import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import { Movie, AppOptions, UserPreferences } from "./types";

function App() {
  const [options, setOptions] = useState<AppOptions>({ genres: [], moods: [] });
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [hasSearched, setHasSearched] = useState<boolean>(false);
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null);

  const [prefs, setPrefs] = useState<UserPreferences>({
    genre: "",
    mood: "",
    content: "",
    element: "",
  });

  useEffect(() => {
    axios
      .get<AppOptions>("http://127.0.0.1:8000/api/options/")
      .then((response) => {
        setOptions(response.data);
        if (response.data.genres.length > 0) {
          setPrefs((prev) => ({ ...prev, genre: response.data.genres[0] }));
        }
        if (response.data.moods.length > 0) {
          setPrefs((prev) => ({ ...prev, mood: response.data.moods[0] }));
        }
      })
      .catch((error) => console.error("Error fetching options:", error));
  }, []);

  const handleSearch = () => {
    setLoading(true);
    setHasSearched(true);
    setSelectedMovie(null);

    axios
      .post<Movie[]>("http://127.0.0.1:8000/api/recommend/", prefs)
      .then((response) => {
        setMovies(response.data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error searching movies:", error);
        setLoading(false);
      });
  };

  const handleChange = (field: keyof UserPreferences, value: string) => {
    setPrefs({ ...prefs, [field]: value });
  };

  return (
    <div className="App">
      <header className="header">
        <h1>🎬 AI Movie Assistant</h1>
        <p>Tell me what you like, and I'll find the perfect match.</p>
      </header>

      <div className="container">
        <div className="wizard-box">
          <div className="wizard-header">
            <h2>Your Preferences</h2>
            <p className="wizard-sub">Customize your search</p>
          </div>

          <div className="form-group">
            <label>Genre</label>
            <select
              value={prefs.genre}
              onChange={(e) => handleChange("genre", e.target.value)}
            >
              {options.genres.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Mood / Vibe</label>
            <select
              value={prefs.mood}
              onChange={(e) => handleChange("mood", e.target.value)}
            >
              {options.moods.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Content / Topic</label>
            <input
              type="text"
              value={prefs.content}
              onChange={(e) => handleChange("content", e.target.value)}
              placeholder="e.g. Space Travel, Mafia, High School..."
            />
            <small className="input-hint">
              What is the movie about? Use single keywords.
            </small>
          </div>

          <div className="form-group">
            <label>Must-Have Element</label>
            <input
              type="text"
              value={prefs.element}
              onChange={(e) => handleChange("element", e.target.value)}
              placeholder="e.g. Robot, Dragon, Plot Twist, 1980s..."
            />
            <small className="input-hint">
              Is there a specific detail you are looking for?
            </small>
          </div>

          <button onClick={handleSearch} disabled={loading}>
            {loading ? "Analyzing Database..." : "Discover Movies ✨"}
          </button>
        </div>

        <div className="results-section">
          {movies.length > 0 ? (
            <div className="results-grid">
              {movies.map((movie) => (
                <div key={movie.id} className="movie-card">
                  <div className="card-header">
                    {/* Jahr im Titel anzeigen */}
                    <h3>
                      {movie.title}{" "}
                      <span className="year-badge">({movie.year})</span>
                    </h3>
                    <span className="score-badge">
                      {Math.round(movie.score * 100)}% Match
                    </span>
                  </div>

                  {/* CSS-Klasse line-clamp sorgt für das "..." nach 3 Zeilen */}
                  <p className="movie-overview line-clamp">{movie.overview}</p>

                  {/* Öffnet das Modal */}
                  <button
                    className="more-btn"
                    onClick={() => setSelectedMovie(movie)}
                  >
                    Read more
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              {hasSearched && !loading ? (
                <p>No movies found. Try different keywords!</p>
              ) : (
                <div className="placeholder-text">
                  <span style={{ fontSize: "3rem" }}>🍿</span>
                  <p>Your recommendations will appear here.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {selectedMovie && (
        <div className="modal-overlay" onClick={() => setSelectedMovie(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedMovie.title}</h2>
              <button
                className="close-btn"
                onClick={() => setSelectedMovie(null)}
              >
                ×
              </button>
            </div>

            <div className="modal-body">
              <div className="modal-meta">
                <div className="meta-item">📅 {selectedMovie.year}</div>
                <div className="meta-item">⏱ {selectedMovie.runtime} min</div>
                <div className="meta-item">⭐ {selectedMovie.rating}/10</div>
              </div>

              <div className="modal-tags">
                <span className="tag-match">
                  {Math.round(selectedMovie.score * 100)}% Match
                </span>
                {selectedMovie.genres
                  .split(" ")
                  .slice(0, 3)
                  .map((g, i) => (
                    <span key={i} className="tag-genre">
                      {g}
                    </span>
                  ))}
              </div>

              <h4>Plot Summary</h4>
              <p className="full-text">{selectedMovie.overview}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
