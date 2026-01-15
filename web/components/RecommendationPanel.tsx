'use client';

import { useState, useEffect } from 'react';
import { FiZap, FiStar } from 'react-icons/fi';
import { Category } from '@/lib/db';

interface RecommendationPanelProps {
  FEATURE_LABELS: Record<string, string>;
  categorySlug?: string;
  category?: Category | null;
}

interface Recommendation {
  rank: number;
  score: number;
  service_name: string;
}

export default function RecommendationPanel({ FEATURE_LABELS, categorySlug, category }: RecommendationPanelProps) {
  const [context, setContext] = useState('');
  const [features, setFeatures] = useState<Record<string, boolean>>({});
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);

  // Initialize context when category changes
  useEffect(() => {
    if (category?.ranking_contexts) {
      const firstContext = Object.keys(category.ranking_contexts)[0];
      setContext(firstContext || '');
      setFeatures({});
    }
  }, [category]);

  const contextOptions = category?.ranking_contexts
    ? Object.entries(category.ranking_contexts).map(([value, info]) => ({
      value,
      label: info.label
    }))
    : [];

  useEffect(() => {
    if (!context || !categorySlug) return;

    async function fetchRecommendations() {
      setLoading(true);
      const params = new URLSearchParams({ context, category: categorySlug });

      Object.entries(features).forEach(([key, value]) => {
        if (value) params.set(key, 'true');
      });

      try {
        const res = await fetch(`/api/recommend?${params}`);
        const data = await res.json();
        setRecommendations(data);
      } catch (error) {
        console.error('Error fetching recommendations:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchRecommendations();
  }, [context, features, categorySlug]);

  const toggleFeature = (key: string) => {
    setFeatures(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  return (
    <div className="card bg-gradient-to-br from-primary-50 to-white border-primary-100">
      <div className="flex items-center gap-2 mb-6">
        <FiZap className="text-primary-600" size={24} />
        <h2 className="text-2xl font-bold text-gray-900">Find Your Perfect {category?.name.replace(' Apps', '') || 'Service'}</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Use Case
            </label>
            <select
              value={context}
              onChange={(e) => setContext(e.target.value)}
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="" disabled>Select use case...</option>
              {contextOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-700">
              Must-Have Features
            </label>
            {Object.entries(FEATURE_LABELS).slice(0, 6).map(([key, label]) => (
              <label key={key} className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={!!features[key]}
                  onChange={() => toggleFeature(key)}
                  className="w-5 h-5 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-gray-700">{label}</span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-3">Recommended For You</h3>
          <div className="space-y-3">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="w-8 h-8 border-3 border-primary-200 border-t-primary-600 rounded-full animate-spin" />
              </div>
            ) : recommendations.length > 0 ? (
              recommendations.slice(0, 5).map((rec, index) => (
                <div
                  key={index}
                  className={`
                    flex items-center justify-between p-3 rounded-lg border-2
                    ${index === 0
                      ? 'border-yellow-400 bg-yellow-50'
                      : 'border-gray-100 bg-white'
                    }
                  `}
                >
                  <div className="flex items-center gap-3">
                    {index === 0 && <FiStar className="text-yellow-500" size={20} />}
                    <div>
                      <h4 className="font-semibold text-gray-900">{rec.service_name}</h4>
                      <p className="text-xs text-gray-500">Rank #{rec.rank}</p>
                    </div>
                  </div>
                  <span className="text-lg font-bold text-primary-600">{rec.score.toFixed(1)}</span>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">
                No services match your exact criteria. Try removing some filters.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

