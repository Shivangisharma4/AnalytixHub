'use client';

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Cell,
} from 'recharts';

interface Service {
  id: number;
  name: string;
  url: string;
  pricing: string | null;
  platforms: string;
  features: Record<string, boolean>;
  additional_features: string[];
}

interface FeatureChartProps {
  services: Service[];
  FEATURE_LABELS: Record<string, string>;
}

const COLORS = [
  '#0ea5e9', // primary-500
  '#8b5cf6', // violet-500
  '#10b981', // emerald-500
  '#f59e0b', // amber-500
  '#ef4444', // red-500
  '#ec4899', // pink-500
];

export default function FeatureChart({ services, FEATURE_LABELS }: FeatureChartProps) {
  const totalFeaturesCount = Object.keys(FEATURE_LABELS).length;
  // Prepare data for radar chart - top 5 services
  const topServices = services.slice(0, 5);

  const radarData = Object.entries(FEATURE_LABELS).map(([key, label]) => {
    const data: any = { feature: label };
    topServices.forEach((service, index) => {
      data[service.name] = service.features[key] ? 1 : 0;
    });
    return data;
  });

  // Prepare data for feature availability bar chart
  const featureAvailability = Object.entries(FEATURE_LABELS).map(([key, label]) => {
    const count = services.filter(s => s.features[key]).length;
    return {
      feature: label.replace(' ', '\n'),
      count,
      percentage: Math.round((count / services.length) * 100),
    };
  }).sort((a, b) => b.count - a.count);

  // Prepare data for service feature count
  const serviceFeatureCount = services.map(service => {
    // Only count features that are in the current category's schema
    const relevantKeys = Object.keys(FEATURE_LABELS);
    const count = Object.entries(service.features).filter(([key, val]) => relevantKeys.includes(key) && val).length;
    return {
      name: service.name,
      count: count,
    };
  }).sort((a, b) => b.count - a.count);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Radar Chart - Top Services Comparison */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Services Feature Comparison</h3>
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#e5e7eb" />
            <PolarAngleAxis dataKey="feature" tick={{ fill: '#6b7280', fontSize: 11 }} />
            <PolarRadiusAxis angle={90} domain={[0, 1]} tick={false} />
            {topServices.map((service, index) => (
              <Radar
                key={service.id}
                name={service.name}
                dataKey={service.name}
                stroke={COLORS[index % COLORS.length]}
                fill={COLORS[index % COLORS.length]}
                fillOpacity={0.2}
                strokeWidth={2}
              />
            ))}
            <Legend />
            <Tooltip
              formatter={(value: number) => (value ? 'Available' : 'Not Available')}
              contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Bar Chart - Feature Availability Across Services */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Feature Availability</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={featureAvailability} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis type="number" domain={[0, services.length]} tick={{ fill: '#6b7280' }} />
            <YAxis
              type="category"
              dataKey="feature"
              tick={{ fill: '#6b7280', fontSize: 11 }}
              width={80}
            />
            <Tooltip
              formatter={(value: number, name: string, props: any) => [
                `${value} services (${props.payload.percentage}%)`,
                'Has Feature'
              ]}
              contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
            <Bar dataKey="count" radius={[0, 4, 4, 0]}>
              {featureAvailability.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Feature Count by Service */}
      <div className="card lg:col-span-2">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Feature Count by Service</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={serviceFeatureCount}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="name"
              tick={{ fill: '#6b7280', fontSize: 11 }}
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis domain={[0, totalFeaturesCount]} tick={{ fill: '#6b7280' }} />
            <Tooltip
              formatter={(value: number) => [`${value}/${totalFeaturesCount} features`, 'Total']}
              contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
            <Bar dataKey="count" radius={[4, 4, 0, 0]} fill="#0ea5e9" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
