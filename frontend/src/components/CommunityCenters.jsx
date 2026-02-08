import React, { useEffect, useState } from "react";
import {
  GoogleMap,
  Marker,
  useLoadScript
} from "@react-google-maps/api";

import HospitalIcon from "../assets/hospital.png";
import PoliceIcon from "../assets/police-station.png";
import UserIcon from "../assets/pin.png";

const GOOGLE_MAP_API =
  "AIzaSyABXrzOdYntmVFt7vHZPMHEtAnvZLr7N-s";

const mapContainerStyle = {
  width: "100%",
  height: "100vh"
};

function CommunityCenters() {

  const { isLoaded } = useLoadScript({
    googleMapsApiKey: GOOGLE_MAP_API
  });

  const [places, setPlaces] = useState([]);
  const [currentLocation, setCurrentLocation] = useState(null);

  useEffect(() => {

    navigator.geolocation.getCurrentPosition(

      async (position) => {

        const coords = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };

        setCurrentLocation(coords);

        try {

          const response = await fetch(
            "http://127.0.0.1:5000/get-community-centers",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json"
              },
              body: JSON.stringify(coords)
            }
          );

          const data = await response.json();

          if (data.status === "success") {

            const parsed = data.places.map(place => ({
              ...place,
              lat: Number(place.lat),
              lng: Number(place.lng)
            }));

            setPlaces(parsed);

          }

        }

        catch (err) {

          console.error(err);

        }

      },

      (err) => {

        console.error(err);

        alert("Enable location access");

      }

    );

  }, []);

  if (!isLoaded || !currentLocation)
    return <h2>Loading map...</h2>;


  return (

    <GoogleMap
      mapContainerStyle={mapContainerStyle}
      center={currentLocation}
      zoom={14}
    >

      {/* USER MARKER */}

      <Marker
        position={currentLocation}
        icon={{
          url: UserIcon,
          scaledSize: new window.google.maps.Size(40, 40),
          anchor: new window.google.maps.Point(20, 40)
        }}
        title="Your location"
      />


      {/* COMMUNITY CENTERS */}

      {

        places.map((place, index) => {

          const iconUrl =
            place.type === "hospital"
              ? HospitalIcon
              : PoliceIcon;

          return (

            <Marker

              key={index}

              position={{
                lat: place.lat,
                lng: place.lng
              }}

              icon={{
                url: iconUrl,
                scaledSize:
                  new window.google.maps.Size(35, 35),

                anchor:
                  new window.google.maps.Point(17, 35)
              }}

              title={place.name}

            />

          );

        })

      }

    </GoogleMap>

  );

}

export default CommunityCenters;
