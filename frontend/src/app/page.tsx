"use client";

import { useState } from "react";

const CHECK = (
  <svg className="w-5 h-5 text-emerald-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
);

const plans = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    messages: "50 msgs/mo",
    features: ["Basic AI auto-replies", "Compliance dashboard", "1 WhatsApp number", "Community support"],
    highlighted: false,
  },
  {
    name: "Starter",
    price: "$19",
    period: "/mo",
    messages: "500 msgs/mo",
    features: ["Compliance Shield", "AI commerce agent", "Order lookup", "Consumption dashboard", "Email support"],
    highlighted: false,
  },
  {
    name: "Pro",
    price: "$39",
    period: "/mo",
    messages: "2,000 msgs/mo",
    features: [
      "Abandoned cart recovery",
      "Shopify / WooCommerce / Sheets sync",
      "In-chat payment links",
      "Festival campaign templates",
      "Priority support",
    ],
    highlighted: true,
  },
  {
    name: "Scale",
    price: "$79",
    period: "/mo",
    messages: "10,000 msgs/mo",
    features: ["Team inbox (3 agents)", "Broadcast campaigns", "Full analytics", "All Pro features", "Dedicated support"],
    highlighted: false,
  },
];

const features = [
  {
    icon: "🛡️",
    title: "Compliance Shield",
    desc: "Rate limiting, spam scoring, template management, ban-risk alerts. Designed to help you stay within WhatsApp's guidelines.",
  },
  {
    icon: "🤖",
    title: "AI Commerce Agent",
    desc: "AI-powered intent classification handles order status, product questions, returns, and more — in multiple languages.",
  },
  {
    icon: "🛒",
    title: "Cart Recovery",
    desc: "Detect abandoned carts and send personalized recovery messages with payment links.",
  },
  {
    icon: "💳",
    title: "In-Chat Payments",
    desc: "UPI, Razorpay, Stripe — help buyers complete purchases without leaving the chat.",
  },
  {
    icon: "📊",
    title: "Cost Transparency",
    desc: "See what each message costs. Per-category breakdown. Monthly caps. Zero hidden markups on Meta fees.",
  },
  {
    icon: "🔗",
    title: "Multi-Platform Sync",
    desc: "Shopify, WooCommerce, Google Sheets, CSV, or our built-in catalog. Works however you sell.",
  },
];

function WaitlistForm({ size = "default" }: { size?: "default" | "large" }) {
  const [email, setEmail] = useState("");
  const [waitlisted, setWaitlisted] = useState(false);

  if (waitlisted) {
    return (
      <div className="bg-emerald-50 text-emerald-700 p-4 rounded-xl text-center">
        <div className="text-lg font-semibold mb-1">You&apos;re on the list! 🎉</div>
        <p className="text-sm">We&apos;ll notify you at <strong>{email}</strong> when early access is ready.</p>
      </div>
    );
  }

  const py = size === "large" ? "py-3" : "py-2.5";

  return (
    <div className="flex flex-col sm:flex-row gap-3 w-full">
      <input
        type="email"
        placeholder="Enter your email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className={`flex-1 px-4 ${py} rounded-xl border border-gray-300 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition`}
      />
      <button
        onClick={() => {
          if (email && email.includes("@")) setWaitlisted(true);
        }}
        className={`bg-emerald-500 hover:bg-emerald-600 text-white font-semibold px-6 ${py} rounded-xl transition whitespace-nowrap`}
      >
        Join Waitlist
      </button>
    </div>
  );
}

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center text-white font-bold text-sm">
              CC
            </div>
            <span className="font-bold text-xl">ChatCommerce</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-gray-600">
            <a href="#features" className="hover:text-gray-900 transition">Features</a>
            <a href="#pricing" className="hover:text-gray-900 transition">Pricing</a>
            <a href="#how-it-works" className="hover:text-gray-900 transition">How It Works</a>
          </div>
          <a
            href="#waitlist"
            className="bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium px-4 py-2 rounded-lg transition"
          >
            Join Waitlist
          </a>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-amber-50 text-amber-700 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
            <span className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
            Coming Soon — Join the Waitlist
          </div>
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.1] mb-6">
            Sell on WhatsApp.
            <br />
            <span className="bg-gradient-to-r from-emerald-500 to-teal-500 bg-clip-text text-transparent">
              Stay Compliant.
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-10 leading-relaxed">
            AI-powered commerce automation for micro-sellers. Recover abandoned carts, handle customer queries in any
            language, and reduce the risk of getting banned.{" "}
            <strong className="text-gray-900">Zero hidden markup on Meta fees.</strong>
          </p>
          <div className="max-w-md mx-auto mb-4">
            <WaitlistForm size="large" />
          </div>
          <p className="text-sm text-gray-500">
            Be the first to get early access. No spam, ever.
          </p>
        </div>
      </section>

      {/* Why WhatsApp Commerce */}
      <section className="bg-gray-50 border-y border-gray-100">
        <div className="max-w-6xl mx-auto px-4 py-10 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="text-3xl font-extrabold text-emerald-600">Massive Reach</div>
            <div className="text-sm text-gray-500 mt-1">Hundreds of millions of WhatsApp users in India alone</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-extrabold text-emerald-600">High Engagement</div>
            <div className="text-sm text-gray-500 mt-1">WhatsApp messages see significantly higher open rates than email</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-extrabold text-emerald-600">Quick Setup</div>
            <div className="text-sm text-gray-500 mt-1">Designed to get you live in minutes, not days</div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Everything you need to sell on WhatsApp</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Built for micro-sellers who want to automate, not complicate. From compliance to cart recovery.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((f) => (
              <div
                key={f.title}
                className="p-6 rounded-2xl border border-gray-200 hover:border-emerald-300 hover:shadow-lg transition group"
              >
                <div className="text-3xl mb-4">{f.icon}</div>
                <h3 className="text-lg font-semibold mb-2 group-hover:text-emerald-600 transition">{f.title}</h3>
                <p className="text-gray-600 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-24 px-4 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl sm:text-4xl font-bold text-center mb-16">Designed to get you live fast</h2>
          <div className="space-y-12">
            {[
              { step: "1", title: "Connect your WhatsApp", desc: "One-click Meta embedded signup. We guide you through business verification." },
              { step: "2", title: "Link your store", desc: "Shopify, WooCommerce, Google Sheets, or add products manually. Your choice." },
              { step: "3", title: "Set up templates", desc: "Choose from pre-approved templates or create your own. We help you categorize correctly to save on costs." },
              { step: "4", title: "Go live", desc: "Your AI agent starts handling customer messages. Monitor everything from the dashboard." },
            ].map((item) => (
              <div key={item.step} className="flex items-start gap-6">
                <div className="w-12 h-12 rounded-full bg-emerald-500 text-white font-bold text-xl flex items-center justify-center shrink-0">
                  {item.step}
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-1">{item.title}</h3>
                  <p className="text-gray-600">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Compliance section */}
      <section className="py-24 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div>
              <div className="inline-flex items-center gap-2 bg-red-50 text-red-700 text-sm font-medium px-3 py-1 rounded-full mb-4">
                #1 Pain Point
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-6">
                WhatsApp bans are a real risk.
                <br />
                <span className="text-emerald-600">We help you avoid them.</span>
              </h2>
              <p className="text-lg text-gray-600 mb-8">
                Our Compliance Shield monitors your messaging patterns in real-time. Rate limiting, spam scoring,
                template categorization — designed to help prevent bans before they happen.
              </p>
              <ul className="space-y-3">
                {[
                  "Real-time spam score monitoring",
                  "Automatic rate limiting per contact",
                  "Template categorization guidance (helps reduce messaging costs)",
                  "Quality threshold alerts",
                  "Opt-in/opt-out tracking",
                  "Ban-risk assessment with actionable recommendations",
                ].map((item) => (
                  <li key={item} className="flex items-center gap-3 text-gray-700">
                    {CHECK}
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-gray-900 rounded-2xl p-8 text-white">
              <div className="flex items-center gap-2 mb-6">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-gray-400 text-sm ml-2">Compliance Dashboard</span>
              </div>
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-gray-800 rounded-lg">
                  <span className="text-gray-300">Spam Score</span>
                  <span className="text-emerald-400 font-bold">0.12 (Low)</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-800 rounded-lg">
                  <span className="text-gray-300">Ban Risk</span>
                  <span className="text-emerald-400 font-bold">Low</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-800 rounded-lg">
                  <span className="text-gray-300">Messages Today</span>
                  <span className="text-white font-bold">147 / 500</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-800 rounded-lg">
                  <span className="text-gray-300">Marketing Ratio</span>
                  <span className="text-yellow-400 font-bold">32%</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-800 rounded-lg">
                  <span className="text-gray-300">Monthly Cost</span>
                  <span className="text-white font-bold">$4.23 (no markup)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 px-4 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Simple, transparent pricing</h2>
            <p className="text-lg text-gray-600">
              Zero markup on Meta message fees. You only pay the platform subscription.
            </p>
            <p className="text-sm text-emerald-600 font-medium mt-2">Annual billing discount planned</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {plans.map((plan) => (
              <div
                key={plan.name}
                className={`rounded-2xl p-6 ${
                  plan.highlighted
                    ? "bg-emerald-500 text-white ring-4 ring-emerald-500/25 scale-[1.02]"
                    : "bg-white border border-gray-200"
                }`}
              >
                {plan.highlighted && (
                  <div className="text-xs font-bold uppercase tracking-wider text-emerald-100 mb-2">Most Popular</div>
                )}
                <div className="text-lg font-semibold mb-1">{plan.name}</div>
                <div className="flex items-baseline gap-1 mb-1">
                  <span className="text-4xl font-extrabold">{plan.price}</span>
                  <span className={`text-sm ${plan.highlighted ? "text-emerald-100" : "text-gray-500"}`}>
                    {plan.period}
                  </span>
                </div>
                <div className={`text-sm mb-6 ${plan.highlighted ? "text-emerald-100" : "text-gray-500"}`}>
                  {plan.messages}
                </div>
                <ul className="space-y-2 mb-6">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm">
                      <svg
                        className={`w-4 h-4 mt-0.5 shrink-0 ${plan.highlighted ? "text-emerald-200" : "text-emerald-500"}`}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {f}
                    </li>
                  ))}
                </ul>
                <a
                  href="#waitlist"
                  className={`block text-center py-2.5 rounded-lg font-medium text-sm transition ${
                    plan.highlighted
                      ? "bg-white text-emerald-600 hover:bg-emerald-50"
                      : "bg-gray-900 text-white hover:bg-gray-800"
                  }`}
                >
                  Join Waitlist
                </a>
              </div>
            ))}
          </div>
          <p className="text-center text-sm text-gray-500 mt-8">
            All plans include unlimited customer-initiated replies (free under Meta&apos;s pricing model). No hidden fees.
          </p>
        </div>
      </section>

      {/* Waitlist CTA */}
      <section id="waitlist" className="py-24 px-4">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">Be the first to try ChatCommerce</h2>
          <p className="text-lg text-gray-600 mb-8">
            We&apos;re opening early access soon. Join the waitlist and we&apos;ll let you know when it&apos;s your turn.
          </p>
          <div className="max-w-md mx-auto">
            <WaitlistForm size="large" />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-12 px-4">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-emerald-500 flex items-center justify-center text-white font-bold text-xs">
              CC
            </div>
            <span className="font-semibold">ChatCommerce</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-gray-500">
            <a href="#" className="hover:text-gray-700 transition">Privacy</a>
            <a href="#" className="hover:text-gray-700 transition">Terms</a>
            <a href="#" className="hover:text-gray-700 transition">Support</a>
          </div>
          <p className="text-sm text-gray-400">
            &copy; 2026 ChatCommerce. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
