/**
 * API base URL — must be set via VITE_API_URL at build time (Vercel) or in .env (local).
 * Vite inlines this value during `vite build`; runtime env vars on Vercel do not apply.
 */
export const API_BASE_URL = import.meta.env.VITE_API_URL?.replace(/\/$/, '') ?? '';
