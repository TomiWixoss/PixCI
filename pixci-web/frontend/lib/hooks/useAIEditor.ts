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
  pxvgCodes: string[]
  base64Images: string[]
  unsubmittedReferences: string[]
  conversationHistory: Message[]
}

export function useAIEditor() {
  const [history, setHistory] = useState<HistoryNode[]>([])
  const [currentIndex, setCurrentIndex] = useState<number>(-1)
  const [isProcessing, setIsProcessing] = useState(false)

  const currentNode = currentIndex >= 0 ? history[currentIndex] : null

  const addInitialState = useCallback((pxvgCodes: string[], base64Images: string[]) => {
    const rootNode: HistoryNode = {
      id: 'root-start',
      prompt: 'Ảnh Gốc',
      pxvgCodes,
      base64Images,
      unsubmittedReferences: pxvgCodes,
      conversationHistory: []
    }
    setHistory([rootNode])
    setCurrentIndex(0)
  }, [])

  const appendImagesToCurrent = useCallback((newPxvgCodes: string[], newBase64Images: string[]) => {
    setHistory(prev => {
      const newHist = [...prev]
      if (!newHist[currentIndex]) return prev
      
      const current = { ...newHist[currentIndex] }
      current.pxvgCodes = [...current.pxvgCodes, ...newPxvgCodes]
      current.base64Images = [...current.base64Images, ...newBase64Images]
      current.unsubmittedReferences = [...(current.unsubmittedReferences || []), ...newPxvgCodes]
      
      newHist[currentIndex] = current
      return newHist
    })
  }, [currentIndex])

  const removeImageFromCurrent = useCallback((indexToRemove: number) => {
    setHistory(prev => {
      const newHist = [...prev]
      if (!newHist[currentIndex]) return prev
      
      const current = { ...newHist[currentIndex] }
      const pxvgToRemove = current.pxvgCodes[indexToRemove]
      
      current.pxvgCodes = current.pxvgCodes.filter((_, i) => i !== indexToRemove)
      current.base64Images = current.base64Images.filter((_, i) => i !== indexToRemove)
      current.unsubmittedReferences = current.unsubmittedReferences.filter(code => code !== pxvgToRemove)
      
      newHist[currentIndex] = current
      return newHist
    })
  }, [currentIndex])

  const submitPrompt = async (prompt: string) => {
    if (!currentNode) {
      toast.error('Chưa có ảnh gốc nào được nạp!')
      return
    }

    setIsProcessing(true)
    try {
      const isFirstEdit = currentIndex === 0
      
      const result = await editPixelArtWithAI({
        inputPxvgCodes: currentNode.unsubmittedReferences,
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
        pxvgCodes: [result.editedPxvg],
        base64Images: [decoded.image_base64],
        unsubmittedReferences: [],
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
    appendImagesToCurrent,
    removeImageFromCurrent,
    submitPrompt,
    rollbackTo,
    reset
  }
}
