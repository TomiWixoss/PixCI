import { SVGProps } from "react"

export function PixelWand(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="currentColor" {...props}>
      <path d="M14 2h4v4h4v4h-4v4h-4v-4h-4V6h4V2z" fill="#FFD700" />
      <rect x="16" y="6" width="2" height="2" fill="#FFF" />
      <path d="M10 20h2v-2h2v-2h2v-2h-2v2h-2v2h-2v2zM8 22h2v-2H8v2zM6 24h2v-2H6v2zM4 26h2v-2H4v2zM2 30h2v-2H2v2z" fill="#8A2BE2" />
      <path d="M4 30h2v-2H4v2zM6 28h2v-2H6v2z" fill="#FF69B4" />
    </svg>
  )
}
