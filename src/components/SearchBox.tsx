import React, { useState } from 'react';
import { Search, Link } from 'lucide-react';

interface SearchBoxProps {
  onSearch: (url: string) => void;
  loading: boolean;
}

export const SearchBox: React.FC<SearchBoxProps> = ({ onSearch, loading }) => {
  const [url, setUrl] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onSearch(url.trim());
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit(e as any);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto animate-slide-up">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Input Group */}
        <div className="relative">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Link className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Pega tu enlace de YouTube, Facebook, Vimeo o TikTok aquí..."
            className="input-field pl-12 text-lg h-14 placeholder:text-gray-400"
            disabled={loading}
            autoComplete="off"
            autoFocus
          />
        </div>

        {/* Search Button */}
        <button
          type="submit"
          disabled={loading || !url.trim()}
          className="btn-primary w-full h-14 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <div className="loading-spinner" />
              Analizando...
            </>
          ) : (
            <>
              <Search className="h-6 w-6" />
              Buscar Video
            </>
          )}
        </button>
      </form>

      {/* Supported Platforms */}
      <div className="mt-8 text-center">
        <p className="text-sm text-gray-500 mb-3">Plataformas soportadas:</p>
        <div className="flex justify-center items-center gap-6 flex-wrap">
          <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">YouTube</span>
          <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">Facebook</span>
          <span className="px-3 py-1 bg-cyan-100 text-cyan-700 rounded-full text-xs font-medium">Vimeo</span>
          <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">TikTok</span>
          <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">+100 más</span>
        </div>
      </div>
    </div>
  );
};