'use client';

import { useState } from 'react';
import { FiCheck, FiX } from 'react-icons/fi';

interface Service {
  id: number;
  name: string;
  url: string;
  pricing: string | null;
  platforms: string;
  features: Record<string, boolean>;
  additional_features: string[];
}

interface ComparisonViewProps {
  services: Service[];
  comparison: {
    [service: string]: {
      [feature: string]: boolean;
    };
  };
  FEATURE_LABELS: Record<string, string>;
}

export default function ComparisonView({ services, comparison, FEATURE_LABELS }: ComparisonViewProps) {
  const [selectedServices, setSelectedServices] = useState<string[]>([]);
  const [filterFeatures, setFilterFeatures] = useState<string[]>([]);

  // Reset filters when category changes
  useEffect(() => {
    setFilterFeatures(Object.keys(FEATURE_LABELS));
  }, [FEATURE_LABELS]);

  const toggleService = (serviceName: string) => {
    setSelectedServices(prev =>
      prev.includes(serviceName)
        ? prev.filter(s => s !== serviceName)
        : prev.length < 4 ? [...prev, serviceName] : prev
    );
  };

  const toggleFeature = (feature: string) => {
    setFilterFeatures(prev =>
      prev.includes(feature)
        ? prev.filter(f => f !== feature)
        : [...prev, feature]
    );
  };

  const displayServices = selectedServices.length > 0
    ? services.filter(s => selectedServices.includes(s.name))
    : services.slice(0, 4);

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Feature Comparison</h2>
        <p className="text-gray-600">Compare features side by side</p>
      </div>

      {/* Service selector */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-3">Select Services to Compare (max 4)</h3>
        <div className="flex flex-wrap gap-2">
          {services.map(service => (
            <button
              key={service.id}
              onClick={() => toggleService(service.name)}
              className={`
                px-4 py-2 rounded-lg font-medium transition-all
                ${selectedServices.includes(service.name)
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
              `}
            >
              {service.name}
            </button>
          ))}
        </div>
      </div>

      {/* Feature filter */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-3">Filter Features</h3>
        <div className="flex flex-wrap gap-2">
          {Object.entries(FEATURE_LABELS).map(([key, label]) => (
            <button
              key={key}
              onClick={() => toggleFeature(key)}
              className={`
                px-3 py-1 rounded-full text-sm transition-all
                ${filterFeatures.includes(key)
                  ? 'bg-primary-100 text-primary-700 border border-primary-300'
                  : 'bg-gray-100 text-gray-500'
                }
              `}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Comparison table */}
      <div className="card overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 font-semibold text-gray-900">Feature</th>
              {displayServices.map(service => (
                <th key={service.id} className="text-center py-3 px-4 font-semibold text-gray-900">
                  {service.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Object.entries(FEATURE_LABELS)
              .filter(([key]) => filterFeatures.includes(key))
              .map(([key, label]) => (
                <tr key={key} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 font-medium text-gray-700">{label}</td>
                  {displayServices.map(service => {
                    const hasFeature = service.features[key];
                    return (
                      <td key={service.id} className="text-center py-3 px-4">
                        {hasFeature ? (
                          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-green-100 text-green-600">
                            <FiCheck size={18} />
                          </span>
                        ) : (
                          <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-red-100 text-red-400">
                            <FiX size={18} />
                          </span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {/* Pricing comparison */}
      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-4">Pricing</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {displayServices.map(service => (
            <div key={service.id} className="p-4 bg-gray-50 rounded-lg">
              <h4 className="font-semibold text-gray-900 mb-2">{service.name}</h4>
              <p className="text-primary-600 font-bold">{service.pricing || 'Contact for pricing'}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
