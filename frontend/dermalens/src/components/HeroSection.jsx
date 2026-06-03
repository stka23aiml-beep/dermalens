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

        {/* BUTTONS */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="mt-10 flex gap-5"
        >

          <button className="px-8 py-4 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold shadow-[0_0_40px_rgba(34,211,238,0.25)] hover:scale-105 transition-all duration-300">

            Upload Image

          </button>

          <button className="px-8 py-4 rounded-2xl border border-cyan-400/20 bg-white/5 backdrop-blur-xl text-cyan-100 hover:bg-cyan-400/10 transition-all duration-300">

            Live Demo

          </button>

        </motion.div>

               {/* FLOATING STATS */}
        <div className="flex gap-6 mt-14">

          <div className="bg-white/5 border border-white/10 backdrop-blur-xl rounded-2xl px-6 py-4">

            <p className="text-cyan-300 text-3xl font-black">
              AI
            </p>

            <p className="text-slate-400 text-sm mt-1">
              Validation Active
            </p>

          </div>

        </div>

      </div>

      {/* RIGHT SIDE */}
      <div className="hidden lg:flex items-center justify-center flex-1">

        <AIOrb />

      </div>

    </section>
  );
}