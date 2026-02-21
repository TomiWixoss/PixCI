import { SVGProps } from "react"

export function PixelLogo(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" {...props}>
      <path d="M4 2H20V4H22V20H20V22H4V20H2V4H4V2Z" fill="var(--text-color)" />
      <rect x="4" y="4" width="16" height="16" fill="var(--panel-bg)" />
      <rect x="6" y="6" width="4" height="4" fill="var(--accent-purple)" />
      <rect x="14" y="6" width="4" height="4" fill="var(--accent-pink)" />
      <rect x="10" y="10" width="4" height="4" fill="var(--text-color)" />
      <rect x="6" y="14" width="12" height="4" fill="var(--accent-yellow)" />
      <rect x="18" y="4" width="2" height="2" fill="#FFFFFF" />
    </svg>
  )
}
