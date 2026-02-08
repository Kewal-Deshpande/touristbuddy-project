import React, { useState, useEffect } from "react";
import { GoogleMap, LoadScript, Marker } from "@react-google-maps/api";
import crimeIcon from "../assets/warning.png";

const defaultCenter = {
  lat: 18.5004949,
  lng: 73.8529037,
};

const mapContainerStyle = {
  width: "100%",
  height: "100vh",
};

function CrimeLocations() {
  const [crimeData, setCrimeData] = useState([]);

  const fetchCrimeData = async () => {
    try {
      const response = await fetch("http://localhost:5000/get-crime-locations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      const data = await response.json();
      
      if (data.status === "success") {
        console.log(data);
        
        setCrimeData(data.data);
      } else {
        alert("Error fetching crime data");
      }
    } catch (error) {
      console.error("Error fetching crime data:", error);
    }
  };

  useEffect(() => {
    fetchCrimeData();
  }, []);

  return (
    <GoogleMap mapContainerStyle={mapContainerStyle} center={defaultCenter} zoom={13}>
      {crimeData.map((crime, index) => (
        <Marker
          key={index}
          position={{
            lat: parseFloat(crime.Latitude),
            lng: parseFloat(crime.Longitude),
          }}
          icon={{
            url: crimeIcon,
            scaledSize: new window.google.maps.Size(30, 30),
          }}
        />
      ))}
    </GoogleMap>
  );
}

export default CrimeLocations;
