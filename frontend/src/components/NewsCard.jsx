import { formatDistanceToNow } from 'date-fns';
import { Link } from 'react-router-dom';
import { Star, Eye, Share2 } from 'lucide-react';

export default function NewsCard({ article, isFavorited, onFavoriteToggle, onBroadcastClick }) {
  
  const getImpactColor = (score) => {
    if (score >= 0.8) return 'bg-red-100 text-red-800';
    if (score >= 0.5) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden flex flex-col h-full transition-transform hover:scale-[1.01]">
      <div className="p-5 flex-grow">
        <div className="flex justify-between items-start mb-3">
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {article.source_name || 'Source'}
          </span>
          <span className="text-xs text-gray-500">
            {article.published_at ? formatDistanceToNow(new Date(article.published_at), { addSuffix: true }) : 'Unknown'}
          </span>
        </div>
        
        <Link to={`/article/${article.id}`} className="block mt-2">
          <p className="text-xl font-semibold text-gray-900 hover:text-blue-600 line-clamp-2">
            {article.title}
          </p>
        </Link>
        
        <p className="mt-3 text-sm text-gray-600 line-clamp-3">
          {article.summary}
        </p>

        <div className="mt-4 flex flex-wrap gap-2">
          {(article.tags || []).slice(0, 3).map((tag, idx) => (
            <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
              {tag}
            </span>
          ))}
          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getImpactColor(article.impact_score)}`}>
            Impact: {article.impact_score?.toFixed(2)}
          </span>
        </div>
      </div>
      
      <div className="bg-gray-50 px-5 py-3 border-t border-gray-100 flex justify-between items-center">
        <div className="flex space-x-4">
          <button 
            onClick={() => onFavoriteToggle(article)}
            className="text-gray-400 hover:text-yellow-500 transition-colors"
            title="Favorite"
          >
            <Star className={isFavorited ? "fill-yellow-500 text-yellow-500" : ""} size={20} />
          </button>
          
          <Link to={`/article/${article.id}`} className="text-gray-400 hover:text-blue-500 transition-colors" title="View Details">
            <Eye size={20} />
          </Link>
        </div>
        
        {onBroadcastClick && (
          <button 
            onClick={() => onBroadcastClick(article)}
            className="text-gray-400 hover:text-indigo-500 transition-colors"
            title="Broadcast"
          >
            <Share2 size={20} />
          </button>
        )}
      </div>
    </div>
  );
}
