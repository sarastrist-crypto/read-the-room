import { useState, useRef, useEffect } from "react";
import "@/App.css";
import axios from "axios";
import { Zap, Target, RefreshCw, AlertTriangle, Mic2 } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EVENT_TYPES = [
  "Keynote",
  "Workshop",
  "Panel Discussion",
  "Team Meeting",
  "Client Pitch",
  "Board Presentation",
  "Training Session",
  "Webinar",
  "Conference Breakout",
  "Town Hall",
  "Sales Kickoff",
  "Product Demo",
  "Investor Meeting",
  "Networking Event",
  "Fireside Chat"
];

function App() {
  const [eventType, setEventType] = useState("");
  const [roomSize, setRoomSize] = useState("");
  const [audienceContext, setAudienceContext] = useState("");
  const [strategy, setStrategy] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const resultRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setStrategy(null);
    setLoading(true);

    try {
      const response = await axios.post(`${API}/generate-strategy`, {
        event_type: eventType,
        room_size: roomSize,
        audience_context: audienceContext
      });
      setStrategy(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to generate strategy. Try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (strategy && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [strategy]);

  const isFormValid = eventType && roomSize && audienceContext.trim();

  return (
    <div className="min-h-screen bg-[#F4F4F0]">
      <div className="max-w-2xl mx-auto px-4 py-8 sm:py-12">
        {/* Header */}
        <header className="mb-12">
          <p className="text-xs font-bold uppercase tracking-[0.15em] text-[#4A4A4A] mb-2" data-testid="app-tagline">
            Pre-Talk Prep Tool
          </p>
          <h1 
            className="font-heading text-4xl sm:text-5xl lg:text-6xl font-black uppercase tracking-tighter leading-none text-[#0D0D0D]"
            data-testid="app-title"
          >
            Room Reader
          </h1>
          <p className="font-body text-base text-[#4A4A4A] mt-4 leading-relaxed">
            Enter your event details. Get a specific engagement strategy in under 60 seconds.
          </p>
        </header>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-8" data-testid="strategy-form">
          {/* Event Type */}
          <div>
            <label 
              htmlFor="event-type" 
              className="block text-xs font-bold uppercase tracking-[0.15em] text-[#4A4A4A] mb-3"
            >
              Event Type
            </label>
            <select
              id="event-type"
              value={eventType}
              onChange={(e) => setEventType(e.target.value)}
              className="brutalist-select"
              data-testid="event-type-select"
              required
            >
              <option value="" disabled>Select your event format</option>
              {EVENT_TYPES.map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          {/* Room Size */}
          <div>
            <label 
              htmlFor="room-size" 
              className="block text-xs font-bold uppercase tracking-[0.15em] text-[#4A4A4A] mb-3"
            >
              Room Size
            </label>
            <input
              id="room-size"
              type="text"
              value={roomSize}
              onChange={(e) => setRoomSize(e.target.value)}
              className="brutalist-input"
              placeholder="e.g., 30 people, 500-person theater"
              data-testid="room-size-input"
              required
            />
          </div>

          {/* Audience Context */}
          <div>
            <label 
              htmlFor="audience-context" 
              className="block text-xs font-bold uppercase tracking-[0.15em] text-[#4A4A4A] mb-3"
            >
              Audience Context
            </label>
            <textarea
              id="audience-context"
              value={audienceContext}
              onChange={(e) => setAudienceContext(e.target.value)}
              className="brutalist-input resize-none"
              rows={3}
              placeholder="e.g., Mid-level managers in financial services, skeptical about new tech"
              data-testid="audience-context-input"
              required
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!isFormValid || loading}
            className="brutalist-button w-full"
            data-testid="generate-strategy-btn"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-4">
                Reading the Room
                <span className="loading-bar">
                  <span></span>
                  <span></span>
                  <span></span>
                  <span></span>
                  <span></span>
                </span>
              </span>
            ) : (
              "Read the Room"
            )}
          </button>
        </form>

        {/* Error */}
        {error && (
          <div 
            className="mt-8 p-4 bg-[#E63946] text-white border-2 border-[#0D0D0D] font-bold"
            data-testid="error-message"
          >
            {error}
          </div>
        )}

        {/* Strategy Output */}
        {strategy && (
          <div 
            ref={resultRef}
            className="output-card mt-12 animate-fadeIn"
            data-testid="strategy-output-card"
          >
            <h2 className="font-heading text-2xl sm:text-3xl font-bold tracking-tight text-white mb-8 uppercase">
              Your Strategy
            </h2>

            {/* Room Energy */}
            <div className="mb-8" data-testid="room-energy-section">
              <div className="flex items-center gap-3 mb-3">
                <Zap className="w-5 h-5 text-[#FFD166]" />
                <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-[#FFD166]">
                  Room Energy Read
                </h3>
              </div>
              <p className="font-body text-base leading-relaxed text-[#F4F4F0]">
                {strategy.room_energy}
              </p>
            </div>

            {/* Opening Move */}
            <div className="mb-8" data-testid="opening-move-section">
              <div className="flex items-center gap-3 mb-3">
                <Mic2 className="w-5 h-5 text-[#F4F4F0]" />
                <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-[#F4F4F0]">
                  Opening Move
                </h3>
              </div>
              <p className="font-heading text-xl sm:text-2xl font-semibold text-white leading-snug">
                {strategy.opening_move}
              </p>
            </div>

            {/* Engagement Anchor */}
            <div className="mb-8 border-2 border-[#F4F4F0] p-4" data-testid="engagement-anchor-section">
              <div className="flex items-center gap-3 mb-3">
                <Target className="w-5 h-5 text-[#F4F4F0]" />
                <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-[#F4F4F0]">
                  Engagement Anchor
                </h3>
              </div>
              <p className="font-body text-base leading-relaxed text-[#F4F4F0]">
                {strategy.engagement_anchor}
              </p>
            </div>

            {/* Recovery Move */}
            <div className="mb-8" data-testid="recovery-move-section">
              <div className="flex items-center gap-3 mb-3">
                <RefreshCw className="w-5 h-5 text-[#F4F4F0]" />
                <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-[#F4F4F0]">
                  Recovery Move
                </h3>
              </div>
              <p className="font-body text-base leading-relaxed text-[#F4F4F0]">
                {strategy.recovery_move}
              </p>
            </div>

            {/* Thing to Avoid */}
            <div data-testid="avoid-section">
              <div className="flex items-center gap-3 mb-3">
                <AlertTriangle className="w-5 h-5 text-[#E63946]" />
                <h3 className="text-xs font-bold uppercase tracking-[0.15em] text-[#E63946]">
                  Avoid This
                </h3>
              </div>
              <p className="font-body text-base leading-relaxed text-[#E63946] font-bold">
                {strategy.thing_to_avoid}
              </p>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="mt-16 pt-8 border-t-2 border-[#0D0D0D]">
          <p className="text-xs text-[#4A4A4A] text-center uppercase tracking-widest">
            In, out, ready.
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
