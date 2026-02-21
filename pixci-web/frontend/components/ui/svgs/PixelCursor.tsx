import { SVGProps } from "react"
import { motion } from "framer-motion"

export function PixelCursor(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" {...props}>
      <motion.path
        d="M4 4L12 20L14 14L20 12L4 4Z"
        initial={{ pathLength: 0.8, opacity: 0.5 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
      />
    </svg>
  )
}
