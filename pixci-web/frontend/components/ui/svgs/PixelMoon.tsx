import { SVGProps } from "react"

export function PixelMoon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" {...props}>
      <path d="M12 2h2v2h2v2h2v2h2v4h-2v2h-2v2h-2v2h-2v2h-4v-2H8v-2H6v-2H4V8h2V6h2V4h4V2z" fill="currentColor" />
      <path d="M14 6h-2V4h-2v2H8v2H6v4h2v2h2v2h2v2h2v-2h2v-2h-2v-2h-2V8h2V6z" fill="var(--panel-bg)" />
    </svg>
  )
}
