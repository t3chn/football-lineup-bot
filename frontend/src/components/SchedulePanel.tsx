import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { api } from '../api/client';
import { useState } from 'react';

interface SchedulePanelProps {
  teamName: string;
}

function SchedulePanel({ teamName }: SchedulePanelProps) {
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('list');

  const { data: fixtures, isLoading, error } = useQuery({
    queryKey: ['fixtures', teamName],
    queryFn: () => api.getTeamFixtures(teamName),
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
          <span className="ml-3 text-gray-300">Loading fixtures...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="backdrop-blur-xl bg-red-500/10 rounded-3xl p-8 border border-red-500/20">
        <p className="text-red-300">Failed to load fixtures</p>
      </div>
    );
  }

  const getMatchTypeColor = (isHome: boolean) => {
    return isHome
      ? 'bg-green-500/20 text-green-400 border-green-500/30'
      : 'bg-blue-500/20 text-blue-400 border-blue-500/30';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return {
      date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      day: date.toLocaleDateString('en-US', { weekday: 'short' }),
    };
  };

  return (
    <div className="space-y-6">
      {/* View Mode Toggle */}
      <div className="backdrop-blur-xl bg-white/10 rounded-3xl p-6 border border-white/20">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-bold text-white">Upcoming Matches</h3>
          <div className="flex items-center gap-2 bg-white/10 rounded-full p-1">
            <button
              onClick={() => setViewMode('list')}
              className={`px-4 py-2 rounded-full font-semibold transition-all ${
                viewMode === 'list'
                  ? 'bg-gradient-to-r from-green-400 to-blue-500 text-white'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              List
            </button>
            <button
              onClick={() => setViewMode('calendar')}
              className={`px-4 py-2 rounded-full font-semibold transition-all ${
                viewMode === 'calendar'
                  ? 'bg-gradient-to-r from-green-400 to-blue-500 text-white'
                  : 'text-gray-300 hover:text-white'
              }`}
            >
              Calendar
            </button>
          </div>
        </div>
      </div>

      {/* Fixtures List */}
      {viewMode === 'list' && (
        <div className="space-y-4">
          {fixtures?.matches?.map((match: any, index: number) => {
            const dateInfo = formatDate(match.date);
            return (
              <motion.div
                key={match.fixture_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="backdrop-blur-xl bg-white/10 rounded-2xl border border-white/20 overflow-hidden hover:bg-white/15 transition-all"
              >
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-white">{dateInfo.date}</div>
                        <div className="text-xs text-gray-400">{dateInfo.day}</div>
                      </div>
                      <div className="w-px h-12 bg-white/20"></div>
                      <div>
                        <div className="text-sm text-gray-400">{match.league.name}</div>
                        <div className="text-xs text-gray-500">{match.league.round}</div>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${getMatchTypeColor(match.is_home)}`}>
                      {match.is_home ? 'HOME' : 'AWAY'}
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      {match.is_home ? (
                        <>
                          <div className="text-right flex-1">
                            <div className="text-xl font-bold text-white">{teamName}</div>
                            <div className="text-sm text-gray-400">Home</div>
                          </div>
                          <div className="text-2xl font-bold text-gray-500">VS</div>
                          <div className="flex-1">
                            <div className="text-xl font-bold text-gray-300">{match.opponent.name}</div>
                            <div className="text-sm text-gray-400">Away</div>
                          </div>
                        </>
                      ) : (
                        <>
                          <div className="text-right flex-1">
                            <div className="text-xl font-bold text-gray-300">{match.opponent.name}</div>
                            <div className="text-sm text-gray-400">Home</div>
                          </div>
                          <div className="text-2xl font-bold text-gray-500">VS</div>
                          <div className="flex-1">
                            <div className="text-xl font-bold text-white">{teamName}</div>
                            <div className="text-sm text-gray-400">Away</div>
                          </div>
                        </>
                      )}
                    </div>

                    <div className="text-right ml-4">
                      <div className="text-lg font-semibold text-green-400">{dateInfo.time}</div>
                      <div className="text-xs text-gray-400">{match.venue || 'TBD'}</div>
                    </div>
                  </div>

                  {/* Match Details Button */}
                  <div className="mt-4 pt-4 border-t border-white/10">
                    <button className="w-full py-2 bg-white/5 hover:bg-white/10 rounded-lg text-sm text-gray-300 hover:text-white transition-all">
                      View Match Details →
                    </button>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Calendar View */}
      {viewMode === 'calendar' && (
        <div className="backdrop-blur-xl bg-white/10 rounded-3xl p-6 border border-white/20">
          <div className="grid grid-cols-7 gap-2">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="text-center text-xs text-gray-400 font-semibold py-2">
                {day}
              </div>
            ))}
            {/* Calendar days would go here - simplified for demo */}
            {Array.from({ length: 35 }, (_, i) => {
              const hasMatch = fixtures?.matches?.some((m: any) => {
                const matchDay = new Date(m.date).getDate();
                return matchDay === i - 5; // Offset for calendar positioning
              });

              return (
                <div
                  key={i}
                  className={`aspect-square rounded-lg flex items-center justify-center text-sm ${
                    hasMatch
                      ? 'bg-gradient-to-br from-green-400/20 to-blue-500/20 text-white font-bold border border-green-400/30'
                      : i > 5 && i < 36
                      ? 'bg-white/5 text-gray-500 hover:bg-white/10 cursor-pointer'
                      : ''
                  }`}
                >
                  {i > 5 && i < 36 ? i - 5 : ''}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* No Fixtures Message */}
      {(!fixtures?.matches || fixtures.matches.length === 0) && (
        <div className="backdrop-blur-xl bg-white/10 rounded-3xl p-8 border border-white/20 text-center">
          <div className="text-6xl mb-4">📅</div>
          <p className="text-gray-400">No upcoming fixtures found</p>
        </div>
      )}
    </div>
  );
}

export default SchedulePanel;
