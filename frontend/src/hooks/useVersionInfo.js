import { useState, useEffect } from 'react';

/**
 * Custom hook to fetch version information for frontend and backend
 */
export function useVersionInfo() {
  const [backend, setBackend] = useState({
    app_version: 'Loading...',
    environment: 'Loading...',
    commit_hash: 'Loading...',
    build_date: 'Loading...',
  });

  // Safely access environment variables with fallbacks
  const [frontend] = useState({
    appVersion: (import.meta?.env?.VITE_APP_VERSION) || '1.0.0',
    environment: (import.meta?.env?.VITE_ENVIRONMENT) || (import.meta?.env?.MODE) || 'development',
    commitHash: (import.meta?.env?.VITE_COMMIT_HASH) || 'local-dev',
    buildDate: (import.meta?.env?.VITE_BUILD_DATE) || new Date().toISOString(),
  });

  useEffect(() => {
    // Fetch backend version info
    const fetchBackendVersion = async () => {
      try {
        // Get base URL from environment or default
        const baseURL = (import.meta?.env?.VITE_API_BASE_URL) || 'http://localhost:8000';

        const response = await fetch(`${baseURL}/version`);

        if (response.ok) {
          const data = await response.json();
          setBackend({
            app_version: data.app_version || 'Unknown',
            environment: data.environment || 'Unknown',
            commit_hash: data.commit_hash || 'Unknown',
            build_date: data.build_date || 'Unknown',
          });
        } else {
          throw new Error('Failed to fetch version info');
        }
      } catch (error) {
        console.error('Error fetching backend version:', error);
        setBackend({
          app_version: 'Error',
          environment: 'Error',
          commit_hash: 'Unable to connect',
          build_date: 'N/A',
        });
      }
    };

    fetchBackendVersion();
  }, []);

  return { frontend, backend };
}