import React, { useState, useEffect } from "react";
import PlaceSuggestionInput from "./PlaceSuggestionInput";
import SourceIcon from "../assets/pin.png";
import AlterIcon from "../assets/alter.png";
import DestIcon from "../assets/flag.png";
import axios from "axios";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import { ThreeDot } from "react-loading-indicators";
import RouteSelection from "./RouteSelection";
import "./Safe.css";

function Safe() {

  // USERNAME STATE
  const [username, setUsername] = useState("");

  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [map, setMap] = useState(null);
  const [polylines, setPolylines] = useState([]);
  const [markers, setMarkers] = useState([]);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [clicked, setClicked] = useState(false);
  const [routes, setRoutes] = useState(null);
  const [activeInput, setActiveInput] = useState(null);

  // ASK NAME EVERY VISIT
  useEffect(() => {

    let name = prompt("Enter your name:");

    if (!name || name.trim() === "")
      name = "User";

    localStorage.setItem("username", name);

    setUsername(name);

  }, []);


  // INITIALIZE MAP
  useEffect(() => {

    if (window.google) {

      const mapObj = new window.google.maps.Map(

        document.getElementById("map"),

        {
          center: { lat: 18.5204, lng: 73.8567 },
          zoom: 12,
        }

      );

      setMap(mapObj);

    }

  }, []);


  const handleAlter = () => {

    let temp = source;
    setSource(destination);
    setDestination(temp);

  };


  const handleCurrentLocation = () => {

    if (activeInput === "SOURCE")
      setSource("CURRENT LOCATION");

    else if (activeInput === "DESTINATION")
      setDestination("CURRENT LOCATION");

  };


  const fetchCurrentLocation = () => {

    return new Promise((resolve, reject) => {

      navigator.geolocation.getCurrentPosition(

        (position) => {

          const coords = {

            lat: position.coords.latitude,
            lng: position.coords.longitude,

          };

          setCurrentLocation(coords);

          resolve(coords);

        },

        reject,

        {
          enableHighAccuracy: true,
          timeout: 15000,
          maximumAge: 0,
        }

      );

    });

  };


  // SOS FUNCTION
  const sendSOS = async () => {

    try {

      const coords = await fetchCurrentLocation();

      const name =
        localStorage.getItem("username") || username;

      await axios.post(
        "http://127.0.0.1:5000/send-sos-message",
        {
          lat: coords.lat,
          lng: coords.lng,
          username: name,
        }
      );

      alert("WhatsApp SOS sent successfully!");

    }

    catch (err) {

      console.error(err);

    }

  };


  const geocodeAddress = (geocoder, address) => {

    return new Promise((resolve, reject) => {

      geocoder.geocode({ address }, (results, status) => {

        if (status === "OK" && results[0]) {

          resolve({

            lat: results[0].geometry.location.lat(),
            lng: results[0].geometry.location.lng(),

          });

        }

        else reject(status);

      });

    });

  };


  // SAFE ROUTES FUNCTION (ORIGINAL RESTORED)
  const getSafePaths = async (source, destination) => {

    try {

      setRoutes(null);

      const geocoder =
        new window.google.maps.Geocoder();

      let sourceCoords, destCoords;

      if (source === "CURRENT LOCATION")
        sourceCoords = await fetchCurrentLocation();

      else
        sourceCoords =
          await geocodeAddress(geocoder, source);

      if (destination === "CURRENT LOCATION")
        destCoords = await fetchCurrentLocation();

      else
        destCoords =
          await geocodeAddress(geocoder, destination);

      const response = await axios.post(

        "http://127.0.0.1:5000/get-safe-paths",

        {
          source_lat: sourceCoords.lat,
          source_lng: sourceCoords.lng,
          dest_lat: destCoords.lat,
          dest_lng: destCoords.lng,
        }

      );

      if (response.data.routes && map) {

        setRoutes(response.data.routes);

        polylines.forEach(polyline =>
          polyline.setMap(null)
        );

        markers.forEach(marker =>
          marker.setMap(null)
        );

        const newPolylines = [];
        const newMarkers = [];

        const bounds =
          new window.google.maps.LatLngBounds();

        const dangerLevels =
          response.data.routes.map(
            (r) => r.danger
          );

        const minDanger =
          Math.min(...dangerLevels);

        const maxDanger =
          Math.max(...dangerLevels);

        response.data.routes.forEach(route => {

          const pathCoords =
            route.coordinates.map(([lat, lng]) => {

              const coord = {
                lat: parseFloat(lat),
                lng: parseFloat(lng),
              };

              bounds.extend(coord);

              return coord;

            });

          let strokeColor = "blue";

          if (route.danger === maxDanger)
            strokeColor = "red";

          else if (route.danger === minDanger)
            strokeColor = "green";

          const polyline =
            new window.google.maps.Polyline({

              path: pathCoords,
              geodesic: true,
              strokeColor,
              strokeOpacity: 1,
              strokeWeight: 5,

            });

          polyline.setMap(map);

          newPolylines.push(polyline);

        });

        const firstRoute =
          response.data.routes[0];

        const sourceMarker =
          new window.google.maps.Marker({

            position: {
              lat: parseFloat(firstRoute.coordinates[0][0]),
              lng: parseFloat(firstRoute.coordinates[0][1]),
            },

            map,
            label: "S",

          });

        const destMarker =
          new window.google.maps.Marker({

            position: {
              lat: parseFloat(firstRoute.coordinates.at(-1)[0]),
              lng: parseFloat(firstRoute.coordinates.at(-1)[1]),
            },

            map,
            label: "D",

          });

        newMarkers.push(sourceMarker, destMarker);

        map.fitBounds(bounds);

        setPolylines(newPolylines);
        setMarkers(newMarkers);

      }

    }

    catch (err) {

      console.error(err);

    }

  };


  const handleSearch = async () => {

    if (!source || !destination)
      return alert("Enter locations");

    setClicked(true);

    await getSafePaths(source, destination);

    setClicked(false);

  };


  return (

    <div className="home">

      <div className="input_section">

        {/* GREETING */}

        <h2 style={{
          marginBottom: "10px",
          color: "#333"
        }}>
          Welcome, {username}
        </h2>


        <div className="input_row">

          <div className="input_field">

            <img src={SourceIcon} alt="" />

            <PlaceSuggestionInput
              value={source}
              onLocationSelect={setSource}
              placeholder="Enter Source"
              onFocus={() =>
                setActiveInput("SOURCE")}
              onBlur={() =>
                setActiveInput(null)}
            />

          </div>


          <div
            className="alter_icon"
            onClick={handleAlter}
          >
            <img src={AlterIcon} alt="" />
          </div>


          <div className="input_field">

            <img src={DestIcon} alt="" />

            <PlaceSuggestionInput
              value={destination}
              onLocationSelect={setDestination}
              placeholder="Enter Destination"
              onFocus={() =>
                setActiveInput("DESTINATION")}
              onBlur={() =>
                setActiveInput(null)}
            />

          </div>

        </div>


        <div className="btn_section">

          {

            clicked ?

            <ThreeDot />

            :

            <>

              {

                activeInput &&

                <Button
                  onMouseDown={handleCurrentLocation}
                >
                  Use Current Location
                </Button>

              }


              <Button onClick={handleSearch}>
                Find Safe Route
              </Button>

            </>

          }

        </div>


        <div className="sos_section">

          <Stack>

            <Button
              variant="contained"
              color="error"
              onClick={sendSOS}
            >
              SOS
            </Button>

          </Stack>

        </div>

      </div>


      <div className="map_section">
        <div id="map"></div>
      </div>


      {

        routes &&

        <RouteSelection
          routes={routes}
          map={map}
          setPolylines={setPolylines}
        />

      }

    </div>

  );

}

export default Safe;
