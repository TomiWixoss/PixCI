'use client'

import { useState } from 'react'
import { useAIEditor } from '@/lib/hooks/useAIEditor'
import { useEncode } from '@/lib/hooks/useEncode'
import { FloatingInput } from '@/components/ui/FloatingInput'
import { HistoryTimeline } from '@/components/features/HistoryTimeline'
import { ImageUploader } from '@/components/features/ImageUploader'
import { AnimatePresence, motion } from 'framer-motion'
import { useTheme } from 'next-themes'
import { Moon, Sun, Monitor } from 'lucide-react'
import { PixelStar } from '@/components/ui/svgs/PixelStar'
import { TechGrid } from '@/components/ui/svgs/TechGrid'
import { PixelCornerNodes } from '@/components/ui/svgs/PixelCornerNodes'
import { AIEye } from '@/components/ui/svgs/AIEye'
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
      toast.success('PXVG Engine Khởi tạo thành công!', { icon: '🚀' })
    } catch (error) {
      toast.error('Có lỗi khi số hoá ảnh!')
      setInitialFile(null)
    }
  }

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark')
  }

  return (
    <div className="h-screen w-screen overflow-hidden relative flex flex-col bg-white dark:bg-[#0d0d0d] transition-colors duration-500 selection:bg-[#00ff00] selection:text-black">
      
      {/* Absolute Background Grid */}
      <TechGrid className="absolute inset-0 w-full h-full opacity-[0.05] dark:opacity-[0.1] text-black dark:text-[#00ff00] pointer-events-none z-0" />

      {/* Edge Decorations */}
      <div className="absolute inset-4 pointer-events-none z-50 border-2 border-black/10 dark:border-[#00ff00]/20 hidden md:block">
        <PixelCornerNodes className="w-full h-full text-black/20 dark:text-[#00ff00]/40" />
      </div>

      {/* Floating Stars BG */}
      <div className="absolute inset-0 z-0 overflow-hidden pointer-events-none">
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={i}
            initial={{ y: "100vh", opacity: 0 }}
            animate={{ 
              y: "-20vh", 
              opacity: [0, 1, 0, 1, 0],
              x: Math.sin(i) * 100 
            }}
            transition={{
              duration: 10 + Math.random() * 10,
              repeat: Infinity,
              ease: "linear",
              delay: Math.random() * 5
            }}
            className="absolute text-black/10 dark:text-[#00ff00]/20"
            style={{ left: `${Math.random() * 100}%` }}
          >
            <PixelStar className="w-6 h-6" />
          </motion.div>
        ))}
      </div>

      {/* History Top Bar */}
      {currentNode && (
        <HistoryTimeline 
          history={history} 
          currentIndex={currentIndex} 
          onRollback={rollbackTo} 
        />
      )}

      {/* Controls Container */}
      <div className={`absolute z-50 flex items-center gap-4 right-8 md:right-12 ${currentNode ? 'top-28 md:top-32' : 'top-8 md:top-12'}`}>
        <button 
          onClick={toggleTheme}
          className="brutal-card p-3 rounded-none flex items-center justify-center hover:scale-110 active:scale-95 transition-transform bg-white dark:bg-black text-black dark:text-[#00ff00] hover:bg-black hover:text-white dark:hover:bg-[#00ff00] dark:hover:text-black"
        >
          {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </button>
      </div>

      {/* Main Center Canvas */}
      <main className={`flex-1 flex flex-col items-center justify-center relative p-4 md:p-12 w-full z-10 ${currentNode ? 'mt-20 md:mt-24' : ''}`}>
        
        {/* Background Marquee Text */}
        {!currentNode && (
          <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 overflow-hidden pointer-events-none opacity-[0.03] dark:opacity-[0.05] whitespace-nowrap z-0">
            <motion.div
              animate={{ x: [0, -1000] }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="text-[12vw] font-pixel font-bold leading-none tracking-tighter"
            >
              PIXCI ENGINE PIXCI ENGINE PIXCI ENGINE PIXCI ENGINE
            </motion.div>
          </div>
        )}

        <div className="w-full max-w-5xl flex flex-col items-center justify-center relative z-20">
          
          <AnimatePresence mode="wait">
            {!currentNode ? (
              <motion.div
                key="uploader"
                initial={{ opacity: 0, scale: 0.9, y: 50 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, y: -50, filter: "blur(10px)" }}
                transition={{ type: "spring", stiffness: 300, damping: 25 }}
                className="w-full max-w-2xl brutal-card bg-white dark:bg-[#111] p-1 border-8 border-black dark:border-[#333] relative group"
              >
                {/* Decorative border corners */}
                <div className="absolute -top-3 -left-3 w-6 h-6 bg-black dark:bg-[#00ff00]"></div>
                <div className="absolute -top-3 -right-3 w-6 h-6 bg-black dark:bg-[#00ff00]"></div>
                <div className="absolute -bottom-3 -left-3 w-6 h-6 bg-black dark:bg-[#00ff00]"></div>
                <div className="absolute -bottom-3 -right-3 w-6 h-6 bg-black dark:bg-[#00ff00]"></div>

                <div className="p-8 md:p-12 border-4 border-dashed border-gray-300 dark:border-gray-700 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAiLz4KPHJlY3Qgd2lkdGg9IjEiIGhlaWdodD0iMSIgZmlsbD0iIzAwMCIgZmlsbC1vcGFjaXR5PSIwLjA1Ii8+Cjwvc3ZnPg==')] dark:bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSIjMDAwIiBmaWxsLW9wYWNpdHk9IjAiLz4KPHJlY3Qgd2lkdGg9IjEiIGhlaWdodD0iMSIgZmlsbD0iIzAwZmYwMCIgZmlsbC1vcGFjaXR5PSIwLjEiLz4KPC9zdmc+')]">
                  <div className="text-center mb-10 relative">
                    <motion.div
                      animate={{ y: [0, -10, 0] }}
                      transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                    >
                      <AIEye className="h-20 w-20 mx-auto mb-6 text-black dark:text-[#00ff00] drop-shadow-[5px_5px_0px_rgba(0,0,0,0.2)] dark:drop-shadow-[5px_5px_0px_rgba(0,255,0,0.2)]" />
                    </motion.div>
                    
                    <h1 className="text-3xl md:text-5xl font-pixel font-bold mb-4 uppercase tracking-tighter leading-none">
                      PIXCI STUDIO
                    </h1>
                    <div className="inline-block bg-black text-white dark:bg-[#00ff00] dark:text-black px-4 py-2 text-[10px] md:text-xs font-pixel font-bold uppercase tracking-widest shadow-[4px_4px_0px_0px_#ccc] dark:shadow-[4px_4px_0px_0px_#333]">
                      KHỞI TẠO ĐỘNG CƠ AI PIXEL
                    </div>
                  </div>
                  
                  {encodeMutation.isPending ? (
                    <div className="flex flex-col items-center justify-center py-16 gap-6 brutal-card bg-gray-50 dark:bg-black/50 border-2 border-black dark:border-[#00ff00]">
                      <div className="relative w-16 h-16">
                        <div className="w-16 h-16 border-4 border-black dark:border-[#00ff00] border-t-transparent animate-spin rounded-full absolute inset-0"></div>
                        <PixelStar className="absolute inset-0 m-auto w-6 h-6 animate-pulse text-black dark:text-[#00ff00]" />
                      </div>
                      <p className="font-pixel text-[10px] uppercase font-bold animate-pulse tracking-widest text-[#ff00ff]">ĐANG DI DỊCH VECTOR SANG PXVG...</p>
                    </div>
                  ) : (
                    <div className="transform hover:scale-[1.02] transition-transform">
                      <ImageUploader onFileSelect={handleInitialUpload} />
                    </div>
                  )}
                </div>
              </motion.div>
            ) : (
              <motion.div
                key={`canvas-${currentIndex}`}
                initial={{ filter: 'blur(20px)', scale: 0.9, opacity: 0 }}
                animate={{ filter: 'blur(0px)', scale: 1, opacity: 1 }}
                exit={{ scale: 1.1, opacity: 0 }}
                transition={{ duration: 0.6, type: "spring", bounce: 0.4 }}
                className="relative flex items-center justify-center w-full aspect-square max-h-[55vh] md:max-h-[65vh] group mb-24 md:mb-32"
              >
                <div className="absolute inset-0 bg-gradient-to-tr from-[#ff00ff]/20 to-[#00ffff]/20 dark:from-[#00ff00]/10 dark:to-transparent blur-3xl rounded-full scale-150 -z-10 animate-pulse"></div>

                <div className="brutal-card p-4 md:p-8 bg-white dark:bg-black rounded-none w-full h-full flex items-center justify-center relative shadow-[12px_12px_0px_0px_rgba(0,0,0,1)] dark:shadow-[12px_12px_0px_0px_rgba(0,255,0,0.5)] border-4 border-black dark:border-[#333]">
                  
                  {/* Decorative Frame Elements */}
                  <div className="absolute top-2 left-2 w-4 h-4 border-t-4 border-l-4 border-black dark:border-[#00ff00]"></div>
                  <div className="absolute top-2 right-2 w-4 h-4 border-t-4 border-r-4 border-black dark:border-[#00ff00]"></div>
                  <div className="absolute bottom-2 left-2 w-4 h-4 border-b-4 border-l-4 border-black dark:border-[#00ff00]"></div>
                  <div className="absolute bottom-2 right-2 w-4 h-4 border-b-4 border-r-4 border-black dark:border-[#00ff00]"></div>

                  {/* Processing Overlays */}
                  {isProcessing && (
                    <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="absolute inset-0 z-20 flex bg-white/80 dark:bg-black/90 backdrop-blur-md items-center justify-center"
                    >
                      <div className="text-center p-8 brutal-card border-black dark:border-[#ff00ff] border-4 shadow-[8px_8px_0px_0px_#000] dark:shadow-[8px_8px_0px_0px_#ff00ff]">
                        <AIEye className="h-16 w-16 mx-auto mb-6 text-black dark:text-[#ff00ff] glitch" />
                        <div className="text-black dark:text-[#ff00ff] font-pixel font-bold text-xs uppercase tracking-widest glitch">AI ĐANG MÃ HOÁ TIẾN TRÌNH...</div>
                        
                        <div className="w-full h-4 bg-gray-200 dark:bg-gray-800 mt-6 border-2 border-black dark:border-[#ff00ff] relative overflow-hidden">
                          <motion.div 
                            className="absolute inset-y-0 left-0 bg-black dark:bg-[#ff00ff] w-1/2"
                            animate={{ x: ["-100%", "200%"] }}
                            transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                          />
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {currentNode.base64Image.startsWith('data:') ? (
                     <img
                       src={currentNode.base64Image}
                       alt="AI Pixel Art"
                       className="w-full h-full object-contain pixel-rendering drop-shadow-2xl"
                     />
                  ) : (
                     <img
                       src={`data:image/png;base64,${currentNode.base64Image}`}
                       alt="AI Pixel Art"
                       className="w-full h-full object-contain pixel-rendering drop-shadow-2xl"
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
    </div>
  )
}
