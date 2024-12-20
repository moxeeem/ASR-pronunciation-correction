<template>
  <div class="flex min-h-screen items-center justify-center">
    <div class="w-full max-w-md space-y-8 p-6">
      <div class="text-center">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">English Learning App</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-300">Improve your English skills with interactive exercises</p>
      </div>
      <div class="mt-8 space-y-4">
        <NuxtLink
          to="/auth/login"
          class="flex w-full justify-center rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          Get Started
        </NuxtLink>
      </div>
    </div>
  </div>
</template>