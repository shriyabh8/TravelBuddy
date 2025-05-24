import React from 'react';
import Itinerary from '../components/Itinerary';
import { useParams } from 'react-router-dom';

function ItineraryPage() {
  const { id } = useParams();

  return (
    <div>
      <Itinerary itinerary_key={id} />
    </div>
  );
}

export default ItineraryPage;