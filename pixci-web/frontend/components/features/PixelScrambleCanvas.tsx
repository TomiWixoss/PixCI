'use client'

interface PixelScrambleCanvasProps {
  base64Image: string
  isProcessing: boolean
}

export function PixelScrambleCanvas({ base64Image, isProcessing }: PixelScrambleCanvasProps) {
  const imageSrc = base64Image.startsWith('data:') ? base64Image : `data:image/png;base64,${base64Image}`

  return (
    <img
      src={imageSrc}
      alt="Artwork"
      className={`w-full h-full object-contain pixel-rendering drop-shadow-xl transition-all duration-500 ${
        isProcessing ? 'blur-md opacity-70 scale-105' : ''
      }`}
    />
  )
}
