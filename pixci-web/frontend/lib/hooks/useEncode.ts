import { useMutation } from '@tanstack/react-query'
import { encodeService } from '@/lib/api/services'
import type { EncodeRequest, EncodeResponse } from '@/lib/api/types'

export function useEncode() {
  return useMutation<EncodeResponse, Error, EncodeRequest>({
    mutationFn: (request) => encodeService.encodeImage(request),
  })
}
