<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <header v-if="user" class="bg-white shadow dark:bg-gray-800">
      <nav class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex h-16 justify-between items-center">
          <NuxtLink to="/dashboard" class="text-xl font-bold text-gray-900 dark:text-white">
            English Learning
          </NuxtLink>
          <div class="flex items-center space-x-4">
            <button
              @click="toggleTheme"
              class="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
            >
              <svg
                v-if="isDark"
                class="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                />
              </svg>
              <svg
                v-else
                class="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
                />
              </svg>
            </button>
            <button
              @click="handleSignOut"
              class="rounded-md bg-gray-200 dark:bg-gray-700 px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600"
            >
              Sign Out
            </button>
          </div>
        </div>
      </nav>
    </header>
    <main>
      <slot />
    </main>
  </div>
</template>

<script setup>
const user = useSupabaseUser()
const client = useSupabaseClient()
const router = useRouter()

const isDark = useDark()
const toggleTheme = useToggle(isDark)

const handleSignOut = async () => {
  await client.auth.signOut()
  router.push('/auth/login')
}
</script>