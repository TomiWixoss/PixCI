import { NextRequest, NextResponse } from 'next/server'
import { AIO } from 'aio-llm'

// PXVG System Context
const PXVG_SYSTEM_CONTEXT = `# PXVG (Pixel Vector Graphics)
> PXVG là một ngôn ngữ đánh dấu (Markup Language) dựa trên XML, được thiết kế đặc biệt làm mã trung gian (Static IR) để định nghĩa và sinh hình ảnh Pixel Art.

## Cấu trúc gốc
<pxvg w="32" h="32" xmlns="http://pixci.dev/pxvg">
  <palette><color k="A" hex="#1C1C1EFF" /></palette>
  <layer id="main"><!-- Nội dung --></layer>
  <postprocess><!-- Hiệu ứng --></postprocess>
</pxvg>

## Bảng màu (Palette)
- <palette load="endesga-32" /> - Load palette có sẵn
- <color k="A" hex="#FF0000FF" /> - Định nghĩa màu (key 1 ký tự)

## Thẻ vẽ cơ bản (Tọa độ phải là số nguyên)
- <row y="5" x1="10" x2="20" c="A" /> - Dòng ngang (tiết kiệm token nhất)
- <dots c="A" pts="5,3 6,3 7,4" /> - Nhiều pixel rời
- <rect x="5" y="5" w="10" h="10" c="A" /> - Hình chữ nhật
- <circle cx="16" cy="16" r="8" fill="true" c="A" /> - Hình tròn
- <line x1="0" y1="0" x2="10" y2="10" c="A" /> - Đường thẳng
- <polygon pts="10,10 20,20 10,20" c="A" /> - Đa giác

## Thẻ nâng cao
- <dither x="5" y="5" w="10" h="10" c="A" c2="B" pattern="checkered" /> - Trộn màu
- <gradient x="5" y="5" w="10" h="10" mode="vertical" palette="A,B,C" /> - Chuyển màu

## Transform (trong layer)
- <flip-x />, <flip-y /> - Lật ảnh
- <mirror-x />, <mirror-y /> - Phản chiếu đối xứng
- <alpha-lock v="true" /> - Khóa alpha (chỉ vẽ vào vùng có màu)

## Post-processing (cuối file)
- <outline sel-out="true" thickness="1" /> - Viền tự động
- <shadow dir="top_left" intensity="0.5" /> - Bóng đổ
- <jaggies /> - Khử răng cưa

## Xóa pixel
Dùng c="CLEAR" trong bất kỳ thẻ nào để tẩy pixel.

## Animation
<defs>
  <group id="body"><rect x="10" y="10" w="12" h="8" c="A" /></group>
</defs>
<animation name="idle" columns="2">
  <frame id="1"><use ref="body" /></frame>
  <frame id="2"><use ref="body" y="1" /></frame>
</animation>`

// Initialize AIO client (server-side only)
const aioClient = new AIO({
  providers: [
    {
      provider: 'google-ai',
      apiKeys: [
        {
          key: process.env.GOOGLE_API_KEY || '',
          priority: 10,
        },
        {
          key: process.env.GOOGLE_API_KEY_2 || '',
          priority: 9,
        },
      ],
      models: [
        {
          modelId: 'gemini-3-flash-preview',
          priority: 10,
        },
      ],
      priority: 10,
    },
  ],
  maxRetries: 3,
  retryDelay: 1000,
  enableLogging: true,
})

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export async function POST(request: NextRequest) {
  try {
    const { pxvgCode, userPrompt, conversationHistory } = await request.json()

    if (!userPrompt) {
      return NextResponse.json(
        { error: 'Missing userPrompt' },
        { status: 400 }
      )
    }

    if (!process.env.GOOGLE_API_KEY) {
      return NextResponse.json(
        { error: 'GOOGLE_API_KEY not configured' },
        { status: 500 }
      )
    }

    const systemPrompt = `You are a CONSERVATIVE Pixel Art Color Editor AI. Your job is to make MINIMAL color changes to existing PXVG pixel art.

🚫 ABSOLUTE RESTRICTIONS:
1. DO NOT add new colors to the palette unless EXPLICITLY requested
2. DO NOT change color assignments (c="A" → c="B") unless EXPLICITLY requested
3. DO NOT add new shapes, objects, or drawing elements
4. DO NOT remove existing elements
5. DO NOT change dimensions (w, h attributes)
6. DO NOT modify the structure of <layer>, <row>, <dots>, <rect>, etc.

✅ WHAT YOU CAN DO (ONLY when user explicitly asks):
- Modify existing color HEX values in <palette> (e.g., change #FF0000 to #00FF00)
- Add new colors to palette (only if user says "add color X")
- Change which color is assigned to pixels (only if user says "change X to Y")
- Apply color transformations (only if user says "make darker/lighter/warmer")

⚠️ DEFAULT BEHAVIOR:
When user says something vague like "make it blue" or "change colors":
1. ONLY modify the HEX values of EXISTING colors in the palette
2. DO NOT add new <color> entries
3. DO NOT change c="X" attributes in drawing elements
4. Keep the same color keys (A, B, C, etc.)

${PXVG_SYSTEM_CONTEXT}

CORRECT EXAMPLES:

User: "Make it blue"
❌ WRONG: Adding new colors or changing c="A" to c="B"
✅ CORRECT: Change existing palette colors to blue shades
<palette>
  <color k="A" hex="#1E3A8AFF" />  <!-- was red, now blue -->
  <color k="B" hex="#3B82F6FF" />  <!-- was orange, now lighter blue -->
</palette>
<!-- Keep all <row>, <dots>, <rect> exactly the same -->

User: "Darker"
❌ WRONG: Adding new dark colors
✅ CORRECT: Reduce brightness of existing colors
<palette>
  <color k="A" hex="#0A0A0AFF" />  <!-- was #1A1A1A -->
  <color k="B" hex="#2A2A2AFF" />  <!-- was #4A4A4A -->
</palette>

User: "Add red color"
✅ CORRECT: Now you can add a new color
<palette>
  <color k="A" hex="#1C1C1EFF" />
  <color k="B" hex="#FF0000FF" />  <!-- NEW color added -->
</palette>

User: "Change the sky to purple"
✅ CORRECT: Now you can change color assignments
<row y="5" x1="10" x2="20" c="C" />  <!-- was c="A", now c="C" for purple -->

🎯 GOLDEN RULE: 
If the user doesn't explicitly say to "add colors" or "change assignments", 
then ONLY modify the HEX values of existing palette colors. 
Keep everything else EXACTLY the same.

CONVERSATION MODE:
- First message: You'll receive the original PXVG code
- Follow-up edits: Use conversation history
- Always preserve xmlns="http://pixci.dev/pxvg"
- Return ONLY valid PXVG XML code, no explanations`

    // Build messages array
    const messages: Message[] = []

    // If there's conversation history, use it
    if (conversationHistory && Array.isArray(conversationHistory) && conversationHistory.length > 0) {
      messages.push(...conversationHistory)
      // Add new user prompt
      messages.push({
        role: 'user',
        content: `Continue editing: ${userPrompt}

Return ONLY the edited PXVG code:`,
      })
    } else {
      // First message - include the original PXVG code
      if (!pxvgCode) {
        return NextResponse.json(
          { error: 'Missing pxvgCode for first edit' },
          { status: 400 }
        )
      }
      messages.push({
        role: 'user',
        content: `USER INSTRUCTION: ${userPrompt}

CURRENT PXVG CODE:
${pxvgCode}

Return ONLY the edited PXVG code (no explanations):`,
      })
    }

    const response = await aioClient.chatCompletion({
      provider: 'google-ai',
      model: 'gemini-3-flash-preview',
      systemPrompt,
      messages,
      temperature: 0.7,
      max_tokens: 65536,
    })

    const content = response.choices[0].message.content
    const contentStr = typeof content === 'string' ? content : JSON.stringify(content)

    // Extract PXVG code from response
    const pxvgMatch = contentStr.match(/<pxvg[\s\S]*?<\/pxvg>/i)
    const editedPxvg = pxvgMatch ? pxvgMatch[0] : contentStr

    // Build updated conversation history
    const updatedHistory = [
      ...messages,
      {
        role: 'assistant' as const,
        content: editedPxvg,
      },
    ]

    return NextResponse.json({
      editedPxvg,
      explanation: 'AI edited your pixel art based on your instruction',
      usage: response.usage,
      conversationHistory: updatedHistory,
    })
  } catch (error) {
    console.error('AI Edit Error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'AI edit failed' },
      { status: 500 }
    )
  }
}
