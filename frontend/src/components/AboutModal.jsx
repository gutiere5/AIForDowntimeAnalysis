// src/components/AboutModal.jsx
import 'react';
import { useVersionInfo } from '../hooks/useVersionInfo';

// This is the component that receives 'isOpen' and 'onClose' props
// eslint-disable-next-line react/prop-types
export const AboutModal = ({ isOpen, onClose }) => {
  // Call our hook to get the data
  const { frontend, backend } = useVersionInfo();

  // Helper function to format the date
  const formatDate = (dateString) => {
    if (!dateString || dateString.includes('...')) return dateString;
    try {
      return new Date(dateString).toLocaleString();
        // eslint-disable-next-line no-unused-vars
    } catch (e) {
      return 'Invalid Date';
    }
  };

  // If the modal isn't open, render nothing
  if (!isOpen) {
    return null;
  }

  // This is the Tailwind CSS modal structure
  return (
    // 1. Full-screen overlay with a semi-transparent background
    <div 
      onClick={onClose} 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 transition-opacity"
    >
      {/* 2. The Modal panel itself. onClick(e.stopPropagation) stops clicks inside from closing it. */}
      <div 
        onClick={(e) => e.stopPropagation()} 
        className="relative w-full max-w-2xl rounded-lg bg-white p-6 shadow-xl"
      >
        {/* 3. Modal Header with Title and Close Button */}
        <div className="flex items-start justify-between">
          <h2 className="text-xl font-semibold text-gray-900">
            About this Application
          </h2>
          <button 
            onClick={onClose} 
            className="text-gray-400 hover:text-gray-600"
          >
            {/* Simple 'X' icon */}
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* 4. Modal Body with a dividing line */}
        <div className="mt-4 border-t border-gray-200 pt-4">
          <div className="flex flex-col gap-6 md:flex-row">
            
            {/* === FRONTEND INFO === */}
            <div className="flex-1">
              <h3 className="text-lg font-medium text-gray-800">Frontend</h3>
              <ul className="mt-2 list-none space-y-1 pl-0 text-sm">
                <li><strong>Version:</strong> {frontend.appVersion}</li>
                <li><strong>Environment:</strong> {frontend.environment}</li>
                <li><strong>Build ID:</strong> <code className="text-xs">{frontend.commitHash}</code></li>
                <li><strong>Build Date:</strong> {formatDate(frontend.buildDate)}</li>
              </ul>
            </div>

            {/* === BACKEND INFO === */}
            <div className="flex-1">
              <h3 className="text-lg font-medium text-gray-800">Backend (API)</h3>
              <ul className="mt-2 list-none space-y-1 pl-0 text-sm">

                {/* --- FIXES ARE HERE --- */}
                <li><strong>Version:</strong> {backend.app_version}</li>
                <li><strong>Environment:</strong> {backend.environment}</li>
                <li><strong>Build ID:</strong> <code className="text-xs">{backend.commit_hash}</code></li>
                <li><strong>Build Date:</strong> {formatDate(backend.build_date)}</li>

              </ul>
            </div>
          </div>
        </div>

        {/* 5. Modal Footer with the Close button */}
        <div className="mt-6 flex justify-end border-t border-gray-200 pt-4">
          <button 
            onClick={onClose} 
            className="rounded-md bg-gray-600 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};