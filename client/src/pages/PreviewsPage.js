import React from 'react';
import { useNavigate } from 'react-router-dom';
import ItineraryPreview from '../components/Preview';

function OptionsPage() {
  const navigate = useNavigate();

  const Regenerate = () => {
    console.log('Regenerating...');
  };

  return (
    <div>
      <button onClick={Regenerate}>Regenerate</button>
      <ItineraryPreview/>
      <ItineraryPreview/>
      <ItineraryPreview/>
    </div>
  );
}

export default OptionsPage;