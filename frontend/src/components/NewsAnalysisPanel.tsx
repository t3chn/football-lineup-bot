import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { api } from '../api/client';

interface NewsAnalysisPanelProps {
  teamName: string;
}

function NewsAnalysisPanel({ teamName }: NewsAnalysisPanelProps) {
  const { data: newsData, isLoading, error } = useQuery({
    queryKey: ['news', teamName],
    queryFn: () => api.analyzeTeamNews(teamName),
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
          <span className="ml-3 text-gray-300">Analyzing news...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="backdrop-blur-xl bg-red-500/10 rounded-3xl p-8 border border-red-500/20">
        <p className="text-red-300">Failed to analyze news</p>
      </div>
    );
  }

  const insights = newsData?.analysis?.insights || {};
  const confidence = (newsData?.analysis?.confidence || 0) * 100;

  return (
    <div className="space-y-6">
      {/* News Summary */}
      <div className="backdrop-blur-xl bg-white/10 rounded-3xl p-6 border border-white/20">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-white">Latest Team News</h3>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-400">Confidence:</span>
            <div className="flex items-center">
              <div className="w-24 h-2 bg-white/20 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${confidence}%` }}
                  transition={{ duration: 1 }}
                  className="h-full bg-gradient-to-r from-green-400 to-blue-500"
                />
              </div>
              <span className="ml-2 text-green-400 font-bold text-sm">{confidence.toFixed(0)}%</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white/5 rounded-xl p-4">
            <div className="text-3xl font-bold text-white">{newsData?.analysis?.sources || 0}</div>
            <div className="text-sm text-gray-400">News Sources</div>
          </div>
          <div className="bg-white/5 rounded-xl p-4">
            <div className="text-3xl font-bold text-green-400">
              {insights.likely_starters ? Object.keys(insights.likely_starters).length : 0}
            </div>
            <div className="text-sm text-gray-400">Confirmed Starters</div>
          </div>
          <div className="bg-white/5 rounded-xl p-4">
            <div className="text-3xl font-bold text-orange-400">
              {insights.doubtful ? Object.keys(insights.doubtful).length : 0}
            </div>
            <div className="text-sm text-gray-400">Doubtful Players</div>
          </div>
        </div>
      </div>

      {/* Lineup Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Likely Starters */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="backdrop-blur-xl bg-green-500/10 rounded-3xl p-6 border border-green-500/20"
        >
          <h4 className="text-lg font-bold text-green-400 mb-4 flex items-center gap-2">
            <span className="text-2xl">✅</span> Likely Starters
          </h4>
          {insights.likely_starters && Object.keys(insights.likely_starters).length > 0 ? (
            <div className="space-y-2">
              {Object.entries(insights.likely_starters).map(([player, conf]: [string, any]) => (
                <div key={player} className="flex items-center justify-between p-3 bg-green-500/10 rounded-lg">
                  <span className="text-white font-medium">{player}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-green-900/30 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-green-400"
                        style={{ width: `${conf * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-green-400">{(conf * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No confirmed starters from news analysis</p>
          )}
        </motion.div>

        {/* Doubtful Players */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="backdrop-blur-xl bg-orange-500/10 rounded-3xl p-6 border border-orange-500/20"
        >
          <h4 className="text-lg font-bold text-orange-400 mb-4 flex items-center gap-2">
            <span className="text-2xl">⚠️</span> Doubtful Players
          </h4>
          {insights.doubtful && Object.keys(insights.doubtful).length > 0 ? (
            <div className="space-y-2">
              {Object.entries(insights.doubtful).map(([player, conf]: [string, any]) => (
                <div key={player} className="flex items-center justify-between p-3 bg-orange-500/10 rounded-lg">
                  <span className="text-white font-medium">{player}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-orange-900/30 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-orange-400"
                        style={{ width: `${conf * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-orange-400">{(conf * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No doubtful players reported</p>
          )}
        </motion.div>
      </div>

      {/* Ruled Out */}
      {insights.ruled_out && Object.keys(insights.ruled_out).length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="backdrop-blur-xl bg-red-500/10 rounded-3xl p-6 border border-red-500/20"
        >
          <h4 className="text-lg font-bold text-red-400 mb-4 flex items-center gap-2">
            <span className="text-2xl">❌</span> Ruled Out
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {Object.keys(insights.ruled_out).map((player) => (
              <div key={player} className="p-3 bg-red-500/10 rounded-lg text-center">
                <span className="text-white font-medium">{player}</span>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Formation Hints */}
      {insights.formation_hints && (
        <div className="backdrop-blur-xl bg-blue-500/10 rounded-3xl p-6 border border-blue-500/20">
          <h4 className="text-lg font-bold text-blue-400 mb-2">Expected Formation</h4>
          <div className="text-4xl font-black text-white text-center py-4">
            {insights.formation_hints}
          </div>
          <p className="text-center text-gray-400 text-sm">Based on recent tactical reports</p>
        </div>
      )}

      {/* Tactical Changes */}
      {insights.tactical_changes && insights.tactical_changes.length > 0 && (
        <div className="backdrop-blur-xl bg-purple-500/10 rounded-3xl p-6 border border-purple-500/20">
          <h4 className="text-lg font-bold text-purple-400 mb-4">Tactical Insights</h4>
          <ul className="space-y-2">
            {insights.tactical_changes.map((change: string, index: number) => (
              <li key={index} className="flex items-start gap-2 text-gray-300">
                <span className="text-purple-400 mt-1">•</span>
                <span>{change}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Last Update */}
      <div className="text-center text-sm text-gray-500">
        Last updated: {newsData?.timestamp ? new Date(newsData.timestamp).toLocaleString() : 'N/A'}
      </div>
    </div>
  );
}

export default NewsAnalysisPanel;
