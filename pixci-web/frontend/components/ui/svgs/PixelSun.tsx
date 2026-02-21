import { SVGProps } from "react"

export function PixelSun(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {...props}>
      <rect x="10" y="2" width="4" height="4" fill="currentColor" />
      <rect x="10" y="18" width="4" height="4" fill="currentColor" />
      <rect x="2" y="10" width="4" height="4" fill="currentColor" />
      <rect x="18" y="10" width="4" height="4" fill="currentColor" />
      <rect x="6" y="6" width="12" height="12" fill="currentColor" />
      <rect x="8" y="8" width="8" height="8" fill="var(--panel-bg)" />
    </svg>
  )
}
