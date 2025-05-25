import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import beachImage from '../assets/beach_img.jpeg';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

function FormPage() {
  const [location, setLocation] = useState('');
  const [people, setPeople] = useState('');
  const [additionalInfo, setAdditionalInfo] = useState('');
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = {
      location,
      startDate,
      endDate,
      people,
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

      navigate('/previews');
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-cover bg-center bg-no-repeat relative overflow-hidden p-4 font-sans"
                    style={{ backgroundImage: `url(${beachImage})` }}>
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-2xl bg-white rounded-lg p-10 space-y-6"
      >
        <h2 className="text-6xl font-poppins font-extrabold text-left text-[#36a2a4] mb-8 pl-2">Plan Your Trip!</h2>

        <div className="space-y-2">
          <label className="block text-lg font-open-sans text-[#383a32]">
            Where would you like to go?
          </label>
          <input
            type="text"
            placeholder="Enter a location (eg city/country)."
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="border border-gray-300 font-open-sansrounded w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-1 focus:ring-blue-300 transition duration-200 ease-in-out placeholder-gray-400"
          />
        </div>

        <div>
          <label htmlFor="start-date">Start Date:</label>
          <DatePicker
            id="start-date"
            selected={startDate}
            onChange={(date) => setStartDate(date)}
            selectsStart
            startDate={startDate}
            endDate={endDate}
            dateFormat="MM/dd/yyyy"
            className="p-2 border rounded shadow-sm focus:ring focus:border-blue-300 font-open-sans mr-2 ml-3"
            placeholderText="Start Date"
          />

          <label htmlFor="end-date">End Date:</label>
          <DatePicker
            id="end-date"
            selected={endDate}
            onChange={(date) => setEndDate(date)}
            selectsEnd
            startDate={startDate}
            endDate={endDate}
            minDate={startDate}
            dateFormat="MM/dd/yyyy"
            className="p-2 border rounded shadow-sm focus:ring focus:border-blue-300 font-open-sans ml-3"
            placeholderText="End Date"
          />
      </div>
        
        <div className="space-y-2">
          <label className="block text-lg font-open-sans text-[#383a32]">
            How many people are going????
          </label>
          <input
            type="text"
            placeholder="Enter the number of people"
            value={people}
            onChange={(e) => setPeople(e.target.value)}
            className="border border-gray-300 font-open-sans rounded w-full py-3 px-4 text-gray-700 leading-tight focus:outline-none focus:ring-1 focus:ring-blue-300 transition duration-200 ease-in-out placeholder-gray-400"
          />
        </div>

        <div className="space-y-2">
          <label className="block text-lg font-open-sans text-[#383a32]">
            Please enter any other information you want us to integrate into your itinerary!
          </label>
          <textarea
            rows="5"
            placeholder="Add notes like preferred activities, travel restrictions, etc."
            value={additionalInfo}
            onChange={(e) => setAdditionalInfo(e.target.value)}
            className="w-full px-4 py-3 font-open-sansrounded border border-gray-300 focus:outline-none focus:ring-1 focus:ring-blue-300 bg-white placeholder-gray-400"
          />
        </div>

        <button
          type="submit"
          className="w-full py-3 bg-[#36a2a4] hover:bg-cyan-700 text-white font-open-sans font-bold text-lg rounded-xl shadow-md transition duration-200"
        >
          Generate Itinerary!
        </button>
      </form>
    </div>
  );
}

export default FormPage;
