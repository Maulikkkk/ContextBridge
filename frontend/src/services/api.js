import axios from 'axios';
import { API_BASE_URL } from '../config/api';

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
