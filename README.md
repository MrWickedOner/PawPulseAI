# PawPulse 🐾

> Give every pet owner the ability to catch illness before it arrives — the same way a cardiologist uses data, not just instinct, to understand a heart.

PawPulse is an AI-powered pet health monitoring platform. It learns each pet's unique behavioral and physiological baseline from existing smart devices (FitBark, Whistle, Tractive) and surfaces anomalies — shifts in sleep, activity, gait, or vitals — days before symptoms appear.

## Architecture

```
PawPulseAI/
├── engine/        # AI anomaly detection engine (Python)
├── backend/       # FastAPI API server
├── frontend/      # React web dashboard
└── mobile/        # Expo React Native mobile app
```

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Mobile
```bash
cd mobile
npm install
npx expo start
```

### Demo
Run the seed script to create a demo user with synthetic health data:
```bash
cd backend
python seed_demo_fast.py
```
Login at `http://localhost:5173` with `demo@pawpulse.com` (any password).

## Subscription Tiers
- **Basic ($9/mo):** Anomaly alerts & weekly health summaries
- **Premium ($19/mo):** 30-day trendlines, multi-pet dashboard, shareable vet reports
- **Pro:** White-labeled monitoring for veterinary practices

## Tech Stack
- **AI:** Python (pandas, scipy, scikit-learn, statsmodels)
- **Backend:** FastAPI, SQLite (Turso), JWT auth
- **Frontend:** React, TypeScript, Tailwind CSS, Recharts
- **Mobile:** Expo (React Native), NativeWind, react-native-iap