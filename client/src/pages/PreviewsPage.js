import React from 'react';
import { useNavigate } from 'react-router-dom';
import ItineraryPreview from '../components/Preview';

function OptionsPage() {
  const navigate = useNavigate();

  const Regenerate = () => {
    console.log('Regenerating...');
  };

  return (
    <div className="p-6 flex flex-col items-center">
      <button
          onClick={() => navigate(-1)}
          className="text-indigo-600 hover:underline mb-3 block"
        >
          ← Edit Survey
        </button>
      <div className="flex flex-row gap-4 mb-6">
        <ItineraryPreview />
        <ItineraryPreview />
        <ItineraryPreview />
      </div>
      <button
        onClick={Regenerate}
        className="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700 transition"
      >
        Regenerate
      </button>
    </div>
  );
}

export default OptionsPage;