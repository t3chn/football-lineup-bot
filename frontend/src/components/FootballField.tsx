import type { Player } from '../api/client';

interface FootballFieldProps {
  lineup: Player[];
  formation?: string | null;
}

function FootballField({ lineup }: FootballFieldProps) {
  // Position players on the field based on their positions
  const getPlayerPosition = (position: string): { top: string; left: string } => {
    const positions: Record<string, { top: string; left: string }> = {
      GK: { top: '85%', left: '50%' },
      LB: { top: '70%', left: '15%' },
      CB: { top: '70%', left: '35%' },
      RB: { top: '70%', left: '85%' },
      LW: { top: '25%', left: '15%' },
      RW: { top: '25%', left: '85%' },
      CM: { top: '50%', left: '50%' },
      AM: { top: '35%', left: '50%' },
      ST: { top: '15%', left: '50%' },
    };

    // Handle multiple CB positions
    if (position === 'CB') {
      const cbCount = lineup.filter(p => p.position === 'CB').length;
      if (cbCount === 2) {
        const cbIndex = lineup.filter(p => p.position === 'CB').findIndex(p => p.position === position);
        if (cbIndex === 0) return { top: '70%', left: '35%' };
        if (cbIndex === 1) return { top: '70%', left: '65%' };
      }
    }

    // Handle multiple CM positions
    if (position === 'CM') {
      const cmCount = lineup.filter(p => p.position === 'CM').length;
      if (cmCount === 2) {
        const cmIndex = lineup.filter(p => p.position === 'CM').findIndex(p => p.position === position);
        if (cmIndex === 0) return { top: '50%', left: '35%' };
        if (cmIndex === 1) return { top: '50%', left: '65%' };
      }
      if (cmCount === 3) {
        const cmIndex = lineup.filter(p => p.position === 'CM').findIndex(p => p.position === position);
        if (cmIndex === 0) return { top: '50%', left: '25%' };
        if (cmIndex === 1) return { top: '50%', left: '50%' };
        if (cmIndex === 2) return { top: '50%', left: '75%' };
      }
    }

    return positions[position] || { top: '50%', left: '50%' };
  };

  return (
    <div className="relative w-full aspect-[3/4] bg-gradient-to-b from-green-500 to-green-600 rounded-lg overflow-hidden">
      {/* Field markings */}
      <div className="absolute inset-0">
        {/* Center line */}
        <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-white/30" />

        {/* Center circle */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-24 h-24 border-2 border-white/30 rounded-full" />

        {/* Penalty areas */}
        <div className="absolute bottom-0 left-1/4 right-1/4 h-20 border-2 border-t-2 border-b-0 border-white/30" />
        <div className="absolute top-0 left-1/4 right-1/4 h-20 border-2 border-b-2 border-t-0 border-white/30" />
      </div>

      {/* Players */}
      {lineup.map((player, index) => {
        const position = getPlayerPosition(player.position);
        return (
          <div
            key={index}
            className="absolute transform -translate-x-1/2 -translate-y-1/2"
            style={{ top: position.top, left: position.left }}
          >
            <div className="relative">
              <div className="w-10 h-10 bg-white dark:bg-gray-200 rounded-full flex items-center justify-center shadow-lg">
                <span className="text-xs font-bold text-gray-900">
                  {player.number}
                </span>
              </div>
              {player.is_captain && (
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full flex items-center justify-center">
                  <span className="text-xs font-bold text-gray-900">C</span>
                </div>
              )}
              <div className="absolute top-12 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
                <span className="text-xs text-white bg-black/50 px-1 rounded">
                  {player.name.split(' ').pop()}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default FootballField;
