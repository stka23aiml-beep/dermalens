import { motion } from "framer-motion";

export default function AIOrb() {

  return (

    <div className="relative flex items-center justify-center w-[500px] h-[500px]">

      {/* OUTER RING */}
      <motion.div
        className="absolute w-[420px] h-[420px] rounded-full border border-cyan-400/20"
        animate={{
          rotate: 360
        }}
        transition={{
          duration: 18,
          repeat: Infinity,
          ease: "linear"
        }}
      />

      {/* SECOND RING */}
      <motion.div
        className="absolute w-[320px] h-[320px] rounded-full border border-blue-500/30"
        animate={{
          rotate: -360
        }}
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: "linear"
        }}
      />

      {/* GLOW CORE */}
      <motion.div
        className="absolute w-[220px] h-[220px] rounded-full bg-cyan-400/10 blur-3xl"
        animate={{
          scale: [1, 1.1, 1]
        }}
        transition={{
          duration: 3,
          repeat: Infinity
        }}
      />

      {/* CENTER CORE */}
      <motion.div
        className="relative w-[160px] h-[160px] rounded-full border border-cyan-300/30 backdrop-blur-xl bg-white/5 flex items-center justify-center"
        animate={{
          boxShadow: [
            "0 0 20px rgba(34,211,238,0.2)",
            "0 0 60px rgba(34,211,238,0.5)",
            "0 0 20px rgba(34,211,238,0.2)"
          ]
        }}
        transition={{
          duration: 3,
          repeat: Infinity
        }}
      >

        <div className="text-cyan-300 text-lg font-semibold tracking-widest">

          AI CORE

        </div>

      </motion.div>

      {/* SCANNING LINE */}
      <motion.div
        className="absolute w-[300px] h-[2px] bg-cyan-400/60 blur-sm"
        animate={{
          y: [-150, 150, -150]
        }}
        transition={{
          duration: 3,
          repeat: Infinity
        }}
      />

    </div>
  );
}