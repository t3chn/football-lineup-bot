import { useMemo, useCallback } from 'react';
import type { Player } from '../api/client';

interface FootballFieldProps {
  lineup: Player[];
  formation?: string | null;
}

interface PlayerWithIndex extends Player {
  _positionIndex?: number;
}

function FootballField({ lineup, formation }: FootballFieldProps) {
  // Pre-compute position indices to avoid repeated filtering
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

  const getPlayerPosition = useCallback(
    (player: PlayerWithIndex): { top: string; left: string } => {
      const { position, _positionIndex = 0 } = player;

      // Handle multiple players per position properly
      if (position === 'CB') {
        const cbPositions = [
          { top: '70%', left: '35%' },
          { top: '70%', left: '65%' }
        ];
        return cbPositions[_positionIndex] || cbPositions[0];
      }

      if (position === 'CM') {
        const cmPositions = [
          { top: '50%', left: '35%' },
          { top: '50%', left: '50%' },
          { top: '50%', left: '65%' }
        ];
        return cmPositions[_positionIndex] || cmPositions[0];
      }

      // Default positions for single-player positions
      const positions: Record<string, { top: string; left: string }> = {
        GK: { top: '85%', left: '50%' },
        LB: { top: '70%', left: '15%' },
        RB: { top: '70%', left: '85%' },
        LW: { top: '25%', left: '15%' },
        RW: { top: '25%', left: '85%' },
        AM: { top: '35%', left: '50%' },
        ST: { top: '15%', left: '50%' },
        CF: { top: '15%', left: '50%' },
        CDM: { top: '55%', left: '50%' },
        CAM: { top: '35%', left: '50%' },
        LM: { top: '50%', left: '20%' },
        RM: { top: '50%', left: '80%' },
      };

      return positions[position] || { top: '50%', left: '50%' };
    },
    []
  );

  // Memoize field markings to avoid re-renders
  const fieldMarkings = useMemo(() => (
    <div className="absolute inset-0">
      {/* Center line */}
      <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-white/30" />

      {/* Center circle */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-24 h-24 border-2 border-white/30 rounded-full" />

      {/* Penalty areas */}
      <div className="absolute bottom-0 left-1/4 right-1/4 h-20 border-2 border-t-2 border-b-0 border-white/30" />
      <div className="absolute top-0 left-1/4 right-1/4 h-20 border-2 border-b-2 border-t-0 border-white/30" />
    </div>
  ), []);

  return (
    <div className="relative w-full aspect-[3/4] bg-gradient-to-b from-green-500 to-green-600 rounded-lg overflow-hidden">
      {/* Field markings */}
      {fieldMarkings}

      {/* Formation display */}
      {formation && (
        <div className="absolute top-2 left-2 bg-black/50 text-white px-2 py-1 rounded text-sm">
          {formation}
        </div>
      )}

      {/* Players */}
      {playersWithIndices.map((player, index) => {
        const position = getPlayerPosition(player);
        return (
          <PlayerCard
            key={`${player.position}-${index}`}
            player={player}
            position={position}
          />
        );
      })}
    </div>
  );
}

// Separate component for player card to optimize re-renders
interface PlayerCardProps {
  player: Player;
  position: { top: string; left: string };
}

const PlayerCard = ({ player, position }: PlayerCardProps) => {
  // Extract last name for display
  const displayName = useMemo(() => {
    const nameParts = player.name.split(' ');
    return nameParts[nameParts.length - 1];
  }, [player.name]);

  return (
    <div
      className="absolute transform -translate-x-1/2 -translate-y-1/2 transition-all duration-300 hover:scale-110"
      style={{ top: position.top, left: position.left }}
    >
      <div className="relative">
        <div className="w-10 h-10 bg-white dark:bg-gray-200 rounded-full flex items-center justify-center shadow-lg">
          <span className="text-xs font-bold text-gray-900">
            {player.number || '?'}
          </span>
        </div>
        {player.is_captain && (
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full flex items-center justify-center">
            <span className="text-xs font-bold text-gray-900">C</span>
          </div>
        )}
        <div className="absolute top-12 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
          <span className="text-xs text-white bg-black/50 px-1 rounded">
            {displayName}
          </span>
        </div>
      </div>
    </div>
  );
};

export default FootballField;
