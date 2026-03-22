import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export const getNewsFeed = async (params) => {
  const { data } = await api.get('/news', { params });
  return data;
};

export const getNewsArticle = async (id) => {
  const { data } = await api.get(`/news/${id}`);
  return data;
};

export const summarizeArticle = async (id) => {
  const { data } = await api.post(`/news/${id}/summarize`);
  return data;
};

export const getFavorites = async (params) => {
  const { data } = await api.get('/favorites', { params });
  return data;
};

export const toggleFavorite = async (newsItemId, isFavorited, favoriteId = null) => {
  if (isFavorited && favoriteId) {
    const { data } = await api.delete(`/favorites/${favoriteId}`);
    return data;
  } else {
    const { data } = await api.post('/favorites', { news_item_id: newsItemId });
    return data;
  }
};

export const triggerBroadcast = async (payload) => {
  const { data } = await api.post('/broadcast', payload);
  return data;
};

export const generateAiContent = async (endpoint, newsItemId) => {
  const { data } = await api.post(`/ai/${endpoint}`, { news_item_id: newsItemId });
  return data;
};

export const getSystemStats = async () => {
  const { data } = await api.get('/stats');
  return data;
};

export const triggerRefresh = async () => {
  const { data } = await api.post('/refresh');
  return data;
};

export const getSources = async () => {
  const { data } = await api.get('/sources');
  return data;
};

export const toggleSource = async (id, active) => {
  const { data } = await api.patch(`/sources/${id}`, { active });
  return data;
};
