import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import LineupPredictor from './components/LineupPredictor';
import ModernLineupPredictor from './components/ModernLineupPredictor';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [useModernUI, setUseModernUI] = useState(true);

  if (useModernUI) {
    return (
      <QueryClientProvider client={queryClient}>
        <ModernLineupPredictor />
        {/* UI Toggle Button */}
        <button
          onClick={() => setUseModernUI(false)}
          className="fixed bottom-4 right-4 z-50 px-4 py-2 bg-gray-800/80 backdrop-blur-md text-white rounded-full text-sm font-semibold hover:bg-gray-700/80 transition-all"
        >
          Switch to Classic UI
        </button>
      </QueryClientProvider>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <div className={isDarkMode ? 'dark' : ''}>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
          <header className="bg-white dark:bg-gray-800 shadow">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  Football Lineup Predictor
                </h1>
                <div className="flex gap-2">
                  <button
                    onClick={() => setUseModernUI(true)}
                    className="px-4 py-2 bg-gradient-to-r from-green-400 to-blue-500 text-white rounded-lg font-semibold hover:shadow-lg transition-all"
                  >
                    Try Modern UI
                  </button>
                  <button
                    onClick={() => setIsDarkMode(!isDarkMode)}
                    className="p-2 rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                  >
                    {isDarkMode ? '☀️' : '🌙'}
                  </button>
                </div>
              </div>
            </div>
          </header>
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <LineupPredictor />
          </main>
        </div>
      </div>
    </QueryClientProvider>
  );
}

export default App;
