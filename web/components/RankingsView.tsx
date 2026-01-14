'use client';

import { FiAward, FiStar } from 'react-icons/fi';

interface RankingsViewProps {
  rankings: {
    [context: string]: Array<{
      rank: number;
      score: number;
      service_name: string;
    }>;
  };
  CONTEXT_LABELS: Record<string, string>;
}

const getRankColor = (rank: number) => {
  if (rank === 1) return 'text-yellow-500';
  if (rank === 2) return 'text-gray-400';
  if (rank === 3) return 'text-amber-600';
  return 'text-gray-300';
};

const getRankIcon = (rank: number) => {
  if (rank <= 3) return FiAward;
  return null;
};

export default function RankingsView({ rankings, CONTEXT_LABELS }: RankingsViewProps) {
  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Service Rankings</h2>
        <p className="text-gray-600">Rankings based on different use cases and requirements</p>
      </div>

      {Object.entries(rankings).map(([context, items]) => (
        <div key={context} className="card">
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <FiStar className="text-primary-500" />
            {CONTEXT_LABELS[context] || context}
          </h3>

          <div className="space-y-3">
            {items.map((item, index) => {
              const RankIcon = getRankIcon(item.rank);
              return (
                <div
                  key={index}
                  className={`
                    flex items-center justify-between p-4 rounded-lg border-2 transition-all
                    ${item.rank === 1
                      ? 'border-yellow-400 bg-yellow-50'
                      : item.rank === 2
                        ? 'border-gray-300 bg-gray-50'
                        : item.rank === 3
                          ? 'border-amber-500 bg-amber-50'
                          : 'border-gray-100 hover:border-gray-200'
                    }
                  `}
                >
                  <div className="flex items-center gap-4">
                    <div className={`text-2xl font-bold ${getRankColor(item.rank)} w-10 text-center`}>
                      {RankIcon ? <RankIcon size={28} /> : item.rank}
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{item.service_name}</h4>
                      <p className="text-sm text-gray-500">Rank #{item.rank}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-primary-600">{item.score.toFixed(1)}</p>
                    <p className="text-xs text-gray-500">Score</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
