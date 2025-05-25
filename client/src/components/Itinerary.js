import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import beachImage from '../assets/beach_img.jpeg';

const Itinerary = ({itinerary_key}) => {
  const [allData, setAllData] = useState([]);
  const [showTextbox, setShowTextbox] = useState(false);
  const [input, setInput] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch("http://localhost:3000/itinerary-data");
        const data = await res.json();
        const item = data[String(itinerary_key)];
        setAllData(item ? [item] : []);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
  
    fetchData();
  }, [itinerary_key]);

  const handleTextboxToggle = () => {
    setShowTextbox(prev => !prev);
    if (showTextbox) {
      setInput('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (input.trim() === '') {
      console.log("Input is empty, not submitting.");
      return;
    }

    const formData = {input: input};

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

      setInput(''); 
      setShowTextbox(false);
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  const renderPreview = (obj, reFormat) => {
    if (!obj) return null;
    return Object.entries(obj).map(([key, value]) => {
      const strVal = String(value);
      return (
        <div className={!reFormat ? "min-w-[300px] max-w-[350px] bg-gray-50 rounded-xl shadow-md p-6 border border-gray-100 mb-7" : "w-full max-w-full bg-gray-50 rounded-xl shadow-md p-6 border border-gray-100 mb-7"}
             style={{minHeight: '300px'}}
        >
          <div className="mb-4 text-lg">
            <strong className="capitalize text-[#36a2a4] font-open-sans">{key}:</strong> 
            <p>{strVal}</p>
          </div> 
        </div>
      );
    });
  };

  const mainDataObject = allData[0];

  let flightsCardData = null;
  let hotelsCardData = null;
  let otherDetailsData = {};

  if (mainDataObject) {
    if (mainDataObject.hasOwnProperty("Flights")) {
      flightsCardData = { "Flights": mainDataObject.Flights }; 
    }
    if (mainDataObject.hasOwnProperty("Hotels")) {
      hotelsCardData = { "Hotels": mainDataObject.Hotels };
    }
    Object.entries(mainDataObject).forEach(([key, value]) => {
      if (key !== "Flights" && key !== "Hotels") {
        otherDetailsData[key] = value;
      }
    });
  }

  return (
    <div className="flex flex-col items-center justify-center p-4 bg-cover bg-center bg-no-repeat min-h-screen"
        style={{ backgroundImage: `url(${beachImage})` }}>

      <div className="w-full flex justify-start">
        <button
          onClick={() => navigate('/previews')}
          className="text-[#383a32] font-open-sans hover:text-cyan-700 mb-15 ml-9 pt-2 block"
        >
          ← Back To Previews
        </button>
      </div>

      <div className="max-w-5xl w-full bg-white rounded-2xl shadow-lg p-8 border border-gray-200 min-h-[600px]">
        <h1 className="text-3xl font-poppins font-bold text-gray-800 mb-6">Trip Details</h1>
        <div className="flex-shrink-0 justify-center gap-6 mt-6">
          {mainDataObject === undefined || (flightsCardData === null && hotelsCardData === null) ? (
            <p className="italic text-gray-500">No data available for Flights or Hotels.</p>
          ) : (
            <>
            <div className="flex flex-wrap gap-4 mb-4 justify-center">
              {flightsCardData !== null && (
                <div> {renderPreview(flightsCardData, false)} </div>
              )}
    
              {hotelsCardData !== null && (
                <div> {renderPreview(hotelsCardData, false)} </div>
              )}
            </div>

            {Object.keys(otherDetailsData).length > 0 && (
                <div> {renderPreview(otherDetailsData, true)} </div>
            )}
            
            </>
        )}
        </div>
      </div>  
      
      <button
        onClick={handleTextboxToggle}
        className="
          fixed bottom-6 right-6 z-50
          w-14 h-14 rounded-full
          bg-[#e9cfb5] text-white text-3xl font-bold
          flex items-center justify-center
          shadow-lg hover:shadow-xl
          transform hover:scale-110 transition-transform duration-200 ease-in-out
          focus:outline-none focus:ring-4 focus:ring-blue-400 focus:ring-opacity-75
        "
        aria-label="Open text input"
      >
        {showTextbox ? '✕' : '💬'} 
      </button>

      {showTextbox && (
        <form onSubmit={handleSubmit}>
        <div
          className="
            fixed bottom-24 right-6 z-40
            bg-white rounded-lg shadow-xl p-4
            w-72 h-72 flex flex-col
            transition-all duration-300 ease-in-out
            transform origin-bottom-right
          "
        >
          <h4 className="text-lg font-semibold mb-2 text-gray-800">Chat with your virtual TravelBuddy!</h4>
          <textarea
            className="flex-grow border border-gray-300 rounded-md p-2 w-70 h-70 text-gray-700
                       focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
            placeholder="Type your suggestions here to modify your itinerary..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            autoFocus
          ></textarea>
          <button
              type="submit"
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              Send
            </button>
        </div>  
        </form>
      )}
    </div>
  );
};

export default Itinerary;