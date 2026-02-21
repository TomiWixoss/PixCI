import { SVGProps } from "react"
import { motion } from "framer-motion"

export function AIEye(props: SVGProps<SVGSVGElement>) {
  return (
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      viewBox="0 0 32 32"
      fill="currentColor"
      {...props}
    >
      <path d="M4 14v4h2v2h2v2h2v2h12v-2h2v-2h2v-2h2v-4h-2v-2h-2V8h-2V6H12v2h-2v2H8v2H6v2H4zm2 4v-4h2v-2h2V8h12v2h2v2h2v4h-2v2h-2v2H12v-2H8v-2H6z"/>
      
      <motion.g
        animate={{ scaleX: [1, 0.1, 1] }}
        transition={{ duration: 4, repeat: Infinity, times: [0, 0.1, 0.2] }}
        transform-origin="16px 16px"
      >
        <rect x="12" y="12" width="8" height="8" />
      </motion.g>
    </svg>
  )
}
