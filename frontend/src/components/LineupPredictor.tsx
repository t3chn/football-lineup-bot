import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { api } from '../api/client';
import type { PredictionResponse } from '../api/client';
import FootballField from './FootballField';

function LineupPredictor() {
  const [teamName, setTeamName] = useState('');
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);

  const predictMutation = useMutation({
    mutationFn: api.predictLineup,
    onSuccess: (data) => {
      setPrediction(data);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (teamName.trim()) {
      predictMutation.mutate(teamName.trim());
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Predict Team Lineup
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="team" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Team Name
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                id="team"
                value={teamName}
                onChange={(e) => setTeamName(e.target.value)}
                placeholder="e.g., Arsenal, Chelsea, Liverpool"
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={predictMutation.isPending}
              />
              <button
                type="submit"
                disabled={predictMutation.isPending || !teamName.trim()}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {predictMutation.isPending ? 'Predicting...' : 'Predict'}
              </button>
            </div>
          </div>
          {predictMutation.isError && (
            <div className="p-3 bg-red-100 dark:bg-red-900/30 border border-red-400 dark:border-red-700 rounded-lg text-red-700 dark:text-red-400">
              Failed to get prediction. Please try again.
            </div>
          )}
        </form>
      </div>

      {prediction && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              {prediction.team} Predicted Lineup
            </h3>
            <div className="flex items-center gap-4 mt-2 text-sm text-gray-600 dark:text-gray-400">
              {prediction.formation && (
                <span>Formation: {prediction.formation}</span>
              )}
              <span>Confidence: {(prediction.confidence * 100).toFixed(0)}%</span>
              {prediction.cached && (
                <span className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded text-xs">
                  Cached
                </span>
              )}
            </div>
          </div>

          <FootballField lineup={prediction.lineup} formation={prediction.formation} />

          <div className="mt-6">
            <h4 className="font-medium text-gray-900 dark:text-white mb-3">
              Player List
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {prediction.lineup.map((player, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 p-2 bg-gray-50 dark:bg-gray-700 rounded"
                >
                  <span className="text-sm font-medium text-gray-500 dark:text-gray-400 w-8">
                    {player.number}
                  </span>
                  <span className="flex-1 text-gray-900 dark:text-white">
                    {player.name}
                  </span>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {player.position}
                  </span>
                  {player.is_captain && (
                    <span className="text-xs bg-yellow-400 dark:bg-yellow-600 text-yellow-900 dark:text-yellow-100 px-2 py-1 rounded">
                      C
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default LineupPredictor;
