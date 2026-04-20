# ChatCommerce — WhatsApp Commerce Automation for Micro-Sellers

AI-powered WhatsApp commerce automation platform built for micro-sellers. Automate customer conversations, recover abandoned carts, generate payment links, and stay compliant with Meta's policies.

## Key Features

- **Compliance Shield** — Rate limiting, spam scoring, template management, ban-risk alerts, opt-in tracking. Our core differentiator.
- **AI Commerce Agent** — GPT-4o-mini powered intent classification and multi-language response generation (Hindi, Portuguese, Spanish, English).
- **Abandoned Cart Recovery** — Detect abandoned carts and send personalized recovery messages with payment links.
- **In-Chat Payments** — Razorpay, Stripe, WhatsApp Pay, generic checkout links.
- **Multi-Platform Store Sync** — Shopify Admin API, WooCommerce REST API, Google Sheets API, CSV import, built-in catalog.
- **Consumption Dashboard** — Per-message cost visibility by category. Zero markup on Meta fees.
- **5-Minute Setup Wizard** — Meta embedded signup, store connection, template creation, go live.
- **Festival Campaign Templates** — Pre-built templates for Diwali, Pongal, Carnival, Eid in local languages.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python (FastAPI) |
| Frontend | Next.js 15, Tailwind CSS |
| Database | PostgreSQL |
| AI | OpenAI GPT-4o-mini |
| Payments | Stripe, Razorpay |
| WhatsApp | Meta Cloud API |
| Hosting | Fly.io |

## Project Structure

```
whatsapp-commerce/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Environment configuration
│   │   ├── models/models.py     # SQLAlchemy models
│   │   ├── api/                 # Route handlers
│   │   │   ├── webhook.py       # Meta webhook handler
│   │   ���   ├── auth.py          # Seller authentication
│   │   │   ├── conversations.py # Conversation management
│   │   │   ├── compliance.py    # Compliance dashboard
│   │   │   ├── billing.py       # Stripe billing
│   │   │   ├── analytics.py     # Analytics endpoints
│   │   │   └── catalog.py       # Product catalog
│   │   ├─��� services/
│   │   │   ├── whatsapp.py      # Meta Cloud API client
│   │   │   ├── ai_agent.py      # GPT-4o-mini agent
│   │   │   ├── compliance.py    # Compliance engine
│   │   │   ├── shopify.py       # Shopify connector
│   │   │   ├── woocommerce.py   # WooCommerce connector
│   │   │   ├── sheets.py        # Google Sheets connector
│   │   │   ├── catalog.py       # Built-in catalog
│   │   │   ├── payments.py      # Payment link generation
│   │   │   └── cart_recovery.py # Cart recovery
│   │   └── db/
│   │       ├── database.py      # DB connection
│   │       └── migrations/      # Alembic migrations
│   ├── requirements.txt
│   ├── Dockerfile
│   └── fly.toml
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx             # Landing page
│   │   ├── auth/page.tsx        # Login / Signup
│   │   ├── dashboard/page.tsx   # Main dashboard
│   │   ├── setup/page.tsx       # Setup wizard
│   │   ├── compliance/page.tsx  # Compliance dashboard
│   │   ├── analytics/page.tsx   # Analytics
│   │   └── billing/page.tsx     # Billing & plans
│   ├── Dockerfile
│   └── fly.toml
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 15+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your credentials

# Run
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install

# Copy and configure environment
cp .env.example .env.local

# Run
npm run dev
```

### Environment Variables

See `backend/.env.example` and `frontend/.env.example` for all required variables.

Key variables:
- `DATABASE_URL` — PostgreSQL connection string
- `OPENAI_API_KEY` — For AI agent (falls back to templates if not set)
- `META_WHATSAPP_TOKEN` — Meta Cloud API token (test mode if not set)
- `META_VERIFY_TOKEN` — Webhook verification token
- `STRIPE_SECRET_KEY` — For billing (mock mode if not set)
- `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` — For Indian payments

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /webhook` | Meta webhook verification |
| `POST /webhook` | Incoming WhatsApp messages |
| `POST /webhook/test` | Test message simulation |
| `POST /api/auth/signup` | Seller registration |
| `POST /api/auth/login` | Seller login |
| `GET /api/auth/me` | Current seller profile |
| `GET /api/conversations` | List conversations |
| `GET /api/compliance/overview` | Compliance overview |
| `GET /api/compliance/spam-score` | Current spam score |
| `GET /api/compliance/costs` | Monthly cost breakdown |
| `GET /api/analytics/overview` | Analytics dashboard data |
| `GET /api/billing/plans` | Available plans |
| `POST /api/billing/checkout` | Create Stripe checkout |
| `GET /api/catalog/products` | List products |
| `POST /api/catalog/products` | Create product |
| `POST /api/catalog/products/import/csv` | Import CSV catalog |

## Deployment (Fly.io)

```bash
# Backend
cd backend
fly launch --name whatsapp-commerce-api --region bom
fly secrets set DATABASE_URL=... OPENAI_API_KEY=... META_WHATSAPP_TOKEN=...
fly deploy

# Frontend
cd frontend
fly launch --name whatsapp-commerce-web --region bom
fly deploy
```

## Pricing

| Plan | Price | Messages | Key Features |
|------|-------|----------|-------------|
| Free | $0/mo | 50/mo | Basic AI, compliance dashboard |
| Starter | $19/mo | 500/mo | Compliance Shield, AI agent, order lookup |
| Pro | $39/mo | 2,000/mo | Cart recovery, store sync, payment links |
| Scale | $79/mo | 10,000/mo | Team inbox, broadcasts, full analytics |

Zero markup on Meta message fees. Annual billing saves 20%.

## License

Proprietary. All rights reserved.
