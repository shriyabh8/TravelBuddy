import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Preview = ({itinerary_key}) => {
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
        <div key={key} className="mb-12">
          <strong className="capitalize text-[#36a2a4] text-xl font-open-sans mb-6">{key}:</strong> {displayValue}
        </div>
      );
    });
  };

  return (
    <div className="p-4 max-w-3xl mx-auto">
      {allData.length === 0 ? (
        <p className="italic text-gray-500">No data available.</p>
      ) : (
        <div className="bg-white shadow-xl hover:shadow-2xl hover:bg-gray-200 transition duration-200 ease-in-out rounded-2xl p-6 w-80 min-h-[400px] border border-gray-200">
          {allData.map((item, index) => (
            <div
              key={index}
              onClick={() => navigate(`/itinerary/${itinerary_key}`)}
              className="cursor-pointer mb-6 p-2 w-75 min-h-[450px] rounded transition"
            >
              {renderPreview(item)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Preview;