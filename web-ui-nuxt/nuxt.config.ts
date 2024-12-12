// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: false },
  srcDir: "src/",

  routeRules: {
    '/api/**': {
      proxy: process.env.NODE_ENV === "development" ? "http://localhost:8000/api/**" : "/api/**",
    },
    '/docs': {
      proxy: "http://localhost:8000/docs",
    },
    '/openapi.json': {
      proxy: "http://localhost:8000/openapi.json",
    }
  },

  runtimeConfig: {
    public: {
      baseUrl: process.env.BASE_URL || 'http://localhost:3000',
      supabaseUrl: process.env.SUPABASE_URL,
      supabaseKey: process.env.SUPABASE_KEY
    },
  },

  nitro: {
    vercel: {
      config: {
        routes: [{
          "src": "/api/(.*)",
          "dest": "api/index.py"
        }]
      }
    }
  },

  modules: [
    "@nuxtjs/supabase",
    // "@nuxt/ui",
    "@nuxtjs/tailwindcss"
  ],
  supabase: {
    redirectOptions: {
      login: '/auth/login',
      callback: '/confirm',
      exclude: ['/', '/auth/register'],
    },
    url: process.env.SUPABASE_URL,
    key: process.env.SUPABASE_KEY,
  },
  compatibilityDate: '2024-04-03',
})