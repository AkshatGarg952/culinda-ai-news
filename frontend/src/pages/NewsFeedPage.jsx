import { useState, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { Search, Filter } from 'lucide-react';
import NewsCard from '../components/NewsCard';
import StatsBar from '../components/StatsBar';
import BroadcastModal from '../components/BroadcastModal';
import { getNewsFeed, toggleFavorite, getSources, getFavorites } from '../services/api';

export default function NewsFeedPage() {
  const queryClient = useQueryClient();
  const [keyword, setKeyword] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('date');
  const [page, setPage] = useState(1);
  const [broadcastArticle, setBroadcastArticle] = useState(null);
  const [favoritedIds, setFavoritedIds] = useState(new Map()); // newsItemId -> favoriteId
  const [sourceFilter, setSourceFilter] = useState('');

  // Pre-load all existing favourites from the backend on mount
  useEffect(() => {
    const loadFavorites = async () => {
      try {
        // Fetch up to 200 favourites to cover most cases
        const data = await getFavorites({ page: 1, page_size: 200 });
        const map = new Map();
        (data.items || []).forEach(fav => {
          if (fav.news_item_id) map.set(fav.news_item_id, fav.id);
        });
        setFavoritedIds(map);
      } catch (e) {
        console.error('Failed to load favourites', e);
      }
    };
    loadFavorites();
  }, []);

  const { data: sourcesData } = useQuery({
    queryKey: ['sources'],
    queryFn: getSources,
  });

  const { data, isLoading } = useQuery({
    queryKey: ['newsFeed', searchQuery, sortBy, page, sourceFilter],
    queryFn: () => getNewsFeed({ keyword: searchQuery, sort_by: sortBy, page, page_size: 20, source: sourceFilter || undefined }),
    keepPreviousData: true,
  });

  const handleSearch = (e) => {
    e.preventDefault();
    setSearchQuery(keyword);
    setPage(1);
  };

  const handleFavorite = async (article) => {
    const isFavorited = favoritedIds.has(article.id);
    const favoriteId = favoritedIds.get(article.id) || null;

    // --- Optimistic update: flip the star immediately ---
    if (isFavorited && favoriteId) {
      setFavoritedIds(prev => { const next = new Map(prev); next.delete(article.id); return next; });
    } else {
      setFavoritedIds(prev => new Map(prev).set(article.id, '__pending__'));
    }

    try {
      if (isFavorited && favoriteId) {
        await toggleFavorite(article.id, true, favoriteId);
      } else {
        const result = await toggleFavorite(article.id, false);
        setFavoritedIds(prev => new Map(prev).set(article.id, result.id));
      }
      // Bust the Favorites page cache so it shows fresh data on next visit
      queryClient.invalidateQueries({ queryKey: ['favorites'] });
    } catch (e) {
      console.error(e);
      // --- Revert on failure ---
      if (isFavorited && favoriteId) {
        setFavoritedIds(prev => new Map(prev).set(article.id, favoriteId));
      } else {
        setFavoritedIds(prev => { const next = new Map(prev); next.delete(article.id); return next; });
      }
    }
  };


  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">AI News Dashboard</h1>
        <p className="mt-2 text-gray-600">Curated and automatically deduplicated AI news.</p>
      </div>

      <StatsBar />

      <div className="bg-white p-4 rounded-lg shadow mb-8 flex flex-col md:flex-row justify-between items-center gap-4">
        <form onSubmit={handleSearch} className="flex flex-1 w-full max-w-lg">
          <div className="relative w-full">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              placeholder="Search news by keyword or entity..."
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
            />
          </div>
          <button type="submit" className="ml-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
            Search
          </button>
        </form>

        <div className="flex items-center gap-3 ml-auto">
          <Filter className="h-5 w-5 text-gray-400" />
          <select
            className="block pl-3 pr-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            value={sortBy}
            onChange={(e) => { setSortBy(e.target.value); setPage(1); }}
          >
            <option value="date">Latest First</option>
            <option value="impact">Highest Impact</option>
            <option value="source">By Source</option>
          </select>
          <select
            className="block pl-3 pr-10 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            value={sourceFilter}
            onChange={(e) => { setSourceFilter(e.target.value); setPage(1); }}
          >
            <option value="">All Sources</option>
            {(sourcesData || [])
              .filter((s, idx, arr) => arr.findIndex(x => x.name === s.name) === idx)
              .map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))
            }
          </select>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-64 bg-gray-100 rounded-lg animate-pulse" />
          ))}
        </div>
      ) : data?.items?.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">No news articles found.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {data?.items?.map(article => (
              <NewsCard 
                key={article.id} 
                article={article}
                isFavorited={favoritedIds.has(article.id)}
                onFavoriteToggle={handleFavorite}
                onBroadcastClick={setBroadcastArticle}
              />
            ))}
          </div>
          
          <div className="mt-8 flex justify-center space-x-4">
            <button
              disabled={page === 1}
              onClick={() => setPage(p => p - 1)}
              className="px-4 py-2 border rounded-md disabled:opacity-50"
            >
              Previous
            </button>
            <span className="px-4 py-2">Page {page}</span>
            <button
              disabled={!data?.items || data.items.length < 20}
              onClick={() => setPage(p => p + 1)}
              className="px-4 py-2 border rounded-md disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </>
      )}

      {broadcastArticle && (
        <BroadcastModal 
          article={broadcastArticle} 
          onClose={() => setBroadcastArticle(null)} 
        />
      )}
    </div>
  );
}
