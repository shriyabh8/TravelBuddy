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
  const [start_date, setstart_date] = useState(null);
  const [end_date, setend_date] = useState(null);
  const [buttonText, setButtonText] = useState('Generate Itinerary!');
  const today = new Date();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate form data
    if (!from || !to || !start_date || !end_date) {
      alert('Please fill in all required fields');
      return;
    }

    // Format dates
    // Validate form data
    if (!from || !to || !start_date || !end_date || !people) {
      alert('Please fill in all required fields');
      return;
    }

    // Format dates
    const formattedstart_date = start_date.toISOString().split('T')[0];
      const formattedend_date = end_date.toISOString().split('T')[0];

    const formData = {
      from,
      to,
      start_date: formattedstart_date,
      end_date: formattedend_date,
      start_date: start_date,
      end_date: end_date,
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
        navigate('/previews');
      } catch (error) {
        console.error('Error details:', error);
        alert('Error submitting form: ' + error.message);
      }
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
            selected={start_date}
            onChange={(date) => setstart_date(date)}
            selectsStart
            start_date={start_date}
            end_date={end_date}
            minDate={today}
            dateFormat="MM/dd/yyyy"
            className="p-2 w-55 border rounded shadow-sm focus:ring focus:border-blue-300 font-open-sans mr-4 ml-3"
            placeholderText="Start Date (mm/dd/yyyy)"
          />

          <label>End Date:</label>
          <DatePicker
            selected={end_date}
            onChange={(date) => setend_date(date)}
            selectsEnd
            start_date={start_date}
            end_date={end_date}
            minDate={start_date || today}
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
          onClick={() => setButtonText('Generating Itinerary...')}
          className="w-full py-3 bg-[#36a2a4] hover:bg-cyan-700 text-white font-bold text-lg rounded-xl"
        >
          {buttonText}
        </button>
      </form>
    </div>
  );
}

export default FormPage;
