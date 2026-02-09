import { useState } from 'react';
import axios from 'axios';
import { VideoInfo, VideoInfoRequest } from '../types';

export const useVideoGrabber = () => {
  const [loading, setLoading] = useState(false);
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
  const [error, setError] = useState<string | null>(null);

  const getVideoInfo = async (url: string): Promise<VideoInfo | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post<VideoInfo>('/api/info', { url } as VideoInfoRequest, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      setVideoInfo(response.data);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Error al obtener información del video';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = (url: string, formatId: string, formatType: 'video' | 'audio' = 'video') => {
    const downloadUrl = `/api/download?url=${encodeURIComponent(url)}&format_id=${formatId}&format_type=${formatType}`;
    
    // Create a temporary link to trigger download
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = '';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const reset = () => {
    setVideoInfo(null);
    setError(null);
    setLoading(false);
  };

  return {
    loading,
    videoInfo,
    error,
    getVideoInfo,
    downloadFile,
    reset,
  };
};