// // function ItineraryPreview() {
    
// //     return (
// //       <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4 font-sans">
// //         <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
// //           <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
// //             Information Display
// //           </h2>
// //             <div className="mt-4 text-center text-gray-600 text-sm">
// //             <p>
// //               Displayed First Name: <span className="font-semibold"></span>
// //             </p>
// //             <p>
// //               Displayed Last Name: <span className="font-semibold"></span>
// //             </p>
// //           </div>
// //         </div>
// //       </div>
// //     );
// //   }
  
// //   export default ItineraryPreview;



// import React, { useState, useEffect } from 'react';

// // Main App component
// const ItineraryPreview = () => {
//   // State to hold the data fetched from the "JSON"
//   const [data, setData] = useState([]);
//   const [error, setError] = useState(null);

  

//   useEffect(() => {
//     const fetchLastJsonLine = async () => {
//       try {
//         const response = await fetch('../../../server/data.txt');
//         if (!response.ok) {
//           throw new Error(`Fetch failed: ${response.status} ${response.statusText}`);
//         }
  
//         const text = await response.text();
  
//         const lines = text
//           .trim()
//           .split('\n')
//           .filter((line) => line.trim() !== ''); // Ignore blank lines
  
//         if (lines.length === 0) {
//           throw new Error("The file is empty or only contains blank lines.");
//         }
  
//         const lastLine = lines[lines.length - 1].trim();
//         console.log("Last line from file:", lastLine);
  
//         const parsed = JSON.parse(lastLine); // Throws if invalid
//         setData([parsed]); // Convert to array if using .map()
  
//       } catch (err) {
//         console.error("Error reading last JSON line:", err);
//         setError(err.message);
//       }
//     };
  
//     fetchLastJsonLine();
//   }, []);

//   if (error) return <div>Error: {error}</div>;
//   if (!data) return <div>Loading...</div>;


  

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 font-inter text-gray-800 p-4 sm:p-6 md:p-8">
//       {/* Page Title */}
//       <header className="text-center mb-10">
//         <h1 className="text-4xl sm:text-5xl font-extrabold text-indigo-700 leading-tight tracking-tight rounded-lg p-2 inline-block bg-white shadow-md">
//           Dynamic Content Display
//         </h1>
//         <p className="mt-4 text-lg text-gray-600">
//           Content structured with headers and text, dynamically loaded.
//         </p>
//       </header>

//       {/* Content Grid */}
//       /*{ <main className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
//         {data.map((item) => (
//           <div
//             key={item.id}
//             className="bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden border border-gray-200"
//           >
//             <div className="p-6">
//               {/* Header */}
//               <h2 className="text-2xl font-bold text-indigo-600 mb-3 leading-snug">
//                 {item.header}
//               </h2>
//               {/* Text Content */}
//               <p className="text-gray-700 leading-relaxed">
//                 {item.text}
//               </p>
//             </div>
//             {/* Optional: Footer or Action Button */}
//             <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 text-right">
//               <button className="bg-indigo-500 hover:bg-indigo-600 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-opacity-75">
//                 Read More
//               </button>
//             </div>
//           </div>
//         ))}
//       </main> } */
//       <main className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
//   <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
//     <div className="p-6">
//       <h2 className="text-2xl font-bold text-indigo-600 mb-3">Location: {data.location}</h2>
//       <p className="text-gray-700 mb-2">Dates: {data.dates}</p>
//       <p className="text-gray-700">Additional Info: {data.additionalInfo}</p>
//     </div>
//   </div>
// </main>

//       {/* Footer */}
//       <footer className="mt-12 text-center text-gray-500 text-sm">
//         <p>&copy; {new Date().getFullYear()} Dynamic Content App. All rights reserved.</p>
//       </footer>
//     </div>
//   );
// };

// export default ItineraryPreview;

import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const JsonFromServer = () => {
  const [allData, setAllData] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch("http://localhost:3000/data");
        const data = await res.json();
        setAllData(data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  // Preview helper: show first 3 keys and truncated values
  const renderPreview = (obj) => {
    if (!obj) return null;
    const entries = Object.entries(obj).slice(0, 3);
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
      <h1 className="text-3xl font-bold mb-6 border-b pb-2">Data Previews</h1>
      {allData.length === 0 && <p className="italic text-gray-500">No data available.</p>}

      <div className="grid gap-4">
        {allData.map((item, index) => (
          <div
            key={index}
            onClick={() => navigate(`/itinerary/${index}`)}
            className="cursor-pointer bg-white shadow-md rounded-lg p-4 border border-gray-200 hover:shadow-lg transition"
          >
            {renderPreview(item)}
          </div>
        ))}
      </div>
    </div>
  );
};

export default JsonFromServer;