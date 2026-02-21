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
    'image/webp': ['.webp'],
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
    <div {...getRootProps()} className="w-full min-h-[400px] cursor-pointer">
      <input {...getInputProps()} />
      
      {!preview ? (
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
              <Upload className="w-8 h-8 text-white" />
            ) : (
              <ImageIcon className="w-8 h-8 text-[var(--text-secondary)]" />
            )}
          </div>
          
          {isDragActive ? (
            <p className="text-lg font-medium text-[var(--accent-primary)] mb-2">
              Drop your image here
            </p>
          ) : (
            <>
              <p className="text-lg font-medium text-[var(--text-primary)] mb-2">
                Drag & drop your image
              </p>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                or click to browse files
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
      ) : (
        <div className="relative min-h-[400px] flex items-center justify-center p-8 bg-[var(--bg-elevated)] rounded-xl">
          <div className="relative">
            <div className="w-64 h-64 rounded-xl overflow-hidden border-2 border-[var(--border-subtle)]">
              <img
                src={preview}
                alt="Preview"
                className="w-full h-full object-cover pixel-rendering"
              />
            </div>
            
            <button
              onClick={clearFile}
              className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-[var(--accent-primary)] text-white flex items-center justify-center hover:scale-110 transition-transform"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2">
            <p className="text-sm text-[var(--text-secondary)]">{selectedFile?.name}</p>
            <p className="text-xs text-[var(--text-muted)] text-center">{selectedFile && formatFileSize(selectedFile.size)}</p>
          </div>
        </div>
      )}
    </div>
  )
}
