'use client';

import { useState, useEffect } from 'react';
import Header from './Header';
import RankingsView from './RankingsView';
import ComparisonView from './ComparisonView';
import ServiceCards from './ServiceCards';
import RecommendationPanel from './RecommendationPanel';
import FeatureChart from './FeatureChart';
import { getCategories, getAllServicesWithFeatures, getFeatureComparison, Category } from '@/lib/db';

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

export default function Dashboard() {
  const [view, setView] = useState<View>('overview');
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [services, setServices] = useState<Service[]>([]);
  const [rankings, setRankings] = useState<Rankings>({});
  const [comparison, setComparison] = useState<ComparisonData>({});
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Initial fetch: Categories
  useEffect(() => {
    async function initCategories() {
      try {
        const cats = await getCategories();
        setCategories(cats);
        if (cats.length > 0) {
          setSelectedCategory(cats[0]);
        }
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    }
    initCategories();
  }, []);

  // Fetch data when category changes
  useEffect(() => {
    if (!selectedCategory) return;

    async function fetchData() {
      try {
        setLoading(true);
        const [servicesData, compareData] = await Promise.all([
          getAllServicesWithFeatures(selectedCategory!.slug),
          getFeatureComparison(selectedCategory!.slug),
        ]);

        // Fetch rankings for each context defined in the category
        const contexts = Object.keys(selectedCategory!.ranking_contexts);
        const rankingsData: Rankings = {};

        await Promise.all(
          contexts.map(async (context) => {
            const res = await fetch(`/api/rankings/${context}`);
            if (res.ok) {
              rankingsData[context] = await res.json();
            }
          })
        );

        setServices(servicesData);
        setRankings(rankingsData);
        setComparison(compareData);
      } catch (error) {
        console.error('Error fetching category data:', error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [selectedCategory]);

  const filteredServices = services.filter(service =>
    service.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    service.additional_features.some(f =>
      f.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  // Derive labels from selected category
  const featureLabels: Record<string, string> = {};
  if (selectedCategory) {
    Object.entries(selectedCategory.feature_schema).forEach(([key, val]) => {
      featureLabels[key] = val.label;
    });
  }

  const contextLabels: Record<string, string> = {};
  if (selectedCategory) {
    Object.entries(selectedCategory.ranking_contexts).forEach(([key, val]) => {
      contextLabels[key] = val.label;
    });
  }

  if (loading && categories.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-white">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing ServiceRank...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white">
      <Header
        view={view}
        setView={setView}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        categories={categories}
        selectedCategory={selectedCategory}
        setSelectedCategory={setSelectedCategory}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {view === 'overview' && (
          <div className="space-y-8">
            <div className="text-center mb-12">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                {selectedCategory?.name || 'Service Rankings'}
              </h1>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                {selectedCategory?.description || 'Compare and find the best services for your needs.'}
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {Object.entries(contextLabels).map(([key, label]) => {
                const topService = rankings[key]?.[0];
                return (
                  <div key={key} className="card cursor-pointer hover:shadow-md transition-shadow">
                    <h3 className="text-sm font-medium text-gray-500 mb-2">{label}</h3>
                    <p className="text-2xl font-bold text-primary-600 truncate">{topService?.service_name || 'N/A'}</p>
                    <p className="text-sm text-gray-600 mt-1">Score: {topService?.score.toFixed(1) || 0}</p>
                  </div>
                );
              })}
            </div>

            {loading ? (
              <div className="py-12 text-center text-gray-500 italic">Updating statistics...</div>
            ) : (
              <>
                <FeatureChart services={services} FEATURE_LABELS={featureLabels} />

                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Top Rated</h2>
                  <ServiceCards services={services.slice(0, 6)} FEATURE_LABELS={featureLabels} />
                </div>

                <RecommendationPanel
                  FEATURE_LABELS={featureLabels}
                  categorySlug={selectedCategory?.slug}
                  category={selectedCategory}
                />
              </>
            )}
          </div>
        )}

        {view === 'rankings' && (
          <RankingsView rankings={rankings} CONTEXT_LABELS={contextLabels} />
        )}

        {view === 'compare' && (
          <ComparisonView
            services={services}
            comparison={comparison}
            FEATURE_LABELS={featureLabels}
          />
        )}

        {view === 'services' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">All {selectedCategory?.name}</h2>
            <ServiceCards services={filteredServices} FEATURE_LABELS={featureLabels} />
          </div>
        )}
      </main>

      <footer className="mt-16 py-12 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-600">
          <p className="font-semibold text-gray-900 mb-2">ServiceRank</p>
          <p className="text-sm max-w-md mx-auto mb-6">
            High-fidelity feature comparison and data-driven recommendations for modern software services.
          </p>

          <div className="flex flex-col md:flex-row items-center justify-center gap-4 text-sm border-t border-gray-100 pt-6">
            <p>© {new Date().getFullYear()} Shivangi. All rights reserved.</p>
            <span className="hidden md:inline text-gray-300">|</span>
            <p className="flex items-center justify-center gap-1.5">
              Made with <span className="text-red-500 animate-pulse">❤️</span> by <span className="font-bold text-gray-900">Shivangi</span>
            </p>
          </div>

          <p className="text-xs text-gray-400 mt-6 italic">Last updated: {new Date().toLocaleDateString()}</p>
        </div>
      </footer>
    </div>
  );
}

