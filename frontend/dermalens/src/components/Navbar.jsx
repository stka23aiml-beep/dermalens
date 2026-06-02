function Navbar() {
  return (

    <nav className="w-full bg-[#020617]/60 backdrop-blur-2xl sticky top-0 z-50 border-b border-cyan-500/10">

      <div className="max-w-7xl mx-auto px-6 py-5 flex items-center justify-between">

        {/* Logo */}
        <div className="flex items-center gap-3">

          <div className="h-3 w-3 rounded-full bg-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.9)] animate-pulse" />

          <h1 className="text-xl font-semibold tracking-tight text-white">

            DermaLens

          </h1>

          <span className="text-xs px-2 py-1 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-mono">

            AI

          </span>

        </div>

        {/* Right Side */}
        <div className="flex items-center gap-8 text-sm text-slate-400 font-medium">

          {/* AI Status */}
          <div className="hidden md:flex items-center gap-2 text-cyan-300">

            <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />

            <span>

              AI Restoration Active

            </span>

          </div>

          {/* Links */}
          <span className="hover:text-white transition cursor-pointer">

            Research

          </span>

          <span className="hover:text-white transition cursor-pointer">

            GitHub

          </span>

          {/* CTA */}
          <button className="px-5 py-2 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-500 text-white hover:scale-105 transition-all duration-300 shadow-[0_0_30px_rgba(34,211,238,0.25)]">

            Launch Demo

          </button>

        </div>

      </div>

    </nav>
  );
}

export default Navbar;