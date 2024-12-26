export default defineNuxtRouteMiddleware((to) => {
  const user = useSupabaseUser()

  // Allow callback route for OAuth
  if (to.path === '/callback') {
    return
  }

  if (!user.value && !['/', '/auth/login', '/auth/register'].includes(to.path)) {
    return navigateTo('/auth/login')
  }
})