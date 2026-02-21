import { SVGProps } from "react"

export function PixelPalette(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" fill="currentColor" {...props}>
      <path d="M12 4h8v2h-8V4zm8 2h4v2h-4V6zM6 8h4v2H6V8zm18 0h2v4h-2V8zM4 10h2v12H4V10zm24 2h2v8h-2v-8zM6 22h4v2H6v-2zm18 0h2v2h-2v-2zm-14 2h10v2H10v-2z" fill="#111"/>
      <path d="M12 6h8v2h4v4h2v8h-2v4h-2v2H10v-2H6v-4H4V10h2V8h4V6h2z" fill="#FFF"/>
      <rect x="8" y="12" width="4" height="4" fill="#FF3366" />
      <rect x="14" y="8" width="4" height="4" fill="#FFCC00" />
      <rect x="20" y="12" width="4" height="4" fill="#00CCFF" />
      <rect x="22" y="18" width="4" height="4" fill="#33FF66" />
      <rect x="12" y="18" width="6" height="4" fill="#111" />
    </svg>
  )
}
