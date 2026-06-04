import MetricsCard from "./MetricsCard";
import { motion } from "framer-motion";

export default function ResultSection({

  image,
  enhanced,
  metrics,
  confidence,
  mode,
  insights

}) {

  if (!image || !enhanced) return null;

  return (

    <section className="relative z-10 w-full max-w-7xl mx-auto px-6 pb-20">

      {/* BEFORE / AFTER */}
<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

  {/* ORIGINAL */}
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
  >

    <div className="bg-[#071225] border border-white/10 rounded-[32px] p-4">

      <div className="mb-4">
        <span className="px-3 py-1 rounded-full bg-white/5 text-slate-300 text-xs font-semibold tracking-wider">
          ORIGINAL
        </span>
      </div>

      <img
        src={image}
        alt="original"
        className="w-full h-[420px] object-cover rounded-2xl"
      />

    </div>

  </motion.div>

  {/* ENHANCED */}
  <motion.div
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.15, duration: 0.5 }}
  >

    <div className="bg-[#071225] border border-cyan-500/20 rounded-[32px] p-4 shadow-[0_0_40px_rgba(34,211,238,0.08)]">

      <div className="mb-4">
        <span className="px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-300 text-xs font-semibold tracking-wider">
          ENHANCED
        </span>
      </div>

      <img
        src={enhanced}
        alt="enhanced"
        className="w-full h-[420px] object-cover rounded-2xl"
      />

    </div>

  </motion.div>

</div>

      {/* MODE */}
      {mode && (

        <div className="flex justify-center mt-10">

          <div className="px-5 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-sm font-medium backdrop-blur-xl">

            {mode}

          </div>

        </div>

      )}

      {/* METRICS */}
      {metrics && (

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-12">

          <MetricsCard
            title="Sharpness"
            before={metrics.sharpness_before}
            after={metrics.sharpness_after}
            accent="blue"
          />

          <MetricsCard
            title="Contrast"
            before={metrics.contrast_before}
            after={metrics.contrast_after}
            accent="cyan"
          />

          <MetricsCard
            title="Quality Score"
            before={metrics.quality_before}
            after={metrics.quality_after}
            accent="green"
          />

        </div>

      )}

      {/* CONFIDENCE */}
      {confidence && (

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="mt-12 bg-[#020617]/90 border border-cyan-500/10 rounded-[32px] p-8 backdrop-blur-xl text-center shadow-[0_0_50px_rgba(34,211,238,0.08)]"
        >

          <p className="text-sm text-slate-400 mb-3">

            AI Confidence Validation

          </p>

          <p className={`text-4xl font-black ${
            confidence.delta >= 0
              ? "text-green-400"
              : "text-red-400"
          }`}>

            {(confidence.before * 100).toFixed(2)}%

            <span className="mx-3 text-slate-500">

              →

            </span>

            {(confidence.after * 100).toFixed(2)}%

          </p>

          <p className={`mt-3 text-sm font-medium ${
            confidence.delta >= 0
              ? "text-green-400"
              : "text-red-400"
          }`}>

            Δ {(confidence.delta * 100).toFixed(4)}%

          </p>

          <p className="mt-4 text-xs text-slate-500 max-w-xl mx-auto leading-relaxed">

            {confidence.delta >= 0
              ? "Enhanced image preserved diagnostically relevant structures for AI-assisted analysis."
              : "Residual degradation artifacts may still influence downstream AI confidence."}

          </p>

        </motion.div>

      )}

      {/* INSIGHTS */}
      {insights && (

        <div className="mt-12 bg-[#020617]/90 border border-cyan-500/10 rounded-[32px] p-8 backdrop-blur-xl shadow-[0_0_40px_rgba(34,211,238,0.05)]">

          <h3 className="text-white text-xl font-semibold mb-6">

            AI Insights

          </h3>

          <div className="space-y-4">

            {insights.map((item, index) => (

              <motion.div
                key={index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center gap-3 text-slate-300"
              >

                <div className="w-2 h-2 rounded-full bg-cyan-400" />

                <p>

                  {item}

                </p>

              </motion.div>

            ))}

          </div>

        </div>

      )}

    </section>
  );
}