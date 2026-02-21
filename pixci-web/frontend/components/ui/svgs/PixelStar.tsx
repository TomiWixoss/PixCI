import { SVGProps } from "react"

export function PixelStar(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" {...props}>
      <path d="M11 2h2v4h-2V2zM11 18h2v4h-2v-4zM2 11h4v2H2v-2zM18 11h4v2h-4v-2zM6 6h2v2H6V6zM16 6h2v2h-2V6zM6 16h2v2H6v-2zM16 16h2v2h-2v-2z" fill="currentColor" />
      <rect x="10" y="10" width="4" height="4" fill="currentColor" />
    </svg>
  )
}
