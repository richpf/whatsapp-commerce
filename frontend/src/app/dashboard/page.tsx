"use client";

import { useEffect, useState } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { api } from "@/lib/api";

interface Analytics {
  messages: { total: number; inbound: number; outbound: number; ai_generated: number; ai_rate: number };
  conversations: { total: number; escalated: number; resolved: number; escalation_rate: number };
  ai_confidence_avg: number;
  orders: { total: number; revenue: number };
  cart_recovery: { total_abandoned: number; total_recovered: number; recovery_rate: number; revenue_recovered: number };
}

interface Conversation {
  id: number;
  customer_phone: string;
  customer_name: string;
  status: string;
  ai_confidence_avg: number;
  last_message_at: string;
}

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.getAnalytics(30).catch(() => null),
      api.getConversations({ limit: 10 }).catch(() => ({ conversations: [] })),
    ]).then(([a, c]) => {
      setAnalytics(a);
      setConversations(c?.conversations || []);
      setLoading(false);
    });
  }, []);

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-gray-500 text-sm">Overview of your WhatsApp commerce activity</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full" />
        </div>
      ) : (
        <>
          {/* Stat cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {[
              { label: "Messages (30d)", value: analytics?.messages.total || 0, sub: `${analytics?.messages.ai_rate || 0}% AI-handled` },
              { label: "Conversations", value: analytics?.conversations.total || 0, sub: `${analytics?.conversations.escalation_rate || 0}% escalated` },
              { label: "Revenue", value: `$${(analytics?.orders.revenue || 0).toFixed(0)}`, sub: `${analytics?.orders.total || 0} orders` },
              { label: "Cart Recovery", value: `${analytics?.cart_recovery.recovery_rate || 0}%`, sub: `$${(analytics?.cart_recovery.revenue_recovered || 0).toFixed(0)} recovered` },
            ].map((s) => (
              <div key={s.label} className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="text-sm text-gray-500">{s.label}</div>
                <div className="text-2xl font-bold mt-1">{s.value}</div>
                <div className="text-xs text-gray-400 mt-1">{s.sub}</div>
              </div>
            ))}
          </div>

          {/* Recent conversations */}
          <div className="bg-white rounded-xl border border-gray-200">
            <div className="p-4 border-b border-gray-100">
              <h2 className="font-semibold">Recent Conversations</h2>
            </div>
            {conversations.length === 0 ? (
              <div className="p-8 text-center text-gray-400">
                <p className="text-lg mb-2">No conversations yet</p>
                <p className="text-sm">Messages from your customers will appear here</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {conversations.map((conv) => (
                  <div key={conv.id} className="p-4 flex items-center justify-between hover:bg-gray-50 transition">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-medium">
                        {(conv.customer_name || conv.customer_phone)[0].toUpperCase()}
                      </div>
                      <div>
                        <div className="font-medium text-sm">{conv.customer_name || conv.customer_phone}</div>
                        <div className="text-xs text-gray-400">{conv.customer_phone}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {conv.ai_confidence_avg && (
                        <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">
                          AI: {Math.round(conv.ai_confidence_avg * 100)}%
                        </span>
                      )}
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full ${
                          conv.status === "active"
                            ? "bg-emerald-50 text-emerald-700"
                            : conv.status === "escalated"
                            ? "bg-red-50 text-red-700"
                            : "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {conv.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </DashboardLayout>
  );
}
