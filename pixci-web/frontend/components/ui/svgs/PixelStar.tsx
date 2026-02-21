import { SVGProps } from "react"

export function PixelStar(props: SVGProps<SVGSVGElement>) {
  return (
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 16 16" 
      width="1em" 
      height="1em" 
      fill="currentColor" 
      {...props}
    >
      <rect x="7" y="0" width="2" height="2" />
      <rect x="7" y="2" width="2" height="2" />
      <rect x="7" y="12" width="2" height="2" />
      <rect x="7" y="14" width="2" height="2" />
      
      <rect x="0" y="7" width="2" height="2" />
      <rect x="2" y="7" width="2" height="2" />
      <rect x="12" y="7" width="2" height="2" />
      <rect x="14" y="7" width="2" height="2" />
      
      <rect x="5" y="7" width="6" height="2" />
      <rect x="7" y="5" width="2" height="6" />
      
      <rect x="3" y="3" width="2" height="2" />
      <rect x="11" y="3" width="2" height="2" />
      <rect x="3" y="11" width="2" height="2" />
      <rect x="11" y="11" width="2" height="2" />
    </svg>
  )
}
