<template>
  <div class="flex min-h-screen items-center justify-center">
    <div class="text-center">
      <p class="text-gray-600 dark:text-gray-400">Completing sign in...</p>
    </div>
  </div>
</template>

<script setup>
const router = useRouter()

onMounted(() => {
  // После успешной аутентификации перенаправляем на dashboard
  router.push('/dashboard')
})
</script>