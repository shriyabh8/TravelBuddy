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

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200 p-4">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-xl bg-white shadow-xl rounded-2xl p-8 space-y-6"
      >
        <h2 className="text-2xl font-bold text-center text-gray-800">Plan Your Trip</h2>

        <div>
          <label className="block text-gray-700 font-medium mb-2">
            Where would you like to go?
          </label>
          <input
            type="text"
            placeholder="Enter a location"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-400 bg-gray-50 placeholder-gray-500"
          />
        </div>

        <div>
          <label className="block text-gray-700 font-medium mb-2">
            When would you like to go?
          </label>
          <input
            type="text"
            placeholder="Enter the start and end date"
            value={dates}
            onChange={(e) => setDates(e.target.value)}
            className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-400 bg-gray-50 placeholder-gray-500"
          />
        </div>

        <div>
          <label className="block text-gray-700 font-medium mb-2">
            Please enter any other information you want us to integrate into your itinerary!
          </label>
          <textarea
            rows="5"
            placeholder="Add notes like preferred activities, travel restrictions, etc."
            value={additionalInfo}
            onChange={(e) => setAdditionalInfo(e.target.value)}
            className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-400 bg-gray-50 placeholder-gray-500"
          />
        </div>

        <button
          type="submit"
          className="w-full py-3 bg-indigo-500 hover:bg-indigo-600 text-white font-semibold text-lg rounded-xl shadow-md transition duration-200"
        >
          Generate!
        </button>
      </form>
    </div>
  );
}

export default FormPage;

