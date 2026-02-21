import { SVGProps } from "react"

export function PixelCloud(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 24" fill="none" {...props}>
      <path d="M6 10h6v2H8v2H6v-4z" fill="currentColor" opacity="0.7"/>
      <path d="M14 8h8v4h-6v2h-2v-6z" fill="currentColor"/>
      <path d="M24 8h6v2h-4v2h-2v-4z" fill="currentColor" opacity="0.7"/>
      <path d="M8 14h6v2H10v2H8v-4z" fill="currentColor" opacity="0.5"/>
      <path d="M16 14h8v4h-6v2h-2v-6z" fill="currentColor" opacity="0.5"/>
      <path d="M26 14h6v2h-4v2h-2v-4z" fill="currentColor" opacity="0.5"/>
    </svg>
  )
}
