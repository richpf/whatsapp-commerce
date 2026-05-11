"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://whatsapp-commerce-api.fly.dev";

const Q1_OPTIONS = ["Less than 20", "20–50", "50–200", "200–500", "500+"];
const Q2_OPTIONS = [
  "Shopify / WooCommerce",
  "Google Sheets / Excel",
  "Pen and paper",
  "CRM",
  "WhatsApp Business app only",
  "Other",
];
const Q3_OPTIONS = [
  "₹0 (free app only)",
  "₹500–₹2,000",
  "₹2,000–₹5,000",
  "₹5,000–₹10,000",
  "₹10,000+",
];
const Q4_OPTIONS = [
  "Not worried",
  "Slightly worried",
  "Moderately worried",
  "Very worried",
  "It happened to me already",
];
const Q5_OPTIONS = ["<₹999", "₹999–₹1,999", "₹1,999–₹3,999", "₹3,999–₹7,999", "₹7,999+"];

function RadioGroup({
  options,
  value,
  onChange,
  showOther = false,
  otherValue = "",
  onOtherChange,
}: {
  options: string[];
  value: string;
  onChange: (v: string) => void;
  showOther?: boolean;
  otherValue?: string;
  onOtherChange?: (v: string) => void;
}) {
  return (
    <div className="space-y-2">
      {options.map((opt) => (
        <label
          key={opt}
          className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition ${
            value === opt
              ? "border-emerald-500 bg-emerald-50"
              : "border-gray-200 hover:border-emerald-300 hover:bg-gray-50"
          }`}
        >
          <input
            type="radio"
            name={opt}
            checked={value === opt}
            onChange={() => onChange(opt)}
            className="accent-emerald-500 w-4 h-4 shrink-0"
          />
          <span className="text-sm text-gray-800">{opt}</span>
        </label>
      ))}
      {showOther && value === "Other" && (
        <input
          type="text"
          placeholder="Please specify…"
          value={otherValue}
          onChange={(e) => onOtherChange?.(e.target.value)}
          className="w-full mt-1 px-4 py-2.5 rounded-xl border border-gray-300 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm transition"
        />
      )}
    </div>
  );
}

function SurveyForm({ source }: { source: string | null }) {
  const [q1, setQ1] = useState("");
  const [q2, setQ2] = useState("");
  const [q2Other, setQ2Other] = useState("");
  const [q3, setQ3] = useState("");
  const [q4, setQ4] = useState("");
  const [q5, setQ5] = useState("");
  const [q6, setQ6] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const [totalResponses, setTotalResponses] = useState<number | null>(null);

  const progress = [q1, q2, q3, q4, q5, q6.trim()].filter(Boolean).length;
  const progressPct = Math.round((progress / 6) * 100);

  const handleSubmit = async () => {
    setError("");
    if (!q1 || !q2 || !q3 || !q4 || !q5) {
      setError("Please answer all multiple-choice questions before submitting.");
      return;
    }
    setSubmitting(true);
    try {
      const orderTracking = q2 === "Other" ? (q2Other.trim() || "Other") : q2;
      const url = source
        ? `${API_URL}/api/survey/submit?source=${encodeURIComponent(source)}`
        : `${API_URL}/api/survey/submit`;
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          order_volume: q1,
          order_tracking: orderTracking,
          monthly_spend: q3,
          ban_worry: q4,
          willingness_to_pay: q5,
          missing_feature: q6.trim() || null,
        }),
      });
      if (!res.ok) throw new Error("Submission failed");
      const data = await res.json();
      setTotalResponses(data.total_responses);
      setDone(true);
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (done) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-teal-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
          <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Thank you! 🙏</h2>
          <p className="text-gray-600 mb-4">
            Your response helps us build exactly what WhatsApp sellers need. Results will be shared publicly.
          </p>
          {totalResponses !== null && (
            <p className="text-sm text-emerald-600 font-medium mb-6">
              You&apos;re response #{totalResponses} — join {totalResponses - 1} other sellers who shared their story.
            </p>
          )}
          <a
            href="/"
            className="inline-block bg-emerald-500 hover:bg-emerald-600 text-white font-semibold px-6 py-3 rounded-xl transition"
          >
            ← Back to ChatCommerce
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-teal-50">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
        <div className="max-w-2xl mx-auto px-4 h-14 flex items-center justify-between">
          <a href="/" className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center text-white font-bold text-xs">
              C
            </div>
            <span className="font-bold text-gray-900">ChatCommerce</span>
          </a>
          <span className="text-xs text-gray-500">~3 min survey</span>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto px-4 pt-24 pb-16">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 bg-amber-50 text-amber-700 text-xs font-medium px-3 py-1.5 rounded-full mb-4">
            <span className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
            Results shared publicly
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 mb-3">
            WhatsApp Commerce —{" "}
            <span className="bg-gradient-to-r from-emerald-500 to-teal-500 bg-clip-text text-transparent">
              Quick Survey
            </span>{" "}
            (3 min)
          </h1>
          <p className="text-gray-600 text-base leading-relaxed">
            Help shape the next generation of WhatsApp commerce tools. Results shared publicly.
          </p>
        </div>

        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex justify-between text-xs text-gray-500 mb-1.5">
            <span>{progress} of 6 answered</span>
            <span>{progressPct}%</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full transition-all duration-500"
              style={{ width: `${progressPct}%` }}
            />
          </div>
        </div>

        <div className="space-y-6">
          {/* Q1 */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <p className="font-semibold text-gray-900 mb-1">
              <span className="text-emerald-500 mr-1">Q1.</span>
              What&apos;s your monthly order volume via WhatsApp or social channels?
            </p>
            <p className="text-xs text-gray-400 mb-4">Select one</p>
            <RadioGroup options={Q1_OPTIONS} value={q1} onChange={setQ1} />
          </div>

          {/* Q2 */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <p className="font-semibold text-gray-900 mb-1">
              <span className="text-emerald-500 mr-1">Q2.</span>
              How do you currently track orders and customer data?
            </p>
            <p className="text-xs text-gray-400 mb-4">Select one</p>
            <RadioGroup
              options={Q2_OPTIONS}
              value={q2}
              onChange={setQ2}
              showOther
              otherValue={q2Other}
              onOtherChange={setQ2Other}
            />
          </div>

          {/* Q3 */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <p className="font-semibold text-gray-900 mb-1">
              <span className="text-emerald-500 mr-1">Q3.</span>
              Approximate monthly spend on WhatsApp tools (including Meta fees)?
            </p>
            <p className="text-xs text-gray-400 mb-4">Select one</p>
            <RadioGroup options={Q3_OPTIONS} value={q3} onChange={setQ3} />
          </div>

          {/* Q4 */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <p className="font-semibold text-gray-900 mb-1">
              <span className="text-emerald-500 mr-1">Q4.</span>
              How worried are you about your WhatsApp number getting banned?
            </p>
            <p className="text-xs text-gray-400 mb-4">Select one</p>
            <RadioGroup options={Q4_OPTIONS} value={q4} onChange={setQ4} />
          </div>

          {/* Q5 */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <p className="font-semibold text-gray-900 mb-1">
              <span className="text-emerald-500 mr-1">Q5.</span>
              If a tool could prevent bans, sync orders from Sheets/Shopify, zero markup on Meta fees, AI order management — what would you pay/month?
            </p>
            <p className="text-xs text-gray-400 mb-4">Select one</p>
            <RadioGroup options={Q5_OPTIONS} value={q5} onChange={setQ5} />
          </div>

          {/* Q6 */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <p className="font-semibold text-gray-900 mb-1">
              <span className="text-emerald-500 mr-1">Q6.</span>
              What&apos;s the ONE thing your current WhatsApp commerce setup is missing?
            </p>
            <p className="text-xs text-gray-400 mb-4">Optional — free text</p>
            <textarea
              rows={3}
              value={q6}
              onChange={(e) => setQ6(e.target.value)}
              placeholder="e.g. Automated order confirmation, inventory sync, payment tracking…"
              className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none text-sm transition resize-none"
            />
          </div>

          {error && (
            <p className="text-red-500 text-sm text-center bg-red-50 border border-red-100 rounded-xl px-4 py-3">
              {error}
            </p>
          )}

          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="w-full bg-emerald-500 hover:bg-emerald-600 disabled:bg-emerald-300 text-white font-semibold py-4 rounded-xl transition text-base shadow-sm"
          >
            {submitting ? "Submitting…" : "Submit Survey →"}
          </button>

          <p className="text-center text-xs text-gray-400">
            Anonymous · No account required · Results shared publicly
          </p>
        </div>
      </div>
    </div>
  );
}

function SurveyPageInner() {
  const searchParams = useSearchParams();
  const source = searchParams.get("source");
  return <SurveyForm source={source} />;
}

export default function SurveyPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-teal-50 flex items-center justify-center">
        <div className="text-gray-500">Loading…</div>
      </div>
    }>
      <SurveyPageInner />
    </Suspense>
  );
}
