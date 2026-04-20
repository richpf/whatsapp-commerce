const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private token: string | null = null;

  setToken(token: string) {
    this.token = token;
    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", token);
    }
  }

  getToken(): string | null {
    if (!this.token && typeof window !== "undefined") {
      this.token = localStorage.getItem("auth_token");
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
    }
  }

  private async request(path: string, options: RequestInit = {}) {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...((options.headers as Record<string, string>) || {}),
    };
    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || "Request failed");
    }
    return res.json();
  }

  // Auth
  signup(data: { email: string; password: string; business_name: string }) {
    return this.request("/api/auth/signup", { method: "POST", body: JSON.stringify(data) });
  }
  login(data: { email: string; password: string }) {
    return this.request("/api/auth/login", { method: "POST", body: JSON.stringify(data) });
  }
  getMe() {
    return this.request("/api/auth/me");
  }
  updateMe(data: Record<string, unknown>) {
    return this.request("/api/auth/me", { method: "PATCH", body: JSON.stringify(data) });
  }
  completeSetup() {
    return this.request("/api/auth/setup-complete", { method: "POST" });
  }

  // Conversations
  getConversations(params?: { status?: string; limit?: number; offset?: number }) {
    const qs = new URLSearchParams(params as Record<string, string>).toString();
    return this.request(`/api/conversations?${qs}`);
  }
  getConversation(id: number) {
    return this.request(`/api/conversations/${id}`);
  }
  getMessages(conversationId: number) {
    return this.request(`/api/conversations/${conversationId}/messages`);
  }
  sendMessage(conversationId: number, text: string) {
    return this.request(`/api/conversations/${conversationId}/send`, {
      method: "POST", body: JSON.stringify({ text }),
    });
  }

  // Compliance
  getComplianceOverview() {
    return this.request("/api/compliance/overview");
  }
  getSpamScore() {
    return this.request("/api/compliance/spam-score");
  }
  getCosts(month?: string) {
    return this.request(`/api/compliance/costs${month ? `?month=${month}` : ""}`);
  }
  getComplianceLogs() {
    return this.request("/api/compliance/logs");
  }
  getTemplates() {
    return this.request("/api/compliance/templates");
  }

  // Analytics
  getAnalytics(days?: number) {
    return this.request(`/api/analytics/overview${days ? `?days=${days}` : ""}`);
  }

  // Billing
  getPlans() {
    return this.request("/api/billing/plans");
  }
  getCurrentPlan() {
    return this.request("/api/billing/current");
  }
  createCheckout(plan: string, period: string = "monthly") {
    return this.request("/api/billing/checkout", {
      method: "POST", body: JSON.stringify({ plan, period }),
    });
  }

  // Catalog
  getProducts() {
    return this.request("/api/catalog/products");
  }
  createProduct(data: Record<string, unknown>) {
    return this.request("/api/catalog/products", { method: "POST", body: JSON.stringify(data) });
  }
}

export const api = new ApiClient();
