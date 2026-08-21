import AIOrb from "./AIOrb";
import { motion } from "framer-motion";

export default function HeroSection() {

  return (

    <section className="relative min-h-screen flex items-center justify-between px-8 md:px-20 overflow-hidden">

      {/* LEFT SIDE */}
      <div className="max-w-2xl z-10">

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-cyan-400 uppercase tracking-[0.3em] text-sm mb-6"
        >
          AI Dermatology Enhancement System
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-6xl md:text-8xl font-black leading-[0.95] tracking-tight text-white"
        >

          Restore
          <br />

          <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-white bg-clip-text text-transparent">

            Diagnostic Clarity

          </span>

        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.8 }}
          className="mt-8 text-lg md:text-xl text-slate-400 leading-relaxed max-w-xl"
        >

          AI-aware enhancement and validation framework
          for improving low-quality dermatology image reliability.

        </motion.p>

      </div>

      {/* RIGHT SIDE */}
      <div className="hidden lg:flex items-center justify-center flex-1">

        <AIOrb />

      </div>

    </section>
  );
}