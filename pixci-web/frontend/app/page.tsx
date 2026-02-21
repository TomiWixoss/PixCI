'use client'

import { useState } from 'react'
import { useAIEditor } from '@/lib/hooks/useAIEditor'
import { useEncode } from '@/lib/hooks/useEncode'
import { FloatingInput } from '@/components/ui/FloatingInput'
import { HistoryTimeline } from '@/components/features/HistoryTimeline'
import { ImageUploader } from '@/components/features/ImageUploader'
import { AnimatePresence, motion } from 'framer-motion'
import { useTheme } from 'next-themes'
import { Moon, Sun, Monitor, Image as ImageIcon } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Home() {
  const { theme, setTheme } = useTheme()
  const encodeMutation = useEncode()
  const {
    history,
    currentIndex,
    currentNode,
    isProcessing,
    submitPrompt,
    rollbackTo,
    addInitialState,
    reset
  } = useAIEditor()

  const [initialFile, setInitialFile] = useState<File | null>(null)

  const handleInitialUpload = async (file: File) => {
    setInitialFile(file)
    const renderPreview = new Promise<string>((resolve) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result as string)
      reader.readAsDataURL(file)
    })

    try {
      const result = await encodeMutation.mutateAsync({
        file,
        block_size: 1, // Default to highest fidelity auto-detect
        auto_detect: true,
      })

      const base64Preview = await renderPreview
      addInitialState(result.pxvg_code, base64Preview)
      toast.success('PXVG Engine Khởi tạo OK!', { icon: '🚀' })
    } catch (error) {
      toast.error('Có lỗi khi số hoá ảnh!')
      setInitialFile(null)
    }
  }

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }

  return (
    <div className="h-screen w-screen overflow-hidden relative flex bg-white dark:bg-[#0d0d0d] transition-colors duration-500">
      
      {/* Settings / Top Right Float */}
      <div className="absolute top-6 right-6 z-50 flex items-center gap-4">
        <button 
          onClick={toggleTheme}
          className="brutal-card p-3 rounded-full flex items-center justify-center hover:scale-110 active:scale-95 transition-transform"
        >
          {theme === 'dark' ? <Sun className="h-5 w-5 text-yellow-400" /> : <Moon className="h-5 w-5" />}
        </button>
      </div>

      {/* History Sidebar */}
      {currentNode && (
        <HistoryTimeline 
          history={history} 
          currentIndex={currentIndex} 
          onRollback={rollbackTo} 
        />
      )}

      {/* Main Center Canvas */}
      <main className="flex-1 h-full flex flex-col items-center justify-center relative p-8">
        <div className="w-full max-w-4xl flex flex-col items-center justify-center">
          
          <AnimatePresence mode="wait">
            {!currentNode ? (
              <motion.div
                key="uploader"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, y: -50 }}
                className="w-full max-w-xl brutal-card p-8 rounded-lg"
              >
                <div className="text-center mb-8">
                  <Monitor className="h-16 w-16 mx-auto mb-4 dark:text-[#00ff00]" />
                  <h1 className="text-2xl font-pixel font-bold mb-2 uppercase tracking-tight leading-snug">
                    PixCI AI Studio
                  </h1>
                  <p className="text-gray-500 dark:text-gray-400 font-pixel text-xs leading-relaxed">
                    Upload initial image to start editing (Pixel Style)
                  </p>
                </div>
                
                {encodeMutation.isPending ? (
                  <div className="flex flex-col items-center justify-center py-12 gap-4">
                    <div className="w-12 h-12 border-4 border-black dark:border-[#00ff00] border-t-transparent animate-spin rounded-full"></div>
                    <p className="font-pixel text-xs animate-pulse">ENCODING IMAGE TO PXVG...</p>
                  </div>
                ) : (
                  <ImageUploader onFileSelect={handleInitialUpload} />
                )}
              </motion.div>
            ) : (
              <motion.div
                key={`canvas-${currentIndex}`}
                initial={{ filter: 'blur(20px)', scale: 0.95 }}
                animate={{ filter: 'blur(0px)', scale: 1 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="relative flex items-center justify-center w-full aspect-square max-h-[65vh] group mb-20"
              >
                <div className="brutal-card p-2 md:p-6 bg-white dark:bg-black rounded-sm w-full h-full flex items-center justify-center">
                  {/* Processing Overlays */}
                  {isProcessing && (
                    <div className="absolute inset-0 z-20 flex bg-white/50 dark:bg-black/80 backdrop-blur-sm items-center justify-center">
                      <div className="text-center">
                        <Monitor className="h-12 w-12 mx-auto mb-4 animate-bounce dark:text-[#00ff00]" />
                        <div className="text-[#00ff00] font-pixel text-sm glitch">PROCESSING VECTOR...</div>
                      </div>
                    </div>
                  )}

                  {currentNode.base64Image.startsWith('data:') ? (
                     <img
                       src={currentNode.base64Image}
                       alt="AI Pixel Art"
                       className="w-full h-full object-contain pixel-rendering"
                     />
                  ) : (
                     <img
                       src={`data:image/png;base64,${currentNode.base64Image}`}
                       alt="AI Pixel Art"
                       className="w-full h-full object-contain pixel-rendering"
                     />
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

        </div>
      </main>

      {/* Floating Terminal Input at bottom */}
      {currentNode && (
        <FloatingInput 
          onSubmit={submitPrompt} 
          isProcessing={isProcessing} 
        />
      )}
      
      {/* Raw Background Grid Effect (Optional brutalist touch) */}
      <div className="pointer-events-none absolute inset-0 z-0 opacity-[0.03] dark:opacity-[0.02]" 
           style={{ backgroundImage: 'linear-gradient(var(--text-color) 1px, transparent 1px), linear-gradient(90deg, var(--text-color) 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
      </div>
    </div>
  )
}
