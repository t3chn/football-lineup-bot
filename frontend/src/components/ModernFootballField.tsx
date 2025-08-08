import { useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { Player } from '../api/client';

interface ModernFootballFieldProps {
  lineup: Player[];
  formation?: string | null;
}

function ModernFootballField({ lineup, formation }: ModernFootballFieldProps) {
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [hoveredPlayer, setHoveredPlayer] = useState<Player | null>(null);

  // Parse formation (e.g., "4-3-3" -> [4, 3, 3])
  const formationArray = useMemo(() => {
    if (!formation) return [4, 3, 3];
    const parts = formation.split('-').map(n => parseInt(n, 10));
    if (parts.length === 3 && parts.every(n => !isNaN(n))) {
      return parts;
    }
    return [4, 3, 3]; // Default formation
  }, [formation]);

  // Calculate player positions based on formation
  const getPlayerPosition = (player: Player, index: number): { top: string; left: string } => {
    const { position } = player;

    // Map API positions to standard positions
    const positionMap: Record<string, string> = {
      'SUB': position === 'SUB' && index === 0 ? 'GK' :
            position === 'SUB' && index < 5 ? 'DEF' :
            position === 'SUB' && index < 8 ? 'MID' : 'FW',
    };

    const mappedPosition = positionMap[position] || position;

    // Count players per line based on formation
    const [defenders, midfielders, forwards] = formationArray;
    const totalPlayers = lineup.length;

    // Distribute players by formation
    let lineupPositions: Array<{ top: string; left: string }> = [];

    // GK position
    lineupPositions.push({ top: '88%', left: '50%' });

    // Defenders
    for (let i = 0; i < defenders; i++) {
      const spacing = 70 / (defenders + 1);
      lineupPositions.push({
        top: '72%',
        left: `${15 + spacing * (i + 1)}%`
      });
    }

    // Midfielders
    for (let i = 0; i < midfielders; i++) {
      const spacing = 70 / (midfielders + 1);
      lineupPositions.push({
        top: '50%',
        left: `${15 + spacing * (i + 1)}%`
      });
    }

    // Forwards
    for (let i = 0; i < forwards; i++) {
      const spacing = 60 / (forwards + 1);
      lineupPositions.push({
        top: '25%',
        left: `${20 + spacing * (i + 1)}%`
      });
    }

    // Return position based on index
    return lineupPositions[index] || { top: '50%', left: '50%' };
  };

  return (
    <div className="relative w-full max-w-4xl mx-auto">
      {/* Field Container - Responsive */}
      <div className="relative w-full">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="relative w-full aspect-[3/4] md:aspect-[4/3] lg:aspect-[3/2]"
        >
          {/* Field Background with Gradient */}
          <div className="absolute inset-0 bg-gradient-to-b from-green-600 via-green-500 to-green-600 rounded-lg md:rounded-xl lg:rounded-2xl overflow-hidden shadow-2xl">
            {/* Grass Pattern */}
            <div className="absolute inset-0 opacity-30">
              {[...Array(10)].map((_, i) => (
                <div
                  key={i}
                  className={`absolute w-full h-[10%] ${i % 2 === 0 ? 'bg-green-600' : 'bg-green-700'}`}
                  style={{ top: `${i * 10}%` }}
                />
              ))}
            </div>

            {/* Field Lines */}
            <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
              {/* Outer Box */}
              <rect x="1" y="1" width="98" height="98" fill="none" stroke="white" strokeWidth="0.5" opacity="0.7" />

              {/* Center Line */}
              <line x1="0" y1="50" x2="100" y2="50" stroke="white" strokeWidth="0.5" opacity="0.7" />

              {/* Center Circle */}
              <circle cx="50" cy="50" r="9" fill="none" stroke="white" strokeWidth="0.5" opacity="0.7" />
              <circle cx="50" cy="50" r="0.5" fill="white" opacity="0.7" />

              {/* Penalty Areas */}
              <rect x="25" y="0" width="50" height="18" fill="none" stroke="white" strokeWidth="0.5" opacity="0.7" />
              <rect x="25" y="82" width="50" height="18" fill="none" stroke="white" strokeWidth="0.5" opacity="0.7" />

              {/* Goal Areas */}
              <rect x="37.5" y="0" width="25" height="8" fill="none" stroke="white" strokeWidth="0.5" opacity="0.7" />
              <rect x="37.5" y="92" width="25" height="8" fill="none" stroke="white" strokeWidth="0.5" opacity="0.7" />

              {/* Penalty Spots */}
              <circle cx="50" cy="12" r="0.5" fill="white" opacity="0.7" />
              <circle cx="50" cy="88" r="0.5" fill="white" opacity="0.7" />

              {/* Goals */}
              <rect x="44" y="0" width="12" height="3" fill="none" stroke="white" strokeWidth="0.5" opacity="0.7" />
              <rect x="44" y="97" width="12" height="3" fill="none" stroke="white" strokeWidth="0.5" opacity="0.7" />
            </svg>

            {/* Field Lighting Effect */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 via-transparent to-transparent pointer-events-none" />
          </div>

          {/* Players */}
          {lineup.map((player, index) => {
            const position = getPlayerPosition(player, index);
            const isSelected = selectedPlayer?.name === player.name;
            const isHovered = hoveredPlayer?.name === player.name;

            return (
              <motion.div
                key={`${player.name}-${index}`}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{
                  delay: index * 0.05,
                  type: "spring",
                  stiffness: 200,
                  damping: 20
                }}
                className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer z-10"
                style={{ top: position.top, left: position.left }}
                onClick={() => setSelectedPlayer(player)}
                onMouseEnter={() => setHoveredPlayer(player)}
                onMouseLeave={() => setHoveredPlayer(null)}
              >
                <motion.div
                  animate={{
                    scale: isHovered ? 1.15 : 1,
                    y: isHovered ? -3 : 0,
                  }}
                  transition={{ type: "spring", stiffness: 300 }}
                  className="relative"
                >
                  {/* Player Shadow */}
                  <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-6 h-1.5 bg-black/20 rounded-full blur-sm" />

                  {/* Player Circle */}
                  <div className={`
                    relative w-10 h-10 md:w-12 md:h-12 lg:w-14 lg:h-14 rounded-full flex items-center justify-center
                    bg-gradient-to-br from-white to-gray-100
                    shadow-lg border-2 transition-all duration-200
                    ${isSelected ? 'border-yellow-400 ring-2 ring-yellow-400/30' : 'border-white/80'}
                    ${isHovered ? 'shadow-xl' : ''}
                  `}>
                    <span className="text-sm md:text-base lg:text-lg font-bold text-gray-900">
                      {player.number || '?'}
                    </span>

                    {/* Captain Badge */}
                    {player.is_captain && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="absolute -top-1 -right-1 w-4 h-4 md:w-5 md:h-5 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center shadow-md"
                      >
                        <span className="text-[8px] md:text-[10px] font-black text-white">C</span>
                      </motion.div>
                    )}
                  </div>

                  {/* Player Name - Show on hover or selection */}
                  <AnimatePresence>
                    {(isHovered || isSelected) && (
                      <motion.div
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 5 }}
                        className="absolute top-12 md:top-14 lg:top-16 left-1/2 -translate-x-1/2 whitespace-nowrap z-20"
                      >
                        <div className="px-2 py-1 bg-black/90 backdrop-blur-sm rounded-md shadow-lg">
                          <p className="text-[10px] md:text-xs font-semibold text-white">
                            {player.name.length > 15 ? player.name.split(' ').pop() : player.name}
                          </p>
                          <p className="text-[8px] md:text-[10px] text-green-400 text-center">
                            {player.position}
                          </p>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              </motion.div>
            );
          })}

          {/* Formation Badge */}
          {formation && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="absolute top-2 left-2 md:top-4 md:left-4 px-3 py-1.5 bg-black/80 backdrop-blur-sm rounded-full shadow-lg"
            >
              <span className="text-xs md:text-sm font-bold text-white">Formation: </span>
              <span className="text-xs md:text-sm font-bold text-green-400">{formation}</span>
            </motion.div>
          )}

          {/* Team Name Badge (if needed) */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="absolute top-2 right-2 md:top-4 md:right-4 px-3 py-1.5 bg-black/80 backdrop-blur-sm rounded-full shadow-lg"
          >
            <span className="text-xs md:text-sm font-bold text-green-400">
              {lineup.length} Players
            </span>
          </motion.div>
        </motion.div>
      </div>

      {/* Player Details Modal */}
      <AnimatePresence>
        {selectedPlayer && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center px-4"
            onClick={() => setSelectedPlayer(null)}
          >
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="relative z-10 w-full max-w-sm md:max-w-md"
            >
              <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-xl md:rounded-2xl p-4 md:p-6 shadow-2xl border border-white/10">
                <div className="flex items-center gap-3 md:gap-4 mb-4">
                  <div className="w-16 h-16 md:w-20 md:h-20 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-2xl md:text-3xl font-bold text-white">
                      {selectedPlayer.number || '?'}
                    </span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg md:text-2xl font-bold text-white flex items-center gap-2">
                      {selectedPlayer.name}
                      {selectedPlayer.is_captain && (
                        <span className="px-2 py-0.5 md:px-3 md:py-1 bg-yellow-400/20 text-yellow-400 text-xs md:text-sm font-bold rounded-full">
                          Captain
                        </span>
                      )}
                    </h3>
                    <p className="text-green-400 font-semibold text-sm md:text-base">{selectedPlayer.position}</p>
                  </div>
                </div>

                <div className="space-y-2 md:space-y-3">
                  <div className="flex justify-between items-center p-2 md:p-3 bg-white/5 rounded-lg">
                    <span className="text-gray-400 text-sm md:text-base">Position</span>
                    <span className="text-white font-semibold text-sm md:text-base">{selectedPlayer.position}</span>
                  </div>
                  <div className="flex justify-between items-center p-2 md:p-3 bg-white/5 rounded-lg">
                    <span className="text-gray-400 text-sm md:text-base">Number</span>
                    <span className="text-white font-semibold text-sm md:text-base">{selectedPlayer.number || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between items-center p-2 md:p-3 bg-white/5 rounded-lg">
                    <span className="text-gray-400 text-sm md:text-base">Role</span>
                    <span className="text-white font-semibold text-sm md:text-base">
                      {selectedPlayer.is_captain ? 'Team Captain' : 'Player'}
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => setSelectedPlayer(null)}
                  className="mt-4 md:mt-6 w-full py-2.5 md:py-3 bg-gradient-to-r from-green-400 to-blue-500 text-white font-bold rounded-lg md:rounded-xl hover:shadow-lg transition-all text-sm md:text-base"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default ModernFootballField;
