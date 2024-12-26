// Browser support detection utilities
export function checkAudioSupport(): boolean {
  return !!(
    typeof window !== 'undefined' &&
    navigator.mediaDevices?.getUserMedia &&
    window.AudioContext || window.webkitAudioContext
  )
}