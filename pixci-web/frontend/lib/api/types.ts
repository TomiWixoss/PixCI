export interface HealthResponse {
  status: string
  version: string
}

export interface EncodeRequest {
  file: File
  block_size?: number
  auto_detect?: boolean
}

export interface EncodeResponse {
  pxvg_code: string
  grid_width: number
  grid_height: number
  num_colors: number
  block_size: number
}

export interface DecodeRequest {
  pxvg_code: string
  scale?: number
}

export interface DecodeResponse {
  image_base64: string
  width: number
  height: number
  scaled_width: number
  scaled_height: number
}

export interface ErrorResponse {
  detail: string
  error_code?: string
}
