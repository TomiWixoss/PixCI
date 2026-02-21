import { useState } from 'react'
import { editPixelArtWithAI } from '@/lib/ai/aio-client'
import { decodeService } from '@/lib/api/services'
import toast from 'react-hot-toast'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export interface AIEditState {
  isEditing: boolean
  editedPxvg: string | null
  editedImage: string | null
  error: string | null
  conversationHistory: Message[]
  editCount: number
}

export function useAIEdit() {
  const [state, setState] = useState<AIEditState>({
    isEditing: false,
    editedPxvg: null,
    editedImage: null,
    error: null,
    conversationHistory: [],
    editCount: 0,
  })

  const editWithAI = async (
    pxvgCode: string | null,
    userPrompt: string
  ) => {
    setState((prev) => ({ 
      ...prev, 
      isEditing: true, 
      error: null 
    }))

    try {
      // For first edit, send pxvgCode. For follow-ups, send conversation history
      const result = await editPixelArtWithAI({
        pxvgCode: state.editCount === 0 ? pxvgCode || undefined : undefined,
        userPrompt,
        conversationHistory: state.editCount > 0 ? state.conversationHistory : undefined,
      })

      setState((prev) => ({ 
        ...prev, 
        editedPxvg: result.editedPxvg,
        conversationHistory: result.conversationHistory,
        editCount: prev.editCount + 1,
      }))

      // Decode edited PXVG to image
      const decoded = await decodeService.decodePxvg({
        pxvg_code: result.editedPxvg,
        scale: 10,
      })

      setState((prev) => ({
        ...prev,
        isEditing: false,
        editedImage: decoded.image_base64,
      }))

      toast.success(`AI edit #${state.editCount + 1} completed!`)
      return result
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'AI edit failed'
      setState((prev) => ({
        ...prev,
        isEditing: false,
        error: errorMsg,
      }))
      toast.error(errorMsg)
      throw error
    }
  }

  const reset = () => {
    setState({
      isEditing: false,
      editedPxvg: null,
      editedImage: null,
      error: null,
      conversationHistory: [],
      editCount: 0,
    })
  }

  return {
    ...state,
    editWithAI,
    reset,
  }
}
