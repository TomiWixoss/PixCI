'use client'

import { useEffect, useRef, useState } from 'react'

interface PixelScrambleCanvasProps {
  base64Image: string
  isProcessing: boolean
}

export function PixelScrambleCanvas({ base64Image, isProcessing }: PixelScrambleCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const imgRef = useRef<HTMLImageElement>(null)
  const animationRef = useRef<number | undefined>(undefined)
  const [imageLoaded, setImageLoaded] = useState(false)

  useEffect(() => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.src = base64Image.startsWith('data:') ? base64Image : `data:image/png;base64,${base64Image}`
    
    img.onload = () => {
      imgRef.current = img
      setImageLoaded(true)
      if (!isProcessing) {
        drawNormal()
      }
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [base64Image])

  useEffect(() => {
    if (!imageLoaded) return

    if (isProcessing) {
      startScramble()
    } else {
      drawNormal()
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [isProcessing, imageLoaded])

  const drawNormal = () => {
    const canvas = canvasRef.current
    const img = imgRef.current
    if (!canvas || !img) return

    const ctx = canvas.getContext('2d', { willReadFrequently: true })
    if (!ctx) return

    canvas.width = img.width
    canvas.height = img.height
    ctx.imageSmoothingEnabled = false
    ctx.drawImage(img, 0, 0)
  }

  const startScramble = () => {
    const canvas = canvasRef.current
    const img = imgRef.current
    if (!canvas || !img) return

    const ctx = canvas.getContext('2d', { willReadFrequently: true })
    if (!ctx) return

    canvas.width = img.width
    canvas.height = img.height
    ctx.imageSmoothingEnabled = false

    const blockSize = Math.max(2, Math.floor(Math.min(canvas.width, canvas.height) / 32))
    
    let frame = 0

    const animate = () => {
      if (!isProcessing) {
        drawNormal()
        return
      }

      frame++
      
      // Vẽ lại ảnh gốc mỗi frame
      ctx.drawImage(img, 0, 0)
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)

      // Tính intensity dao động
      const intensity = Math.sin(frame * 0.15) * 0.5 + 0.5 // 0 to 1

      // Scramble random blocks
      const numBlocks = Math.floor(30 * intensity) + 10
      for (let i = 0; i < numBlocks; i++) {
        const x1 = Math.floor(Math.random() * (canvas.width / blockSize)) * blockSize
        const y1 = Math.floor(Math.random() * (canvas.height / blockSize)) * blockSize
        const x2 = Math.floor(Math.random() * (canvas.width / blockSize)) * blockSize
        const y2 = Math.floor(Math.random() * (canvas.height / blockSize)) * blockSize

        // Swap blocks
        for (let dy = 0; dy < blockSize; dy++) {
          for (let dx = 0; dx < blockSize; dx++) {
            if (x1 + dx < canvas.width && y1 + dy < canvas.height &&
                x2 + dx < canvas.width && y2 + dy < canvas.height) {
              const idx1 = ((y1 + dy) * canvas.width + (x1 + dx)) * 4
              const idx2 = ((y2 + dy) * canvas.width + (x2 + dx)) * 4

              // Swap RGBA values
              for (let c = 0; c < 4; c++) {
                const temp = imageData.data[idx1 + c]
                imageData.data[idx1 + c] = imageData.data[idx2 + c]
                imageData.data[idx2 + c] = temp
              }
            }
          }
        }
      }

      ctx.putImageData(imageData, 0, 0)
      animationRef.current = requestAnimationFrame(animate)
    }

    animate()
  }

  return (
    <canvas
      ref={canvasRef}
      className="w-full h-full object-contain pixel-rendering drop-shadow-xl"
      style={{ imageRendering: 'pixelated' }}
    />
  )
}
