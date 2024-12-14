import React from 'react'

function Navbar() {
    return (
      <div className="navbar">
        <div className="leftSide">
          <h1>Your AI Search Engine</h1>
        </div>
        <div className="rightSide">
          <a href="#Search History">Search History</a>
          <a href="#Your Profile">Your Profile</a>
          <a href="#contact">Contact</a>
        </div>
      </div>
    );
  }
  
  export default Navbar;
