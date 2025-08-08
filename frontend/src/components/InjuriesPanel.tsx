import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { api } from '../api/client';

interface InjuriesPanelProps {
  teamName: string;
}

function InjuriesPanel({ teamName }: InjuriesPanelProps) {
  const { data: injuries, isLoading, error } = useQuery({
    queryKey: ['injuries', teamName],
    queryFn: () => api.getTeamInjuries(teamName),
    enabled: !!teamName,
  });

  if (isLoading) {
    return (
      <div className="backdrop-blur-xl bg-white/10 rounded-3xl p-8 border border-white/20">
        <div className="flex items-center justify-center">
          <svg className="animate-spin h-8 w-8 text-green-400" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <span className="ml-3 text-gray-300">Loading injury data...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="backdrop-blur-xl bg-red-500/10 rounded-3xl p-8 border border-red-500/20">
        <p className="text-red-300">Failed to load injury data</p>
      </div>
    );
  }

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'out':
      case 'major':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'minor':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'doubt':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <div className="backdrop-blur-xl bg-white/10 rounded-3xl p-6 border border-white/20">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-white">{injuries?.total_injuries || 0}</div>
            <div className="text-sm text-gray-400">Total Injuries</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-red-400">{injuries?.long_term_injuries?.length || 0}</div>
            <div className="text-sm text-gray-400">Long Term</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-400">
              {(injuries?.impact_score * 100).toFixed(0)}%
            </div>
            <div className="text-sm text-gray-400">Impact Score</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-400">Last Updated</div>
            <div className="text-xs text-gray-500">
              {injuries?.last_updated ? new Date(injuries.last_updated).toLocaleString() : 'N/A'}
            </div>
          </div>
        </div>
      </div>

      {/* Injuries List */}
      <div className="backdrop-blur-xl bg-white/10 rounded-3xl p-6 border border-white/20">
        <h3 className="text-xl font-bold text-white mb-4">Current Injuries & Suspensions</h3>

        {injuries?.injuries && injuries.injuries.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {injuries.injuries.map((injury: any, index: number) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`p-4 rounded-xl border ${getSeverityColor(injury.severity)} backdrop-blur-md`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-semibold text-white text-lg">{injury.player_name}</h4>
                    <p className="text-sm mt-1 opacity-90">{injury.reason}</p>
                    {injury.expected_return && (
                      <p className="text-xs mt-2 opacity-70">
                        Expected return: {new Date(injury.expected_return).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    injury.severity === 'out' ? 'bg-red-500/30 text-red-300' :
                    injury.severity === 'major' ? 'bg-orange-500/30 text-orange-300' :
                    injury.severity === 'minor' ? 'bg-yellow-500/30 text-yellow-300' :
                    'bg-gray-500/30 text-gray-300'
                  }`}>
                    {injury.severity?.toUpperCase()}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="text-6xl mb-4">🎉</div>
            <p className="text-green-400 font-semibold">No injuries reported!</p>
            <p className="text-gray-400 text-sm mt-2">Full squad available</p>
          </div>
        )}
      </div>

      {/* Long Term Injuries */}
      {injuries?.long_term_injuries && injuries.long_term_injuries.length > 0 && (
        <div className="backdrop-blur-xl bg-red-500/10 rounded-3xl p-6 border border-red-500/20">
          <h3 className="text-xl font-bold text-white mb-4">⚠️ Long Term Absences</h3>
          <div className="space-y-3">
            {injuries.long_term_injuries.map((injury: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-3 bg-red-500/10 rounded-lg">
                <span className="text-white font-medium">{injury.player_name}</span>
                <span className="text-red-300 text-sm">{injury.reason}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default InjuriesPanel;
