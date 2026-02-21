'use client'

import { useState, useEffect, useRef } from 'react'
import { useAIEditor } from '@/lib/hooks/useAIEditor'
import { useEncode } from '@/lib/hooks/useEncode'
import { decodeService } from '@/lib/api/services'
import { FloatingInput } from '@/components/ui/FloatingInput'
import { HistoryTimeline } from '@/components/features/HistoryTimeline'
import { ImageUploader } from '@/components/features/ImageUploader'
import { PixelScrambleCanvas } from '@/components/features/PixelScrambleCanvas'
import { AnimatePresence, motion } from 'framer-motion'
import { useTheme } from 'next-themes'
import { PixelStar } from '@/components/ui/svgs/PixelStar'
import { PixelLogo } from '@/components/ui/svgs/PixelLogo'
import { PixelPalette } from '@/components/ui/svgs/PixelPalette'
import { Sun, Moon, Download, Trash2, PlusCircle, X, Github } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Home() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)
  const encodeMutation = useEncode()
  const { history, currentIndex, currentNode, isProcessing, submitPrompt, rollbackTo, addInitialState, appendImagesToCurrent, removeImageFromCurrent, reset } = useAIEditor()
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => setMounted(true), [])

  const handleInitialUpload = async (files: File[]) => {
    try {
      const encodePromises = files.map(file => encodeMutation.mutateAsync({ file, block_size: 1, auto_detect: true }))
      const results = await Promise.all(encodePromises)

      const previewPromises = files.map(file => new Promise<string>((resolve) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result as string)
        reader.readAsDataURL(file)
      }))
      const base64Previews = await Promise.all(previewPromises)

      addInitialState(results.map(r => r.pxvg_code), base64Previews)
      toast.success(`Đã tải lên ${files.length} ảnh.`)
    } catch (error) {
      toast.error('Gặp lỗi trong quá trình xử lý ảnh.')
    }
  }

  const handleAddMoreFiles = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    if (!files.length) return
    
    const toastId = toast.loading('Đang xử lý ảnh mới...')
    try {
      const encodePromises = files.map(file => encodeMutation.mutateAsync({ file, block_size: 1, auto_detect: true }))
      const results = await Promise.all(encodePromises)
      
      const previewPromises = files.map(file => new Promise<string>(resolve => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result as string)
        reader.readAsDataURL(file)
      }))
      const previews = await Promise.all(previewPromises)

      appendImagesToCurrent(results.map(r => r.pxvg_code), previews)
      toast.success(`Đã thêm ${files.length} ảnh mới!`, { id: toastId })
    } catch (err) {
      toast.error('Lỗi thêm ảnh', { id: toastId })
    }
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const handleDownloadOriginals = async () => {
    if (!currentNode) return
    const toastId = toast.loading('Đang xử lý ảnh gốc...')
    try {
      const promises = currentNode.pxvgCodes.map(code => 
        decodeService.decodePxvg({ pxvg_code: code, scale: 1 })
      )
      const results = await Promise.all(promises)
      
      results.forEach((res, idx) => {
        const link = document.createElement('a')
        link.href = res.image_base64.startsWith('data:') ? res.image_base64 : `data:image/png;base64,${res.image_base64}`
        link.download = `pixel-art-original-${Date.now()}-${idx + 1}.png`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      })
      toast.success('Đã tải xuống kích thước gốc!', { id: toastId })
    } catch (e) {
      toast.error('Lỗi khi tải ảnh', { id: toastId })
    }
  }

  return (
    <div className="min-h-screen w-full overflow-hidden flex flex-col font-pixel relative selection:bg-[var(--accent-pink)] selection:text-white">
      
      <header className="w-full p-2 z-50">
        <div className="flex justify-between items-center mb-1.5">
          <div className="flex items-center gap-2 art-canvas !box-shadow-[2px_2px_0_var(--text-color)] !px-2.5 !py-1 rounded-full">
            <PixelLogo className="w-5 h-5" />
            <span className="font-bold text-[11px] tracking-widest uppercase mt-0.5">PixCI Studio</span>
          </div>
          
          <div className="flex gap-1.5">
            {currentNode && (
              <>
                <button 
                  onClick={reset}
                  title="Xóa tất cả (Reset)"
                  className="art-canvas !p-1.5 !rounded-full bg-white dark:bg-transparent hover:bg-[var(--accent-pink)] dark:hover:bg-[var(--accent-pink)] hover:shadow-[2px_2px_0_var(--text-color)] transition-all"
                >
                  <Trash2 className="w-3.5 h-3.5 text-[var(--text-color)]" />
                </button>
                <button 
                  onClick={handleDownloadOriginals}
                  title="Tải ảnh gốc"
                  className="art-canvas !p-1.5 !rounded-full bg-white dark:bg-transparent hover:bg-[var(--accent-purple)] dark:hover:bg-[var(--accent-purple)] hover:shadow-[2px_2px_0_var(--text-color)] transition-all"
                >
                  <Download className="w-3.5 h-3.5 text-[var(--text-color)]" />
                </button>
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  title="Thêm ảnh"
                  className="art-canvas !p-1.5 !rounded-full bg-[var(--accent-yellow)] hover:bg-[var(--accent-yellow)] hover:shadow-[2px_2px_0_var(--text-color)] transition-all"
                >
                  <PlusCircle className="w-3.5 h-3.5 text-[var(--text-color)]" />
                </button>
                <input type="file" ref={fileInputRef} multiple className="hidden" accept="image/png,image/jpeg,image/gif,image/webp" onChange={handleAddMoreFiles} />
              </>
            )}
            <button 
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="art-canvas !p-1.5 !rounded-full hover:bg-[var(--accent-yellow)] hover:shadow-[2px_2px_0_var(--accent-pink)] transition-all"
            >
              {mounted && theme === 'dark' ? <Sun className="w-3.5 h-3.5 text-[var(--text-color)]" /> : <Moon className="w-3.5 h-3.5 text-[var(--text-color)]" />}
            </button>
            <a 
              href="https://github.com/TomiWixoss/PixCI"
              target="_blank"
              rel="noopener noreferrer"
              title="GitHub"
              className="art-canvas !p-1.5 !rounded-full bg-white dark:bg-transparent hover:bg-[var(--accent-pink)] dark:hover:bg-[var(--accent-pink)] hover:shadow-[2px_2px_0_var(--text-color)] transition-all"
            >
              <Github className="w-3.5 h-3.5 text-[var(--text-color)]" />
            </a>
          </div>
        </div>

        {currentNode && (
          <div className="w-full max-w-5xl mx-auto">
            <HistoryTimeline history={history} currentIndex={currentIndex} onRollback={rollbackTo} />
          </div>
        )}
      </header>

      <main className="flex-1 w-full flex flex-col items-center justify-center p-2 relative z-10">
        <AnimatePresence mode="wait">
          {!currentNode ? (
            <motion.div
              key="uploader"
              initial={{ scale: 0.8, opacity: 0, rotate: -5 }}
              animate={{ scale: 1, opacity: 1, rotate: 0 }}
              exit={{ scale: 1.2, opacity: 0, filter: "blur(10px)" }}
              transition={{ type: "spring", bounce: 0.5 }}
              className="w-full max-w-xl art-canvas p-2 bg-white"
            >
              <div className="p-6 border-3 border-dashed border-[var(--accent-purple)] bg-[var(--bg-color)]/30 text-center flex flex-col items-center">
                
                <PixelPalette className="w-16 h-16 mb-4 drop-shadow-[2px_2px_0_rgba(0,0,0,0.1)]" />
                
                <h1 className="text-xl font-bold mb-3 uppercase text-[var(--accent-purple)] drop-shadow-[2px_2px_0_var(--text-color)]">
                  Tải Ảnh Lên
                </h1>
                
                {encodeMutation.isPending ? (
                  <div className="flex flex-col items-center gap-3 mt-3">
                    <PixelStar className="w-8 h-8 animate-spin text-[var(--accent-pink)]" />
                    <p className="text-[10px] uppercase font-bold text-[var(--accent-pink)] animate-pulse">Đang phân tích dữ liệu PXVG...</p>
                  </div>
                ) : (
                  <div className="mt-4">
                    <ImageUploader onFilesSelect={handleInitialUpload} />
                  </div>
                )}
              </div>
            </motion.div>
          ) : (
            <motion.div
              key={`canvas-${currentIndex}`}
              initial={{ scale: 0.9, y: 20, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              transition={{ type: "spring", bounce: 0.4 }}
              className={`relative flex items-center justify-center w-full max-h-[55vh] ${currentNode.base64Images.length > 1 ? 'max-w-3xl' : 'max-w-2xl aspect-square'}`}
            >
              <div className="absolute -bottom-2 w-[110%] h-5 bg-[var(--accent-yellow)] border-2 border-[var(--text-color)] z-0 rounded-full"></div>
              
              <div className="art-canvas p-2 bg-[var(--panel-bg)] w-full h-full flex items-center justify-center relative z-10 overflow-hidden">
                
                {isProcessing && (
                  <div className="absolute top-4 left-1/2 -translate-x-1/2 z-40 pointer-events-none">
                    <div className="bg-[var(--panel-bg)] text-[var(--text-color)] px-3 py-1.5 font-bold uppercase tracking-widest text-[10px] shadow-[2px_2px_0_var(--accent-purple)] border-2 border-[var(--text-color)]">
                      Đang Phân Rã và Tái Tổ Hợp...
                    </div>
                  </div>
                )}

                <div className={`w-full h-full flex items-center justify-center gap-4 ${currentNode.base64Images.length > 1 ? 'flex-wrap overflow-y-auto content-center p-2' : ''}`}>
                  {currentNode.base64Images.map((img, idx) => (
                    <div key={idx} className={`relative flex items-center justify-center ${currentNode.base64Images.length > 1 ? 'w-[45%] md:w-[30%] aspect-square' : 'w-full h-full'}`}>
                      {currentNode.base64Images.length > 1 && (
                        <div className="absolute top-1 left-1 z-20 bg-[var(--text-color)] text-[var(--panel-bg)] text-[9px] px-1.5 py-0.5 font-bold">
                          {idx === 0 ? 'GỐC' : `REF ${idx}`}
                        </div>
                      )}
                      {currentNode.base64Images.length > 1 && !isProcessing && (
                        <button
                          onClick={() => removeImageFromCurrent(idx)}
                          className="absolute top-0.5 right-0.5 z-30 bg-[var(--accent-pink)] text-white p-0.5 rounded-full border border-[var(--text-color)] hover:scale-110 transition-transform"
                          title="Xóa ảnh này"
                        >
                          <X className="w-2.5 h-2.5" />
                        </button>
                      )}
                      <PixelScrambleCanvas 
                        base64Image={img} 
                        isProcessing={isProcessing} 
                      />
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {currentNode && (
        <div className="w-full p-2 pb-3 z-50 flex justify-center">
          <div className="w-full max-w-3xl">
            <FloatingInput onSubmit={submitPrompt} isProcessing={isProcessing} />
          </div>
        </div>
      )}
    </div>
  )
}
