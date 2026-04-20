"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { api } from "@/lib/api";

interface Analytics {
  period_days: number;
  messages: { total: number; inbound: number; outbound: number; ai_generated: number; ai_rate: number };
  conversations: { total: number; escalated: number; resolved: number; escalation_rate: number };
  ai_confidence_avg: number;
  orders: { total: number; revenue: number };
  cart_recovery: { total_abandoned: number; recovery_messages_sent: number; total_recovered: number; recovery_rate: number; revenue_recovered: number };
}

export default function AnalyticsPage() {
  const [data, setData] = useState<Analytics | null>(null);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.getAnalytics(days)
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [days]);

  return (
    <DashboardLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Analytics</h1>
          <p className="text-gray-500 text-sm">Track your WhatsApp commerce performance</p>
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full" />
        </div>
      ) : data ? (
        <div className="space-y-6">
          {/* Message stats */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="font-semibold mb-4">Messages</h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {[
                { label: "Total", value: data.messages.total },
                { label: "Inbound", value: data.messages.inbound },
                { label: "Outbound", value: data.messages.outbound },
                { label: "AI Generated", value: data.messages.ai_generated },
                { label: "AI Rate", value: `${data.messages.ai_rate}%` },
              ].map((s) => (
                <div key={s.label} className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-500">{s.label}</div>
                  <div className="text-xl font-bold mt-1">{s.value}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Conversation stats */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="font-semibold mb-4">Conversations</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: "Total", value: data.conversations.total },
                { label: "Resolved", value: data.conversations.resolved },
                { label: "Escalated", value: data.conversations.escalated },
                { label: "Escalation Rate", value: `${data.conversations.escalation_rate}%` },
              ].map((s) => (
                <div key={s.label} className="bg-gray-50 rounded-lg p-3">
                  <div className="text-xs text-gray-500">{s.label}</div>
                  <div className="text-xl font-bold mt-1">{s.value}</div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Performance */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h2 className="font-semibold mb-4">AI Performance</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-2">Average Confidence</div>
                <div className="text-3xl font-bold">{(data.ai_confidence_avg * 100).toFixed(0)}%</div>
                <div className="mt-2 w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="h-3 rounded-full bg-emerald-500"
                    style={{ width: `${data.ai_confidence_avg * 100}%` }}
                  />
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-2">Automation Rate</div>
                <div className="text-3xl font-bold">{data.messages.ai_rate}%</div>
                <div className="mt-2 w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="h-3 rounded-full bg-blue-500"
                    style={{ width: `${data.messages.ai_rate}%` }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Revenue & Cart Recovery */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h2 className="font-semibold mb-4">Revenue</h2>
              <div className="text-3xl font-bold text-emerald-600">${data.orders.revenue.toFixed(2)}</div>
              <div className="text-sm text-gray-500 mt-1">{data.orders.total} orders</div>
            </div>
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h2 className="font-semibold mb-4">Cart Recovery</h2>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <div className="text-2xl font-bold">{data.cart_recovery.recovery_rate}%</div>
                  <div className="text-xs text-gray-500">Recovery rate</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-emerald-600">${data.cart_recovery.revenue_recovered.toFixed(0)}</div>
                  <div className="text-xs text-gray-500">Recovered</div>
                </div>
                <div>
                  <div className="text-lg font-semibold">{data.cart_recovery.total_abandoned}</div>
                  <div className="text-xs text-gray-500">Abandoned</div>
                </div>
                <div>
                  <div className="text-lg font-semibold">{data.cart_recovery.recovery_messages_sent}</div>
                  <div className="text-xs text-gray-500">Messages sent</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-gray-400">
          <p className="text-lg mb-2">No analytics data yet</p>
          <p className="text-sm">Start using ChatCommerce to see your analytics</p>
        </div>
      )}
    </DashboardLayout>
  );
}
