import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AppState {
  // Encode settings
  blockSize: number
  autoDetect: boolean
  setBlockSize: (size: number) => void
  setAutoDetect: (auto: boolean) => void

  // Decode settings
  scale: number
  setScale: (scale: number) => void

  // Current data
  currentPxvg: string | null
  currentImage: string | null
  setCurrentPxvg: (pxvg: string | null) => void
  setCurrentImage: (image: string | null) => void

  // UI state
  activeTab: 'encode' | 'decode'
  setActiveTab: (tab: 'encode' | 'decode') => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Encode settings
      blockSize: 1,
      autoDetect: false,
      setBlockSize: (size) => set({ blockSize: size }),
      setAutoDetect: (auto) => set({ autoDetect: auto }),

      // Decode settings
      scale: 10,
      setScale: (scale) => set({ scale }),

      // Current data
      currentPxvg: null,
      currentImage: null,
      setCurrentPxvg: (pxvg) => set({ currentPxvg: pxvg }),
      setCurrentImage: (image) => set({ currentImage: image }),

      // UI state
      activeTab: 'encode',
      setActiveTab: (tab) => set({ activeTab: tab }),
    }),
    {
      name: 'pixci-storage',
      partialize: (state) => ({
        blockSize: state.blockSize,
        autoDetect: state.autoDetect,
        scale: state.scale,
      }),
    }
  )
)
