import { SVGProps } from "react"
import { motion } from "framer-motion"

export function PixelLogo(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none" {...props}>
      <motion.rect 
        x="8" y="8" width="48" height="48" rx="4"
        stroke="currentColor" strokeWidth="2"
        initial={{ opacity: 0.5 }}
        animate={{ opacity: 1 }}
      />
      <motion.rect
        x="16" y="16" width="8" height="8"
        fill="currentColor"
        animate={{ scale: [1, 0.8, 1] }}
        transition={{ duration: 2, repeat: Infinity }}
      />
      <motion.rect
        x="28" y="16" width="8" height="8"
        fill="currentColor"
        animate={{ scale: [1, 0.8, 1] }}
        transition={{ duration: 2, repeat: Infinity, delay: 0.2 }}
      />
      <motion.rect
        x="40" y="16" width="8" height="8"
        fill="currentColor"
        animate={{ scale: [1, 0.8, 1] }}
        transition={{ duration: 2, repeat: Infinity, delay: 0.4 }}
      />
      <motion.rect
        x="16" y="28" width="8" height="8"
        fill="currentColor"
        animate={{ scale: [1, 0.8, 1] }}
        transition={{ duration: 2, repeat: Infinity, delay: 0.6 }}
      />
      <motion.rect
        x="28" y="28" width="8" height="8"
        fill="currentColor"
        animate={{ scale: [1, 1.2, 1] }}
        transition={{ duration: 1.5, repeat: Infinity }}
      />
      <motion.rect
        x="40" y="28" width="8" height="8"
        fill="currentColor"
        animate={{ scale: [1, 0.8, 1] }}
        transition={{ duration: 2, repeat: Infinity, delay: 0.8 }}
      />
      <motion.rect
        x="16" y="40" width="8" height="8"
        fill="currentColor"
        animate={{ scale: [1, 0.8, 1] }}
        transition={{ duration: 2, repeat: Infinity, delay: 1 }}
      />
      <motion.rect
        x="28" y="40" width="8" height="8"
        fill="currentColor"
        animate={{ scale: [1, 0.8, 1] }}
        transition={{ duration: 2, repeat: Infinity, delay: 1.2 }}
      />
      <motion.rect
        x="40" y="40" width="8" height="8"
        fill="currentColor"
        animate={{ scale: [1, 0.8, 1] }}
        transition={{ duration: 2, repeat: Infinity, delay: 1.4 }}
      />
    </svg>
  )
}
