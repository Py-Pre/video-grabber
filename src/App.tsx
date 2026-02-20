import { Download, Github, Heart } from 'lucide-react';
import { SearchBox } from './components/SearchBox';
import { VideoInfoCard } from './components/VideoInfoCard';
import { FormatSelector } from './components/FormatSelector';
import { ErrorMessage } from './components/ErrorMessage';
import { useVideoGrabber } from './hooks/useVideoGrabber';

function App() {
  const { loading, videoInfo, error, getVideoInfo, downloadFile, reset } = useVideoGrabber();

  const handleSearch = async (url: string) => {
    await getVideoInfo(url);
  };

  const handleDownload = (formatId: string, formatType: 'video' | 'audio') => {
    if (videoInfo) {
      downloadFile(videoInfo.original_url, formatId, formatType);
    }
  };

  const handleNewSearch = () => {
    reset();
  };

  const handleRetry = () => {
    if (videoInfo?.original_url) {
      getVideoInfo(videoInfo.original_url);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-100 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 animate-gradient opacity-30"></div>
      <div className="absolute inset-0 bg-white/50"></div>
      
      {/* Floating Elements */}
      <div className="absolute top-20 left-10 w-20 h-20 bg-primary-200 rounded-full opacity-20 animate-pulse-slow"></div>
      <div className="absolute top-40 right-20 w-32 h-32 bg-accent-green rounded-full opacity-10 animate-pulse-slow" style={{ animationDelay: '1s' }}></div>
      <div className="absolute bottom-20 left-20 w-24 h-24 bg-primary-300 rounded-full opacity-15 animate-pulse-slow" style={{ animationDelay: '2s' }}></div>

      <div className="relative z-10 container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <header className="text-center mb-12 animate-fade-in">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-white rounded-2xl shadow-soft">
              <Download className="h-8 w-8 text-primary-600" />
            </div>
            <h1 className="text-4xl lg:text-5xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
              VideoGrabber
            </h1>
          </div>
          <p className="text-lg lg:text-xl text-gray-600 max-w-2xl mx-auto leading-relaxed">
            Descarga videos y audio de YouTube, Facebook, Vimeo, TikTok y más de 100 plataformas.
            <br />
            <span className="text-primary-600 font-semibold">Rápido, seguro y sin publicidad.</span>
          </p>
        </header>

        {/* Main Content */}
        <main className="space-y-8">
          {/* Search Section */}
          {!videoInfo && !error && (
            <section className="max-w-4xl mx-auto">
              <SearchBox onSearch={handleSearch} loading={loading} />
            </section>
          )}

          {/* Error Message */}
          {error && (
            <section className="max-w-4xl mx-auto">
              <ErrorMessage 
                message={error} 
                onRetry={handleRetry}
                onDismiss={reset}
              />
              <div className="mt-6 text-center">
                <button
                  onClick={handleNewSearch}
                  className="btn-secondary"
                >
                  Intentar con otro enlace
                </button>
              </div>
            </section>
          )}

          {/* Video Info & Download Section */}
          {videoInfo && !error && (
            <section className="max-w-6xl mx-auto space-y-6">
              <VideoInfoCard videoInfo={videoInfo} />
              
              <div className="grid lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <div className="card">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-xl font-bold text-gray-900">
                        Opciones de descarga
                      </h3>
                      <button
                        onClick={handleNewSearch}
                        className="btn-secondary text-sm"
                      >
                        Nuevo enlace
                      </button>
                    </div>
                    <FormatSelector 
                      formats={videoInfo.formats} 
                      onDownload={handleDownload}
                    />
                  </div>
                </div>
                
                <div className="lg:col-span-1">
                  <div className="card bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200">
                    <h4 className="font-semibold text-blue-900 mb-3">💡 Consejos de descarga</h4>
                    <ul className="space-y-2 text-sm text-blue-800">
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                        Los videos HD pueden tardar más en procesarse
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                        FLAC ofrece calidad de audio sin pérdidas
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                        MP3 320kbps es ideal para la mayoría de usos
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
                        Las descargas inician automáticamente
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </section>
          )}
        </main>

        {/* Footer */}
        <footer className="mt-16 py-8 border-t border-gray-200 bg-white/80 rounded-2xl backdrop-blur-sm">
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center gap-2 text-gray-600">
              <span>Hecho con</span>
              <Heart className="h-4 w-4 text-red-500 fill-current" />
              <span>usando React + FastAPI</span>
            </div>
            
            <div className="flex items-center justify-center gap-6 text-sm text-gray-500">
              <span>&copy; 2026 VideoGrabber</span>
              <span>•</span>
              <a href="#" className="hover:text-primary-600 transition-colors">
                Política de Privacidad
              </a>
              <span>•</span>
              <a href="#" className="flex items-center gap-1 hover:text-primary-600 transition-colors">
                <Github className="h-4 w-4" />
                Código fuente
              </a>
            </div>
            
            <p className="text-xs text-gray-400 max-w-2xl mx-auto">
              VideoGrabber no aloja ni almacena videos. Todas las descargas provienen directamente de sus servidores originales.
              Respeta los derechos de autor y términos de servicio de cada plataforma.
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;