'use client'

import { motion } from 'framer-motion'
import { HistoryNode } from '@/lib/hooks/useAIEditor'
import { Undo2 } from 'lucide-react'

interface HistoryTimelineProps {
  history: HistoryNode[]
  currentIndex: number
  onRollback: (index: number) => void
}

export function HistoryTimeline({ history, currentIndex, onRollback }: HistoryTimelineProps) {
  if (history.length === 0) return null

  return (
    <div className="absolute top-0 left-0 h-full w-64 p-6 hidden lg:flex flex-col gap-6 z-40 bg-white/5 dark:bg-black/50 backdrop-blur-md border-r-2 border-black dark:border-[#333]">
      <div className="flex items-center gap-3 border-b-2 border-black dark:border-[#00ff00] pb-4">
        <Undo2 className="h-6 w-6 dark:text-[#00ff00]" />
        <h2 className="text-sm font-pixel font-bold uppercase tracking-wider dark:text-[#00ff00]">Lịch sử AI</h2>
      </div>

      <div className="flex-1 overflow-y-auto pr-2 space-y-4">
        {history.map((node, index) => {
          const isActive = index === currentIndex
          const isFuture = index > currentIndex

          return (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              key={node.id}
            >
              <button
                onClick={() => onRollback(index)}
                disabled={isActive}
                className={`
                  w-full text-left p-3 border-2 transition-all relative
                  ${isActive 
                    ? 'border-black dark:border-[#00ff00] bg-black text-white dark:bg-[#00ff00] dark:text-black translate-x-1 shadow-[4px_4px_0px_0px_rgba(0,255,0,0.4)] dark:shadow-[4px_4px_0px_0px_rgba(255,255,255,0.2)]' 
                    : 'border-black dark:border-[#333] bg-white dark:bg-[#111] hover:-translate-y-1 hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] dark:hover:shadow-[4px_4px_0px_0px_rgba(0,255,0,0.8)]'
                  }
                  ${isFuture ? 'opacity-40 grayscale' : ''}
                `}
              >
                <div className="text-xs opacity-70 mb-1 font-pixel">[{index}] STEP</div>
                <div className="text-sm font-bold truncate">
                  {node.prompt}
                </div>
              </button>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
