import React from "react";
import { NavLink } from "react-router-dom"; // Import NavLink for active link feature
import "./Navbar.css";
import Logo from "../assets/TouristBuddy_Logo.png";
import Home from "../assets/home.png";
import Menu from "../assets/menu.png";
import { useState } from "react";

function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };
  return (
    <div className="Navbar">
      <nav className={isOpen ? "nav_open" : "nav_closed"}>
        <div className="left">
        <img src={Logo} alt="Logo" style={{ width: "180px", height: "100px" }} />

        </div>
        <div className="right">
          <button className="menu-btn" onClick={toggleMenu}>
            <img src={Menu}></img>
          </button>

          <li className={isOpen ? "list_open" : "list_closed"}>
            <NavLink to="/" activeClassName="active">
              <img src={Home}></img>
              Home
            </NavLink>
          </li>
          <li className={isOpen ? "list_open" : "list_closed"}>
            <NavLink to="/community-centers" activeClassName="active">
              Community Centers
            </NavLink>
          </li>
          <li className={isOpen ? "list_open" : "list_closed"}>
            <NavLink to="/crime-locations" activeClassName="active">
              Crime Locations
            </NavLink>
          </li>
          <li className={isOpen ? "list_open" : "list_closed"}>
            <NavLink to="/report-crime" activeClassName="active">
              Report Crime
            </NavLink>
          </li>
        </div>
      </nav>
    </div>
  );
}

export default Navbar;
