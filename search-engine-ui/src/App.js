import React, { useState } from 'react';
import './App.css';
import SearchBar from './components/SearchBar'; // Importation de SearchBar
// Ajouter un hook useState pour gérer l'état de la réponse de l'API
function App() {
  const [answer, setAnswer] = useState(''); // Pour stocker la réponse de l'API

  // Fonction pour gérer la recherche et appeler l'API
  const handleSearch = async (query) => {
    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: query }),
      });

      if (response.ok) {
        const data = await response.json();
        setAnswer(data.answer); // Mettre à jour l'état avec la réponse
      } else {
        setAnswer('Error: Could not fetch answer'); // En cas d'erreur de l'API
      }
    } catch (error) {
      setAnswer('Error: Failed to fetch answer');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="logo-container">
          <img src="logo.png" alt="Logo" className="logo" />
          <h1>Your SE</h1>
        </div>
        <div className="search-container">
          {/* Utilisation de SearchBar et gestion de la recherche */}
          <SearchBar onSearch={handleSearch} />
        </div>
        {/* Affichage de la réponse de l'API */}
        <div className="answer-container">
          <p>{answer}</p>
        </div>
        <p className="description">
          Welcome to your SE, the free, open-source and non-profit search engine.
          You can start searching by using the search bar above!
        </p>
        <div className="buttons-container">
          <button className="action-button">Google Drive</button>
          <button className="action-button">My Docs</button>
        </div>
      </header>
    </div>
  );
}

export default App;
