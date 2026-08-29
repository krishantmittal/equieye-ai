# Deploying the EquiEye API

The backend is a plain FastAPI app. It needs a Python host and a Postgres
database. Below is the Render + Neon path (both have usable free tiers);
`Dockerfile` is included so the same service runs on Fly.io, Railway, or
Cloud Run without changes.

Everything here has been verified locally except the hosted steps, which
need your accounts.

---

## 1. Database first (Neon)

Do this before the web service — the API needs `DATABASE_URL` at boot.

1. Create a project at **neon.tech** (free tier).
2. Copy the connection string. It looks like:
   `postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require`

**Why not Render's own Postgres:** its free tier expires, and silently
losing the database is the exact failure this persistence layer exists to
prevent. Neon's free tier persists.

**Why not SQLite:** it is the local default and fine for development, but
most PaaS filesystems are ephemeral — the file is wiped on every redeploy,
so every user's watchlist and holdings vanish. `/api/health` reports which
engine is live specifically so this misconfiguration is visible rather
than silent. **Check it after deploying.**

You do not need to create any tables. The app creates them on startup.

---

## 2. Web service (Render)

1. **Render dashboard → New → Blueprint**, select this repo. Render reads
   `render.yaml`, which sets the build command, start command, health
   check, Python version, and worker count.
2. Set the secret env vars (marked `sync: false` in the blueprint, so they
   are never committed):

   | Variable | Value |
   |---|---|
   | `DATABASE_URL` | the Neon string from step 1 |
   | `GROQ_API_KEY` | your rotated Groq key |
   | `NEWS_API_KEY` | your rotated NewsAPI key |
   | `GEMINI_API_KEY` | your rotated Gemini key |
   | `CORS_ORIGINS` | `http://localhost:3000` for now; add the frontend URL when Phase 3 ships |

3. Deploy.

The build installs `requirements-backend.txt` only — **not**
`requirements.txt`, which is the Streamlit app's list and carries
streamlit, plotly, altair, PyPDF2 and Pillow. An import trace confirmed
the API never loads any of them; installing them only inflates the image
and slows cold starts.

---

## 3. Verify the deployment

Replace `$API` with your Render URL.

```bash
curl -s $API/api/health | python3 -m json.tool
```

Check three things in the response:

- `"engine": "postgres"` — **if this says `sqlite`, `DATABASE_URL` did not
  take effect and your data will be wiped on the next redeploy.**
- `"ai_enabled": true` — otherwise `GROQ_API_KEY` is missing or wrong.
- `"status": "ok"`

Then exercise a real path end to end:

```bash
curl -s "$API/api/search?q=TCS"
```

And confirm persistence actually persists — the whole point of the
feature. Save the returned `account_key`, add a stock, then **redeploy**
and read it back with the same key. If the item survives a redeploy, the
database is wired correctly:

```bash
curl -s -X POST $API/api/watchlist -H "Content-Type: application/json" -d '{"ticker":"TCS.NS","name":"Tata Consultancy Services"}'
```

Interactive API docs are at `$API/docs`.

---

## Known limits of this deployment

These are real and worth knowing before you put it in front of users.

- **yfinance will rate-limit.** It is an unofficial scraper, and every
  request now comes from one server IP rather than each user's browser.
  Expect intermittent 502/503 under load. The TTL cache absorbs some of
  this; a licensed feed is the actual fix.
- **Data licensing.** yfinance (Yahoo's terms) and NewsAPI's free tier are
  not licensed for commercial use. Not a blocker for building; a real one
  before charging money or launching publicly.
- **Free tier sleeps.** Render's free web services idle out, so the first
  request after a quiet period pays a cold start.
- **Single worker, in-process cache.** `WEB_CONCURRENCY=1` is deliberate:
  `core/cache.py` caches per process, so extra workers each keep their own
  copy — lowering the hit rate and multiplying yfinance calls from one IP.
  Add a shared cache (Redis) *before* adding workers.
- **Anonymous accounts.** `X-Account-Key` is a bearer credential, not
  authentication. Anyone holding a key can read and write that account.
  Fine for anonymous convenience; replace with real auth before storing
  anything a user would be harmed by leaking.
- **Schema changes need a migration tool.** Startup uses
  `create_all`, which only adds missing tables — it will not alter an
  existing one. Add Alembic before changing a column on a table that
  already holds real rows.

---

## Running locally

```bash
pip install -r requirements-backend.txt
cp .env.example .env      # then fill in your keys
uvicorn api.main:app --reload --port 8000
```

With no `DATABASE_URL` set it uses SQLite at `./data/equieye.db`, which is
gitignored. With no `GROQ_API_KEY`, every numeric endpoint still works and
the AI routes report `ai_enabled: false` rather than failing.
