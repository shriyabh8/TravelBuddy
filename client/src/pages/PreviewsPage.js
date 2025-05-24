import React from 'react';
import { useNavigate } from 'react-router-dom';
import Preview from '../components/Preview';

function OptionsPage() {
  const navigate = useNavigate();

  const Regenerate = (itinerary_key) => {
    console.log('Regenerating...');
  };

  return (
    <div className="p-6 flex flex-col items-center">
      <button
          onClick={() => navigate('/form')}
          className="text-indigo-600 hover:underline mb-3 block"
        >
          ← Edit Survey
        </button>
      <div className="flex flex-row gap-4 mb-6">
        <div>
        <Preview itinerary_key={0} />
        <button
        onClick={Regenerate(0)}
        className="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700 transition"
      >
        Regenerate
      </button>
      </div>
        
      <div>
        <Preview itinerary_key={1} />
        <button
        onClick={Regenerate(1)}
        className="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700 transition"
      >
        Regenerate
      </button>
      </div>
      <div>
        <Preview itinerary_key={2} />
        <button
        onClick={Regenerate(2)}
        className="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700 transition"
      >
        Regenerate
      </button>
      </div>
      </div>
    </div>
  );
}

export default OptionsPage;