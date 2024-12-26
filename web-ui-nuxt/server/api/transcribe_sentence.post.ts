import { defineEventHandler, readMultipartFormData, H3Event } from 'h3'

async function validateFormData(event: H3Event) {
  const form = await readMultipartFormData(event)
  if (!form) {
    throw createError({
      statusCode: 400,
      message: 'No form data received'
    })
  }

  const audioFile = form.find(f => f.name === 'audio')
  const sentenceId = form.find(f => f.name === 'sentence_id')?.data.toString()

  if (!audioFile || !sentenceId) {
    throw createError({
      statusCode: 400,
      message: 'Missing required fields: audio file or sentence ID'
    })
  }

  return { audioFile, sentenceId }
}

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  
  try {
    const { audioFile, sentenceId } = await validateFormData(event)

    // Create a new FormData instance for the backend request
    const formData = new FormData()
    formData.append('audio', new Blob([audioFile.data], { type: 'audio/wav' }), 'recording.wav')
    formData.append('sentence_id', sentenceId)

    const response = await fetch(`${config.backendApiUrl}/api/transcribe_sentence`, {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json'
      }
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ message: `Backend API error: ${response.status}` }))
      throw createError({
        statusCode: response.status,
        message: errorData.message || 'Failed to process audio'
      })
    }

    const data = await response.json()
    
    if (!data?.result) {
      throw createError({
        statusCode: 500,
        message: 'Invalid response format from backend'
      })
    }

    return data
  } catch (error) {
    console.error('Transcription error:', error)
    
    if (error.statusCode) {
      throw error // Re-throw HTTP errors
    }
    
    throw createError({
      statusCode: 500,
      message: error instanceof Error ? error.message : 'Failed to process audio'
    })
  }
})