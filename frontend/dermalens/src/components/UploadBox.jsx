import { useState } from "react";
import { uploadImage } from "../api/api";

function UploadBox() {
  const [image, setImage] = useState(null);
  const [enhanced, setEnhanced] = useState(null);
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [mode, setMode] = useState(null);
  const [insights, setInsights] = useState(null);
  const[confidence, setConfidence] = useState(null);

  const handleChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // reset old state (important)
    setMetrics(null);
    setMode(null);
    setInsights(null);

    setImage(URL.createObjectURL(file));

    try {
      setLoading(true);

      const response = await uploadImage(file);
      if(response.confidence){
        setConfidence(response.confidence);
      }

      // base64 → image
      const imageURL = `data:image/jpeg;base64,${response.image}`;
      setEnhanced(imageURL);

      // metrics
      if (response.metrics) {
        setMetrics(response.metrics);
      }

      if (response.interpretation) {
        setInsights(response.interpretation);
      
      
}

      // mode
      if (response.mode) {
        setMode(response.mode);
      }

    } catch (error) {
      console.error("Upload failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
  <div className="w-full max-w-6xl mx-auto px-6 py-10">

    <div className="bg-[#0f172a]/70 border border-cyan-500/10 backdrop-blur-2xl rounded-[32px] shadow-[0_0_80px_rgba(59,130,246,0.08)] p-10 space-y-10 relative overflow-hidden">
    <div className="absolute -top-32 -right-32 w-96 h-96 bg-blue-500/10 blur-3xl rounded-full" />

    <div className="absolute -bottom-40 -left-32 w-96 h-96 bg-cyan-400/10 blur-3xl rounded-full" /> 

      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-6xl md:text-7xl font-black tracking-tight bg-gradient-to-r from-blue-300 via-cyan-200 to-white bg-clip-text text-transparent text-white tracking-tight">
          DermaLens
        </h1>

        <p className="text-slate-400 max-w-2xl mx-auto leading-relaxed">
          AI-aware image preprocessing and confidence validation framework
          for analyzing low-quality image enhancement reliability.
        </p>
      </div>

      {/* Upload */}
      <div className="flex justify-center">

        <input
          type="file"
          accept="image/*"
          onChange={handleChange}
          className="hidden"
          id="upload"
        />

        <label
          htmlFor="upload"
          className="px-8 py-4 rounded-2xl bg-gradient-to-r from-blue-600 to-cyan-500 hover:scale-105 hover:shadow-[0_0_40px_rgba(59,130,246,0.4)] active:scale-95 transition-all duration-300 text-white font-semibold cursor-pointer"
        >
          {loading ? "Processing..." : "Upload Image"}
        </label>

      </div>

      {/* Images */}
      {image && enhanced && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

          <div className="space-y-3">
            <p className="text-sm text-slate-400 font-medium">
              Original Image
            </p>

            <div className="bg-[#020617]/90 border border-cyan-500/10 rounded-3xl overflow-hidden shadow-[0_0_40px_rgba(59,130,246,0.08)] hover:shadow-[0_0_60px_rgba(59,130,246,0.15)] transition-all duration-500">
              <img
                src={image}
                alt="original"
                className="w-full object-cover"
              />
            </div>
          </div>

          <div className="space-y-3">
            <p className="text-sm text-blue-400 font-medium">
              Enhanced Image
            </p>

            <div className="bg-[#020617]/90 border border-cyan-500/20 rounded-3xl overflow-hidden shadow-[0_0_50px_rgba(59,130,246,0.12)] hover:shadow-[0_0_80px_rgba(59,130,246,0.2)] transition-all duration-500">
              <img
                src={enhanced}
                alt="enhanced"
                className="w-full object-cover"
              />
            </div>
          </div>

        </div>
      )}

      {/* Metrics */}
      {metrics && metrics.sharpness_before && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">

          <div className="bg-[#020617]/90 backdrop-blur-xl border border-white/5 rounded-3xl p-6 text-center shadow-[0_0_30px_rgba(59,130,246,0.06)] hover:-translate-y-1 transition-all duration-300">
            <p className="text-slate-400 text-sm mb-2">Sharpness</p>

            <h2 className="text-white text-3xl md:text-4xl font-black tracking-tight">
              {metrics.sharpness_before.toFixed(2)}
              <span className="text-blue-400 mx-2">→</span>
              {metrics.sharpness_after.toFixed(2)}
            </h2>
          </div>

          <div className="bg-[#020617]/90 backdrop-blur-xl border border-white/5 rounded-3xl p-6 text-center shadow-[0_0_30px_rgba(59,130,246,0.06)] hover:-translate-y-1 transition-all duration-300">
            <p className="text-slate-400 text-sm mb-2">Contrast</p>

            <h2 className="text-white text-3xl md:text-4xl font-black tracking-tight">
              {metrics.contrast_before.toFixed(2)}
              <span className="text-blue-400 mx-2">→</span>
              {metrics.contrast_after.toFixed(2)}
            </h2>
          </div>

          <div className="bg-[#020617]/90 backdrop-blur-xl border border-cyan-500/10 rounded-3xl p-6 text-center shadow-[0_0_40px_rgba(59,130,246,0.1)] hover:-translate-y-1 transition-all duration-300">
            <p className="text-slate-400 text-sm mb-2">Quality Score</p>

            <h2 className="text-blue-400 text-3xl md:text-4xl font-black tracking-tight">
              {metrics.quality_before.toFixed(2)}
              <span className="mx-2">→</span>
              {metrics.quality_after.toFixed(2)}
            </h2>
          </div>

        </div>
      )}

      {/* Confidence Card */}
{confidence && (
  <div className="mt-6 bg-[#020617]/95 border border-cyan-500/10 rounded-3xl p-8 shadow-[0_0_50px_rgba(59,130,246,0.08)] backdrop-blur-xl text-center">

    <p className="text-sm text-gray-400 mb-2">
      AI Confidence Validation
    </p>

    <p
      className={`text-2xl font-bold ${
        confidence.delta >= 0
          ? "text-green-400"
          : "text-red-400"
      }`}
    >
      {(confidence.before * 100).toFixed(2)}%
      {" → "}
      {(confidence.after * 100).toFixed(2)}%
    </p>

    <p
      className={`mt-2 text-sm font-medium ${
        confidence.delta >= 0
          ? "text-green-400"
          : "text-red-400"
      }`}
    >
      Δ {(confidence.delta * 100).toFixed(4)}%
    </p>

    
    <p className="mt-3 text-xs text-gray-500">
    {confidence.delta >= 0
      ? "Enhanced image preserved diagnostic features for AI-assisted evaluation"
      : "Visual clarity improved, though residual artifacts may still influence AI confidence"}
  </p>

  </div>
)}



      {/* Mode */}
      {mode && (
        <div className="flex justify-center">
          <div className="px-4 py-2 rounded-full bg-green-500/10 border border-green-500/20 text-green-400 text-sm font-medium">
            Mode: {mode}
          </div>
        </div>
      )}

      {/* Insights */}
      {insights && (
        <div className="bg-[#020617]/90 border border-cyan-500/10 rounded-3xl p-8 backdrop-blur-xl shadow-[0_0_40px_rgba(59,130,246,0.05)]">

          <h3 className="text-white font-semibold mb-4">
            AI Insights
          </h3>

          <div className="space-y-3">
            {insights.map((item, index) => (
              <p
                key={index}
                className="text-slate-300 flex items-center gap-2"
              >
                <span className="text-blue-400">●</span>
                {item}
              </p>
            ))}
          </div>

        </div>
      )}

    </div>

  </div>
  );
}

export default UploadBox;
