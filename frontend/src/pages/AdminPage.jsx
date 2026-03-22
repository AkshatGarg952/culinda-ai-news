import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { getSources, toggleSource, triggerRefresh } from '../services/api';
import { RefreshCw, Check, X, ShieldAlert } from 'lucide-react';

export default function AdminPage() {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshMessage, setRefreshMessage] = useState('');

  const { data: sources, isLoading, refetch } = useQuery({
    queryKey: ['sources'],
    queryFn: getSources
  });

  const handleToggle = async (id, currentStatus) => {
    try {
      await toggleSource(id, !currentStatus);
      refetch();
    } catch (e) {
      console.error(e);
    }
  };

  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    try {
      await triggerRefresh();
      setRefreshMessage("Ingestion pipeline triggered in the background. Check logs.");
      setTimeout(() => setRefreshMessage(''), 5000);
    } catch (e) {
      setRefreshMessage("Failed to trigger refresh.");
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Configuration</h1>
          <p className="mt-2 text-gray-600">Manage ingestion sources and system state.</p>
        </div>
        
        <div className="flex flex-col items-end">
          <button 
            onClick={handleManualRefresh}
            disabled={isRefreshing}
            className="flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Trigger Fetch Now
          </button>
          {refreshMessage && <span className="text-xs text-green-600 mt-2">{refreshMessage}</span>}
        </div>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-5 sm:px-6 flex justify-between items-center border-b border-gray-200">
          <h3 className="text-lg leading-6 font-medium text-gray-900 flex items-center">
            <ShieldAlert className="w-5 h-5 mr-2 text-indigo-500" />
            Registered Sources
          </h3>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {sources?.length || 0} Total
          </span>
        </div>
        
        {isLoading ? (
          <div className="p-10 flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div></div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source Name</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">URL Setup</th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th scope="col" className="relative px-6 py-3"><span className="sr-only">Toggle</span></th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sources?.map((source) => (
                  <tr key={source.id} className={!source.active ? 'bg-gray-50' : ''}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{source.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 uppercase">
                        {source.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 max-w-xs truncate" title={source.url}>
                      {source.url}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {source.active ? (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Active
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Inactive
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleToggle(source.id, source.active)}
                        className={`inline-flex items-center px-3 py-1 border border-transparent rounded-md shadow-sm text-xs font-medium text-white ${
                          source.active ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'
                        }`}
                      >
                        {source.active ? <><X className="w-4 h-4 mr-1" /> Disable</> : <><Check className="w-4 h-4 mr-1" /> Enable</>}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
