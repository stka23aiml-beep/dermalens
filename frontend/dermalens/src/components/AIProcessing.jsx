import { motion } from "framer-motion";
import { useEffect, useState } from "react";

const steps = [
  "Analyzing lesion texture...",
  "Detecting blur artifacts...",
  "Enhancing illumination map...",
  "Restoring diagnostic structures...",
  "Validating AI confidence..."
];

export default function AIProcessing() {

  const [progress, setProgress] = useState(0);

  const [stepIndex, setStepIndex] = useState(0);

  // Progress animation
  useEffect(() => {

    const interval = setInterval(() => {

      setProgress((prev) => {

        if (prev >= 100) {

          clearInterval(interval);

          return 100;
        }

        return prev + 1;

      });

    }, 35);

    return () => clearInterval(interval);

  }, []);

  // Step switching
  useEffect(() => {

    const stepInterval = setInterval(() => {

      setStepIndex((prev) => {

        if (prev < steps.length - 1) {
          return prev + 1;
        }

        return prev;

      });

    }, 900);

    return () => clearInterval(stepInterval);

  }, []);

  return (

    <div className="relative w-full h-[420px] rounded-[32px] overflow-hidden bg-[#030712]/90 border border-cyan-500/10 flex flex-col items-center justify-center">

      {/* BACKGROUND GLOW */}
      <div className="absolute w-[300px] h-[300px] bg-cyan-500/10 blur-[120px] rounded-full" />

      {/* SCANNING LINE */}
      <motion.div
        className="absolute w-full h-[3px] bg-cyan-400/50 blur-sm"
        animate={{
          y: [-180, 180, -180]
        }}
        transition={{
          duration: 2.5,
          repeat: Infinity,
          ease: "linear"
        }}
      />

      {/* AI CORE */}
      <motion.div
        className="relative w-[140px] h-[140px] rounded-full border border-cyan-400/30 backdrop-blur-xl bg-white/5 flex items-center justify-center"
        animate={{
          boxShadow: [
            "0 0 20px rgba(34,211,238,0.2)",
            "0 0 70px rgba(34,211,238,0.5)",
            "0 0 20px rgba(34,211,238,0.2)"
          ]
        }}
        transition={{
          duration: 2.5,
          repeat: Infinity
        }}
      >

        <motion.div
          animate={{
            rotate: 360
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "linear"
          }}
          className="absolute w-[190px] h-[190px] rounded-full border border-cyan-400/20"
        />

        <div className="text-cyan-300 text-lg font-semibold tracking-[0.3em]">

          AI

        </div>

      </motion.div>

      {/* STATUS TEXT */}
      <motion.p
        key={stepIndex}
        initial={{
          opacity: 0,
          y: 10
        }}
        animate={{
          opacity: 1,
          y: 0
        }}
        transition={{
          duration: 0.4
        }}
        className="mt-10 text-cyan-100 text-lg tracking-wide"
      >

        {steps[stepIndex]}

      </motion.p>

      {/* PROGRESS */}
      <div className="w-[60%] h-[12px] bg-white/10 rounded-full mt-8 overflow-hidden">

        <motion.div
          className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-blue-500"
          animate={{
            width: `${progress}%`
          }}
        />

      </div>

      {/* PERCENT */}
      <div className="mt-5 text-cyan-300 text-2xl font-bold">

        {progress}%

      </div>

    </div>
  );
}