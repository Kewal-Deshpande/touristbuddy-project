// ReportCrime.jsx
import React, { useState } from "react";
import "./ReportCrime.css";

const ReportCrime = () => {
  const [formData, setFormData] = useState({
    name: "",
    contact: "",
    location: "",
    crimeType: "",
    description: "",
    evidence: null,
  });

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: files ? files[0] : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Save to localStorage (optional)
    const existingReports = JSON.parse(localStorage.getItem("crimeReports")) || [];
    existingReports.push(formData);
    localStorage.setItem("crimeReports", JSON.stringify(existingReports));

    alert("Crime report submitted successfully!");

    // Reset form fields
    setFormData({
      name: "",
      contact: "",
      location: "",
      crimeType: "",
      description: "",
      evidence: null,
    });

    // Reset file input manually
    e.target.reset();
  };

  return (
    <div className="report-crime-container">
      <h2>Report a Crime</h2>
      <form onSubmit={handleSubmit}>
        {/* Name */}
        <div className="form-group">
          <label>Name (Optional)</label>
          <input
            type="text"
            name="name"
            placeholder="Your name"
            value={formData.name}
            onChange={handleChange}
          />
        </div>

        {/* Contact */}
        <div className="form-group">
          <label>Contact</label>
          <input
            type="text"
            name="contact"
            placeholder="Phone or Email"
            value={formData.contact}
            onChange={handleChange}
            required
          />
        </div>

        {/* Location */}
        <div className="form-group">
          <label>Location</label>
          <input
            type="text"
            name="location"
            placeholder="Crime location"
            value={formData.location}
            onChange={handleChange}
            required
          />
        </div>

        {/* Crime Type */}
        <div className="form-group">
          <label>Crime Type</label>
          <select
            name="crimeType"
            value={formData.crimeType}
            onChange={handleChange}
            required
          >
            <option value="">Select</option>
            <option value="theft">Theft</option>
            <option value="harassment">Harassment</option>
            <option value="violence">Violence</option>
            <option value="fraud">Fraud</option>
            <option value="other">Other</option>
          </select>
        </div>

        {/* Description */}
        <div className="form-group">
          <label>Description</label>
          <textarea
            name="description"
            placeholder="Describe the incident"
            value={formData.description}
            onChange={handleChange}
            required
            rows="4"
          />
        </div>

        {/* Evidence */}
        <div className="form-group">
          <label>Upload Evidence (Optional)</label>
          <input
            type="file"
            name="evidence"
            accept="image/*,video/*"
            onChange={handleChange}
          />
        </div>

        {/* Submit */}
        <div className="form-group">
          <button type="submit">Submit Report</button>
        </div>
      </form>
    </div>
  );
};

export default ReportCrime;
