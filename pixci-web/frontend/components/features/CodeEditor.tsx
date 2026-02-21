'use client'

import { useState } from 'react'
import Editor from '@monaco-editor/react'
import { Copy, Download, Check } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { downloadFile } from '@/lib/utils'
import toast from 'react-hot-toast'

interface CodeEditorProps {
  value: string
  onChange?: (value: string) => void
  readOnly?: boolean
  language?: string
  height?: string
}

export function CodeEditor({ 
  value, 
  onChange, 
  readOnly = false,
  language = 'xml',
  height = '400px'
}: CodeEditorProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(value)
      setCopied(true)
      toast.success('Đã copy vào clipboard!')
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      toast.error('Không thể copy')
    }
  }

  const handleDownload = () => {
    downloadFile(value, 'output.pxvg.xml', 'text/xml')
    toast.success('Đã tải xuống file!')
  }

  return (
    <div className="relative border border-gray-300 rounded-lg overflow-hidden">
      <div className="absolute top-2 right-2 z-10 flex gap-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleCopy}
          className="bg-white/90 hover:bg-white"
        >
          {copied ? (
            <Check className="h-4 w-4 text-green-600" />
          ) : (
            <Copy className="h-4 w-4" />
          )}
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleDownload}
          className="bg-white/90 hover:bg-white"
        >
          <Download className="h-4 w-4" />
        </Button>
      </div>
      <Editor
        height={height}
        language={language}
        value={value}
        onChange={(val) => onChange?.(val || '')}
        theme="vs-light"
        options={{
          readOnly,
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          wordWrap: 'on',
          automaticLayout: true,
        }}
      />
    </div>
  )
}
