import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { getNewsArticle, summarizeArticle, toggleFavorite, getFavorites } from '../services/api';
import { format } from 'date-fns';
import { Share2, Star, ExternalLink, ArrowLeft, Bot, Zap } from 'lucide-react';
import BroadcastModal from '../components/BroadcastModal';

export default function ArticleDetailPage() {
  const { id } = useParams();
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [aiSummary, setAiSummary] = useState(null);
  const [showBroadcast, setShowBroadcast] = useState(false);
  const [isFavorited, setIsFavorited] = useState(false);
  const [favoriteRecordId, setFavoriteRecordId] = useState(null);

  // Check if article is already in favourites on mount
  useEffect(() => {
    if (!id) return;
    getFavorites({ page: 1, page_size: 200 })
      .then(data => {
        const match = (data.items || []).find(f => f.news_item_id === id);
        if (match) {
          setIsFavorited(true);
          setFavoriteRecordId(match.id);
        }
      })
      .catch(() => {});
  }, [id]);

  const { data: article, isLoading, refetch } = useQuery({
    queryKey: ['article', id],
    queryFn: () => getNewsArticle(id),
  });

  const handleSummarize = async () => {
    setIsSummarizing(true);
    try {
      const res = await summarizeArticle(id);
      setAiSummary(res.generated_content);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSummarizing(false);
    }
  };

  const handleFavorite = async () => {
    try {
      if (isFavorited && favoriteRecordId) {
        await toggleFavorite(id, true, favoriteRecordId);
        setIsFavorited(false);
        setFavoriteRecordId(null);
      } else {
        const result = await toggleFavorite(id, false);
        setIsFavorited(true);
        setFavoriteRecordId(result.id);
      }
    } catch (e) {
      console.error(e);
    }
  };

  if (isLoading) return <div className="animate-pulse h-96 bg-gray-100 rounded-lg"></div>;
  if (!article) return <div className="text-center py-10">Article not found</div>;

  return (
    <div className="max-w-4xl mx-auto">
      <Link to="/" className="inline-flex items-center text-sm font-medium text-blue-600 hover:text-blue-500 mb-6">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Feed
      </Link>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex space-x-2">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                Source
              </span>
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                <Zap className="w-4 h-4 mr-1" />
                Impact: {article.impact_score?.toFixed(2)}
              </span>
            </div>
            <span className="text-sm text-gray-500">
              {article.published_at ? format(new Date(article.published_at), 'PPP') : 'Unknown Date'}
            </span>
          </div>

          <h1 className="text-3xl font-bold text-gray-900 mb-4 tracking-tight">{article.title}</h1>
          
          <div className="flex items-center justify-between border-b border-gray-200 pb-6 mb-6">
            <span className="text-gray-600 font-medium">By {article.author || 'Unknown Author'}</span>
            
            <div className="flex space-x-4">
              <button onClick={handleFavorite} className={`flex items-center px-4 py-2 rounded-md transition-colors ${
                isFavorited
                  ? 'text-yellow-600 bg-yellow-50 hover:bg-yellow-100'
                  : 'text-gray-500 hover:text-yellow-500 bg-gray-50'
              }`}>
                <Star className={`w-5 h-5 mr-2 ${isFavorited ? 'fill-yellow-500 text-yellow-500' : ''}`} />
                {isFavorited ? 'Favourited' : 'Favourite'}
              </button>
              <button onClick={() => setShowBroadcast(true)} className="flex items-center justify-center text-white bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md">
                <Share2 className="w-5 h-5 mr-2" /> Broadcast
              </button>
            </div>
          </div>

          <div className="prose max-w-none text-gray-700 text-lg leading-relaxed mb-8">
            {article.summary}
          </div>

          <div className="flex flex-wrap gap-2 mb-8">
            {article.tags?.map((tag, idx) => (
              <span key={idx} className="inline-flex items-center px-3 py-1 rounded-md text-sm font-medium bg-gray-100 text-gray-800">
                #{tag}
              </span>
            ))}
          </div>

          {/* AI Feature Box */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100 rounded-lg p-6 mb-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Bot className="w-5 h-5 mr-2 text-blue-600" />
                AI Summary
              </h3>
              {!aiSummary && (
                <button 
                  onClick={handleSummarize}
                  disabled={isSummarizing}
                  className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-50 shadow-sm"
                >
                  {isSummarizing ? 'Generating...' : 'Generate AI Summary'}
                </button>
              )}
            </div>
            {aiSummary ? (
              <p className="text-gray-800 italic border-l-4 border-blue-400 pl-4">{aiSummary}</p>
            ) : (
              <p className="text-gray-500 text-sm">Click the button to generate a 2-sentence AI summary of this article.</p>
            )}
          </div>

          <div className="flex justify-center border-t border-gray-200 pt-8">
            <a 
              href={article.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-gray-900 hover:bg-gray-800"
            >
              Read Original Source <ExternalLink className="ml-2 w-5 h-5" />
            </a>
          </div>
        </div>
      </div>

      {showBroadcast && <BroadcastModal article={article} onClose={() => setShowBroadcast(false)} />}
    </div>
  );
}
