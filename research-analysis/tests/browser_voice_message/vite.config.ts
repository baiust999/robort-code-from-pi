import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({ plugins: [react()], server: { port: 18091, strictPort: true, fs: { allow: ['/'] } } });
