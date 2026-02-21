import { SVGProps } from "react"

export function PixelImage(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" {...props}>
      <path d="M2 2h20v20H2V2z" fill="currentColor" opacity="0.1" />
      <path d="M2 2h20v4H2V2zM2 18h20v4H2v-4zM2 6h4v12H2V6zM18 6h4v12h-4V6z" fill="currentColor" />
      <rect x="8" y="8" width="4" height="4" fill="currentColor" />
      <path d="M6 14h12v4H6v-4z" fill="currentColor" />
      <rect x="10" y="12" width="4" height="2" fill="currentColor" />
    </svg>
  )
}
