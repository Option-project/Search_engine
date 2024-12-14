import React, { useState } from 'react';

function SearchBar({ onSearch }) {
  const [query, setQuery] = useState(''); // État pour le champ de recherche

  const handleSearch = () => {
    onSearch(query); // Appelle la fonction parent pour traiter la recherche
    setQuery(''); // Réinitialise le champ de recherche
  };

  return (
    <div className="searchBar">
      <input
        type="text"
        placeholder="Ask Anything..." // Placeholder pour guider l'utilisateur
        value={query}
        onChange={(e) => setQuery(e.target.value)} // Met à jour l'état à chaque frappe
      />
      <button onClick={handleSearch}>Search</button>
    </div>
  );
}

export default SearchBar;
