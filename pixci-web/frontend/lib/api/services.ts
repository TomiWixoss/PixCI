import { apiClient } from './client'
import type { 
  HealthResponse, 
  EncodeRequest, 
  EncodeResponse, 
  DecodeRequest, 
  DecodeResponse 
} from './types'

export const healthService = {
  check: () => apiClient.get<HealthResponse>('/health'),
}

export const encodeService = {
  encodeImage: async (request: EncodeRequest): Promise<EncodeResponse> => {
    const formData = new FormData()
    formData.append('file', request.file)
    formData.append('block_size', String(request.block_size || 1))
    formData.append('auto_detect', String(request.auto_detect || false))

    return apiClient.post<EncodeResponse>('/encode', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
}

export const decodeService = {
  decodePxvg: (request: DecodeRequest): Promise<DecodeResponse> => {
    return apiClient.post<DecodeResponse>('/decode', {
      pxvg_code: request.pxvg_code,
      scale: request.scale || 10,
    })
  },
}
