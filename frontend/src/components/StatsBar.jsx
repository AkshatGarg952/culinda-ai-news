import { useQuery } from '@tanstack/react-query';
import { getSystemStats } from '../services/api';
import { Activity, Database, CheckCircle, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function StatsBar() {
  const { data, isLoading } = useQuery({
    queryKey: ['systemStats'],
    queryFn: getSystemStats
  });

  if (isLoading || !data) {
    return <div className="h-64 bg-gray-100 rounded-lg animate-pulse mb-8" />;
  }

  const metrics = [
    { label: 'Total Articles', value: data.total_articles, icon: Database, color: 'text-blue-500' },
    { label: 'Active Sources', value: `${data.active_sources}/${data.total_sources}`, icon: Activity, color: 'text-green-500' },
    { label: 'Dedup Precision', value: `${data.dedup_rate_percentage}%`, icon: CheckCircle, color: 'text-purple-500' },
    { label: 'Avg Impact', value: data.average_impact.toFixed(2), icon: TrendingUp, color: 'text-orange-500' },
  ];
  
  const chartData = [
    { name: 'Articles', val: data.total_articles },
    { name: 'Duplicates Blocked', val: Math.floor(data.total_articles * (data.dedup_rate_percentage / 100)) }
  ];

  return (
    <div className="mb-8 flex flex-col gap-4">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((item, index) => (
          <div key={index} className="bg-white rounded-lg shadow p-6 flex items-center">
            <div className={`p-3 rounded-full bg-opacity-10 mr-4 ${item.color.replace('text-', 'bg-')}`}>
              <item.icon className={`h-6 w-6 ${item.color}`} />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">{item.label}</p>
              <p className="text-2xl font-semibold text-gray-900">{item.value}</p>
            </div>
          </div>
        ))}
      </div>
      
      <div className="bg-white rounded-lg shadow p-6 h-64">
        <h3 className="text-sm font-medium text-gray-500 mb-4">Ingestion vs Duplication Pipeline</h3>
        <ResponsiveContainer width="100%" height="80%">
          <BarChart data={chartData}>
            <XAxis dataKey="name" stroke="#8884d8" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="val" fill="#4f46e5" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
