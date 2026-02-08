import React, { useState } from "react";
import "./RouteSelection.css";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";

function RouteSelection({ routes, map, setPolylines }) {
  const [selectedRouteIndex, setSelectedRouteIndex] = useState(null);
  const [watchId, setWatchId] = useState(null);
  const [userMarker, setUserMarker] = useState(null);
  const [steps, setSteps] = useState([]);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  const handleRadioChange = (event) => {
    const index = parseInt(event.target.value);
    setSelectedRouteIndex(index);
  
    if (!map) return;
  
    // Clear existing polylines
    setPolylines((prevPolylines) => {
      prevPolylines.forEach((polyline) => polyline.setMap(null));
      return [];
    });
  
    const newPolylines = [];
  
    // First, draw all unselected routes in gray
    routes.forEach((route, i) => {
      if (i === index) return; // Skip selected route
  
      const pathCoords = route.coordinates.map((coord) => ({
        lat: parseFloat(coord[0]),
        lng: parseFloat(coord[1]),
      }));
  
      const polyline = new window.google.maps.Polyline({
        path: pathCoords,
        geodesic: true,
        strokeColor: "gray",
        strokeOpacity: 1.0,
        strokeWeight: 4,
        zIndex: 1,
      });
  
      polyline.setMap(map);
      newPolylines.push(polyline);
    });
  
    // Now draw selected route in blue (on top)
    const selectedRoute = routes[index];
    const selectedPathCoords = selectedRoute.coordinates.map((coord) => ({
      lat: parseFloat(coord[0]),
      lng: parseFloat(coord[1]),
    }));
  
    const selectedPolyline = new window.google.maps.Polyline({
      path: selectedPathCoords,
      geodesic: true,
      strokeColor: "blue",
      strokeOpacity: 1.0,
      strokeWeight: 5,
      zIndex: 2, // ensures it's above gray
    });
  
    selectedPolyline.setMap(map);
    newPolylines.push(selectedPolyline);
  
    setPolylines(newPolylines);
  };
  
  
  
  

  const handleSelect = () => {
    if (selectedRouteIndex === null || !map) {
      alert("Please select a route");
      return;
    }
  
    const selectedRoute = routes[selectedRouteIndex];
  
    // Clear all existing polylines
    setPolylines((prevPolylines) => {
      prevPolylines.forEach((polyline) => polyline.setMap(null));
      return [];
    });
  
    const pathCoords = selectedRoute.coordinates.map((coord) => ({
      lat: parseFloat(coord[0]),
      lng: parseFloat(coord[1]),
    }));
  
    const newPolyline = new window.google.maps.Polyline({
      path: pathCoords,
      geodesic: true,
      strokeColor: "blue",
      strokeOpacity: 1.0,
      strokeWeight: 5,
    });
  
    newPolyline.setMap(map);
    setPolylines([newPolyline]);
  
    // Save steps
    if (selectedRoute.steps) {
      setSteps(selectedRoute.steps);
      setCurrentStepIndex(0);
    }
  
    console.log("Selected Route:", selectedRoute);
  };
  

  const updateCurrentStep = (lat, lng) => {
    const threshold = 0.0005; // Roughly 50m

    for (let i = currentStepIndex; i < steps.length; i++) {
      const stepLat = steps[i].location.lat;
      const stepLng = steps[i].location.lng;

      const distance = Math.sqrt(
        Math.pow(stepLat - lat, 2) + Math.pow(stepLng - lng, 2)
      );

      if (distance < threshold) {
        setCurrentStepIndex(i + 1);
        speak(steps[i].instruction);
        break;
      }
    }
  };

  const handleStartRoute = () => {
    if (!map || selectedRouteIndex === null) return;

    const id = navigator.geolocation.watchPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        const newLatLng = new window.google.maps.LatLng(latitude, longitude);

        // Update or create marker
        if (userMarker) {
          userMarker.setPosition(newLatLng);
        } else {
          const marker = new window.google.maps.Marker({
            position: newLatLng,
            map,
            title: "Your Location",
            icon: {
              path: window.google.maps.SymbolPath.CIRCLE,
              scale: 8,
              fillColor: "#4285F4",
              fillOpacity: 1,
              strokeWeight: 2,
              strokeColor: "#ffffff",
            },
          });
          setUserMarker(marker);
        }

        // Center the map on user
        map.setCenter(newLatLng);

        // Update step
        updateCurrentStep(latitude, longitude);
      },
      (error) => {
        console.error("Error watching location:", error);
        if (error.code === 3) {
          alert("Location timeout. Try moving to a better spot or check permissions.");
        }
      },
      {
        enableHighAccuracy: true,
        maximumAge: 0,
        timeout: 5000,
      }
    );

    setWatchId(id);
  };

  const handleStopRoute = () => {
    if (watchId) {
      navigator.geolocation.clearWatch(watchId);
      setWatchId(null);
    }

    if (userMarker) {
      userMarker.setMap(null);
      setUserMarker(null);
    }

    setSteps([]);
    setCurrentStepIndex(0);
  };

  const speak = (text) => {
    console.log(text);

    const utterance = new SpeechSynthesisUtterance();
    utterance.text = text.replace(/<[^>]+>/g, ""); // Remove HTML tags
    utterance.lang = "en-US";
    utterance.pitch = 1;
    utterance.rate = 1;
    utterance.volume = 1;
    speechSynthesis.speak(utterance);
  };

  return (
    <div className="RouteSelection">
      {routes && routes.length > 0 ? (
        <>
          <h2>Select Route</h2>
          <div className="all-routes">
            {routes.map((route, index) => (
              <div key={index} className="route-card">
                <input
                  type="radio"
                  name="route"
                  value={index}
                  onChange={handleRadioChange}
                  checked={selectedRouteIndex === index}
                />
                <div className="route-info">
                  <h3>Route {index + 1}</h3>
                  <p style={{ color: "red" }}>
                    Danger level: {Math.round(route.danger)}
                  </p>
                  <p>Distance: {route.distance}</p>
                  <p>Time: {route.duration}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="btn">
            <Stack spacing={2} direction="row">
              <Button variant="contained" onClick={handleSelect}>
                Select Route
              </Button>
            </Stack>
          </div>
        </>
      ) : (
        <p>No routes found</p>
      )}

      {selectedRouteIndex !== null && (
        <div className="results">
          <p>Selected Route: Route {selectedRouteIndex + 1}</p>
          <Stack spacing={2} direction="row">
            <Button
              variant="outlined"
              color="success"
              onClick={handleStartRoute}
            >
              Start Route
            </Button>
            {watchId && (
              <Button
                variant="outlined"
                color="error"
                onClick={handleStopRoute}
              >
                Stop Route
              </Button>
            )}
          </Stack>

          {steps.length > 0 && currentStepIndex < steps.length && (
            <div className="current-step" style={{ marginTop: "15px" }}>
              <h4>Next Step:</h4>
              <p
                dangerouslySetInnerHTML={{
                  __html: steps[currentStepIndex].instruction,
                }}
              />
              <p>Distance: {steps[currentStepIndex].distance}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default RouteSelection;
