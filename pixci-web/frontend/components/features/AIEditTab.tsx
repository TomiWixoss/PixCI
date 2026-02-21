'use client'

import { useState } from 'react'
import { ImageUploader } from './ImageUploader'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { useEncode } from '@/lib/hooks/useEncode'
import { useAIEdit } from '@/lib/hooks/useAIEdit'
import toast from 'react-hot-toast'
import { Sparkles, Image as ImageIcon, Wand2, RotateCcw, MessageSquare } from 'lucide-react'

export function AIEditTab() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [originalPxvg, setOriginalPxvg] = useState<string>('')
  const [originalImage, setOriginalImage] = useState<string>('')
  const [userPrompt, setUserPrompt] = useState('')

  const encodeMutation = useEncode()
  const { isEditing, editedImage, editCount, conversationHistory, editWithAI, reset } = useAIEdit()

  const handleEncode = async () => {
    if (!selectedFile) {
      toast.error('Please select an image first!')
      return
    }

    try {
      const result = await encodeMutation.mutateAsync({
        file: selectedFile,
        block_size: 1,
        auto_detect: true,
      })

      setOriginalPxvg(result.pxvg_code)
      
      // Create preview of original image
      const reader = new FileReader()
      reader.onload = () => {
        setOriginalImage(reader.result as string)
      }
      reader.readAsDataURL(selectedFile)

      // Reset AI edit state when new image is encoded
      reset()
      toast.success('Image encoded to PXVG!')
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Encoding failed')
    }
  }

  const handleAIEdit = async () => {
    if (!originalPxvg && editCount === 0) {
      toast.error('Please encode an image first!')
      return
    }

    if (!userPrompt.trim()) {
      toast.error('Please enter edit instructions!')
      return
    }

    try {
      await editWithAI(editCount === 0 ? originalPxvg : null, userPrompt)
      setUserPrompt('') // Clear input after successful edit
    } catch (error) {
      console.error('AI edit error:', error)
    }
  }

  const handleReset = () => {
    reset()
    setUserPrompt('')
    toast.success('Reset to original image')
  }

  return (
    <div className="space-y-6">
      {/* Step 1: Upload Image */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ImageIcon className="h-6 w-6" />
            Step 1: Upload Image
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <ImageUploader onFileSelect={setSelectedFile} />
          
          {selectedFile && (
            <Button
              onClick={handleEncode}
              isLoading={encodeMutation.isPending}
              className="w-full"
            >
              {encodeMutation.isPending ? 'Encoding...' : 'Encode to PXVG'}
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Step 2: AI Edit */}
      {originalPxvg && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Wand2 className="h-6 w-6" />
                Step 2: AI Edit Instructions
                {editCount > 0 && (
                  <span className="text-sm font-normal text-gray-500">
                    (Edit #{editCount + 1})
                  </span>
                )}
              </div>
              {editCount > 0 && (
                <Button
                  onClick={handleReset}
                  variant="outline"
                  size="sm"
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Reset
                </Button>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder={
                editCount === 0
                  ? "e.g., Make the mushroom blue, Add a sun in the sky..."
                  : "Continue editing: e.g., Now add a shadow, Make it darker..."
              }
              value={userPrompt}
              onChange={(e) => setUserPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !isEditing) {
                  handleAIEdit()
                }
              }}
            />

            <Button
              onClick={handleAIEdit}
              isLoading={isEditing}
              disabled={!userPrompt.trim()}
              className="w-full"
            >
              <Sparkles className="h-4 w-4 mr-2" />
              {isEditing ? 'AI is editing...' : editCount === 0 ? 'Edit with AI' : 'Continue Editing'}
            </Button>

            {/* Conversation History */}
            {conversationHistory.length > 0 && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center gap-2 mb-3">
                  <MessageSquare className="h-4 w-4 text-gray-600" />
                  <h4 className="text-sm font-medium text-gray-700">
                    Edit History ({Math.floor(conversationHistory.length / 2)} edits)
                  </h4>
                </div>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {conversationHistory
                    .filter((msg) => msg.role === 'user')
                    .map((msg, idx) => (
                      <div key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="font-medium text-blue-600">#{idx + 1}:</span>
                        <span className="flex-1">
                          {msg.content.includes('USER INSTRUCTION:')
                            ? msg.content.split('USER INSTRUCTION:')[1].split('\n')[0].trim()
                            : msg.content.split('Continue editing:')[1]?.split('\n')[0].trim() || msg.content}
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 3: Results */}
      {(originalImage || editedImage) && (
        <Card>
          <CardHeader>
            <CardTitle>Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Original */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">Original</h3>
                <div className="border-2 border-gray-300 rounded-lg p-4 bg-gray-50 flex items-center justify-center">
                  {originalImage && (
                    <img
                      src={originalImage}
                      alt="Original"
                      className="max-w-full h-auto"
                      style={{ imageRendering: 'pixelated' }}
                    />
                  )}
                </div>
              </div>

              {/* Edited */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-2">
                  AI Edited {editCount > 0 && `(${editCount} edit${editCount > 1 ? 's' : ''})`}
                  {isEditing && ' (Processing...)'}
                </h3>
                <div className="border-2 border-blue-300 rounded-lg p-4 bg-blue-50 flex items-center justify-center">
                  {editedImage ? (
                    <img
                      src={`data:image/png;base64,${editedImage}`}
                      alt="Edited"
                      className="max-w-full h-auto"
                      style={{ imageRendering: 'pixelated' }}
                    />
                  ) : isEditing ? (
                    <div className="text-gray-500">Generating...</div>
                  ) : (
                    <div className="text-gray-400">No edit yet</div>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
