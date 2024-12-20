export async function blobToWav(blob: Blob): Promise<Blob> {
  return new Promise((resolve, reject) => {
    const fileReader = new FileReader()
    
    fileReader.onload = async (e) => {
      try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)()
        const arrayBuffer = e.target?.result as ArrayBuffer
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
        
        // Convert to WAV format
        const wavBuffer = audioBufferToWav(audioBuffer)
        const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' })
        
        resolve(wavBlob)
      } catch (error) {
        reject(error)
      }
    }
    
    fileReader.onerror = () => reject(new Error('Failed to read audio file'))
    fileReader.readAsArrayBuffer(blob)
  })
}

function audioBufferToWav(buffer: AudioBuffer): ArrayBuffer {
  const numChannels = 1 // Mono
  const sampleRate = 16000
  const format = 1 // PCM
  const bitDepth = 16

  const dataLength = buffer.length * numChannels * (bitDepth / 8)
  const bufferLength = 44 + dataLength
  const arrayBuffer = new ArrayBuffer(bufferLength)
  const view = new DataView(arrayBuffer)

  // WAV header
  writeString(view, 0, 'RIFF')
  view.setUint32(4, 36 + dataLength, true)
  writeString(view, 8, 'WAVE')
  writeString(view, 12, 'fmt ')
  view.setUint32(16, 16, true)
  view.setUint16(20, format, true)
  view.setUint16(22, numChannels, true)
  view.setUint32(24, sampleRate, true)
  view.setUint32(28, sampleRate * numChannels * (bitDepth / 8), true)
  view.setUint16(32, numChannels * (bitDepth / 8), true)
  view.setUint16(34, bitDepth, true)
  writeString(view, 36, 'data')
  view.setUint32(40, dataLength, true)

  // Write audio data
  const channelData = buffer.getChannelData(0)
  let offset = 44
  for (let i = 0; i < channelData.length; i++) {
    const sample = Math.max(-1, Math.min(1, channelData[i]))
    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true)
    offset += 2
  }

  return arrayBuffer
}

function writeString(view: DataView, offset: number, string: string) {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i))
  }
}