export async function processAudioForAPI(audioBlob: Blob): Promise<Blob> {
  // Проверяем входной блоб
  if (!(audioBlob instanceof Blob)) {
    throw new Error('Invalid audio data')
  }

  try {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const arrayBuffer = await audioBlob.arrayBuffer()
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
    
    // Конвертируем в моно если нужно
    const monoBuffer = audioBuffer.numberOfChannels === 1 ? 
      audioBuffer : 
      convertToMono(audioBuffer)
    
    // Конвертируем в WAV
    const wavBlob = await audioBufferToWav(monoBuffer)
    return new Blob([wavBlob], { type: 'audio/wav' })
  } catch (error) {
    console.error('Audio processing error:', error)
    throw new Error('Failed to process audio')
  }
}

function convertToMono(audioBuffer: AudioBuffer): AudioBuffer {
  const ctx = new (window.AudioContext || window.webkitAudioContext)()
  const monoBuffer = ctx.createBuffer(1, audioBuffer.length, audioBuffer.sampleRate)
  const monoData = monoBuffer.getChannelData(0)

  // Микшируем все каналы в один
  for (let i = 0; i < audioBuffer.length; i++) {
    let sum = 0
    for (let channel = 0; channel < audioBuffer.numberOfChannels; channel++) {
      sum += audioBuffer.getChannelData(channel)[i]
    }
    monoData[i] = sum / audioBuffer.numberOfChannels
  }

  return monoBuffer
}

async function audioBufferToWav(buffer: AudioBuffer): Promise<ArrayBuffer> {
  const length = buffer.length * 2 // 16-bit samples
  const arrayBuffer = new ArrayBuffer(44 + length)
  const view = new DataView(arrayBuffer)

  // WAV Header
  writeString(view, 0, 'RIFF')
  view.setUint32(4, 36 + length, true)
  writeString(view, 8, 'WAVE')
  writeString(view, 12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, 1, true) // PCM
  view.setUint16(22, 1, true) // Mono
  view.setUint32(24, buffer.sampleRate, true)
  view.setUint32(28, buffer.sampleRate * 2, true)
  view.setUint16(32, 2, true)
  view.setUint16(34, 16, true)
  writeString(view, 36, 'data')
  view.setUint32(40, length, true)

  // Convert and write audio data
  const samples = buffer.getChannelData(0)
  let offset = 44
  for (let i = 0; i < samples.length; i++) {
    const sample = Math.max(-1, Math.min(1, samples[i]))
    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true)
    offset += 2
  }

  return arrayBuffer
}

function writeString(view: DataView, offset: number, string: string): void {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i))
  }
}