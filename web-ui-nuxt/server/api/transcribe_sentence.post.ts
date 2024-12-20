import { defineEventHandler, readMultipartFormData } from 'h3'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  
  try {
    const form = await readMultipartFormData(event)
    if (!form) {
      throw new Error('No form data received')
    }

    const audioFile = form.find(f => f.name === 'audio')
    const sentenceId = form.find(f => f.name === 'sentence_id')?.data.toString()

    if (!audioFile || !sentenceId) {
      throw new Error('Missing required fields')
    }

    // Forward the request to the backend API
    const formData = new FormData()
    formData.append('audio', new Blob([audioFile.data], { type: 'audio/wav' }), 'recording.wav')
    formData.append('sentence_id', sentenceId)

    const response = await fetch(`${config.backendApiUrl}/api/transcribe_sentence`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`)
    }

    return response.json()
  } catch (error) {
    console.error('Transcription error:', error)
    throw createError({
      statusCode: 500,
      message: error instanceof Error ? error.message : 'Failed to process audio'
    })
  }
})