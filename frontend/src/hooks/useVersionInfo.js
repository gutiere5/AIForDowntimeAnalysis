// src/hooks/useVersionInfo.js
import { useState, useEffect } from 'react';

export const useVersionInfo = () => {
  const [versionInfo, setVersionInfo] = useState({
    frontend: {
      appVersion: import.meta.env.VITE_APP_VERSION || 'unknown',
      commitHash: import.meta.env.VITE_COMMIT_HASH || 'unknown',
      buildDate: import.meta.env.VITE_BUILD_DATE || 'unknown',
      environment: import.meta.env.MODE || 'unknown',
    },
    backend: {
      appVersion: 'loading...',
      environment: 'loading...',
      commitHash: 'loading...',
      buildDate: 'loading...',
    },
  });

  useEffect(() => {
    // This function runs once to fetch data from your backend
    const fetchBackendInfo = async () => {
      try {
        // This URL must match your running backend
        const response = await fetch('http://localhost:8000/about');

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const data = await response.json();

        setVersionInfo((prevInfo) => ({
          ...prevInfo,
          backend: data,
        }));

      } catch (error) {
        console.error("Failed to fetch backend version info:", error);
        setVersionInfo((prevInfo) => ({
          ...prevInfo,
          backend: {
            appVersion: 'Error',
            environment: 'Error',
            commitHash: 'Error',
            buildDate: 'Error',
          },
        }));
      }
    };

    fetchBackendInfo();
  }, []); // The empty [] means this only runs one time

  return versionInfo;
};