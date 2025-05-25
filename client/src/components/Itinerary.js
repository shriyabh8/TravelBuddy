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
        const item = data[itinerary_key];
        setAllData(item ? [item] : []);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
  
    fetchData();
  }, [itinerary_key]);

  
  const renderPreview = (obj) => {
    if (!obj) return null;
    return Object.entries(obj).map(([key, value]) => {
      const strVal = String(value);
      return (
        <div key={key} className="mb-1">
          <strong className="capitalize text-indigo-700">{key}:</strong> {strVal}
        </div>
      );
    });
  };

  return (
    <div className="flex flex-col items-center justify-center p-4">

      <div className="w-full flex justify-start">
      <button
    onClick={() => navigate('/previews')}
    className="text-[#383a32] font-open-sanshover:underline hover:text-cyan-700 mb-12 ml-9 pt-2 block"
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
  </div>

  );
};

export default Itinerary;