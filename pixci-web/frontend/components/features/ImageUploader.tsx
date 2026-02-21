'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X, Image as ImageIcon } from 'lucide-react'
import { cn, formatFileSize } from '@/lib/utils'
import { Button } from '@/components/ui/Button'

interface ImageUploaderProps {
  onFileSelect: (file: File) => void
  maxSize?: number
  accept?: Record<string, string[]>
}

export function ImageUploader({ 
  onFileSelect, 
  maxSize = 10 * 1024 * 1024,
  accept = {
    'image/png': ['.png'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/gif': ['.gif'],
  }
}: ImageUploaderProps) {
  const [preview, setPreview] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setSelectedFile(file)
      const reader = new FileReader()
      reader.onload = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
      onFileSelect(file)
    }
  }, [onFileSelect])

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple: false,
  })

  const clearFile = () => {
    setPreview(null)
    setSelectedFile(null)
  }

  return (
    <div className="w-full">
      {!preview ? (
        <div
          {...getRootProps()}
          className={cn(
            'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
            isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400',
            fileRejections.length > 0 && 'border-red-500 bg-red-50'
          )}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          {isDragActive ? (
            <p className="text-blue-600 font-medium">Thả file vào đây...</p>
          ) : (
            <>
              <p className="text-gray-600 mb-2">
                Kéo thả ảnh vào đây hoặc click để chọn
              </p>
              <p className="text-sm text-gray-500">
                PNG, JPG, GIF (tối đa {formatFileSize(maxSize)})
              </p>
            </>
          )}
          {fileRejections.length > 0 && (
            <p className="text-red-600 text-sm mt-2">
              {fileRejections[0].errors[0].message}
            </p>
          )}
        </div>
      ) : (
        <div className="relative">
          <div className="border-2 border-gray-300 rounded-lg p-4">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <img
                  src={preview}
                  alt="Preview"
                  className="w-32 h-32 object-contain rounded border border-gray-200"
                />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-gray-900 truncate">
                      {selectedFile?.name}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      {selectedFile && formatFileSize(selectedFile.size)}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={clearFile}
                    className="ml-2"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
