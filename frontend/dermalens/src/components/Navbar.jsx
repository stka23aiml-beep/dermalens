import { motion } from "framer-motion";

export default function UploadSection({

  handleChange

}) {

  return (

    <motion.section
      id="upload-section"

      initial={{
        opacity: 0,
        y: 20
      }}

      animate={{
        opacity: 1,
        y: 0
      }}

      transition={{
        duration: 0.6
      }}

      className="relative z-10 flex justify-center px-6 -mt-10 pb-24"
    >

      <div className="
        w-full
        max-w-4xl
        rounded-[36px]
        border
        border-cyan-500/10
        bg-[#020617]/70
        backdrop-blur-2xl
        p-12
        shadow-[0_0_80px_rgba(34,211,238,0.06)]
      ">

        {/* HEADER */}
        <div className="text-center mb-10">

          <p className="text-cyan-300 text-sm tracking-[0.3em] uppercase">

            AI Upload Gateway

          </p>

          <h2 className="text-white text-4xl font-black mt-4">

            Upload Dermatology Image

          </h2>

          <p className="text-slate-400 mt-4 max-w-xl mx-auto leading-relaxed">

            Analyze degraded dermatology images using
            adaptive AI restoration and confidence validation.

          </p>

        </div>

        {/* DROPZONE -- the entire label is clickable, so no separate
            "Select Image" button is needed inside it (that was purely
            decorative and implied a second action that didn't exist). */}
        <label
          htmlFor="upload"
          className="
            relative
            block
            rounded-[32px]
            border-2
            border-dashed
            border-cyan-500/20
            bg-white/[0.03]
            hover:bg-cyan-500/[0.03]
            hover:border-cyan-400/40
            transition-all
            duration-300
            cursor-pointer
            overflow-hidden
          "
        >

          {/* Glow */}
          <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/0 via-cyan-400/5 to-blue-500/0" />

          <div className="relative flex flex-col items-center justify-center py-24 px-8 text-center">

            {/* Orb */}
            <div className="w-24 h-24 rounded-full bg-cyan-400/10 border border-cyan-400/20 flex items-center justify-center backdrop-blur-xl shadow-[0_0_40px_rgba(34,211,238,0.15)]">

              <div className="text-cyan-300 text-4xl">

                ⬆

              </div>

            </div>

            <h3 className="text-white text-2xl font-bold mt-8">

              Drag & Drop Image

            </h3>

            <p className="text-slate-400 mt-4 max-w-md leading-relaxed">

              Supports low-light, blurry, noisy,
              and compressed dermatology images.

            </p>

          </div>

        </label>

        {/* INPUT */}
        <input
          id="upload"
          type="file"
          accept="image/*"
          onChange={handleChange}
          className="hidden"
        />

      </div>

    </motion.section>
  );
}