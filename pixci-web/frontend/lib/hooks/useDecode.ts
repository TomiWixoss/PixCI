import { useMutation } from '@tanstack/react-query'
import { decodeService } from '@/lib/api/services'
import type { DecodeRequest, DecodeResponse } from '@/lib/api/types'

export function useDecode() {
  return useMutation<DecodeResponse, Error, DecodeRequest>({
    mutationFn: (request) => decodeService.decodePxvg(request),
  })
}
