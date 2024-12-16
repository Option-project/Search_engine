import React, { useState, useEffect } from 'react';
import './App.css';
import SearchBar from './components/SearchBar'; // Import SearchBar

function App() {
  const [answer, setAnswer] = useState(''); // To store the API response
  const [vectorStoreInitialized, setVectorStoreInitialized] = useState(false); // Track vector store initialization

  // Function to create the vector store on app load
  const initializeVectorStore = async () => {
    try {
      const response = await fetch('http://localhost:8000/vector_store', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        setVectorStoreInitialized(true); // Mark the vector store as initialized
      } else {
        console.error('Error: Could not initialize vector store');
      }
    } catch (error) {
      console.error('Error: Failed to initialize vector store', error);
    }
  };

  // Function to handle search and call the `/query` endpoint
  const handleSearch = async (query) => {
    if (!vectorStoreInitialized) {
      setAnswer('Error: Vector store not initialized');
      return;
    }

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
        setAnswer(data.answer); // Update state with the response
      } else {
        setAnswer('Error: Could not fetch answer'); // API error
      }
    } catch (error) {
      console.error('Error: Failed to fetch answer', error);
      setAnswer('Error: Failed to fetch answer');
    }
  };

  // Initialize the vector store on component mount
  useEffect(() => {
    initializeVectorStore();
  }, []); // Empty dependency array ensures this runs only once

  return (
    <div className="App">
      <header className="App-header">
        <div className="logo-container">
          <img src="logo.png" alt="Logo" className="logo" />
          <h1>Your SE</h1>
        </div>
        <div className="search-container">
          {/* Using SearchBar and handling search */}
          <SearchBar onSearch={handleSearch} />
        </div>
        {/* Displaying the API response */}
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
