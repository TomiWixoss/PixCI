import { SVGProps, useId } from "react"

export function PixelCornerNodes(props: SVGProps<SVGSVGElement>) {
  return (
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 100 100"
      preserveAspectRatio="xMidYMid slice"
      {...props}
    >
      {/* Top Left */}
      <g fill="currentColor">
        <rect x="0" y="0" width="10" height="2" />
        <rect x="0" y="2" width="2" height="8" />
        <rect x="4" y="4" width="2" height="2" />
      </g>
      
      {/* Top Right */}
      <g fill="currentColor">
        <rect x="90" y="0" width="10" height="2" />
        <rect x="98" y="2" width="2" height="8" />
        <rect x="94" y="4" width="2" height="2" />
      </g>
      
      {/* Bottom Left */}
      <g fill="currentColor">
        <rect x="0" y="98" width="10" height="2" />
        <rect x="0" y="90" width="2" height="8" />
        <rect x="4" y="94" width="2" height="2" />
      </g>
      
      {/* Bottom Right */}
      <g fill="currentColor">
        <rect x="90" y="98" width="10" height="2" />
        <rect x="98" y="90" width="2" height="8" />
        <rect x="94" y="94" width="2" height="2" />
      </g>
      
      {/* Edge decors */}
      <rect x="48" y="0" width="4" height="2" fill="currentColor" opacity="0.6"/>
      <rect x="48" y="98" width="4" height="2" fill="currentColor" opacity="0.6"/>
      <rect x="0" y="48" width="2" height="4" fill="currentColor" opacity="0.6"/>
      <rect x="98" y="48" width="2" height="4" fill="currentColor" opacity="0.6"/>
    </svg>
  )
}
