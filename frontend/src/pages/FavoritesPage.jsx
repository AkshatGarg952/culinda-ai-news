import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getFavorites, toggleFavorite, generateAiContent } from '../services/api';
import NewsCard from '../components/NewsCard';
import BroadcastModal from '../components/BroadcastModal';
import { Share2 } from 'lucide-react';

export default function FavoritesPage() {
  const [page, setPage] = useState(1);
  const [broadcastArticle, setBroadcastArticle] = useState(null);
  const [newsletterContent, setNewsletterContent] = useState(null);
  const [isGeneratingDigest, setIsGeneratingDigest] = useState(false);


  const { data, isLoading, refetch } = useQuery({
    queryKey: ['favorites', page],
    queryFn: () => getFavorites({ page, page_size: 20 }),
    keepPreviousData: true,
    staleTime: 0,          // always consider data stale
    refetchOnMount: true,  // re-fetch every time the page is visited
  });

  const handleUnfavorite = async (article) => {
    const favItem = data.items.find(f => f.news_item.id === article.id);
    if (favItem) {
      await toggleFavorite(article.id, true, favItem.id);
      refetch();
    }
  };

  const handleBroadcastAll = async () => {
    if (!data?.items?.length) return;
    setIsGeneratingDigest(true);
    try {
      const ids = data.items.map(f => f.news_item.id);
      const res = await fetch('/api/ai/newsletter-digest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ news_item_ids: ids }),
      });
      const json = await res.json();
      setNewsletterContent(json.generated_content || data.items.map(f => `• ${f.news_item.title}\n  ${f.news_item.url}`).join('\n\n'));
    } catch {
      setNewsletterContent(data.items.map(f => `• ${f.news_item.title}\n  ${f.news_item.url}`).join('\n\n'));
    } finally {
      setIsGeneratingDigest(false);
    }
  };

  const mapToArticle = (favorite) => ({
    ...favorite.news_item,
    favorite_id: favorite.id
  });

  return (
    <div>
      <div className="mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Favorites</h1>
          <p className="mt-2 text-gray-600">Your saved AI news ready for broadcasting.</p>
        </div>
        <button
          onClick={handleBroadcastAll}
          disabled={isGeneratingDigest || !data?.items?.length}
          className="flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
        >
          <Share2 className="w-4 h-4 mr-2" />
          {isGeneratingDigest ? 'Generating...' : 'Broadcast All (Newsletter)'}
        </button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-64 bg-gray-100 rounded-lg animate-pulse" />
          ))}
        </div>
      ) : data?.items?.length === 0 ? (
        <div className="text-center py-16 bg-white shadow rounded-lg">
          <p className="text-gray-500 text-lg">You haven't favorited any articles yet.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {data?.items?.map(fav => (
            <NewsCard 
              key={fav.id} 
              article={mapToArticle(fav)}
              isFavorited={true}
              onFavoriteToggle={handleUnfavorite}
              onBroadcastClick={setBroadcastArticle}
            />
          ))}
        </div>
      )}

      {broadcastArticle && (
        <BroadcastModal article={broadcastArticle} onClose={() => setBroadcastArticle(null)} />
      )}

      {newsletterContent && (
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-lg font-semibold text-gray-900">Newsletter Digest</h3>
            <button onClick={() => setNewsletterContent(null)} className="text-gray-400 hover:text-gray-600 text-sm">Dismiss</button>
          </div>
          <textarea
            rows={12}
            readOnly
            className="w-full border border-gray-200 rounded-md p-3 text-sm text-gray-700 bg-gray-50"
            value={newsletterContent}
          />
          <button
            onClick={() => { navigator.clipboard.writeText(newsletterContent); }}
            className="mt-3 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700"
          >
            Copy to Clipboard
          </button>
        </div>
      )}
    </div>
  );
}
