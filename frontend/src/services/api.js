import axios from 'axios';
import { API_BASE_URL } from '../config/api';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000,
});

export function getApiErrorMessage(err, fallback) {
  if (err?.response?.data?.error) return err.response.data.error;
  if (err?.response?.data?.detail) {
    return typeof err.response.data.detail === 'string'
      ? err.response.data.detail
      : JSON.stringify(err.response.data.detail);
  }
  if (err?.response?.status === 502) {
    return 'Backend crashed (502). The server may be out of memory — redeploy after the latest fix.';
  }
  if (err?.code === 'ERR_NETWORK') {
    return 'Cannot reach the backend. Check VITE_API_URL and CORS settings.';
  }
  return fallback;
}

export async function fetchHealth() {
  const { data } = await client.get('/health');
  return data;
}

export async function generateMeetingBrief(query) {
  const { data } = await client.post('/meeting-brief', { query });
  return data;
}

export default client;
