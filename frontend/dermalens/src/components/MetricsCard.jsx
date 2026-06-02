import { motion } from "framer-motion";

export default function MetricsCard({

  title,
  before,
  after,
  accent = "cyan"

}) {

  const accentStyles = {

    cyan: "text-cyan-400",
    blue: "text-blue-400",
    green: "text-green-400",
    red: "text-red-400"

  };

  return (

    <motion.div

      initial={{
        opacity: 0,
        y: 20
      }}

      animate={{
        opacity: 1,
        y: 0
      }}

      transition={{
        duration: 0.5
      }}

      whileHover={{
        y: -5
      }}

      className="
        bg-[#020617]/90
        backdrop-blur-xl
        border border-white/5
        rounded-3xl
        p-6
        text-center
        shadow-[0_0_30px_rgba(59,130,246,0.06)]
        transition-all
        duration-300
      "
    >

      <p className="text-slate-400 text-sm mb-3">

        {title}

      </p>

      <h2 className={`text-3xl md:text-4xl font-black tracking-tight ${accentStyles[accent]}`}>

        {Number(before).toFixed(2)}

        <span className="mx-2 text-slate-500">

          →

        </span>

        {Number(after).toFixed(2)}

      </h2>

    </motion.div>
  );
}