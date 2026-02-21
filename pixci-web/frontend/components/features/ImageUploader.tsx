'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { X } from 'lucide-react'
import { cn, formatFileSize } from '@/lib/utils'
import { PixelUpload } from '../ui/svgs/PixelUpload'
import { PixelImage } from '../ui/svgs/PixelImage'

interface ImageUploaderProps {
  onFilesSelect: (files: File[]) => void
  maxSize?: number
  accept?: Record<string, string[]>
}

export function ImageUploader({ 
  onFilesSelect, 
  maxSize = 10 * 1024 * 1024,
  accept = {
    'image/png': ['.png'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/gif': ['.gif'],
    'image/webp': ['.webp'],
  }
}: ImageUploaderProps) {
  const [previews, setPreviews] = useState<string[]>([])
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFiles(acceptedFiles)
      const newPreviews = acceptedFiles.map(file => URL.createObjectURL(file))
      setPreviews(newPreviews)
      onFilesSelect(acceptedFiles)
    }
  }, [onFilesSelect])

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple: true,
  })

  const clearFile = (e: React.MouseEvent) => {
    e.stopPropagation()
    setPreviews([])
    setSelectedFiles([])
  }

  return (
    <div {...getRootProps()} className="w-full min-h-[400px] cursor-pointer">
      <input {...getInputProps()} />
      
      {previews.length === 0 ? (
        <div className={cn(
          "min-h-[400px] flex flex-col items-center justify-center p-8 transition-all rounded-xl",
          isDragActive 
            ? "bg-[var(--accent-primary)]/10 border-2 border-[var(--accent-primary)]" 
            : "bg-[var(--bg-elevated)] hover:bg-[var(--bg-secondary)] border-2 border-dashed border-[var(--border-subtle)]"
        )}>
          <div className={cn(
            "w-20 h-20 rounded-2xl flex items-center justify-center mb-6 transition-all",
            isDragActive ? "bg-[var(--accent-primary)]" : "bg-[var(--bg-secondary)]"
          )}>
            {isDragActive ? (
              <PixelUpload className="w-12 h-12 text-[var(--accent-pink)] drop-shadow-[2px_2px_0_var(--text-color)]" />
            ) : (
              <PixelImage className="w-16 h-16 text-[var(--text-color)] opacity-70 mb-4" />
            )}
          </div>
          
          {isDragActive ? (
            <p className="text-lg font-medium text-[var(--accent-primary)] mb-2">
              Thả ảnh vào đây
            </p>
          ) : (
            <>
              <p className="text-lg font-medium text-[var(--text-primary)] mb-2">
                Kéo & thả ảnh của bạn
              </p>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                hoặc bấm để duyệt tệp tin
              </p>
            </>
          )}
          
          <p className="text-xs text-[var(--text-muted)]">
            PNG, JPG, GIF, WebP • Max {formatFileSize(maxSize)}
          </p>
          
          {fileRejections.length > 0 && (
            <p className="text-red-500 text-sm mt-4">
              {fileRejections[0].errors[0].message === "file-too-large" ? "File too large" : "Invalid file type"}
            </p>
          )}
        </div>
      ) : previews.length > 0 ? (
        <div className="relative min-h-[400px] flex items-center justify-center p-8 bg-[var(--bg-elevated)] rounded-xl">
          <div className="relative">
            <div className="w-64 h-64 rounded-xl overflow-hidden border-2 border-[var(--border-subtle)]">
              <img
                src={previews[0]}
                alt="Preview"
                className="w-full h-full object-cover pixel-rendering"
              />
              {previews.length > 1 && (
                <div className="absolute inset-0 bg-black/60 flex items-center justify-center text-white font-bold text-3xl">
                  +{previews.length - 1}
                </div>
              )}
            </div>
            
            <button
              onClick={clearFile}
              className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-[var(--accent-primary)] text-white flex items-center justify-center hover:scale-110 transition-transform"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2">
            <p className="text-sm text-[var(--text-secondary)] whitespace-nowrap">{selectedFiles.length} file(s) selected</p>
          </div>
        </div>
      ) : null}
    </div>
  )
}
