'use client'

import { useState } from 'react'
import { ImageUploader } from './ImageUploader'
import { CodeEditor } from './CodeEditor'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { useEncode } from '@/lib/hooks/useEncode'
import { useAppStore } from '@/lib/store/useAppStore'
import toast from 'react-hot-toast'
import { Settings, Image as ImageIcon } from 'lucide-react'

export function EncodeTab() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const { blockSize, autoDetect, setBlockSize, setAutoDetect, setCurrentPxvg } = useAppStore()
  const encodeMutation = useEncode()

  const handleEncode = async () => {
    if (!selectedFile) {
      toast.error('Vui lòng chọn file ảnh!')
      return
    }

    try {
      const result = await encodeMutation.mutateAsync({
        file: selectedFile,
        block_size: blockSize,
        auto_detect: autoDetect,
      })

      setCurrentPxvg(result.pxvg_code)
      toast.success(
        `Encode thành công! Grid: ${result.grid_width}x${result.grid_height}, Màu: ${result.num_colors}`
      )
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Encode thất bại')
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left Panel - Upload & Settings */}
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ImageIcon className="h-6 w-6" />
              Tải ảnh lên
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ImageUploader onFileSelect={setSelectedFile} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-6 w-6" />
              Cài đặt Encode
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoDetect}
                  onChange={(e) => setAutoDetect(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm font-medium">Tự động phát hiện block size</span>
              </label>
            </div>

            {!autoDetect && (
              <Input
                type="number"
                label="Block Size"
                value={blockSize}
                onChange={(e) => setBlockSize(Number(e.target.value))}
                min={1}
                max={16}
              />
            )}

            <Button
              onClick={handleEncode}
              isLoading={encodeMutation.isPending}
              disabled={!selectedFile}
              className="w-full"
            >
              {encodeMutation.isPending ? 'Đang xử lý...' : 'Encode sang PXVG'}
            </Button>

            {encodeMutation.isSuccess && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-800">
                  <strong>Grid:</strong> {encodeMutation.data.grid_width}x{encodeMutation.data.grid_height}
                  <br />
                  <strong>Số màu:</strong> {encodeMutation.data.num_colors}
                  <br />
                  <strong>Block size:</strong> {encodeMutation.data.block_size}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Right Panel - PXVG Output */}
      <Card>
        <CardHeader>
          <CardTitle>PXVG Code</CardTitle>
        </CardHeader>
        <CardContent>
          {encodeMutation.data ? (
            <CodeEditor
              value={encodeMutation.data.pxvg_code}
              readOnly
              height="600px"
            />
          ) : (
            <div className="h-[600px] flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg">
              <p className="text-gray-500">PXVG code sẽ hiển thị ở đây sau khi encode</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
