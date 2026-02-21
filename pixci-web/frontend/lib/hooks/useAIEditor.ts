import { useState, useCallback } from 'react'
import { editPixelArtWithAI } from '@/lib/ai/aio-client'
import { decodeService } from '@/lib/api/services'
import toast from 'react-hot-toast'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export interface HistoryNode {
  id: string
  prompt: string
  pxvgCode: string
  base64Image: string
  conversationHistory: Message[]
}

export function useAIEditor() {
  const [history, setHistory] = useState<HistoryNode[]>([])
  const [currentIndex, setCurrentIndex] = useState<number>(-1)
  const [isProcessing, setIsProcessing] = useState(false)

  const currentNode = currentIndex >= 0 ? history[currentIndex] : null

  const addInitialState = useCallback((pxvgCode: string, base64Image: string) => {
    const rootNode: HistoryNode = {
      id: 'root-start',
      prompt: 'Ảnh Gốc',
      pxvgCode,
      base64Image,
      conversationHistory: []
    }
    setHistory([rootNode])
    setCurrentIndex(0)
  }, [])

  const submitPrompt = async (prompt: string) => {
    if (!currentNode) {
      toast.error('Chưa có ảnh gốc nào được nạp!')
      return
    }

    setIsProcessing(true)
    try {
      const isFirstEdit = currentIndex === 0
      
      const result = await editPixelArtWithAI({
        pxvgCode: isFirstEdit ? currentNode.pxvgCode : undefined,
        userPrompt: prompt,
        conversationHistory: isFirstEdit ? undefined : currentNode.conversationHistory,
      })

      const decoded = await decodeService.decodePxvg({
        pxvg_code: result.editedPxvg,
        scale: 10,
      })

      const newNode: HistoryNode = {
        id: `edit-${Date.now()}`,
        prompt,
        pxvgCode: result.editedPxvg,
        base64Image: decoded.image_base64,
        conversationHistory: result.conversationHistory
      }

      // If we are rolled back, slicing history discards future branches
      const newHistory = [...history.slice(0, currentIndex + 1), newNode]
      setHistory(newHistory)
      setCurrentIndex(newHistory.length - 1)
      
      toast.success('Đã chỉnh sửa hình ảnh hoàn tất.')
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Quá trình phân tích thất bại.')
      console.error(error)
    } finally {
      setIsProcessing(false)
    }
  }

  const rollbackTo = (index: number) => {
    if (index >= 0 && index < history.length) {
      setCurrentIndex(index)
      toast('Đã phục hồi phiên bản: ' + history[index].prompt)
    }
  }

  const reset = () => {
    setHistory([])
    setCurrentIndex(-1)
  }

  return {
    history,
    currentIndex,
    currentNode,
    isProcessing,
    addInitialState,
    submitPrompt,
    rollbackTo,
    reset
  }
}
