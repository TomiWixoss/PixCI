// Client-side AI functions that call Next.js API routes
// API key is stored securely on the server

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export interface AIEditRequest {
  pxvgCode?: string // Optional for follow-up edits
  userPrompt: string
  conversationHistory?: Message[]
}

export interface AIEditResponse {
  editedPxvg: string
  explanation: string
  conversationHistory: Message[]
  usage?: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

export async function editPixelArtWithAI(
  request: AIEditRequest
): Promise<AIEditResponse> {
  const response = await fetch('/api/ai/edit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'AI edit failed')
  }

  return response.json()
}
