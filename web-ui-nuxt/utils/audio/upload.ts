import { processAudioForAPI } from './processor'

export async function prepareAudioForUpload(audioBlob: Blob): Promise<FormData> {
  try {
    // Убедимся что у нас WAV
    const processedAudio = await processAudioForAPI(audioBlob)
    
    const formData = new FormData()
    // Важно: имя файла должно заканчиваться на .wav
    formData.append('audio', processedAudio, 'recording.wav')
    
    return formData
  } catch (error) {
    console.error('Error preparing audio:', error)
    throw error
  }
}