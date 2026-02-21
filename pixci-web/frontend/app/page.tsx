'use client'

import { useState } from 'react'
import { EncodeTab } from '@/components/features/EncodeTab'
import { DecodeTab } from '@/components/features/DecodeTab'
import { useAppStore } from '@/lib/store/useAppStore'
import { Image as ImageIcon, Code, Github } from 'lucide-react'

export default function Home() {
  const { activeTab, setActiveTab } = useAppStore()

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <ImageIcon className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">PixCI Web</h1>
                <p className="text-sm text-gray-600">Pixel Art Converter</p>
              </div>
            </div>
            <a
              href="https://github.com/yourusername/pixci"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-gray-900 transition-colors"
            >
              <Github className="h-5 w-5" />
              <span className="hidden sm:inline">GitHub</span>
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('encode')}
                className={`
                  flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${
                    activeTab === 'encode'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <ImageIcon className="h-5 w-5" />
                Encode (Ảnh → PXVG)
              </button>
              <button
                onClick={() => setActiveTab('decode')}
                className={`
                  flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${
                    activeTab === 'decode'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <Code className="h-5 w-5" />
                Decode (PXVG → Ảnh)
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div className="animate-fadeIn">
          {activeTab === 'encode' ? <EncodeTab /> : <DecodeTab />}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-600">
            <p>
              PixCI Web v1.0.0 - Enterprise-grade pixel art conversion tool
            </p>
            <p className="mt-1">
              Powered by FastAPI + Next.js + PXVG Format
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
