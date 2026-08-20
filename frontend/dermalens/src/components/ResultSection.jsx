import { useMemo, useState } from "react";
import { motion } from "framer-motion";

export default function ResultSection({
  image,
  enhanced,
  metrics,
  confidence,
  mode,
  insights,
  enhancementAccepted,
}) {
  const [zoomOriginal, setZoomOriginal] = useState(1);
  const [zoomResult, setZoomResult] = useState(1);
  const [compare, setCompare] = useState(50);

  if (!image || !enhanced) return null;

  const accepted =
    enhancementAccepted !== undefined ? enhancementAccepted : true;

  const sharpnessBefore = Number(metrics?.sharpness_before ?? 0);
  const sharpnessAfter = Number(metrics?.sharpness_after ?? 0);
  const contrastBefore = Number(metrics?.contrast_before ?? 0);
  const contrastAfter = Number(metrics?.contrast_after ?? 0);
  const qualityBefore = Number(metrics?.quality_before ?? 0);
  const qualityAfter = Number(metrics?.quality_after ?? 0);

  const percentChange = (before, after) => {
    if (!Number.isFinite(before) || before === 0) return null;
    return ((after - before) / Math.abs(before)) * 100;
  };

  const formatChange = (before, after) => {
    const change = percentChange(before, after);

    if (change === null) return "—";
    if (Math.abs(change) < 0.5) return "Stable";

    return change > 0
      ? `↑ ${change.toFixed(0)}%`
      : `↓ ${Math.abs(change).toFixed(0)}%`;
  };

  const blurFinding = useMemo(() => {
    if (sharpnessBefore < 10) return "Severe blur detected";
    if (sharpnessBefore < 40) return "Moderate blur detected";
    if (sharpnessBefore < 80) return "Mild blur detected";
    return "Image is relatively sharp";
  }, [sharpnessBefore]);

  const contrastFinding = useMemo(() => {
    if (contrastBefore < 15) return "Low contrast detected";
    if (contrastBefore < 30) return "Moderate contrast";
    return "Contrast is adequate";
  }, [contrastBefore]);

  const enhancementLabel = accepted
    ? mode || "Adaptive enhancement applied"
    : "Original preserved — no safe enhancement selected";

  const displayedConfidence =
    confidence?.final !== undefined
      ? confidence.final
      : confidence?.after;

  const confidenceDelta =
    confidence?.delta !== undefined
      ? confidence.delta * 100
      : null;

  const qualityChange = percentChange(qualityBefore, qualityAfter);

  const qualityStatus =
    qualityChange === null
      ? "Not available"
      : qualityChange > 2
        ? "Improved"
        : qualityChange < -2
          ? "Reduced"
          : "Stable";

  const zoomIn = (current, setter) => {
    setter(Math.min(current + 0.25, 2.5));
  };

  const zoomOut = (current, setter) => {
    setter(Math.max(current - 0.25, 1));
  };

  return (
    <section className="relative z-10 w-full max-w-7xl mx-auto px-6 pb-24">
      {/* HEADER */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-5">
          <div>
            <p className="text-cyan-300 text-xs font-semibold tracking-[0.3em] uppercase">
              DermaLens Analysis
            </p>

            <h2 className="text-white text-3xl md:text-4xl font-black mt-3">
              Image quality assessment
            </h2>

            <p className="text-slate-400 mt-3 max-w-2xl leading-relaxed">
              DermaLens evaluates image degradation, applies adaptive
              restoration when useful, and preserves the original when a safe
              improvement cannot be established.
            </p>
          </div>

          <div
            className={`self-start md:self-auto px-4 py-2 rounded-full border text-sm font-semibold ${
              accepted
                ? "bg-cyan-500/10 border-cyan-400/20 text-cyan-300"
                : "bg-amber-500/10 border-amber-400/20 text-amber-300"
            }`}
          >
            {accepted ? "Enhancement applied" : "Original preserved"}
          </div>
        </div>
      </motion.div>

      {/* QUALITY ANALYSIS */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="rounded-[28px] border border-white/10 bg-[#071225]/80 backdrop-blur-xl p-6 md:p-8 mb-8"
      >
        <div className="flex items-center justify-between gap-4 mb-6">
          <div>
            <p className="text-white text-xl font-bold">
              Image quality analysis
            </p>
            <p className="text-slate-500 text-sm mt-1">
              Detected degradation and selected restoration path
            </p>
          </div>

          <div className="hidden sm:block text-xs text-slate-500">
            Adaptive pipeline
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <FindingCard
            label="Blur"
            value={blurFinding}
            detail={`Sharpness ${sharpnessBefore.toFixed(2)}`}
            positive={sharpnessBefore >= 80}
          />

          <FindingCard
            label="Contrast"
            value={contrastFinding}
            detail={`Contrast ${contrastBefore.toFixed(2)}`}
            positive={contrastBefore >= 30}
          />

          <FindingCard
            label="Enhancement"
            value={enhancementLabel}
            detail={accepted ? "Candidate accepted" : "Safe fallback used"}
            positive={accepted}
            warning={!accepted}
          />
        </div>
      </motion.div>

      {/* ORIGINAL / RESULT */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ImagePanel
          title="Original"
          subtitle="Uploaded image"
          image={image}
          zoom={zoomOriginal}
          setZoom={setZoomOriginal}
          onZoomIn={() => zoomIn(zoomOriginal, setZoomOriginal)}
          onZoomOut={() => zoomOut(zoomOriginal, setZoomOriginal)}
          accent="neutral"
        />

        <ImagePanel
          title={accepted ? "DermaLens Result" : "Original Preserved"}
          subtitle={
            accepted
              ? "Selected adaptive enhancement"
              : "Enhancement was not selected"
          }
          image={enhanced}
          zoom={zoomResult}
          setZoom={setZoomResult}
          onZoomIn={() => zoomIn(zoomResult, setZoomResult)}
          onZoomOut={() => zoomOut(zoomResult, setZoomResult)}
          accent={accepted ? "cyan" : "amber"}
        />
      </div>

      {/* COMPARE */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="mt-8 rounded-[28px] border border-white/10 bg-[#071225]/80 backdrop-blur-xl p-5 md:p-7"
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-5">
          <div>
            <p className="text-white font-bold">Compare</p>
            <p className="text-slate-500 text-sm mt-1">
              Drag the divider to inspect changes at the same location.
            </p>
          </div>

          <div className="text-xs text-slate-500">
            Original ↔ Result
          </div>
        </div>

        <div className="relative w-full aspect-[4/3] md:aspect-[16/9] overflow-hidden rounded-2xl bg-black border border-white/10 select-none">
          <img
            src={enhanced}
            alt="DermaLens result comparison"
            className="absolute inset-0 w-full h-full object-contain"
          />

          <div
            className="absolute inset-y-0 left-0 overflow-hidden border-r-2 border-white/80"
            style={{ width: `${compare}%` }}
          >
            <img
              src={image}
              alt="Original comparison"
              className="absolute inset-0 w-full h-full object-contain max-w-none"
              style={{ width: "100%", height: "100%" }}
            />
          </div>

          <div
            className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-10 h-10 rounded-full bg-white text-slate-900 flex items-center justify-center shadow-xl pointer-events-none"
            style={{ left: `${compare}%` }}
          >
            ↔
          </div>

          <input
            aria-label="Before and after comparison"
            type="range"
            min="0"
            max="100"
            value={compare}
            onChange={(e) => setCompare(Number(e.target.value))}
            className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize"
          />

          <span className="absolute top-4 left-4 px-3 py-1 rounded-full bg-black/60 text-white text-xs font-semibold backdrop-blur-md">
            ORIGINAL
          </span>

          <span className="absolute top-4 right-4 px-3 py-1 rounded-full bg-black/60 text-white text-xs font-semibold backdrop-blur-md">
            {accepted ? "DERMALENS" : "ORIGINAL"}
          </span>
        </div>
      </motion.div>

      {/* QUALITY CHANGE */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mt-8 rounded-[28px] border border-white/10 bg-[#071225]/80 backdrop-blur-xl p-6 md:p-8"
      >
        <div className="mb-6">
          <p className="text-white text-xl font-bold">Quality change</p>
          <p className="text-slate-500 text-sm mt-1">
            Measured changes between the uploaded and selected result image.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <QualityChangeCard
            label="Sharpness"
            before={sharpnessBefore}
            after={sharpnessAfter}
            change={formatChange(sharpnessBefore, sharpnessAfter)}
          />

          <QualityChangeCard
            label="Contrast"
            before={contrastBefore}
            after={contrastAfter}
            change={formatChange(contrastBefore, contrastAfter)}
          />

          <QualityChangeCard
            label="Quality"
            before={qualityBefore}
            after={qualityAfter}
            change={qualityStatus}
          />

          <QualityChangeCard
            label="Structure"
            before="—"
            after="—"
            change="SSIM later"
            muted
          />
        </div>
      </motion.div>

      {/* ENHANCEMENT DETAILS */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
        className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        <div className="rounded-[28px] border border-white/10 bg-[#071225]/80 backdrop-blur-xl p-6 md:p-8">
          <p className="text-white text-xl font-bold">What DermaLens did</p>

          <div className="mt-5 space-y-3">
            {insights?.length ? (
              insights.map((item, index) => (
                <motion.div
                  key={`${item}-${index}`}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.06 }}
                  className="flex gap-3 items-start"
                >
                  <span className="mt-2 w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0" />
                  <p className="text-slate-300 text-sm leading-relaxed">
                    {item}
                  </p>
                </motion.div>
              ))
            ) : (
              <p className="text-slate-500 text-sm">
                No additional enhancement notes were returned.
              </p>
            )}
          </div>
        </div>

        <div className="rounded-[28px] border border-white/10 bg-[#071225]/80 backdrop-blur-xl p-6 md:p-8">
          <p className="text-white text-xl font-bold">Model signal</p>

          <p className="text-slate-500 text-sm mt-1">
            Technical information from the current downstream model.
          </p>

          {confidence && displayedConfidence !== undefined ? (
            <div className="mt-6">
              <p className="text-slate-400 text-sm">Final model confidence</p>

              <p className="text-3xl font-black text-white mt-1">
                {(displayedConfidence * 100).toFixed(2)}%
              </p>

              {confidenceDelta !== null && (
                <p
                  className={`text-sm mt-2 ${
                    confidenceDelta >= 0
                      ? "text-emerald-400"
                      : "text-amber-400"
                  }`}
                >
                  {confidenceDelta >= 0 ? "↑" : "↓"}{" "}
                  {Math.abs(confidenceDelta).toFixed(2)} percentage points
                </p>
              )}

              <p className="text-xs text-slate-500 leading-relaxed mt-4">
                This is a downstream model signal, not a diagnosis and not the
                primary criterion for image enhancement.
              </p>
            </div>
          ) : (
            <p className="text-slate-500 text-sm mt-6">
              Model signal unavailable.
            </p>
          )}
        </div>
      </motion.div>

      {/* DOWNSTREAM ANALYSIS */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="mt-8 rounded-[28px] border border-cyan-400/15 bg-gradient-to-br from-cyan-500/[0.07] to-blue-500/[0.04] backdrop-blur-xl p-6 md:p-8"
      >
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div>
            <p className="text-cyan-300 text-xs font-semibold tracking-[0.25em] uppercase">
              Next stage
            </p>

            <h3 className="text-white text-2xl font-black mt-2">
              Downstream abnormality analysis
            </h3>

            <p className="text-slate-400 mt-2 max-w-2xl leading-relaxed">
              The image is prepared for the next analysis layer. DermaLens can
              route the image toward lesion, wound, or future abnormality
              models without making a diagnosis here.
            </p>
          </div>

          <button
            type="button"
            disabled
            className="shrink-0 px-6 py-3 rounded-2xl bg-cyan-500/10 border border-cyan-400/20 text-cyan-200 font-semibold cursor-not-allowed opacity-80"
          >
            Analyze Skin Abnormality
          </button>
        </div>

        <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-3">
          <RouteChip title="Lesion" status="ISIC model" />
          <RouteChip title="Wound / Cut" status="Future model" />
          <RouteChip title="Other" status="Future model" />
        </div>
      </motion.div>
    </section>
  );
}

function FindingCard({
  label,
  value,
  detail,
  positive = false,
  warning = false,
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">
      <div className="flex items-center justify-between gap-3">
        <p className="text-slate-400 text-sm">{label}</p>

        <span
          className={`w-2 h-2 rounded-full ${
            warning
              ? "bg-amber-400"
              : positive
                ? "bg-emerald-400"
                : "bg-cyan-400"
          }`}
        />
      </div>

      <p className="text-white font-semibold mt-3 leading-snug">{value}</p>
      <p className="text-slate-500 text-xs mt-2">{detail}</p>
    </div>
  );
}

function ImagePanel({
  title,
  subtitle,
  image,
  zoom,
  onZoomIn,
  onZoomOut,
  accent,
}) {
  const border =
    accent === "cyan"
      ? "border-cyan-400/25"
      : accent === "amber"
        ? "border-amber-400/25"
        : "border-white/10";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-[28px] border ${border} bg-[#071225]/80 backdrop-blur-xl p-4`}
    >
      <div className="flex items-center justify-between gap-3 px-1 pb-4">
        <div>
          <p className="text-white font-bold">{title}</p>
          <p className="text-slate-500 text-xs mt-1">{subtitle}</p>
        </div>

        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={onZoomOut}
            className="w-8 h-8 rounded-lg border border-white/10 bg-white/[0.03] text-slate-300 hover:bg-white/[0.07]"
            aria-label={`Zoom out ${title}`}
          >
            −
          </button>

          <span className="text-xs text-slate-500 min-w-10 text-center">
            {Math.round(zoom * 100)}%
          </span>

          <button
            type="button"
            onClick={onZoomIn}
            className="w-8 h-8 rounded-lg border border-white/10 bg-white/[0.03] text-slate-300 hover:bg-white/[0.07]"
            aria-label={`Zoom in ${title}`}
          >
            +
          </button>
        </div>
      </div>

      <div className="relative h-[360px] rounded-2xl overflow-auto bg-black border border-white/5">
        <div className="w-full h-full flex items-center justify-center overflow-hidden">
          <img
            src={image}
            alt={title}
            className="max-w-none object-contain transition-transform duration-200"
            style={{
              width: `${zoom * 100}%`,
              height: `${zoom * 100}%`,
            }}
          />
        </div>
      </div>
    </motion.div>
  );
}

function QualityChangeCard({
  label,
  before,
  after,
  change,
  muted = false,
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.025] p-5">
      <p className="text-slate-400 text-sm">{label}</p>

      <div className="flex items-end gap-2 mt-3">
        <span className="text-white text-xl font-bold">
          {typeof before === "number" ? before.toFixed(2) : before}
        </span>

        <span className="text-slate-600 pb-1">→</span>

        <span className="text-white text-xl font-bold">
          {typeof after === "number" ? after.toFixed(2) : after}
        </span>
      </div>

      <p
        className={`text-xs font-semibold mt-2 ${
          muted
            ? "text-slate-500"
            : change?.startsWith("↑") || change === "Improved"
              ? "text-emerald-400"
              : change?.startsWith("↓") || change === "Reduced"
                ? "text-amber-400"
                : "text-slate-400"
        }`}
      >
        {change}
      </p>
    </div>
  );
}

function RouteChip({ title, status }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/10 px-4 py-3">
      <p className="text-white text-sm font-semibold">{title}</p>
      <p className="text-slate-500 text-xs mt-1">{status}</p>
    </div>
  );
}