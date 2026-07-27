import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000,
});

export async function fetchHealth() {
  const { data } = await client.get('/health');
  return data;
}

export async function generateMeetingBrief(query) {
  const { data } = await client.post('/meeting-brief', { query });
  return data;
}

export default client;
