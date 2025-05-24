import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Itinerary = ({itinerary_key}) => {
  const [allData, setAllData] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch("http://localhost:3000/itinerary-data");
        const data = await res.json();
        const item = Array.isArray(data) ? data[itinerary_key] : null;
        setAllData(item ? [item] : []);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
  
    fetchData();
  }, [itinerary_key]);

  
  const renderPreview = (obj) => {
    if (!obj) return null;
    const entries = Object.entries(obj).slice(0, 4);
    return entries.map(([key, value]) => {
      let displayValue;
      if (typeof value === "object" && value !== null) {
        const strVal = JSON.stringify(value);
        displayValue = strVal.length > 40 ? strVal.slice(0, 40) + "..." : strVal;
      } else {
        const strVal = String(value);
        displayValue = strVal.length > 40 ? strVal.slice(0, 40) + "..." : strVal;
      }
      return (
        <div key={key} className="mb-1">
          <strong className="capitalize text-indigo-700">{key}:</strong> {displayValue}
        </div>
      );
    });
  };

  return (
    <div className="p-4 max-w-3xl mx-auto">
      <button
    onClick={() => navigate(-1)}
    className="text-indigo-600 hover:underline mb-6 block"
  >
    ← Back To Previews
  </button>

  <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
    <h1 className="text-3xl font-bold text-gray-800 mb-6">Trip Details</h1>
      {allData.length === 0 ? (
        <p className="italic text-gray-500">No data available.</p>
      ) : (
          allData.map((item, index) => (
            <div
              key={index}
              className="cursor-pointer mb-4 hover:bg-gray-50 p-2 rounded transition"
            >
              {renderPreview(item)}
            </div>
          ))
      )}
    </div>
  </div>

  );
};

export default Itinerary;