export const useDark = () => useState('dark', () => false)
export const useToggle = (isDark: Ref<boolean>) => {
  return () => {
    isDark.value = !isDark.value
    updateTheme(isDark.value)
  }
}

const updateTheme = (isDark: boolean) => {
  if (isDark) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}