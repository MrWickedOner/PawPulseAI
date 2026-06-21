# PawPulse Mobile App

React Native (Expo) application for pet health monitoring.

## Features
- **Health Dashboard**: Real-time monitoring of your pets with Victory Native charts.
- **Anomaly Alerts**: Push notifications and in-app alerts for behavioral/physiological shifts.
- **Onboarding**: Step-by-step wizard for adding pets and connecting smart collars.
- **Subscriptions**: In-App Purchase integration for Premium tiers (Anomaly alerts, multi-pet support).
- **Vet Reports**: Shareable health summaries for veterinarians.
- **Security**: Optional biometric unlock (FaceID/Fingerprint).

## Tech Stack
- **Expo SDK 56**
- **TypeScript**
- **NativeWind v4** (Tailwind CSS for React Native)
- **React Navigation** (Bottom Tabs, Native Stacks)
- **TanStack React Query** (Data fetching & caching)
- **Victory Native** (Charting)
- **Lucide React Native** (Iconography)

## Development

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm start
   ```

3. **Backend Configuration**:
   Update `extra.apiUrl` in `app.json` to your machine's local IP address (e.g., `http://192.168.1.XX:8000/api/v1`) when testing on a physical device or emulator.

## Project Structure
- `src/api`: Axios client and configuration.
- `src/components`: Reusable UI components (e.g., `PetCard`).
- `src/navigation`: Navigation tree and deep linking config.
- `src/screens`: Individual app screens.
- `src/services`: API interaction logic and native module services.
- `src/hooks`: Custom React hooks (e.g., `useFeatures` for tier-based logic).
