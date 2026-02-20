import { AlertCircle, X, RefreshCw } from 'lucide-react';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry, onDismiss }) => {
  return (
    <div className="card bg-red-50 border-red-200 animate-slide-up">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0">
          <AlertCircle className="h-6 w-6 text-red-500 mt-0.5" />
        </div>
        
        <div className="flex-1">
          <h3 className="text-lg font-medium text-red-800 mb-2">
            Error al procesar el enlace
          </h3>
          <p className="text-red-700 mb-4 leading-relaxed">
            {message}
          </p>
          
          <div className="flex flex-wrap gap-3">
            {onRetry && (
              <button
                onClick={onRetry}
                className="flex items-center gap-2 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-800 rounded-lg font-medium transition-colors duration-200"
              >
                <RefreshCw className="h-4 w-4" />
                Intentar de nuevo
              </button>
            )}
            
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="flex items-center gap-2 px-4 py-2 bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 rounded-lg font-medium transition-colors duration-200"
              >
                <X className="h-4 w-4" />
                Cerrar
              </button>
            )}
          </div>

          <div className="mt-4 p-3 bg-red-100 rounded-lg">
            <h4 className="text-sm font-medium text-red-800 mb-2">Sugerencias:</h4>
            <ul className="text-sm text-red-700 space-y-1">
              <li>• Verifica que el enlace sea válido y esté accesible</li>
              <li>• Asegúrate de que el video no sea privado o restringido</li>
              <li>• Intenta con el enlace directo del video (no de playlist)</li>
              <li>• Algunos videos pueden no estar disponibles para descarga</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};