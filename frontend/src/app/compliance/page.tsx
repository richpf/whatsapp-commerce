"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { api } from "@/lib/api";

interface ComplianceData {
  ban_risk: {
    risk_level: string;
    spam_score: number;
    risk_factors: string[];
    recommendations: string[];
    plan_usage: { count: number; limit: number; remaining: number; usage_pct: number };
  };
  costs: {
    month: string;
    total_usd: number;
    total_inr: number;
    total_messages: number;
    breakdown: Record<string, { cost_usd: number; messages: number }>;
  };
  plan_usage: { count: number; limit: number; remaining: number; usage_pct: number };
}

export default function CompliancePage() {
  const [data, setData] = useState<ComplianceData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getComplianceOverview()
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const riskColor = (level: string) => {
    if (level === "critical") return "text-red-600 bg-red-50";
    if (level === "medium") return "text-yellow-600 bg-yellow-50";
    return "text-emerald-600 bg-emerald-50";
  };

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Compliance Shield</h1>
        <p className="text-gray-500 text-sm">Monitor your WhatsApp compliance and avoid bans</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full" />
        </div>
      ) : data ? (
        <div className="space-y-6">
          {/* Risk overview */}
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="text-sm text-gray-500 mb-2">Ban Risk Level</div>
              <div className={`inline-flex items-center gap-2 text-lg font-bold px-3 py-1 rounded-full ${riskColor(data.ban_risk.risk_level)}`}>
                {data.ban_risk.risk_level === "low" ? "🟢" : data.ban_risk.risk_level === "medium" ? "🟡" : "🔴"}
                {data.ban_risk.risk_level.toUpperCase()}
              </div>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="text-sm text-gray-500 mb-2">Spam Score</div>
              <div className="text-2xl font-bold">{data.ban_risk.spam_score}</div>
              <div className="text-xs text-gray-400">Threshold: 0.70</div>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <div className="text-sm text-gray-500 mb-2">Plan Usage</div>
              <div className="text-2xl font-bold">
                {data.plan_usage.count} / {data.plan_usage.limit}
              </div>
              <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${data.plan_usage.usage_pct > 90 ? "bg-red-500" : data.plan_usage.usage_pct > 70 ? "bg-yellow-500" : "bg-emerald-500"}`}
                  style={{ width: `${Math.min(data.plan_usage.usage_pct, 100)}%` }}
                />
              </div>
              <div className="text-xs text-gray-400 mt-1">{data.plan_usage.remaining} messages remaining</div>
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="font-semibold mb-3">Recommendations</h2>
            <div className="space-y-2">
              {data.ban_risk.recommendations.map((rec, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  <span className="text-emerald-500 mt-0.5">💡</span>
                  <span className="text-gray-700">{rec}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Cost breakdown */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="font-semibold mb-3">Monthly Costs — {data.costs.month}</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500">Total (USD)</div>
                <div className="text-lg font-bold">${data.costs.total_usd.toFixed(2)}</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500">Total (INR)</div>
                <div className="text-lg font-bold">₹{data.costs.total_inr.toFixed(2)}</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500">Messages</div>
                <div className="text-lg font-bold">{data.costs.total_messages}</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500">Markup</div>
                <div className="text-lg font-bold text-emerald-600">0%</div>
              </div>
            </div>
            {Object.entries(data.costs.breakdown).length > 0 && (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b">
                    <th className="pb-2">Category</th>
                    <th className="pb-2">Messages</th>
                    <th className="pb-2">Cost (USD)</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(data.costs.breakdown).map(([cat, info]) => (
                    <tr key={cat} className="border-b border-gray-50">
                      <td className="py-2 capitalize">{cat}</td>
                      <td className="py-2">{info.messages}</td>
                      <td className="py-2">${info.cost_usd.toFixed(4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Risk factors */}
          {data.ban_risk.risk_factors.length > 0 && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-5">
              <h2 className="font-semibold text-red-700 mb-3">Risk Factors</h2>
              <ul className="space-y-2">
                {data.ban_risk.risk_factors.map((factor, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-red-700">
                    <span>⚠️</span>
                    {factor}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">
          <p className="text-lg mb-2">No compliance data yet</p>
          <p className="text-sm">Start sending messages to see compliance metrics</p>
        </div>
      )}
    </DashboardLayout>
  );
}
