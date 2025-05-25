import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import beachImage from '../assets/beach_img.jpeg';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

function FormPage() {
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const [people, setPeople] = useState('');
  const [additionalInfo, setAdditionalInfo] = useState('');
  const [startDate, setStartDate] = useState(null);
  const [endDate, setEndDate] = useState(null);
  const today = new Date();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate form data
    if (!from || !to || !startDate || !endDate) {
      alert('Please fill in all required fields');
      return;
    }

    // Format dates
    // Validate form data
    if (!from || !to || !startDate || !endDate || !people) {
      alert('Please fill in all required fields');
      return;
    }

    // Format dates
    const formattedStartDate = startDate.toISOString().split('T')[0];
      const formattedEndDate = endDate.toISOString().split('T')[0];

    const formData = {
      from,
      to,
      start_date: formattedStartDate,
      end_date: formattedEndDate,
      people,
      additionalInfo,
    };


    console.log('Form data being sent:', formData); // Add logging to see the data structure

    try {
      try {
        const response = await fetch('http://localhost:5001/submit_trip_data', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Server error: ${response.status} - ${errorText}`);
        }

        const result = await response.json();
        console.log('Server response:', result);
        
        if (result.key) {
          // Store the key in localStorage for later use
          localStorage.setItem("itinerary_key", result.key);
          navigate('/previews');
        } else {
          throw new Error('Invalid response from server');
        }
      } catch (error) {
        console.error('Error details:', error);
        alert('Error submitting form: ' + error.message);
      }

      // Save the key for itinerary fetch later
      // Save form data in localStorage
      localStorage.setItem("trip_form_data", JSON.stringify({
        from,
        to,
        startDate: startDate?.toISOString(),
        endDate: endDate?.toISOString(),
        people,
        additionalInfo,
      }));

      // Redirect
      navigate('/previews');
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center bg-cover bg-center bg-no-repeat relative overflow-hidden p-4 font-sans"
      style={{ backgroundImage: `url(${beachImage})` }}
    >
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-2xl bg-white rounded-lg p-10 space-y-6"
      >
        <h2 className="text-6xl font-extrabold text-left text-[#36a2a4] mb-8 pl-2">Plan Your Trip!</h2>

        <div className="space-y-3">
          <label className="block text-lg font-open-sans text-[#383a32]">
            Where would you like to go?
          </label>
          <div>
          <label>Origin:</label>
          <input
            type="text"
            placeholder="Starting place?"
            value={from}
            onChange={(e) => setFrom(e.target.value)}
            className="p-2 border rounded shadow-sm focus:ring focus:border-blue-300 font-open-sans mr-2 ml-3"
          />

          <label> Destination:</label>
          <input
            type="text"
            placeholder="Where to?"
            value={to}
            onChange={(e) => setTo(e.target.value)}
            className="p-2 border rounded shadow-sm focus:ring focus:border-blue-300 font-open-sans mr-2 ml-3"
          />
      </div>

        </div>

        <div>
          <label>Start Date:</label>
          <DatePicker
            selected={startDate}
            onChange={(date) => setStartDate(date)}
            selectsStart
            startDate={startDate}
            endDate={endDate}
            minDate={today}
            dateFormat="MM/dd/yyyy"
            className="p-2 w-55 border rounded shadow-sm focus:ring focus:border-blue-300 font-open-sans mr-4 ml-3"
            placeholderText="Start Date (mm/dd/yyyy)"
          />

          <label>End Date:</label>
          <DatePicker
            selected={endDate}
            onChange={(date) => setEndDate(date)}
            selectsEnd
            startDate={startDate}
            endDate={endDate}
            minDate={startDate || today}
            dateFormat="MM/dd/yyyy"
            className="p-2 border rounded ml-3"
            placeholderText="End Date (mm/dd/yyyy)"
          />
        </div>

        <div>
          <label className="block text-lg text-[#383a32]">How many people are going?</label>
          <input
            type="text"
            value={people}
            onChange={(e) => setPeople(e.target.value)}
            className="border rounded w-full py-3 px-4"
          />
        </div>

        <div>
          <label className="block text-lg text-[#383a32]">
            Please enter any other information you want us to integrate into your itinerary!
          </label>
          <textarea
            rows="5"
            value={additionalInfo}
            onChange={(e) => setAdditionalInfo(e.target.value)}
            className="w-full px-4 py-3 border rounded"
            placeholder="E.g. activities, dietary preferences, pace, etc."
          />
        </div>

        <button
          type="submit"
          className="w-full py-3 bg-[#36a2a4] hover:bg-cyan-700 text-white font-bold text-lg rounded-xl"
        >
          Generate Itinerary!
        </button>
      </form>
    </div>
  );
}

export default FormPage;
