import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { LayoutDashboard, Star, Settings } from 'lucide-react';
import NewsFeedPage from './pages/NewsFeedPage';
import ArticleDetailPage from './pages/ArticleDetailPage';
import FavoritesPage from './pages/FavoritesPage';
import AdminPage from './pages/AdminPage';

function NavigationBar() {
  return (
    <nav className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center cursor-pointer">
              <Link to="/" className="text-xl font-bold text-gray-900 border-none no-underline flex items-center gap-2">
                <span className="text-blue-600">AI</span>News
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <Link to="/" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium gap-2">
                <LayoutDashboard size={18} /> Feed
              </Link>
              <Link to="/favorites" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium gap-2">
                <Star size={18} /> Favorites
              </Link>
              <Link to="/admin" className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium gap-2">
                <Settings size={18} /> Admin
              </Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <NavigationBar />
        <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<NewsFeedPage />} />
            <Route path="/article/:id" element={<ArticleDetailPage />} />
            <Route path="/favorites" element={<FavoritesPage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
