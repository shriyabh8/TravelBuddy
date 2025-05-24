import React, { useState } from 'react';

function FormPage() {
  const [location, setLocation] = useState('');
  const [dates, setDates] = useState('');
  const [additionalInfo, setAdditionalInfo] = useState('');


  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = {
      location,
      dates,
      additionalInfo,
    };

    try {
      const response = await fetch('http://localhost:3000/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const result = await response.json();
      console.log('Submission successful:', result);
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  // return (
  //   <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4 font-sans">
  //     <form
  //       onSubmit={handleSubmit}
  //       className="w-full max-w-xl bg-white shadow-xl rounded-2xl p-8 space-y-8"
  //     >
  //       <h2 className="text-6xl font-bold text-left text-pink-600 mb-8 pl-6">Plan Your Trip!</h2>

  //       <div className="space-y-2 pl-6 pr-6">
  //         <label className="block text-xl font-semibold text-blue-800">
  //           Where would you like to go?
  //         </label>
  //         <input
  //           type="text"
  //           placeholder="Enter a location"
  //           value={location}
  //           onChange={(e) => setLocation(e.target.value)}
  //           className="shadow appearance-none border rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent transition duration-200 ease-in-out"
  //         />
  //       </div>

  //       <div className="space-y-2 pl-6 pr-6">
  //         <label className="block text-xl font-semibold text-blue-800">
  //           When would you like to go?
  //         </label>
  //         <input
  //           type="text"
  //           placeholder="Enter the start and end date"
  //           value={dates}
  //           onChange={(e) => setDates(e.target.value)}
  //           className="shadow appearance-none border rounded-md w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent transition duration-200 ease-in-out"
  //         />
  //       </div>

  //       <div className="space-y-2 pl-6 pr-6">
  //         <label className="block text-xl font-semibold text-blue-800">
  //           Please enter any other information you want us to integrate into your itinerary!
  //         </label>
  //         <textarea
  //           rows="5"
  //           placeholder="Add notes like preferred activities, travel restrictions, etc."
  //           value={additionalInfo}
  //           onChange={(e) => setAdditionalInfo(e.target.value)}
  //           className="w-full px-4 py-3 rounded-xl border border-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400 bg-gray-50 placeholder-gray-500"
  //         />
  //       </div>

  //       <button
  //         type="submit"
  //         className="w-full py-3 bg-pink-600 hover:bg-pink-700 text-white font-semibold text-lg rounded-xl shadow-md transition duration-200"
  //       >
  //         Generate
  //       </button>
  //     </form>
  //   </div>
  // );

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4 font-sans">
      <form
        onSubmit={handleSubmit}

        className="w-full max-w-2xl bg-white rounded-lg p-10 space-y-6"
      >
        <h2 className="text-6xl font-bold text-left text-pink-600 mb-8 pl-6">Plan Your Trip!</h2>

        <div className="space-y-2">
          <label className="block text-lg font-normal text-gray-800">
            Where would you like to go?
          </label>
          <input
            type="text"
            placeholder="Enter a location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}

            className="border border-gray-300 rounded w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-1 focus:ring-blue-300 transition duration-200 ease-in-out placeholder-gray-400"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-lg font-normal text-gray-800">
            When would you like to go?
          </label>
          <input
            type="text"
            placeholder="Enter the start and end date"
            value={dates}
            onChange={(e) => setDates(e.target.value)}

            className="border border-gray-300 rounded w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-1 focus:ring-blue-300 transition duration-200 ease-in-out placeholder-gray-400"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-lg font-normal text-gray-800">
            Please enter any other information you want us to integrate into your itinerary!
          </label>
          <textarea
            rows="5"
            placeholder="Add notes like preferred activities, travel restrictions, etc."
            value={additionalInfo}
            onChange={(e) => setAdditionalInfo(e.target.value)}

            className="w-full px-4 py-3 rounded border border-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-300 bg-white placeholder-gray-400"
          />
        </div>

        <button
          type="submit"

          className="w-1000 mx-auto block py-3 bg-gray-200 hover:bg-gray-300 text-gray-1000 font-normal text-lg rounded-md shadow-sm transition duration-200"
        >
          Generate!
        </button>
      </form>
    </div>
  );
}

export default FormPage;

