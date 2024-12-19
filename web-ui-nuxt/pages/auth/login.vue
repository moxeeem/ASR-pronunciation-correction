<script setup>
const supabase = useSupabaseClient()
const router = useRouter()

const form = ref({
  email: '',
  password: ''
})

const loading = ref(false)
const error = ref(null)

async function signInWithGithub() {
  try {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'github'
    })
    if (error) throw error
  } catch (err) {
    error.value = err.message
  }
}

async function signInWithEmail() {
  try {
    loading.value = true
    error.value = null
    
    const { error: signInError } = await supabase.auth.signInWithPassword({
      email: form.value.email,
      password: form.value.password
    })
    
    if (signInError) throw signInError
    
    router.push('/dashboard')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
    <div class="w-full max-w-md space-y-8 rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
      <div class="text-center">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Sign in to your account</h2>
      </div>

      <form @submit.prevent="signInWithEmail" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">Email</label>
          <input
            v-model="form.email"
            type="email"
            required
            class="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-900 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-200">Password</label>
          <input
            v-model="form.password"
            type="password"
            required
            class="mt-1 block w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-gray-900 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
          />
        </div>

        <div v-if="error" class="text-red-600 dark:text-red-400 text-sm">{{ error }}</div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full rounded-md bg-blue-600 py-2 text-white hover:bg-blue-700 disabled:opacity-50 dark:bg-blue-500 dark:hover:bg-blue-600"
        >
          {{ loading ? 'Signing in...' : 'Sign in' }}
        </button>
      </form>

      <div class="relative">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-gray-300 dark:border-gray-600"></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="bg-white px-2 text-gray-500 dark:bg-gray-800 dark:text-gray-400">Or continue with</span>
        </div>
      </div>

      <button
        @click="signInWithGithub"
        class="flex w-full items-center justify-center gap-2 rounded-md border border-gray-300 bg-white py-2 text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
      >
        <span>GitHub</span>
      </button>

      <div class="text-center">
        <NuxtLink
          to="/auth/register"
          class="text-sm text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
        >
          Don't have an account? Sign up
        </NuxtLink>
      </div>
    </div>
  </div>
</template>