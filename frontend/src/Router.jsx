import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import ReportCrime from "./components/ReportCrime";
import CrimeLocations from "./components/CrimeLocations";
import CommunityCenters from "./components/CommunityCenters";
import Safe from "./components/Safe";
import Home from "./components/Home";
function AppRouter() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/report-crime" element={<ReportCrime /> } />
        <Route path="/crime-locations" element={<CrimeLocations />}></Route>
        <Route path="/community-centers" element={<CommunityCenters />}></Route>
        <Route path="/" element={<Safe />}></Route>
      </Routes>
    </Router>
  );
}

export default AppRouter;
