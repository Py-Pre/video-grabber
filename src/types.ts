export interface VideoFormat {
  format_id: string;
  ext: string;
  quality: string;
  file_size?: string;
  type: 'video' | 'audio';
}

export interface VideoInfo {
  title: string;
  thumbnail?: string;
  duration?: number;
  formats: VideoFormat[];
  original_url: string;
}

export interface VideoInfoRequest {
  url: string;
}

export type FormatType = 'video' | 'audio';

export interface DownloadProgress {
  percentage: number;
  speed?: string;
  eta?: string;
}