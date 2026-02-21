import { SVGProps } from "react"

export function PixelCloud(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 24" fill="currentColor" {...props}>
      <path d="M12 4h8v4h8v4h8v8H4v-4h4V8h4V4z" fill="#FFF" opacity="0.8"/>
      <path d="M12 4h8v2h-8V4zm8 4h8v2h-8V8zM4 12h4v2H4v-2zM32 12h8v2h-8v-2zM0 16h4v4H0v-4zm36 0h4v4h-4v-4z" fill="#111" opacity="0.1"/>
    </svg>
  )
}
