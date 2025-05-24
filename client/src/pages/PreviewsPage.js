import React from 'react';
import { useNavigate } from 'react-router-dom';
import ItineraryPreview from '../components/Preview';

function OptionsPage() {
  const navigate = useNavigate();

  const Regenerate = () => {
    console.log('Regenerating...');
  };

  return (
    <div className="p-6 flex flex-col items-center ml-8">
      <div className="w-full flex justify-start">
        <button
            onClick={() => navigate(-1)}
            className="justify-left text-[#383a32] font-open-sans underline hover:font-bold mb-3 block"
          >
            ← Edit Survey
          </button>
      </div>
      <div className="flex flex-row gap-10 mb-10">
        <ItineraryPreview />
        <ItineraryPreview />
        <ItineraryPreview />
      </div>
      <button
        onClick={Regenerate}
        className="px-6 py-3 bg-[#36a2a4] hover:bg-cyan-700 text-white font-open-sans font-bold text-lg rounded-xl shadow-md transition duration-200"
      >
        Regenerate Itineraries
      </button>
    </div>
  );
}

export default OptionsPage;