export interface AudioSource {
  name: string;
  index: number;
}

export interface ListSourcesResponse {
  sources: AudioSource[];
}

export interface SwitchSourceResponse {
  success: boolean;
  message: string;
}

export interface ErrorResponse {
  error: string;
}
