'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X, Image as ImageIcon } from 'lucide-react'
import { cn, formatFileSize } from '@/lib/utils'

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

  const clearFile = (e: React.MouseEvent) => {
    e.stopPropagation()
    setPreview(null)
    setSelectedFile(null)
  }

  return (
    <div className="w-full font-pixel">
      {!preview ? (
        <div
          {...getRootProps()}
          className={cn(
            'border-4 border-dashed p-8 md:p-12 text-center cursor-pointer transition-all bg-white dark:bg-black',
            isDragActive 
              ? 'border-black dark:border-[#00ff00] bg-gray-100 dark:bg-[#111] scale-105' 
              : 'border-black dark:border-[#333] hover:border-black dark:hover:border-[#00ff00] hover:-translate-y-1',
            fileRejections.length > 0 && 'border-red-500 bg-red-50 dark:bg-red-900/20'
          )}
        >
          <input {...getInputProps()} />
          <Upload className={cn("mx-auto h-12 w-12 mb-4", isDragActive ? "text-black dark:text-[#00ff00] animate-bounce" : "text-gray-400 dark:text-gray-600")} />
          {isDragActive ? (
            <p className="font-bold text-black dark:text-[#00ff00] text-sm uppercase">THẢ ẢNH VÀO ĐÂY...</p>
          ) : (
            <>
              <p className="text-black dark:text-gray-300 text-sm mb-3 uppercase leading-relaxed">
                KÉO THẢ HOẶC CLICK ĐỂ <br/> CHỌN ẢNH GỐC
              </p>
              <p className="text-[10px] text-gray-500">
                PNG, JPG, GIF (MAX {formatFileSize(maxSize)})
              </p>
            </>
          )}
          {fileRejections.length > 0 && (
            <p className="text-red-600 text-[10px] mt-4 uppercase font-bold glitch">
              {fileRejections[0].errors[0].message === "file-too-large" ? "FILE QUÁ LỚN!" : "FILE KHÔNG HỢP LỆ!"}
            </p>
          )}
        </div>
      ) : (
        <div className="relative brutal-card p-4 sm:p-6 bg-white dark:bg-black group">
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
            <div className="flex-shrink-0 w-32 h-32 brutal-card overflow-hidden bg-gray-100 p-1">
              <img
                src={preview}
                alt="Preview"
                className="w-full h-full object-cover pixel-rendering"
              />
            </div>
            <div className="flex-1 min-w-0 text-center sm:text-left flex flex-col justify-center h-32">
              <p className="font-bold text-sm text-black dark:text-[#00ff00] truncate uppercase mb-2">
                {selectedFile?.name}
              </p>
              <p className="text-[10px] text-gray-500 mb-4">
                {selectedFile && formatFileSize(selectedFile.size)}
              </p>
              <button
                onClick={clearFile}
                className="brutal-btn px-4 py-2 text-[10px] flex items-center justify-center gap-2 self-center sm:self-start bg-red-500 text-white shadow-[3px_3px_0px_0px_#000] dark:shadow-[3px_3px_0px_0px_rgba(255,0,0,0.5)]"
              >
                <X className="h-3 w-3" /> HỦY BỎ
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
