import { useState } from "react";

import HeroSection from "./HeroSection";
import BackgroundGlow from "./BackgroundGlow";
import AIProcessing from "./AIProcessing";
import ResultSection from "./ResultSection";
import UploadSection from "./UploadSection";
import Navbar from "./Navbar";


/*
 * Backend URL
 *
 * Local development:
 *   frontend -> 127.0.0.1:5173
 *   backend  -> 127.0.0.1:8000
 *
 * GitHub Codespaces:
 *   frontend -> <codespace>-5173.app.github.dev
 *   backend  -> <codespace>-8000.app.github.dev
 *
 * We automatically select the correct backend URL.
 */
function getBackendURL() {
  const hostname = window.location.hostname;

  // GitHub Codespaces frontend URL
  if (hostname.includes("-5173.app.github.dev")) {
    return `https://${hostname.replace(
      "-5173.app.github.dev",
      "-8000.app.github.dev"
    )}`;
  }

  // Normal local development
  return "http://127.0.0.1:8000";
}


export default function UploadBox() {

  const [loading, setLoading] = useState(false);

  const [image, setImage] = useState(null);

  const [enhanced, setEnhanced] = useState(null);

  const [metrics, setMetrics] = useState(null);

  const [confidence, setConfidence] = useState(null);

  const [mode, setMode] = useState("");

  const [insights, setInsights] = useState([]);

  // NEW: tracks whether the validation gate accepted or rejected the
  // enhancement. Was previously not read from the backend response at
  // all, so ResultSection had no way to know and always rendered as if
  // the enhancement had been accepted -- even when it had actually been
  // reverted to the original image.
  const [enhancementAccepted, setEnhancementAccepted] = useState(true);


  async function handleChange(e) {

    const file = e.target.files[0];

    if (!file) return;


    setLoading(true);

    setEnhanced(null);

    setMetrics(null);

    setConfidence(null);

    setMode("");

    setInsights([]);

    setEnhancementAccepted(true);


    const formData = new FormData();

    formData.append("file", file);


    setImage(URL.createObjectURL(file));


    try {

      const backendURL = getBackendURL();

      console.log("Backend URL:", backendURL);

      const res = await fetch(
        `${backendURL}/upload`,
        {
          method: "POST",
          body: formData
        }
      );


      if (!res.ok) {

        const errorText = await res.text();

        console.error(
          "Backend error:",
          res.status,
          errorText
        );

        throw new Error(
          `Backend returned ${res.status}`
        );
      }


      const data = await res.json();


      if (!data.image) {
        throw new Error(
          "Backend response does not contain an image."
        );
      }


      setEnhanced(
        `data:image/jpeg;base64,${data.image}`
      );


      setMetrics(data.metrics);

      setConfidence(data.confidence);

      setMode(data.mode);

      setInsights(
        data.interpretation || []
      );

      // NEW: capture the gate's decision. Defaults to true if the field
      // is somehow missing from an older backend response, so this never
      // crashes -- it just falls back to the old (pre-gate) display
      // behavior in that case.
      setEnhancementAccepted(
        data.enhancement_accepted !== undefined
          ? data.enhancement_accepted
          : true
      );


    } catch (err) {

      console.error(
        "Image processing failed:",
        err
      );

      alert(
        "Failed to process image. Check the browser console and backend."
      );


    } finally {

      setLoading(false);

    }
  }


  return (

    <div className="relative min-h-screen bg-[#020617] overflow-hidden">

      <BackgroundGlow />

      <Navbar />

      <HeroSection />


      {!loading && !enhanced ? (

        <UploadSection
          handleChange={handleChange}
        />

      ) : loading ? (

        <div className="relative z-10 px-6 pb-24 -mt-10">

          <div className="max-w-4xl mx-auto">

            <AIProcessing />

          </div>

        </div>

      ) : null}


      {/* RESULTS */}

      {!loading && enhanced && (

        <ResultSection
          image={image}
          enhanced={enhanced}
          metrics={metrics}
          confidence={confidence}
          mode={mode}
          insights={insights}
          enhancementAccepted={enhancementAccepted}
        />

      )}

    </div>

  );
}