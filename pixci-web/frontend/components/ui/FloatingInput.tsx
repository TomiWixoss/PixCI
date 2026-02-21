'use client'

import { useState, FormEvent, useRef, useEffect } from 'react'
import { Send, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs))
}

interface FloatingInputProps {
  onSubmit: (prompt: string) => void
  isProcessing: boolean
  placeholder?: string
}

export function FloatingInput({ onSubmit, isProcessing, placeholder = "Nhập lệnh cho AI (VD: Đổi nấm thành màu đỏ...)" }: FloatingInputProps) {
  const [value, setValue] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (value.trim() && !isProcessing) {
      onSubmit(value.trim())
      setValue('')
    }
  }

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  return (
    <motion.div 
      initial={{ y: 50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
      className="absolute bottom-10 left-1/2 -translate-x-1/2 w-full max-w-2xl px-4 z-50"
    >
      <form onSubmit={handleSubmit} className="brutal-card p-2 flex items-center gap-3 bg-white dark:bg-black w-full rounded-sm">
        <div className="flex-shrink-0 pl-2">
          {isProcessing ? (
            <Sparkles className="h-6 w-6 text-[var(--color-primary)] animate-pulse" />
          ) : (
            <div className="w-6 h-6 bg-black dark:bg-[#00ff00] animate-pulse" style={{ clipPath: 'polygon(0 0, 100% 50%, 0 100%)' }}></div>
          )}
        </div>
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={isProcessing}
          placeholder={isProcessing ? "AI Đang xử lý không gian Pixel..." : placeholder}
          className="flex-1 bg-transparent border-none outline-none text-base sm:text-lg font-pixel placeholder:text-gray-400 dark:placeholder:text-gray-600 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!value.trim() || isProcessing}
          className={cn(
            "brutal-btn p-3 px-6 flex items-center justify-center gap-2",
            (!value.trim() || isProcessing) && "opacity-50 cursor-not-allowed"
          )}
        >
          <span className="hidden sm:inline">GỬI LỆNH</span>
          <Send className="h-5 w-5" />
        </button>
      </form>
    </motion.div>
  )
}
