'use client'

import { useState, useEffect } from 'react'
import { useAIEditor } from '@/lib/hooks/useAIEditor'
import { useEncode } from '@/lib/hooks/useEncode'
import { FloatingInput } from '@/components/ui/FloatingInput'
import { HistoryTimeline } from '@/components/features/HistoryTimeline'
import { ImageUploader } from '@/components/features/ImageUploader'
import { PixelScrambleCanvas } from '@/components/features/PixelScrambleCanvas'
import { AnimatePresence, motion } from 'framer-motion'
import { useTheme } from 'next-themes'
import { PixelStar } from '@/components/ui/svgs/PixelStar'
import { PixelLogo } from '@/components/ui/svgs/PixelLogo'
import { PixelPalette } from '@/components/ui/svgs/PixelPalette'
import { Sun, Moon } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Home() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)
  const encodeMutation = useEncode()
  const { history, currentIndex, currentNode, isProcessing, submitPrompt, rollbackTo, addInitialState } = useAIEditor()

  useEffect(() => setMounted(true), [])

  const handleInitialUpload = async (file: File) => {
    const renderPreview = new Promise<string>((resolve) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result as string)
      reader.readAsDataURL(file)
    })

    try {
      const result = await encodeMutation.mutateAsync({ file, block_size: 1, auto_detect: true })
      const base64Preview = await renderPreview
      addInitialState(result.pxvg_code, base64Preview)
      toast.success('Hệ thống đã nhận diện dữ liệu ảnh.')
    } catch (error) {
      toast.error('Gặp lỗi trong quá trình xử lý ảnh.')
    }
  }

  return (
    <div className="h-screen w-screen overflow-hidden flex flex-col font-pixel relative selection:bg-[var(--accent-pink)] selection:text-white">
      
      <header className="w-full p-4 z-50">
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center gap-3 art-canvas !box-shadow-[4px_4px_0_var(--text-color)] !px-4 !py-2 rounded-full">
            <PixelLogo className="w-8 h-8" />
            <span className="font-bold text-sm tracking-widest uppercase mt-0.5">PixCI Studio</span>
          </div>
          
          <button 
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className="art-canvas !p-3 !rounded-full hover:bg-[var(--accent-yellow)] hover:shadow-[4px_4px_0_var(--accent-pink)] transition-all"
          >
            {mounted && theme === 'dark' 
              ? <Sun className="w-6 h-6 text-[var(--text-color)]" /> 
              : <Moon className="w-6 h-6 text-[var(--text-color)]" />
            }
          </button>
        </div>

        {currentNode && (
          <div className="w-full max-w-5xl mx-auto">
            <HistoryTimeline history={history} currentIndex={currentIndex} onRollback={rollbackTo} />
          </div>
        )}
      </header>

      <main className="flex-1 w-full flex flex-col items-center justify-center p-4 relative z-10">
        <AnimatePresence mode="wait">
          {!currentNode ? (
            <motion.div
              key="uploader"
              initial={{ scale: 0.8, opacity: 0, rotate: -5 }}
              animate={{ scale: 1, opacity: 1, rotate: 0 }}
              exit={{ scale: 1.2, opacity: 0, filter: "blur(10px)" }}
              transition={{ type: "spring", bounce: 0.5 }}
              className="w-full max-w-2xl art-canvas p-4 bg-white"
            >
              <div className="p-12 border-4 border-dashed border-[var(--accent-purple)] bg-[var(--bg-color)]/30 text-center flex flex-col items-center">
                
                <PixelPalette className="w-24 h-24 mb-6 drop-shadow-[4px_4px_0_rgba(0,0,0,0.1)]" />
                
                <h1 className="text-3xl font-bold mb-4 uppercase text-[var(--accent-purple)] drop-shadow-[2px_2px_0_var(--text-color)]">
                  Tải Ảnh Lên
                </h1>
                
                {encodeMutation.isPending ? (
                  <div className="flex flex-col items-center gap-4 mt-4">
                    <PixelStar className="w-10 h-10 animate-spin text-[var(--accent-pink)]" />
                    <p className="text-xs uppercase font-bold text-[var(--accent-pink)] animate-pulse">Đang phân tích dữ liệu PXVG...</p>
                  </div>
                ) : (
                  <div className="mt-4">
                    <ImageUploader onFileSelect={handleInitialUpload} />
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
              className="relative flex items-center justify-center w-full max-w-3xl aspect-square max-h-[60vh]"
            >
              <div className="absolute -bottom-4 w-[110%] h-8 bg-[var(--accent-yellow)] border-4 border-[var(--text-color)] z-0 rounded-full"></div>
              
              <div className="art-canvas p-4 bg-[var(--panel-bg)] w-full h-full flex items-center justify-center relative z-10 overflow-hidden">
                
                {isProcessing && (
                  <div className="absolute top-8 left-1/2 -translate-x-1/2 z-40 pointer-events-none">
                    <div className="bg-[var(--panel-bg)] text-[var(--text-color)] px-6 py-3 font-bold uppercase tracking-widest text-sm shadow-[4px_4px_0_var(--accent-purple)] border-4 border-[var(--text-color)]">
                      Đang Phân Rã và Tái Tổ Hợp...
                    </div>
                  </div>
                )}

                <PixelScrambleCanvas 
                  base64Image={currentNode.base64Image} 
                  isProcessing={isProcessing} 
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {currentNode && (
        <div className="w-full p-6 pb-8 z-50 flex justify-center">
          <div className="w-full max-w-4xl">
            <FloatingInput onSubmit={submitPrompt} isProcessing={isProcessing} />
          </div>
        </div>
      )}
    </div>
  )
}
