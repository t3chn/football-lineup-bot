import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from '../api/client';
import type { PredictionResponse } from '../api/client';
import ModernFootballField from './ModernFootballField';
import { motion, AnimatePresence } from 'framer-motion';

// New components for enhanced features
import InjuriesPanel from './InjuriesPanel';
import SchedulePanel from './SchedulePanel';
import NewsAnalysisPanel from './NewsAnalysisPanel';
import NotificationsPanel from './NotificationsPanel';

function ModernLineupPredictorEnhanced() {
  const [teamName, setTeamName] = useState('');
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [isFieldView, setIsFieldView] = useState(true);
  const [activeTab, setActiveTab] = useState<'lineup' | 'injuries' | 'schedule' | 'news' | 'notifications'>('lineup');

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

  const popularTeams = ['Arsenal', 'Chelsea', 'Liverpool', 'Manchester United', 'Manchester City'];

  const tabs = [
    { id: 'lineup', label: '⚽ Lineup', icon: '📋' },
    { id: 'injuries', label: '🏥 Injuries', icon: '🚑' },
    { id: 'schedule', label: '📅 Schedule', icon: '🗓️' },
    { id: 'news', label: '📰 News', icon: '📢' },
    { id: 'notifications', label: '🔔 Alerts', icon: '💬' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Animated background */}
      <div className="fixed inset-0 overflow-hidden">
        <div className="absolute -inset-[10px] opacity-50">
          <div className="absolute top-0 -left-4 w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob"></div>
          <div className="absolute top-0 -right-4 w-96 h-96 bg-yellow-500 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-2000"></div>
          <div className="absolute -bottom-8 left-20 w-96 h-96 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob animation-delay-4000"></div>
        </div>
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-12"
        >
          <h1 className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-green-400 via-blue-500 to-purple-600 mb-4 tracking-tight">
            Fantasy Football Hub
          </h1>
          <p className="text-xl text-gray-300 font-light">
            AI-Powered Lineup Predictions & Real-time Analytics
          </p>
        </motion.div>

        {/* Search Card with Glassmorphism */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="max-w-4xl mx-auto mb-8"
        >
          <div className="backdrop-blur-xl bg-white/10 rounded-3xl p-6 shadow-2xl border border-white/20">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-200 mb-3">
                  Select or Enter Team Name
                </label>

                {/* Popular Teams Quick Select */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {popularTeams.map((team) => (
                    <button
                      key={team}
                      type="button"
                      onClick={() => setTeamName(team)}
                      className={`px-4 py-2 rounded-full text-sm font-semibold transition-all transform hover:scale-105 active:scale-95 ${
                        teamName === team
                          ? 'bg-gradient-to-r from-green-400 to-blue-500 text-white shadow-lg'
                          : 'bg-white/10 text-gray-300 hover:bg-white/20 border border-white/10'
                      }`}
                    >
                      {team}
                    </button>
                  ))}
                </div>

                <div className="relative">
                  <input
                    type="text"
                    value={teamName}
                    onChange={(e) => setTeamName(e.target.value)}
                    placeholder="Enter team name..."
                    className="w-full px-6 py-4 bg-white/10 backdrop-blur-md rounded-2xl text-white placeholder-gray-400 border border-white/20 focus:outline-none focus:ring-2 focus:ring-green-400/50 focus:border-transparent transition-all text-lg"
                  />
                  <button
                    type="submit"
                    disabled={predictMutation.isPending || !teamName.trim()}
                    className="absolute right-2 top-1/2 -translate-y-1/2 px-8 py-2.5 bg-gradient-to-r from-green-400 to-blue-500 text-white font-bold rounded-xl shadow-lg hover:shadow-green-400/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] active:scale-[0.98]"
                  >
                    {predictMutation.isPending ? (
                      <span className="flex items-center gap-2">
                        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Analyzing...
                      </span>
                    ) : (
                      'Analyze Team'
                    )}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </motion.div>

        {/* Enhanced Tab Navigation */}
        {teamName && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-7xl mx-auto mb-6"
          >
            <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-2 border border-white/20">
              <div className="flex flex-wrap gap-2">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
                      activeTab === tab.id
                        ? 'bg-gradient-to-r from-green-400 to-blue-500 text-white shadow-lg'
                        : 'text-gray-300 hover:text-white hover:bg-white/10'
                    }`}
                  >
                    <span className="text-xl">{tab.icon}</span>
                    <span>{tab.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Content Panels */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="max-w-7xl mx-auto"
          >
            {/* Lineup Tab */}
            {activeTab === 'lineup' && prediction && (
              <div>
                {/* Team Header */}
                <div className="backdrop-blur-xl bg-white/10 rounded-3xl p-6 mb-6 border border-white/20">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-3xl font-bold text-white mb-2">
                        {prediction.team}
                      </h2>
                      <div className="flex items-center gap-6 text-sm">
                        <span className="text-gray-300">
                          Formation: <span className="text-green-400 font-bold">{prediction.formation}</span>
                        </span>
                        <span className="text-gray-300">
                          Confidence:
                          <span className="ml-2 inline-flex items-center">
                            <div className="w-32 h-2 bg-white/20 rounded-full overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${prediction.confidence * 100}%` }}
                                transition={{ duration: 1, ease: "easeOut" }}
                                className="h-full bg-gradient-to-r from-green-400 to-blue-500"
                              />
                            </div>
                            <span className="ml-2 text-green-400 font-bold">
                              {(prediction.confidence * 100).toFixed(0)}%
                            </span>
                          </span>
                        </span>
                      </div>
                    </div>

                    {/* View Toggle */}
                    <div className="flex items-center gap-2 bg-white/10 rounded-full p-1">
                      <button
                        onClick={() => setIsFieldView(true)}
                        className={`px-4 py-2 rounded-full font-semibold transition-all ${
                          isFieldView
                            ? 'bg-gradient-to-r from-green-400 to-blue-500 text-white'
                            : 'text-gray-300 hover:text-white'
                        }`}
                      >
                        Field View
                      </button>
                      <button
                        onClick={() => setIsFieldView(false)}
                        className={`px-4 py-2 rounded-full font-semibold transition-all ${
                          !isFieldView
                            ? 'bg-gradient-to-r from-green-400 to-blue-500 text-white'
                            : 'text-gray-300 hover:text-white'
                        }`}
                      >
                        List View
                      </button>
                    </div>
                  </div>
                </div>

                {/* Content */}
                {isFieldView ? (
                  <ModernFootballField
                    lineup={prediction.lineup}
                    formation={prediction.formation}
                  />
                ) : (
                  <div className="backdrop-blur-xl bg-white/10 rounded-3xl p-6 border border-white/20">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {prediction.lineup.map((player, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.05 }}
                          whileHover={{ scale: 1.02, y: -2 }}
                          className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20 hover:border-green-400/50 transition-all"
                        >
                          <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center font-bold text-white text-lg">
                              {player.number}
                            </div>
                            <div className="flex-1">
                              <div className="font-semibold text-white flex items-center gap-2">
                                {player.name}
                                {player.is_captain && (
                                  <span className="px-2 py-0.5 bg-yellow-400/20 text-yellow-400 text-xs font-bold rounded-full">
                                    Captain
                                  </span>
                                )}
                              </div>
                              <div className="text-sm text-gray-400">{player.position}</div>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Injuries Tab */}
            {activeTab === 'injuries' && teamName && (
              <InjuriesPanel teamName={teamName} />
            )}

            {/* Schedule Tab */}
            {activeTab === 'schedule' && teamName && (
              <SchedulePanel teamName={teamName} />
            )}

            {/* News Tab */}
            {activeTab === 'news' && teamName && (
              <NewsAnalysisPanel teamName={teamName} />
            )}

            {/* Notifications Tab */}
            {activeTab === 'notifications' && teamName && (
              <NotificationsPanel teamName={teamName} />
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

export default ModernLineupPredictorEnhanced;
