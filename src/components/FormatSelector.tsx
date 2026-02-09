import React, { useState } from 'react';
import { Download, Play, Music, Monitor, Headphones, FileText } from 'lucide-react';
import { VideoFormat, FormatType } from '../types';

interface FormatSelectorProps {
  formats: VideoFormat[];
  onDownload: (formatId: string, formatType: FormatType) => void;
}

export const FormatSelector: React.FC<FormatSelectorProps> = ({ formats, onDownload }) => {
  const [selectedType, setSelectedType] = useState<FormatType>('video');
  const [selectedFormat, setSelectedFormat] = useState<string | null>(null);

  const videoFormats = formats.filter(f => f.type === 'video');
  const audioFormats = formats.filter(f => f.type === 'audio');

  const currentFormats = selectedType === 'video' ? videoFormats : audioFormats;

  const getFormatIcon = (ext: string, type: FormatType) => {
    if (type === 'audio') {
      switch (ext) {
        case 'mp3': return <Music className="h-5 w-5 text-green-500" />;
        case 'aac': return <Headphones className="h-5 w-5 text-blue-500" />;
        case 'flac': return <FileText className="h-5 w-5 text-purple-500" />;
        case 'ogg': return <Music className="h-5 w-5 text-orange-500" />;
        default: return <Music className="h-5 w-5 text-gray-500" />;
      }
    } else {
      return <Monitor className="h-5 w-5 text-blue-500" />;
    }
  };

  const getQualityBadgeColor = (quality: string) => {
    if (quality.includes('1080p') || quality.includes('4K') || quality.includes('2160p')) {
      return 'bg-red-100 text-red-700';
    } else if (quality.includes('720p') || quality.includes('Lossless')) {
      return 'bg-orange-100 text-orange-700';
    } else if (quality.includes('480p') || quality.includes('320kbps')) {
      return 'bg-yellow-100 text-yellow-700';
    } else {
      return 'bg-gray-100 text-gray-700';
    }
  };

  const formatFileSize = (size: string | undefined) => {
    if (!size) return '';
    const sizeNum = parseInt(size);
    if (sizeNum > 1024 * 1024 * 1024) {
      return `~${(sizeNum / (1024 * 1024 * 1024)).toFixed(1)} GB`;
    } else if (sizeNum > 1024 * 1024) {
      return `~${(sizeNum / (1024 * 1024)).toFixed(1)} MB`;
    } else if (sizeNum > 1024) {
      return `~${(sizeNum / 1024).toFixed(1)} KB`;
    }
    return '';
  };

  const handleDownload = (format: VideoFormat) => {
    setSelectedFormat(format.format_id);
    onDownload(format.format_id, format.type);
    setTimeout(() => setSelectedFormat(null), 2000); // Reset after 2s
  };

  return (
    <div className="space-y-6">
      {/* Format Type Selector */}
      <div className="flex bg-gray-100 p-1 rounded-xl">
        <button
          onClick={() => setSelectedType('video')}
          className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-medium transition-all duration-200 ${
            selectedType === 'video'
              ? 'bg-white text-primary-700 shadow-sm'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          <Play className="h-5 w-5" />
          Video ({videoFormats.length})
        </button>
        <button
          onClick={() => setSelectedType('audio')}
          className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-medium transition-all duration-200 ${
            selectedType === 'audio'
              ? 'bg-white text-primary-700 shadow-sm'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          <Headphones className="h-5 w-5" />
          Audio ({audioFormats.length})
        </button>
      </div>

      {/* Format List */}
      <div className="space-y-3 max-h-80 overflow-y-auto">
        {currentFormats.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              {selectedType === 'video' ? <Play className="h-8 w-8" /> : <Headphones className="h-8 w-8" />}
            </div>
            No hay formatos {selectedType === 'video' ? 'de video' : 'de audio'} disponibles
          </div>
        ) : (
          currentFormats.map((format, index) => (
            <div
              key={`${format.format_id}-${index}`}
              className="format-btn group"
            >
              <div className="flex items-center gap-3 flex-1">
                {getFormatIcon(format.ext, format.type)}
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-gray-900 uppercase text-sm">
                      {format.ext}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getQualityBadgeColor(format.quality)}`}>
                      {format.quality}
                    </span>
                  </div>
                  {format.file_size && (
                    <p className="text-sm text-gray-500">
                      {formatFileSize(format.file_size)}
                    </p>
                  )}
                </div>
              </div>
              <button
                onClick={() => handleDownload(format)}
                disabled={selectedFormat === format.format_id}
                className="btn-primary text-sm px-4 py-2 h-auto disabled:opacity-50"
              >
                {selectedFormat === format.format_id ? (
                  <>
                    <div className="loading-spinner !w-4 !h-4" />
                    Descargando...
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4" />
                    Descargar
                  </>
                )}
              </button>
            </div>
          ))
        )}
      </div>

      {/* Format Info */}
      {currentFormats.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <FileText className="h-3 w-3 text-white" />
            </div>
            <div className="text-sm text-blue-700">
              <p className="font-medium mb-1">
                {selectedType === 'video' ? 'Información sobre videos' : 'Información sobre audio'}
              </p>
              <p className="text-blue-600">
                {selectedType === 'video' 
                  ? 'Los videos se descargan con la mejor calidad de audio incluida. Los formatos HD pueden requerir más tiempo de procesamiento.'
                  : 'Los archivos de audio se extraen con la máxima calidad disponible. FLAC es sin pérdida, MP3/AAC son comprimidos.'
                }
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};