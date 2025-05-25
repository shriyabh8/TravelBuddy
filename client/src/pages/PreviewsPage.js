import React from 'react';
import { useNavigate } from 'react-router-dom';
import beachImage from '../assets/beach_img.jpeg';
import Preview from '../components/Preview';

function OptionsPage() {
  const navigate = useNavigate();

  const Regenerate = (itinerary_key) => {
    console.log('Regenerating...');
  };

  return (
    <div className="p-6 flex flex-col items-center bg-cover bg-center bg-no-repeat min-h-screen"
        style={{ backgroundImage: `url(${beachImage})` }}>
      <div className="w-full flex justify-start">
        <button
            onClick={() => navigate('/form')}
            className="justify-left text-[#383a32] font-open-sans hover:text-cyan-700 mb-3 block p-4"
          >
            ← Edit Survey
          </button>
      </div>
      
      <div className="flex flex-row gap-10 mb-10">
        <div className="flex flex-col items-center">
        <Preview itinerary_key={0} />
        <button
        onClick={Regenerate(0)}
        className="px-6 py-3 bg-[#36a2a4] hover:bg-cyan-700 text-white font-open-sans font-bold text-lg rounded-xl shadow-md transition duration-200"
      >
        Regenerate
      </button>
      </div>
        
      <div className="flex flex-col items-center">
        <Preview itinerary_key={1} />
        <button
        onClick={Regenerate(1)}
        className="px-6 py-3 bg-[#36a2a4] hover:bg-cyan-700 text-white font-open-sans font-bold text-lg rounded-xl shadow-md transition duration-200"
      >
        Regenerate
      </button>
      </div>

      <div className="flex flex-col items-center">
        <Preview itinerary_key={2} />
        <button
        onClick={Regenerate(2)}
        className="px-6 py-3 bg-[#36a2a4] hover:bg-cyan-700 text-white font-open-sans font-bold text-lg rounded-xl shadow-md transition duration-200"
      >
        Regenerate
      </button>
      </div>
      </div>
      </div>
  );
};

export default OptionsPage;