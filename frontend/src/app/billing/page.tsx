"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { api } from "@/lib/api";

interface Plan {
  id: string;
  name: string;
  price_monthly: number;
  price_annual: number;
  messages: number;
  features: string[];
}

export default function BillingPage() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [currentPlan, setCurrentPlan] = useState<string>("free");
  const [annual, setAnnual] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getPlans().catch(() => ({ plans: [] })),
      api.getCurrentPlan().catch(() => ({ plan: "free" })),
    ]).then(([p, c]) => {
      setPlans(p.plans || []);
      setCurrentPlan(c.plan || "free");
      setLoading(false);
    });
  }, []);

  const handleUpgrade = async (planId: string) => {
    try {
      const res = await api.createCheckout(planId, annual ? "annual" : "monthly");
      if (res.checkout_url) {
        window.location.href = res.checkout_url;
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Billing</h1>
        <p className="text-gray-500 text-sm">Manage your subscription and billing</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Current plan */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-500">Current Plan</div>
                <div className="text-xl font-bold capitalize">{currentPlan}</div>
              </div>
              <div className="bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full text-sm font-medium">Active</div>
            </div>
          </div>

          {/* Billing toggle */}
          <div className="flex items-center justify-center gap-3">
            <span className={`text-sm ${!annual ? "font-semibold" : "text-gray-500"}`}>Monthly</span>
            <button
              onClick={() => setAnnual(!annual)}
              className={`w-12 h-6 rounded-full p-0.5 transition ${annual ? "bg-emerald-500" : "bg-gray-300"}`}
            >
              <div
                className={`w-5 h-5 bg-white rounded-full transition-transform ${annual ? "translate-x-6" : ""}`}
              />
            </button>
            <span className={`text-sm ${annual ? "font-semibold" : "text-gray-500"}`}>
              Annual <span className="text-emerald-600 text-xs">Save 20%</span>
            </span>
          </div>

          {/* Plans */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {plans.map((plan) => {
              const isCurrent = currentPlan === plan.id;
              const price = annual ? plan.price_annual : plan.price_monthly;
              const highlighted = plan.id === "pro";
              return (
                <div
                  key={plan.id}
                  className={`rounded-xl p-5 ${
                    highlighted
                      ? "bg-emerald-500 text-white ring-2 ring-emerald-500/25"
                      : "bg-white border border-gray-200"
                  }`}
                >
                  {highlighted && (
                    <div className="text-xs font-bold uppercase text-emerald-100 mb-2">Most Popular</div>
                  )}
                  <div className="font-semibold text-lg">{plan.name}</div>
                  <div className="flex items-baseline gap-1 mt-1">
                    <span className="text-3xl font-extrabold">
                      ${annual ? Math.round(price / 12) : price}
                    </span>
                    <span className={`text-sm ${highlighted ? "text-emerald-100" : "text-gray-500"}`}>/mo</span>
                  </div>
                  <div className={`text-sm mt-1 mb-4 ${highlighted ? "text-emerald-100" : "text-gray-500"}`}>
                    {plan.messages.toLocaleString()} msgs/mo
                  </div>
                  <ul className="space-y-1.5 mb-4">
                    {plan.features.map((f) => (
                      <li key={f} className="text-sm flex items-start gap-1.5">
                        <span className={highlighted ? "text-emerald-200" : "text-emerald-500"}>✓</span>
                        {f}
                      </li>
                    ))}
                  </ul>
                  {isCurrent ? (
                    <div className={`text-center py-2 rounded-lg text-sm font-medium ${
                      highlighted ? "bg-emerald-600 text-emerald-100" : "bg-gray-100 text-gray-600"
                    }`}>
                      Current Plan
                    </div>
                  ) : (
                    <button
                      onClick={() => handleUpgrade(plan.id)}
                      className={`w-full py-2 rounded-lg text-sm font-medium transition ${
                        highlighted
                          ? "bg-white text-emerald-600 hover:bg-emerald-50"
                          : "bg-gray-900 text-white hover:bg-gray-800"
                      }`}
                    >
                      {plan.price_monthly === 0 ? "Downgrade" : "Upgrade"}
                    </button>
                  )}
                </div>
              );
            })}
          </div>

          <p className="text-center text-sm text-gray-500">
            All plans include zero markup on Meta message fees. Cancel anytime.
          </p>
        </div>
      )}
    </DashboardLayout>
  );
}
