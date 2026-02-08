import React, { useEffect, useState, useRef } from 'react';

function MyMap() {
  const [map, setMap] = useState(null);
  const [markers, setMarkers] = useState([]);
  const mapRef = useRef(null);


  useEffect(() => {
    // Load the Google Maps API (replace with your actual loading method)
    // This is highly dependent on how you're loading the API in your project

    if (typeof window !== 'undefined' && window.google) {
        // Check for Google Maps API availability
      const initMap = () => {
        if (mapRef.current) {
          const newMap = new window.google.maps.Map(mapRef.current, {
            center: { lat: 37.7749, lng: -122.4194 }, // Default center
            zoom: 12,
          });
          setMap(newMap);
        }
      };

      if (window.google && window.google.maps) {
        initMap();
      } else {
        //Handle API loading failure
        console.error("Google Maps API not loaded")
      }
    }


    //Cleanup function for removing event listeners and clearing map if needed
    return () => {
      if (map) {
        //Optionally clear markers and other map elements if needed

        markers.forEach(marker => marker.setMap(null));
      }
    };
  }, []);

  useEffect(() => {
    // Add markers when the markers state changes
    if (map && markers.length > 0) {
      markers.forEach(marker => {
        marker.setMap(map);
      });
    }
  }, [map, markers]);

  const addMarker = (lat, lng) => {
    const newMarker = new window.google.maps.Marker({
      position: { lat: lat, lng: lng },
      map: map,
      title: 'New Marker',
    });

    setMarkers([...markers, newMarker]);
  };


  return (
    <div>
      <div ref={mapRef} style={{ height: '500px', width: '100%' }} />
      <button onClick={() => addMarker(37.78, -122.42)}>Add Marker</button> {/*Example usage*/}
    </div>
  );
}

export default MyMap;
