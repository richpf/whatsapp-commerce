"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";

const steps = [
  { id: "whatsapp", title: "Connect WhatsApp", icon: "📱" },
  { id: "store", title: "Link Your Store", icon: "🏪" },
  { id: "templates", title: "Set Up Templates", icon: "📝" },
  { id: "golive", title: "Go Live", icon: "🚀" },
];

const storeOptions = [
  { id: "shopify", name: "Shopify", desc: "Connect via OAuth", icon: "🟢" },
  { id: "woocommerce", name: "WooCommerce", desc: "REST API connection", icon: "🟣" },
  { id: "google_sheets", name: "Google Sheets", desc: "For manual sellers", icon: "📗" },
  { id: "csv", name: "CSV Import", desc: "Upload product catalog", icon: "📄" },
  { id: "manual", name: "Built-in Catalog", desc: "Add products manually", icon: "✏️" },
];

const templatePresets = [
  { name: "order_confirmation", category: "utility", content: "Hi {{1}}! Your order #{{2}} has been confirmed. Total: {{3}}. We'll notify you when it ships!" },
  { name: "cart_recovery", category: "utility", content: "Hi {{1}}! You left some items in your cart. Complete your purchase: {{2}}" },
  { name: "shipping_update", category: "utility", content: "Hi {{1}}! Your order #{{2}} has shipped. Track it here: {{3}}" },
  { name: "diwali_sale", category: "marketing", content: "🪔 Happy Diwali, {{1}}! Celebrate with up to {{2}}% off on all products. Shop now: {{3}}", festival: true },
  { name: "welcome_message", category: "utility", content: "Welcome to {{1}}! 👋 We're here to help. Reply with any questions about our products." },
];

export default function SetupPage() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [storeType, setStoreType] = useState("");
  const [storeConfig, setStoreConfig] = useState<Record<string, string>>({});
  const [selectedTemplates, setSelectedTemplates] = useState<string[]>(templatePresets.map((t) => t.name));
  const [loading, setLoading] = useState(false);

  const handleComplete = async () => {
    setLoading(true);
    try {
      await api.updateMe({
        store_type: storeType || "manual",
        store_config: storeConfig,
      });
      await api.completeSetup();
      router.push("/dashboard");
    } catch {
      router.push("/dashboard");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center text-white font-bold text-sm">CC</div>
            <span className="font-bold text-xl">ChatCommerce</span>
          </Link>
          <h1 className="text-2xl font-bold">Setup Wizard</h1>
          <p className="text-gray-500">Let&apos;s get you selling on WhatsApp in under 5 minutes</p>
        </div>

        {/* Progress */}
        <div className="flex items-center justify-between mb-10 max-w-lg mx-auto">
          {steps.map((step, i) => (
            <div key={step.id} className="flex items-center">
              <div className={`flex items-center gap-2 ${i <= currentStep ? "text-emerald-600" : "text-gray-400"}`}>
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg ${
                  i < currentStep ? "bg-emerald-500 text-white" : i === currentStep ? "bg-emerald-100 border-2 border-emerald-500" : "bg-gray-100"
                }`}>
                  {i < currentStep ? "✓" : step.icon}
                </div>
                <span className="text-xs font-medium hidden sm:block">{step.title}</span>
              </div>
              {i < steps.length - 1 && (
                <div className={`w-8 sm:w-16 h-0.5 mx-2 ${i < currentStep ? "bg-emerald-500" : "bg-gray-200"}`} />
              )}
            </div>
          ))}
        </div>

        {/* Step content */}
        <div className="bg-white rounded-2xl border border-gray-200 p-6 sm:p-8">
          {currentStep === 0 && (
            <div className="text-center">
              <h2 className="text-xl font-semibold mb-4">Connect Your WhatsApp Business</h2>
              <p className="text-gray-600 mb-8 max-w-md mx-auto">
                We&apos;ll use Meta&apos;s embedded signup to connect your WhatsApp Business account securely.
              </p>
              <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6 max-w-sm mx-auto mb-6">
                <div className="text-4xl mb-3">📱</div>
                <p className="text-sm text-emerald-700">
                  In production, this launches Meta&apos;s embedded signup flow. For now, we&apos;ll simulate the connection.
                </p>
              </div>
              <button
                onClick={() => setCurrentStep(1)}
                className="bg-emerald-500 hover:bg-emerald-600 text-white font-semibold px-8 py-3 rounded-xl transition"
              >
                Connect WhatsApp (Simulated)
              </button>
            </div>
          )}

          {currentStep === 1 && (
            <div>
              <h2 className="text-xl font-semibold mb-2">Link Your Store</h2>
              <p className="text-gray-600 mb-6">Choose how you manage your products and orders.</p>
              <div className="grid sm:grid-cols-2 gap-3">
                {storeOptions.map((store) => (
                  <button
                    key={store.id}
                    onClick={() => setStoreType(store.id)}
                    className={`text-left p-4 rounded-xl border-2 transition ${
                      storeType === store.id ? "border-emerald-500 bg-emerald-50" : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <div className="text-2xl mb-2">{store.icon}</div>
                    <div className="font-medium">{store.name}</div>
                    <div className="text-sm text-gray-500">{store.desc}</div>
                  </button>
                ))}
              </div>

              {storeType === "shopify" && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <label className="block text-sm font-medium mb-1">Shopify Store URL</label>
                  <input
                    type="text"
                    placeholder="your-store.myshopify.com"
                    value={storeConfig.shop_url || ""}
                    onChange={(e) => setStoreConfig({ ...storeConfig, shop_url: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 focus:border-emerald-500 outline-none"
                  />
                </div>
              )}

              {storeType === "woocommerce" && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg space-y-3">
                  <div>
                    <label className="block text-sm font-medium mb-1">Site URL</label>
                    <input
                      type="text"
                      placeholder="https://your-store.com"
                      value={storeConfig.url || ""}
                      onChange={(e) => setStoreConfig({ ...storeConfig, url: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg border border-gray-300 focus:border-emerald-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Consumer Key</label>
                    <input
                      type="text"
                      placeholder="ck_..."
                      value={storeConfig.consumer_key || ""}
                      onChange={(e) => setStoreConfig({ ...storeConfig, consumer_key: e.target.value })}
                      className="w-full px-3 py-2 rounded-lg border border-gray-300 focus:border-emerald-500 outline-none"
                    />
                  </div>
                </div>
              )}

              {storeType === "google_sheets" && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                  <label className="block text-sm font-medium mb-1">Spreadsheet ID</label>
                  <input
                    type="text"
                    placeholder="Paste your Google Sheets ID"
                    value={storeConfig.spreadsheet_id || ""}
                    onChange={(e) => setStoreConfig({ ...storeConfig, spreadsheet_id: e.target.value })}
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 focus:border-emerald-500 outline-none"
                  />
                </div>
              )}

              <div className="flex justify-between mt-8">
                <button onClick={() => setCurrentStep(0)} className="text-gray-500 hover:text-gray-700">
                  Back
                </button>
                <button
                  onClick={() => setCurrentStep(2)}
                  className="bg-emerald-500 hover:bg-emerald-600 text-white font-semibold px-6 py-2.5 rounded-xl transition"
                >
                  Continue
                </button>
              </div>
            </div>
          )}

          {currentStep === 2 && (
            <div>
              <h2 className="text-xl font-semibold mb-2">Message Templates</h2>
              <p className="text-gray-600 mb-6">
                Select pre-approved templates. Utility templates cost ~8x less than marketing!
              </p>
              <div className="space-y-3">
                {templatePresets.map((t) => (
                  <label
                    key={t.name}
                    className={`flex items-start gap-3 p-4 rounded-xl border-2 cursor-pointer transition ${
                      selectedTemplates.includes(t.name)
                        ? "border-emerald-500 bg-emerald-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedTemplates.includes(t.name)}
                      onChange={() => {
                        setSelectedTemplates((prev) =>
                          prev.includes(t.name) ? prev.filter((n) => n !== t.name) : [...prev, t.name]
                        );
                      }}
                      className="mt-1 accent-emerald-500"
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm">{t.name.replace(/_/g, " ")}</span>
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${
                            t.category === "marketing" ? "bg-orange-100 text-orange-700" : "bg-blue-100 text-blue-700"
                          }`}
                        >
                          {t.category}
                        </span>
                        {t.festival && <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">festival</span>}
                      </div>
                      <p className="text-sm text-gray-500 mt-1">{t.content}</p>
                    </div>
                  </label>
                ))}
              </div>
              <div className="flex justify-between mt-8">
                <button onClick={() => setCurrentStep(1)} className="text-gray-500 hover:text-gray-700">
                  Back
                </button>
                <button
                  onClick={() => setCurrentStep(3)}
                  className="bg-emerald-500 hover:bg-emerald-600 text-white font-semibold px-6 py-2.5 rounded-xl transition"
                >
                  Continue
                </button>
              </div>
            </div>
          )}

          {currentStep === 3 && (
            <div className="text-center">
              <div className="text-6xl mb-4">🚀</div>
              <h2 className="text-2xl font-bold mb-2">You&apos;re all set!</h2>
              <p className="text-gray-600 mb-8 max-w-md mx-auto">
                Your WhatsApp commerce automation is ready to go. Your AI agent will start handling customer messages automatically.
              </p>
              <div className="bg-gray-50 rounded-xl p-6 max-w-sm mx-auto mb-8 text-left space-y-3">
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-emerald-500">✓</span> WhatsApp connected
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-emerald-500">✓</span> Store: {storeType || "manual catalog"}
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-emerald-500">✓</span> {selectedTemplates.length} templates selected
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="text-emerald-500">✓</span> Compliance Shield active
                </div>
              </div>
              <button
                onClick={handleComplete}
                disabled={loading}
                className="bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-white font-semibold px-8 py-3 rounded-xl transition"
              >
                {loading ? "Setting up..." : "Go to Dashboard"}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
