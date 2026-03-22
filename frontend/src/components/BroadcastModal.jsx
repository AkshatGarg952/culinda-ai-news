import { useState, useEffect } from 'react';
import { triggerBroadcast, generateAiContent } from '../services/api';
import { X, Send, Linkedin, Mail, MessageCircle, FileText, Rss, Eye, Edit3 } from 'lucide-react';

const URL_SPLIT_REGEX = /(https?:\/\/[^\s]+)/g;
const URL_TEST_REGEX = /^https?:\/\//;

// Renders text with proper line breaks and clickable highlighted URLs
function FormattedPreview({ text }) {
  if (!text) return <span className="text-gray-400 italic">No content yet...</span>;


  return (
    <div className="space-y-1">
      {text.split('\n').map((line, lineIdx) => {
        const parts = line.split(URL_SPLIT_REGEX);
        return (
          <p key={lineIdx} className={line.trim() === '' ? 'h-3' : 'leading-relaxed'}>
            {parts.map((part, partIdx) =>
              URL_TEST_REGEX.test(part) ? (
                <a
                  key={partIdx}
                  href={part}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 underline decoration-blue-400 hover:text-blue-800 hover:decoration-blue-600 break-all font-medium transition-colors"
                  onClick={(e) => e.stopPropagation()}
                >
                  {part}
                </a>
              ) : (
                <span key={partIdx}>{part}</span>
              )
            )}
          </p>
        );
      })}
    </div>
  );
}

export default function BroadcastModal({ article, onClose }) {
  const [platform, setPlatform] = useState('linkedin');
  const [content, setContent] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [sent, setSent] = useState(false);
  const [viewMode, setViewMode] = useState('preview'); // 'preview' | 'edit'

  const platforms = [
    { id: 'linkedin', name: 'LinkedIn', icon: Linkedin },
    { id: 'email', name: 'Email', icon: Mail },
    { id: 'whatsapp', name: 'WhatsApp', icon: MessageCircle },
    { id: 'blog', name: 'Blog', icon: FileText },
    { id: 'newsletter', name: 'Newsletter', icon: Rss },
  ];

  useEffect(() => {
    setViewMode('preview');
    if ((platform === 'linkedin' || platform === 'blog') && article.id) {
      handleGenerateAI();
    } else {
      setContent(getDefaultContent(platform));
    }
  }, [platform]);

  const getDefaultContent = (pf) => {
    switch (pf) {
      case 'email':
        return `Subject: ${article.title}\n\nHi,\n\nCheck out this news:\n\n${article.summary || ''}\n\nArticle Link:\n${article.url}\n\nBest regards`;
      case 'whatsapp':
        return `*${article.title}*\n\n${article.summary || ''}\n\nRead more:\n${article.url}`;
      case 'newsletter':
        return `📰 ${article.title}\n\n${article.summary || ''}\n\nFull article:\n${article.url}`;
      default:
        return '';
    }
  };

  const handleGenerateAI = async () => {
    setIsGenerating(true);
    try {
      const endpoint = platform === 'linkedin' ? 'linkedin-caption' : 'blog-paragraph';
      const response = await generateAiContent(endpoint, article.id);
      setContent(response.generated_content);
    } catch (error) {
      setContent(`Failed to generate AI content. Please write manually.\n\n${article.title}\n\n${article.url}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSend = async () => {
    setIsSending(true);
    try {
      if (article.favorite_id) {
        await triggerBroadcast({ favorite_id: article.favorite_id, platform, content });
      }
      
      // Actual broadcast actions for platforms that support deep-linking
      if (platform === 'whatsapp') {
        window.open(`https://wa.me/?text=${encodeURIComponent(content)}`, '_blank');
      } else if (platform === 'linkedin') {
        navigator.clipboard.writeText(content);
        alert("Caption copied to clipboard! Opening LinkedIn so you can paste and post.");
        window.open('https://www.linkedin.com/feed/', '_blank');
      } else if (platform === 'blog') {
        navigator.clipboard.writeText(content);
        alert("Blog content copied to clipboard! You can now paste it into your CMS (e.g., WordPress, Medium).");
      }

      setSent(true);
      setTimeout(onClose, 2000);
    } catch (error) {
      console.error(error);
      setSent(true);
      setTimeout(onClose, 2000);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b border-gray-100">
          <h3 className="text-lg font-medium text-gray-900">Broadcast Story</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
            <X size={20} />
          </button>
        </div>

        <div className="p-6">
          {/* Platform Tabs */}
          <div className="flex space-x-4 mb-6 overflow-x-auto pb-2">
            {platforms.map(p => (
              <button
                key={p.id}
                onClick={() => setPlatform(p.id)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium whitespace-nowrap ${
                  platform === p.id ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:bg-gray-100'
                }`}
              >
                <p.icon size={16} />
                <span>{p.name}</span>
              </button>
            ))}
          </div>

          {/* Content Preview/Edit */}
          <div className="mb-4">
            {/* Label + View/Edit toggle */}
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700 flex items-center gap-2">
                Content Preview
                {isGenerating && (
                  <span className="text-blue-500 text-xs italic ml-1 flex items-center gap-1">
                    <span className="inline-block w-3 h-3 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></span>
                    Generating with AI...
                  </span>
                )}
              </label>
              <div className="flex items-center bg-gray-100 rounded-md p-0.5">
                <button
                  onClick={() => setViewMode('preview')}
                  className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors ${
                    viewMode === 'preview' ? 'bg-white text-blue-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Eye size={12} /> Preview
                </button>
                <button
                  onClick={() => setViewMode('edit')}
                  className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-medium transition-colors ${
                    viewMode === 'edit' ? 'bg-white text-blue-700 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <Edit3 size={12} /> Edit
                </button>
              </div>
            </div>

            {/* Preview Mode */}
            {viewMode === 'preview' ? (
              <div
                className="w-full border border-gray-200 rounded-md bg-gray-50 p-4 text-sm text-gray-800 overflow-y-auto"
                style={{ minHeight: '200px', maxHeight: '280px' }}
              >
                <FormattedPreview text={content} />
              </div>
            ) : (
              /* Edit Mode */
              <textarea
                rows={10}
                className="w-full border border-gray-300 rounded-md shadow-sm p-3 focus:ring-blue-500 focus:border-blue-500 text-sm font-mono"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                disabled={isGenerating}
                placeholder="Edit your content here..."
              />
            )}

            {viewMode === 'edit' && (
              <p className="text-xs text-gray-400 mt-1">
                Switch to Preview to see formatted output with clickable links.
              </p>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 border-t border-gray-100 flex justify-end">
          <button
            onClick={onClose}
            className="bg-white border text-gray-700 px-4 py-2 rounded-md mr-3 text-sm font-medium hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSend}
            disabled={isGenerating || isSending || sent}
            className={`flex items-center space-x-2 px-4 py-2 text-white rounded-md text-sm font-medium ${
              sent ? 'bg-green-600' : 'bg-blue-600 hover:bg-blue-700'
            } disabled:opacity-60`}
          >
            <Send size={16} />
            <span>{sent ? 'Sent Successfully!' : 'Send Broadcast'}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
