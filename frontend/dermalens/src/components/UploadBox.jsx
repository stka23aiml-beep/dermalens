import { useState } from "react";

import HeroSection from "./HeroSection";
import BackgroundGlow from "./BackgroundGlow";
import AIProcessing from "./AIProcessing";
import ResultSection from "./ResultSection";
import UploadSection from "./UploadSection";
import Navbar from "./Navbar";

export default function UploadBox() {

  const [loading, setLoading] = useState(false);

  const [image, setImage] = useState(null);

  const [enhanced, setEnhanced] = useState(null);

  const [metrics, setMetrics] = useState(null);

  const [confidence, setConfidence] = useState(null);

  const [mode, setMode] = useState("");

  const [insights, setInsights] = useState([]);

  async function handleChange(e) {

    const file = e.target.files[0];

    if (!file) return;

    setLoading(true);

    setEnhanced(null);

    setMetrics(null);

    setConfidence(null);

    setMode("");

    setInsights([]);

    const formData = new FormData();

    formData.append("file", file);

    setImage(URL.createObjectURL(file));

    try {

      const res = await fetch(
        "http://127.0.0.1:8000/upload",
        {
          method: "POST",
          body: formData
        }
      );

      const data = await res.json();

      setEnhanced(
        `data:image/jpeg;base64,${data.image}`
      );

      setMetrics(data.metrics);

      setConfidence(data.confidence);

      setMode(data.mode);

      setInsights(data.interpretation);

    } catch (err) {

      console.error(err);
      alert("Failed to process image.");

    } finally {

      setLoading(false);

    }
  }

  return (

    <div className="relative min-h-screen bg-[#020617] overflow-hidden">

      <BackgroundGlow />
      <Navbar />

      <HeroSection />

      {!loading ? (

  <UploadSection
    handleChange={handleChange}
  />

) : (

  <div className="relative z-10 px-6 pb-24 -mt-10">

    <div className="max-w-4xl mx-auto">

      <AIProcessing />

    </div>

  </div>

)}

      {/* RESULTS */}
      {!loading && enhanced && (

        <ResultSection
          image={image}
          enhanced={enhanced}
          metrics={metrics}
          confidence={confidence}
          mode={mode}
          insights={insights}
        />

      )}

    </div>
  );
}