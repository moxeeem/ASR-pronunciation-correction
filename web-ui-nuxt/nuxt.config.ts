// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
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
    "@nuxt/ui",
    "@nuxtjs/tailwindcss"
  ],
  supabase: {
    redirectOptions: {
      login: '/login',
      callback: '/confirm',
      exclude: ['/register']
    },
  },
})