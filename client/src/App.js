import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import FormPage from './pages/FormPage';
import OptionsPage from './pages/PreviewsPage';
import ItineraryPage from './pages/ItineraryPage';

function App() {
  return (
    <Router>
      <div>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/form" element={<FormPage />} />
          <Route path="/previews/" element={<OptionsPage />} />
          <Route path="/itinerary/:id" element={<ItineraryPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;