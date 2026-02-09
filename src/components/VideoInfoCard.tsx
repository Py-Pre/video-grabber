import React from 'react';
import { Clock, Eye, ExternalLink } from 'lucide-react';
import { VideoInfo } from '../types';

interface VideoInfoCardProps {
  videoInfo: VideoInfo;
}

export const VideoInfoCard: React.FC<VideoInfoCardProps> = ({ videoInfo }) => {
  const formatDuration = (seconds?: number): string => {
    if (!seconds) return '--:--';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const getDomain = (url: string): string => {
    try {
      const domain = new URL(url).hostname.replace('www.', '');
      return domain.charAt(0).toUpperCase() + domain.slice(1);
    } catch {
      return 'Fuente desconocida';
    }
  };

  return (
    <div className="card animate-slide-up">
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Thumbnail */}
        <div className="lg:col-span-1">
          <div className="relative aspect-video w-full rounded-xl overflow-hidden bg-gray-100">
            {videoInfo.thumbnail ? (
              <img
                src={videoInfo.thumbnail}
                alt="Video thumbnail"
                className="w-full h-full object-cover"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                  target.nextElementSibling?.classList.remove('hidden');
                }}
              />
            ) : null}
            <div className={`${videoInfo.thumbnail ? 'hidden' : ''} absolute inset-0 flex items-center justify-center`}>
              <div className="text-gray-400">
                <Eye className="h-12 w-12 mx-auto mb-2" />
                <p className="text-sm">Sin imagen</p>
              </div>
            </div>
            
            {/* Duration overlay */}
            {videoInfo.duration && (
              <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-sm font-medium">
                {formatDuration(videoInfo.duration)}
              </div>
            )}
          </div>
        </div>

        {/* Video Information */}
        <div className="lg:col-span-2 space-y-4">
          <div>
            <h2 className="text-xl lg:text-2xl font-bold text-gray-900 leading-tight mb-3">
              {videoInfo.title || 'Título no disponible'}
            </h2>
            
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
              {videoInfo.duration && (
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  {formatDuration(videoInfo.duration)}
                </div>
              )}
              
              <div className="flex items-center gap-1">
                <ExternalLink className="h-4 w-4" />
                {getDomain(videoInfo.original_url)}
              </div>
              
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                {videoInfo.formats?.filter(f => f.type === 'video').length || 0} videos, {' '}
                {videoInfo.formats?.filter(f => f.type === 'audio').length || 0} audios
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-primary-50 rounded-lg p-3 text-center">
              <div className="text-lg font-bold text-primary-700">
                {videoInfo.formats?.filter(f => f.type === 'video').length || 0}
              </div>
              <div className="text-xs text-primary-600">Formatos de video</div>
            </div>
            
            <div className="bg-accent-green/10 rounded-lg p-3 text-center">
              <div className="text-lg font-bold text-green-700">
                {videoInfo.formats?.filter(f => f.type === 'audio').length || 0}
              </div>
              <div className="text-xs text-green-600">Formatos de audio</div>
            </div>
            
            <div className="bg-orange-50 rounded-lg p-3 text-center">
              <div className="text-lg font-bold text-orange-700">HD</div>
              <div className="text-xs text-orange-600">
                {videoInfo.formats?.some(f => f.quality.includes('720p') || f.quality.includes('1080p')) 
                  ? 'Disponible' : 'No disponible'}
              </div>
            </div>
          </div>

          {/* Source URL (truncated) */}
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500 mb-1">URL original:</p>
            <p className="text-sm text-gray-700 font-mono truncate" title={videoInfo.original_url}>
              {videoInfo.original_url}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};