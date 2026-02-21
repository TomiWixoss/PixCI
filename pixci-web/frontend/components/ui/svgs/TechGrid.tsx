import { SVGProps } from "react"

export function TechGrid(props: SVGProps<SVGSVGElement>) {
  return (
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 100 100" 
      preserveAspectRatio="none"
      {...props}
    >
      <defs>
        <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
          <path d="M 10 0 L 0 0 0 10" fill="none" stroke="currentColor" strokeWidth="0.5" opacity="0.2" />
        </pattern>
        <pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse">
          <rect x="9.5" y="9.5" width="1" height="1" fill="currentColor" opacity="0.3" />
        </pattern>
      </defs>
      <rect width="100" height="100" fill="url(#grid)" />
      <rect width="100" height="100" fill="url(#dots)" />
      
      {/* Decorative tech lines */}
      <path d="M 0 50 L 30 50 L 35 45 L 80 45 L 85 50 L 100 50" fill="none" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
      <path d="M 50 0 L 50 20 L 55 25 L 55 70 L 45 80 L 45 100" fill="none" stroke="currentColor" strokeWidth="0.5" opacity="0.4" />
    </svg>
  )
}
