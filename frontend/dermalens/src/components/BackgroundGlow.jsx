import { motion } from "framer-motion";

export default function BackgroundGlow() {

  return (

    <div className="absolute inset-0 overflow-hidden -z-10">

      {/* TOP LEFT ORB */}
      <motion.div
        className="absolute top-[-120px] left-[-120px] w-[500px] h-[500px] bg-cyan-500/15 rounded-full blur-[140px]"
        animate={{
          x: [0, 40, 0],
          y: [0, 30, 0],
          scale: [1, 1.1, 1]
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* BOTTOM RIGHT ORB */}
      <motion.div
        className="absolute bottom-[-150px] right-[-100px] w-[500px] h-[500px] bg-blue-500/15 rounded-full blur-[140px]"
        animate={{
          x: [0, -30, 0],
          y: [0, -40, 0],
          scale: [1, 1.15, 1]
        }}
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* CENTER GLOW */}
      <motion.div
        className="absolute top-[30%] left-[35%] w-[400px] h-[400px] bg-cyan-400/10 rounded-full blur-[120px]"
        animate={{
          opacity: [0.3, 0.6, 0.3],
          scale: [1, 1.2, 1]
        }}
        transition={{
          duration: 8,
          repeat: Infinity
        }}
      />

      {/* GRID OVERLAY */}
      <div
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.15) 1px, transparent 1px)",
          backgroundSize: "60px 60px"
        }}
      />

    </div>
  );
}