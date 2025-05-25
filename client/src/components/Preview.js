import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Preview = ({itinerary_key}) => {
  const [allData, setAllData] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    console.log("Itinerary key:", itinerary_key);
    const fetchData = async () => {
      try {
        const res = await fetch("http://localhost:5001/generate_itinerary/" + itinerary_key);
        const data = await res.json();
        console.log('Form data received:', data);
        setAllData([data]);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
  
    fetchData();
  }, [itinerary_key]);

  const renderPreview = (obj) => {
    if (!obj) return null;
    // Filter to only show Flights and Hotels
    const entries = Object.entries(obj).filter(([key]) => key === 'Flights' || key === 'Hotels');
    return entries.map(([key, value]) => {
      let displayValue;
      if (typeof value === "object" && value !== null) {
        const strVal = JSON.stringify(value);
        displayValue = strVal.split('\n').map((line, i) => (
          <React.Fragment key={i}>
            {line}
            {i < strVal.split('\n').length - 1 && <br />}
          </React.Fragment>
        ));
      } else {
        const strVal = String(value);
        displayValue = strVal.split('\n').map((line, i) => (
          <React.Fragment key={i}>
            {line}
            {i < strVal.split('\n').length - 1 && <br />}
          </React.Fragment>
        ));
      }
      return (
        <div key={key} className="mb-12">
          <strong className="capitalize text-[#36a2a4] text-xl font-open-sans mb-6">{key}:</strong>{' '}
          <span className="whitespace-pre-line">{displayValue}</span>
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