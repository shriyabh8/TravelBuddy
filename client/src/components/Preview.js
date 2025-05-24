import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const JsonFromServer = () => {
  const [allData, setAllData] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch("http://localhost:3000/itinerary-data");
        const data = await res.json();
        const lastItem = Array.isArray(data) ? data[data.length - 1] : null;
        setAllData(lastItem ? [lastItem] : []);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
  
    fetchData();
  }, []);

  
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
      {allData.length === 0 ? (
        <p className="italic text-gray-500">No data available.</p>
      ) : (
        <div className="bg-white shadow-md rounded-lg p-6 border border-gray-200">
          {allData.map((item, index) => (
            <div
              key={index}
              onClick={() => navigate(`/itinerary/${index}`)}
              className="cursor-pointer mb-4 hover:bg-gray-50 p-2 rounded transition"
            >
              <div className="text-sm text-gray-500 mb-1">Item #{index + 1}</div>
              {renderPreview(item)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default JsonFromServer;