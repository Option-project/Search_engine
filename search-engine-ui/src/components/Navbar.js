import React from 'react'


function Navbar() {
    return (
      <div className="navbar">
        {/* Section gauche avec logo et texte */}
        <div className="leftSide">
          <img src="logo1.png" alt="Logo1" className="navbar-logo1" /> 
          <h1>Your SE</h1>
        </div>

        {/* Section droite avec les liens */}
        <div className="rightSide">
          <a href="#Search History">Search History</a>
          <a href="#Your Profile">Your Profile</a>
          <a href="#contact">Contact</a>
        </div>
      </div>
    );
}

export default Navbar;