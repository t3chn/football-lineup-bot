import { useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import type { Player } from '../api/client';

interface ModernFootballFieldProps {
  lineup: Player[];
  formation?: string | null;
}

interface PlayerWithIndex extends Player {
  _positionIndex?: number;
}

function ModernFootballField({ lineup, formation }: ModernFootballFieldProps) {
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [hoveredPlayer, setHoveredPlayer] = useState<Player | null>(null);

  const playersWithIndices = useMemo(() => {
    const positionCounts: Record<string, number> = {};

    return lineup.map(player => {
      const position = player.position;
      const index = positionCounts[position] || 0;
      positionCounts[position] = index + 1;

      return {
        ...player,
        _positionIndex: index
      } as PlayerWithIndex;
    });
  }, [lineup]);

  const getPlayerPosition = (player: PlayerWithIndex): { top: string; left: string } => {
    const { position, _positionIndex = 0 } = player;

    // Dynamic positioning based on formation
    if (position === 'CB') {
      const cbPositions = [
        { top: '75%', left: '35%' },
        { top: '75%', left: '65%' }
      ];
      return cbPositions[_positionIndex] || cbPositions[0];
    }

    if (position === 'CM') {
      const cmPositions = [
        { top: '55%', left: '30%' },
        { top: '55%', left: '50%' },
        { top: '55%', left: '70%' }
      ];
      return cmPositions[_positionIndex] || cmPositions[0];
    }

    const positions: Record<string, { top: string; left: string }> = {
      GK: { top: '88%', left: '50%' },
      LB: { top: '75%', left: '15%' },
      RB: { top: '75%', left: '85%' },
      LW: { top: '30%', left: '20%' },
      RW: { top: '30%', left: '80%' },
      AM: { top: '40%', left: '50%' },
      ST: { top: '20%', left: '50%' },
      CF: { top: '20%', left: '50%' },
      CDM: { top: '60%', left: '50%' },
      CAM: { top: '40%', left: '50%' },
      LM: { top: '55%', left: '20%' },
      RM: { top: '55%', left: '80%' },
    };

    return positions[position] || { top: '50%', left: '50%' };
  };

  return (
    <div className="relative">
      {/* 3D Perspective Container */}
      <div className="perspective-1000">
        <motion.div
          initial={{ rotateX: 15 }}
          animate={{ rotateX: 0 }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="relative w-full aspect-[3/4] transform-gpu preserve-3d"
        >
          {/* Field Background with Gradient */}
          <div className="absolute inset-0 bg-gradient-to-b from-green-600 via-green-500 to-green-600 rounded-2xl overflow-hidden shadow-2xl">
            {/* Grass Pattern */}
            <div className="absolute inset-0 opacity-30">
              {[...Array(10)].map((_, i) => (
                <div
                  key={i}
                  className="absolute w-full h-[10%] bg-green-700"
                  style={{ top: `${i * 20}%` }}
                />
              ))}
            </div>

            {/* Field Lines with Glow Effect */}
            <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
              {/* Center Line */}
              <line x1="0" y1="50" x2="100" y2="50" stroke="white" strokeWidth="0.3" opacity="0.8" />

              {/* Center Circle */}
              <circle cx="50" cy="50" r="9" fill="none" stroke="white" strokeWidth="0.3" opacity="0.8" />
              <circle cx="50" cy="50" r="0.5" fill="white" opacity="0.8" />

              {/* Penalty Areas */}
              <rect x="30" y="0" width="40" height="16" fill="none" stroke="white" strokeWidth="0.3" opacity="0.8" />
              <rect x="30" y="84" width="40" height="16" fill="none" stroke="white" strokeWidth="0.3" opacity="0.8" />

              {/* Goal Areas */}
              <rect x="40" y="0" width="20" height="6" fill="none" stroke="white" strokeWidth="0.3" opacity="0.8" />
              <rect x="40" y="94" width="20" height="6" fill="none" stroke="white" strokeWidth="0.3" opacity="0.8" />

              {/* Penalty Spots */}
              <circle cx="50" cy="11" r="0.3" fill="white" opacity="0.8" />
              <circle cx="50" cy="89" r="0.3" fill="white" opacity="0.8" />
            </svg>

            {/* Field Lighting Effect */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-black/20" />
          </div>

          {/* Players */}
          {playersWithIndices.map((player, index) => {
            const position = getPlayerPosition(player);
            const isSelected = selectedPlayer?.name === player.name;
            const isHovered = hoveredPlayer?.name === player.name;

            return (
              <motion.div
                key={`${player.position}-${index}`}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{
                  delay: index * 0.1,
                  type: "spring",
                  stiffness: 200,
                  damping: 20
                }}
                className="absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer"
                style={{ top: position.top, left: position.left }}
                onClick={() => setSelectedPlayer(player)}
                onMouseEnter={() => setHoveredPlayer(player)}
                onMouseLeave={() => setHoveredPlayer(null)}
              >
                <motion.div
                  animate={{
                    scale: isHovered ? 1.2 : 1,
                    y: isHovered ? -5 : 0,
                  }}
                  transition={{ type: "spring", stiffness: 300 }}
                  className="relative"
                >
                  {/* Player Shadow */}
                  <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-8 h-2 bg-black/30 rounded-full blur-sm" />

                  {/* Player Circle with Gradient */}
                  <div className={`
                    relative w-14 h-14 rounded-full flex items-center justify-center
                    bg-gradient-to-br from-white to-gray-200
                    shadow-lg border-2 transition-all duration-300
                    ${isSelected ? 'border-yellow-400 ring-4 ring-yellow-400/30' : 'border-white/50'}
                    ${isHovered ? 'shadow-2xl' : ''}
                  `}>
                    <span className="text-lg font-bold text-gray-900">
                      {player.number || '?'}
                    </span>

                    {/* Captain Badge */}
                    {player.is_captain && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center shadow-lg"
                      >
                        <span className="text-xs font-black text-white">C</span>
                      </motion.div>
                    )}
                  </div>

                  {/* Player Name */}
                  <motion.div
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 + 0.3 }}
                    className="absolute top-16 left-1/2 -translate-x-1/2 whitespace-nowrap"
                  >
                    <div className="px-3 py-1 bg-black/80 backdrop-blur-md rounded-lg shadow-lg">
                      <p className="text-xs font-semibold text-white">
                        {player.name.split(' ').pop()}
                      </p>
                      <p className="text-[10px] text-green-400 text-center">
                        {player.position}
                      </p>
                    </div>
                  </motion.div>
                </motion.div>
              </motion.div>
            );
          })}

          {/* Formation Badge */}
          {formation && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="absolute top-4 left-4 px-4 py-2 bg-black/80 backdrop-blur-md rounded-full shadow-lg"
            >
              <span className="text-sm font-bold text-white">Formation: </span>
              <span className="text-sm font-bold text-green-400">{formation}</span>
            </motion.div>
          )}
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
              className="relative z-10 w-full max-w-md"
            >
              <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-6 shadow-2xl border border-white/10">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-20 h-20 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-3xl font-bold text-white">
                      {selectedPlayer.number || '?'}
                    </span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold text-white flex items-center gap-2">
                      {selectedPlayer.name}
                      {selectedPlayer.is_captain && (
                        <span className="px-3 py-1 bg-yellow-400/20 text-yellow-400 text-sm font-bold rounded-full">
                          Captain
                        </span>
                      )}
                    </h3>
                    <p className="text-green-400 font-semibold">{selectedPlayer.position}</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                    <span className="text-gray-400">Position</span>
                    <span className="text-white font-semibold">{selectedPlayer.position}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                    <span className="text-gray-400">Number</span>
                    <span className="text-white font-semibold">{selectedPlayer.number || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                    <span className="text-gray-400">Role</span>
                    <span className="text-white font-semibold">
                      {selectedPlayer.is_captain ? 'Team Captain' : 'Player'}
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => setSelectedPlayer(null)}
                  className="mt-6 w-full py-3 bg-gradient-to-r from-green-400 to-blue-500 text-white font-bold rounded-xl hover:shadow-lg transition-all"
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
