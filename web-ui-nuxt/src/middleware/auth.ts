export default defineNuxtRouteMiddleware((to) => {
  const user = useSupabaseUser()

  if (!user.value && !['/', '/auth/login', '/auth/register'].includes(to.path)) {
    return navigateTo('/auth/login')
  }
})