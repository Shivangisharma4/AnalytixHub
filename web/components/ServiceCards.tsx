'use client';

import { FiCheck, FiExternalLink, FiTag } from 'react-icons/fi';

interface Service {
  id: number;
  name: string;
  url: string;
  pricing: string | null;
  platforms: string;
  features: Record<string, boolean>;
  additional_features: string[];
}

interface ServiceCardsProps {
  services: Service[];
  FEATURE_LABELS: Record<string, string>;
}

export default function ServiceCards({ services, FEATURE_LABELS }: ServiceCardsProps) {
  const totalFeaturesCount = Object.keys(FEATURE_LABELS).length;
  const getPlatformIcons = (platforms: string) => {
    try {
      const parsed = JSON.parse(platforms);
      return Array.isArray(parsed) ? parsed : ['web'];
    } catch {
      return ['web'];
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {services.map(service => {
        // Only count features that are in the current category's schema
        const relevantKeys = Object.keys(FEATURE_LABELS);
        const featureCount = Object.entries(service.features).filter(([key, val]) => relevantKeys.includes(key) && val).length;
        const platforms = getPlatformIcons(service.platforms);

        return (
          <div key={service.id} className="card hover:shadow-lg transition-shadow group">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
                  {service.name}
                </h3>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-sm text-gray-500">{service.pricing || 'Contact for pricing'}</span>
                </div>
              </div>
              <a
                href={service.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-primary-600 transition-colors"
              >
                <FiExternalLink size={18} />
              </a>
            </div>

            <div className="flex items-center gap-2 mb-4">
              {platforms.map(platform => (
                <span
                  key={platform}
                  className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-md capitalize"
                >
                  {platform}
                </span>
              ))}
            </div>

            <div className="mb-4">
              <div className="flex items-center justify-between text-sm mb-2">
                <span className="text-gray-600">Features</span>
                <span className="font-semibold text-primary-600">{featureCount}/{totalFeaturesCount}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all"
                  style={{ width: `${(featureCount / (totalFeaturesCount || 1)) * 100}%` }}
                />
              </div>
            </div>

            <div className="space-y-2">
              {Object.entries(FEATURE_LABELS).slice(0, 5).map(([key, label]) => (
                <div key={key} className="flex items-center gap-2 text-sm">
                  {service.features[key] ? (
                    <FiCheck className="text-green-500 flex-shrink-0" size={16} />
                  ) : (
                    <span className="w-4 h-4 flex-shrink-0" />
                  )}
                  <span className={service.features[key] ? 'text-gray-700' : 'text-gray-400'}>
                    {label}
                  </span>
                </div>
              ))}
            </div>

            {service.additional_features.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                <div className="flex items-center gap-1 text-xs text-gray-500 mb-2">
                  <FiTag size={12} />
                  <span>Unique features</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {service.additional_features.slice(0, 3).map((feature, i) => (
                    <span
                      key={i}
                      className="px-2 py-1 bg-primary-50 text-primary-700 text-xs rounded"
                    >
                      {feature}
                    </span>
                  ))}
                  {service.additional_features.length > 3 && (
                    <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                      +{service.additional_features.length - 3}
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
