'use client'

import { HistoryNode } from '@/lib/hooks/useAIEditor'
import { motion } from 'framer-motion'

interface HistoryTimelineProps {
  history: HistoryNode[]
  currentIndex: number
  onRollback: (index: number) => void
}

export function HistoryTimeline({ history, currentIndex, onRollback }: HistoryTimelineProps) {
  if (history.length <= 0) return null

  return (
    <div className="flex items-center gap-4 overflow-x-auto scrollbar-hide py-4 px-2">
      {history.map((node, index) => {
        const isActive = index === currentIndex
        const isFuture = index > currentIndex

        return (
          <motion.div 
            key={node.id} 
            initial={{ scale: 0, opacity: 0 }} 
            animate={{ scale: 1, opacity: 1 }}
            className="flex-shrink-0"
          >
            <button
              onClick={() => onRollback(index)}
              disabled={isActive}
              className={`
                group flex flex-col items-center bg-white p-2 border-4 border-[var(--text-color)] transition-all
                ${isActive 
                  ? 'bg-[var(--accent-pink)] -translate-y-2 shadow-[4px_4px_0_var(--text-color)]' 
                  : 'hover:-translate-y-1 hover:shadow-[4px_4px_0_var(--accent-purple)]'}
                ${isFuture ? 'opacity-40 grayscale' : ''}
              `}
              style={{ transform: isActive ? 'rotate(0deg)' : `rotate(${index % 2 === 0 ? '-3deg' : '3deg'})` }}
            >
              <div className="w-16 h-16 border-2 border-[var(--text-color)] bg-[var(--bg-color)] p-1 overflow-hidden">
                <img 
                  src={node.base64Image.startsWith('data:') ? node.base64Image : `data:image/png;base64,${node.base64Image}`} 
                  className="w-full h-full object-cover pixel-rendering" 
                  alt="thumb"
                />
              </div>
              <div className={`mt-2 text-[8px] font-bold uppercase truncate w-16 text-center ${isActive ? 'text-white' : 'text-[var(--text-color)]'}`}>
                {node.prompt === 'Ảnh Gốc' ? 'ORIGIN' : `V.${index}`}
              </div>
            </button>
          </motion.div>
        )
      })}
    </div>
  )
}
