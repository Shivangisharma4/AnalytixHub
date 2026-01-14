'use client';

import { useState, useEffect } from 'react';
import Header from './Header';
import RankingsView from './RankingsView';
import ComparisonView from './ComparisonView';
import ServiceCards from './ServiceCards';
import RecommendationPanel from './RecommendationPanel';
import FeatureChart from './FeatureChart';

type View = 'overview' | 'rankings' | 'compare' | 'services';

export interface Service {
  id: number;
  name: string;
  url: string;
  pricing: string | null;
  platforms: string;
  features: Record<string, boolean>;
  additional_features: string[];
}

export interface Rankings {
  [context: string]: Array<{
    rank: number;
    score: number;
    service_name: string;
  }>;
}

export interface ComparisonData {
  [service: string]: {
    [feature: string]: boolean;
  };
}

const FEATURE_LABELS: Record<string, string> = {
  free_tier: 'Free Tier',
  collaboration: 'Collaboration',
  reminders: 'Reminders',
  due_dates: 'Due Dates',
  tags_labels: 'Tags/Labels',
  subtasks: 'Subtasks',
  attachments: 'Attachments',
  offline_mode: 'Offline Mode',
  calendar_view: 'Calendar View',
  integrations: 'Integrations',
  api_available: 'API',
};

const CONTEXT_LABELS: Record<string, string> = {
  personal_use: 'Personal Use',
  team_collaboration: 'Team Collaboration',
  enterprise: 'Enterprise',
  minimalist: 'Minimalist',
};

export default function Dashboard() {
  const [view, setView] = useState<View>('overview');
  const [services, setServices] = useState<Service[]>([]);
  const [rankings, setRankings] = useState<Rankings>({});
  const [comparison, setComparison] = useState<ComparisonData>({});
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const [servicesRes, rankingsRes, compareRes] = await Promise.all([
          fetch('/api/services'),
          fetch('/api/rankings'),
          fetch('/api/compare'),
        ]);

        const [servicesData, rankingsData, compareData] = await Promise.all([
          servicesRes.json(),
          rankingsRes.json(),
          compareRes.json(),
        ]);

        setServices(servicesData);
        setRankings(rankingsData);
        setComparison(compareData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  const filteredServices = services.filter(service =>
    service.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    service.additional_features.some(f =>
      f.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-white">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading rankings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white">
      <Header view={view} setView={setView} searchQuery={searchQuery} setSearchQuery={setSearchQuery} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {view === 'overview' && (
          <div className="space-y-8">
            <div className="text-center mb-12">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                Todo Service Rankings
              </h1>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Compare and find the best todo list service based on features, pricing, and your specific needs.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              {Object.entries(CONTEXT_LABELS).map(([key, label]) => {
                const topService = rankings[key]?.[0];
                return (
                  <div key={key} className="card cursor-pointer hover:shadow-md transition-shadow">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">{label}</h3>
                    <p className="text-2xl font-bold text-primary-600">{topService?.service_name || 'N/A'}</p>
                    <p className="text-sm text-gray-600 mt-1">Score: {topService?.score.toFixed(1) || 0}</p>
                  </div>
                );
              })}
            </div>

            <FeatureChart services={services} FEATURE_LABELS={FEATURE_LABELS} />

            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Top Services</h2>
              <ServiceCards services={services.slice(0, 6)} FEATURE_LABELS={FEATURE_LABELS} />
            </div>

            <RecommendationPanel FEATURE_LABELS={FEATURE_LABELS} />
          </div>
        )}

        {view === 'rankings' && (
          <RankingsView rankings={rankings} CONTEXT_LABELS={CONTEXT_LABELS} />
        )}

        {view === 'compare' && (
          <ComparisonView
            services={services}
            comparison={comparison}
            FEATURE_LABELS={FEATURE_LABELS}
          />
        )}

        {view === 'services' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">All Services</h2>
            <ServiceCards services={filteredServices} FEATURE_LABELS={FEATURE_LABELS} />
          </div>
        )}
      </main>

      <footer className="mt-16 py-8 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600">
          <p>Todo Service Rankings - Feature comparison and recommendations</p>
          <p className="text-sm mt-2">Last updated: {new Date().toLocaleDateString()}</p>
        </div>
      </footer>
    </div>
  );
}

export { FEATURE_LABELS, CONTEXT_LABELS };
