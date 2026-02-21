'use client'

import { useState } from 'react'
import { CodeEditor } from './CodeEditor'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { useDecode } from '@/lib/hooks/useDecode'
import { useAppStore } from '@/lib/store/useAppStore'
import toast from 'react-hot-toast'
import { Code, Image as ImageIcon, Download } from 'lucide-react'
import { downloadFile, base64ToBlob } from '@/lib/utils'

export function DecodeTab() {
  const [pxvgCode, setPxvgCode] = useState('')
  const { scale, setScale } = useAppStore()
  const decodeMutation = useDecode()

  const handleDecode = async () => {
    if (!pxvgCode.trim()) {
      toast.error('Vui lòng nhập PXVG code!')
      return
    }

    try {
      const result = await decodeMutation.mutateAsync({
        pxvg_code: pxvgCode,
        scale,
      })

      toast.success(
        `Decode thành công! Kích thước: ${result.scaled_width}x${result.scaled_height}px`
      )
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Decode thất bại')
    }
  }

  const handleDownloadImage = () => {
    if (!decodeMutation.data) return

    const blob = base64ToBlob(decodeMutation.data.image_base64)
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'decoded-image.png'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    toast.success('Đã tải xuống ảnh!')
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left Panel - PXVG Input */}
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Code className="h-6 w-6" />
              PXVG Code Input
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CodeEditor
              value={pxvgCode}
              onChange={setPxvgCode}
              height="400px"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Cài đặt Decode</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              type="number"
              label="Scale (Phóng to)"
              value={scale}
              onChange={(e) => setScale(Number(e.target.value))}
              min={1}
              max={20}
            />

            <Button
              onClick={handleDecode}
              isLoading={decodeMutation.isPending}
              disabled={!pxvgCode.trim()}
              className="w-full"
            >
              {decodeMutation.isPending ? 'Đang xử lý...' : 'Decode sang Ảnh'}
            </Button>

            {decodeMutation.isSuccess && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <p className="text-sm text-green-800">
                  <strong>Grid gốc:</strong> {decodeMutation.data.width}x{decodeMutation.data.height}
                  <br />
                  <strong>Kích thước xuất:</strong> {decodeMutation.data.scaled_width}x{decodeMutation.data.scaled_height}px
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Right Panel - Image Output */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <ImageIcon className="h-6 w-6" />
              Ảnh kết quả
            </CardTitle>
            {decodeMutation.data && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleDownloadImage}
              >
                <Download className="h-4 w-4 mr-2" />
                Tải xuống
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {decodeMutation.data ? (
            <div className="flex items-center justify-center p-4 bg-gray-50 rounded-lg">
              <img
                src={`data:image/png;base64,${decodeMutation.data.image_base64}`}
                alt="Decoded"
                className="max-w-full h-auto"
                style={{ imageRendering: 'pixelated' }}
              />
            </div>
          ) : (
            <div className="h-[600px] flex items-center justify-center border-2 border-dashed border-gray-300 rounded-lg">
              <p className="text-gray-500">Ảnh sẽ hiển thị ở đây sau khi decode</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
