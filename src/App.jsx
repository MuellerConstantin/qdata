import React from 'react';
import {Routes, Route, Navigate} from 'react-router-dom';
import TitleBar from './components/organisms/layout/TitleBar';
import Home from './screens/Home';

/**
 * The application's root component.
 *
 * @return {JSX.Element} Application's root component
 */
export default function App() {
  return (
    <div className="h-screen flex flex-col">
      <TitleBar />
      <div
        className={'grow bg-white h-0 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-200'}
      >
        <Routes>
          <Route path="/" element={<Navigate to="/home" />} />
          <Route path="/home" element={<Home />} />
        </Routes>
      </div>
    </div>
  );
}
