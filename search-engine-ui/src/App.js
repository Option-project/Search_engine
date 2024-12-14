import React from 'react';
import './App.css';




function App() {
  return (
    <div className="App">
      <header className="App-header">
        <div className="logo-container">
          <img src="logo.png" alt="Logo" className="logo" />
          <h1>Your SE</h1>
        </div>
        <div className="search-container">
          <input
            type="text"
            className="search-input"
            placeholder="Search on your SE..."
          />
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
