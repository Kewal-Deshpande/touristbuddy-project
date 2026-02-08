import React, { useState, useEffect } from "react";

const PlaceSuggestionInput = ({
  onLocationSelect,
  value,
  inputClass,
  ulClass,
  placeholder,
  onFocus,
  onBlur, 
}) => {
  const [inputValue, setInputValue] = useState(value || "");
  const [suggestions, setSuggestions] = useState([]);
  const [service, setService] = useState(null);
  const [validSelection, setValidSelection] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);

  useEffect(() => {
    setInputValue(value || "");
    setValidSelection(value === "CURRENT LOCATION");
  }, [value]);

  useEffect(() => {
    if (window.google && window.google.maps && window.google.maps.places) {
      setService(new window.google.maps.places.AutocompleteService());
    }
  }, []);

  const handleChange = (e) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    setValidSelection(false);
    setSelectedIndex(-1);

    if (newValue.length > 2 && service) {
      service.getPlacePredictions({ input: newValue }, (predictions, status) => {
        if (status === "OK") {
          setSuggestions(predictions || []);
        } else {
          setSuggestions([]);
        }
      });
    } else {
      setSuggestions([]);
    }
  };

  const handleSelect = (place) => {
    setInputValue(place.description);
    setSuggestions([]);
    setValidSelection(true);
    setSelectedIndex(-1);
    onLocationSelect(place.description);
  };


  const handleKeyDown = (e) => {
    if (e.key === "ArrowDown") {
      setSelectedIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : prev));
    } else if (e.key === "ArrowUp") {
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : prev));
    } else if (e.key === "Enter" && selectedIndex !== -1) {
      handleSelect(suggestions[selectedIndex]);
    }
  };

  return (
    <div style={{ position: "relative" }}>
      <input
        type="text"
        value={inputValue}
        onChange={handleChange}
        onBlur={(e) => {
          setTimeout(() => {
            if (onBlur) onBlur(e);
          }, 100);
        }}
        onFocus={(e) => {
          if (onFocus) onFocus(e); // 👈 Call parent onFocus
        }}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className={inputClass}
        style={{
          padding: "10px",
          fontSize: "16px",
          border: "1px solid #ccc",
          borderRadius: "4px",
          fontFamily: 'poppins'
        }}
      />
      {suggestions.length > 0 && (
        <ul
          className={ulClass}
          style={{
            position: "absolute",
            top: "100%",
            left: 0,
            right: 0,
            background: "white",
            listStyle: "none",
            padding: "10px",
            margin: 0,
            border: "1px solid #ccc",
            borderRadius: "4px",
            zIndex: 1000,
            boxShadow: "0px 4px 6px rgba(0,0,0,0.1)",
          }}
        >
          {suggestions.map((place, index) => (
            <li
              key={place.place_id}
              onClick={() => handleSelect(place)}
              style={{
                padding: "8px",
                cursor: "pointer",
                borderBottom: "1px solid #eee",
                background: index === selectedIndex ? "#f0f0f0" : "white",
              }}
            >
              {place.description}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default PlaceSuggestionInput;
