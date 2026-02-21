import { SVGProps } from "react"
import { motion } from "framer-motion"

export function PixelPattern(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="currentColor" {...props}>
      {[...Array(25)].map((_, i) => (
        <motion.rect
          key={i}
          x={(i % 5) * 20 + 5}
          y={Math.floor(i / 5) * 20 + 5}
          width="4"
          height="4"
          initial={{ opacity: 0.1 }}
          animate={{ opacity: [0.1, 0.4, 0.1] }}
          transition={{ 
            duration: 2, 
            repeat: Infinity, 
            delay: i * 0.1 
          }}
        />
      ))}
    </svg>
  )
}
