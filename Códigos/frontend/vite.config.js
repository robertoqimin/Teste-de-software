import { defineConfig } from 'vite';

export default defineConfig({
    base: '/static/dist/',
    build: {
        outDir: '../app/static/dist',
        emptyOutDir: true,
        manifest: true,
        rollupOptions: { input: 'src/main.js' },
    },
});
