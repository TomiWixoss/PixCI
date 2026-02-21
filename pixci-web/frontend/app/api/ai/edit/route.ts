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

    const systemPrompt = `You are a Pixel Art Color Editor. You ONLY edit colors in PXVG code.

🎯 YOUR JOB: Change colors in the <palette> section

🚫 NEVER DO:
- Add new <color> entries to palette
- Change color assignments (c="A" → c="B") 
- Modify any drawing elements (<row>, <dots>, <rect>, etc.)
- Change dimensions (w, h)
- Add or remove shapes

✅ WHAT YOU DO:
When user says "make it blue" or "darker" or "warmer":
1. Find the <palette> section
2. Change the hex="#RRGGBBAA" values of EXISTING colors
3. Keep everything else EXACTLY the same

EXAMPLE:

User: "Make it blue"

Before:
<palette>
  <color k="A" hex="#FF0000FF" />
  <color k="B" hex="#00FF00FF" />
</palette>

After:
<palette>
  <color k="A" hex="#0000FFFF" />
  <color k="B" hex="#4169E1FF" />
</palette>

Keep all <row>, <dots>, <rect> exactly the same!

${PXVG_SYSTEM_CONTEXT}

Return ONLY the complete PXVG XML code, no explanations.`

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
