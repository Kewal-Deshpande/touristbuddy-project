import "./Home.css";
import React, { useState, useEffect } from "react";
import PlaceSuggestionInput from "./PlaceSuggestionInput";
import SourceIcon from "../assets/pin.png";
import AlterIcon from "../assets/alter.png";
import DestIcon from "../assets/flag.png";
import axios from "axios";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
const GOOGLE_MAP_API = "AIzaSyABXrzOdYntmVFt7vHZPMHEtAnvZLr7N-s";

function Home() {
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [map, setMap] = useState(null);
  const [curLocation, setCurLocation] = useState(null);
  const [nearestCommunityCenter, setNearestCommunityCenter] = useState(null);
  const directionsRenderer = null;
  const [polyline, setPolyline] = useState(null);

  useEffect(() => {
    if (window.google) {
      setMap(
        new window.google.maps.Map(document.getElementById("map"), {
          center: { lat: 18.5204, lng: 73.8567 }, // Default center (Pune)
          zoom: 12,
        })
      );
    }
  }, []);

  const handleFindRoute = async () => {
    if (!source || !destination) {
      alert("Please enter source and destination coordinates.");
      return;
    }

    const srcCoords = await getCoordinates(source);
    const destCoords = await getCoordinates(destination);

    try {
      const response = await axios.post("http://127.0.0.1:5000/safe-route", {
        source: srcCoords,
        destination: destCoords,
      });

      if (response.data.safe_routes.length > 0) {
        drawRoute(response.data.safe_routes[0]);
      } else {
        alert("No safe route found!");
      }
    } catch (error) {
      console.error("Error fetching safe route:", error);
    }
  };

  const drawRoute = (route) => {
    const directionsService = new window.google.maps.DirectionsService();
    const directionsRenderer = new window.google.maps.DirectionsRenderer({
      map,
    });

    const path = route.overview_polyline.points;
    directionsService.route(
      {
        origin: source,
        destination: destination,
        travelMode: window.google.maps.TravelMode.DRIVING,
        provideRouteAlternatives: true,
      },
      (result, status) => {
        if (status === "OK") {
          directionsRenderer.setDirections(result);
        } else {
          console.error("Directions request failed:", status);
        }
      }
    );
  };

  async function getCoordinates(address) {
    address = address.split(", ").join("+");
    address = address.split(" ").join("+");
    const response = await fetch(
      `https://maps.googleapis.com/maps/api/geocode/json?address=${address}&key=${GOOGLE_MAP_API}`
    );
    const data = await response.json();

    const { lat, lng } = data.results[0].geometry.location;
    const res = {
      latitude: lat,
      longitude: lng,
    };

    return res;
  }

  const handleAlter = () => {
    let temp = source;
    setSource(destination);
    setDestination(temp);
  };

  const getCurrentLocation = async () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
        },
        (error) => {
          console.error("error: ", error);
        }
      );
    } else {
      console.error("Cannot get location of your device");
    }
  };


  const showNearestCommunityCenter = async () => {

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          setCurLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          console.error("error: no cur location:  ", error);
          return;
        }
      );

      console.log("cur location", curLocation);
      

      const res = await axios.post(
        "http://127.0.0.1:5000/get-nearest-community-center",
        curLocation
      );
      const response = res.data;
      if (response.error) {
        console.error(response.error);
        return;
      }
      if (response.nearest_community_center === "null") {
        console.error("No nearest community center");
        return;
      }
      let center = response.nearest_community_center;
      console.log("Nearest Center: ", center);

      const srcCoords = {latitude : curLocation.lat,longitude : curLocation.lng};
      const destCoords = {
        latitude: center.latitude,
        longitude: center.longitude,
      };

      console.log(`${srcCoords.latitude} ${srcCoords.longitude}`);
      console.log(`${destCoords.latitude} ${destCoords.longitude}`);

      try {
        const response = await axios.post("http://127.0.0.1:5000/safe-route", {
          source: srcCoords,
          destination: destCoords,
        });
        console.log("route: " , response.data.safe_routes);

        if (response.data.safe_routes.length > 0) {
          const route = response.data.safe_routes[0];
          const directionsService = new window.google.maps.DirectionsService();
          const directionsRenderer = new window.google.maps.DirectionsRenderer({
            map,
          });

          const path = route.overview_polyline.points;
          directionsService.route(
            {
              origin: curLocation,
              destination: {
                lat : destCoords.latitude, lng : destCoords.longitude
              },
              travelMode: window.google.maps.TravelMode.DRIVING,
              provideRouteAlternatives: true,
            },
            (result, status) => {
              if (status === "OK") {
                directionsRenderer.setDirections(result);
              } else {
                console.error("Directions request failed:", status);
              }
            }
          );
        } else {
          alert("No safe route found!");
        }
      } catch (error) {
        console.error("Error fetching safe route:", error);
      }
    } else {
      console.error("Cannot get location of your device");
    }
  };

  return (
    <div className="home">
      <div className="input_section">
        <div className="input_row">
          <div className="input_field">
            <img src={SourceIcon} alt="Source Icon" />
            <PlaceSuggestionInput
              value={source}
              onLocationSelect={(place) => setSource(place)}
              inputClass="inputs"
              ulClass="suggestions-dropdown"
              placeholder="Enter Source"
            />
          </div>

          <div className="alter_icon" onClick={handleAlter}>
            <img src={AlterIcon} alt="Switch Icon" />
          </div>

          <div className="input_field">
            <img src={DestIcon} alt="Destination Icon" />
            <PlaceSuggestionInput
              value={destination}
              onLocationSelect={(place) => setDestination(place)}
              inputClass="inputs"
              ulClass="suggestions-dropdown"
              placeholder="Enter Destination"
            />
          </div>
        </div>

        <div className="btn_section">
          <Stack spacing={2} direction="row">
            <Button variant="contained" onClick={handleFindRoute}>
              Find Safe Route
            </Button>
          </Stack>
        </div>

        <div className="sos_section">
          <Stack spacing={2} direction="row">
            <Button
              variant="contained"
              color="error"
              onClick={showNearestCommunityCenter}
            >
              SOS
            </Button>
          </Stack>
        </div>
      </div>
      <div className="map_section">
        <div
          id="map"
          //   style={{ width: "100%", height: "500px", marginTop: "10px" }}
        ></div>
      </div>
    </div>
  );
}

export default Home;
