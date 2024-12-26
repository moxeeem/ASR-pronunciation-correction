import { ref } from 'vue';
import type { TranscriptionResponse } from '~/types/api';

export function useApi() {
  const config = useRuntimeConfig();
  const error = ref<string | null>(null);
  const isLoading = ref(false);

  async function transcribeSentence(
    audio: Blob,
    sentenceId: string
  ): Promise<TranscriptionResponse> {
    error.value = null;
    isLoading.value = true;

    try {
      const formData = new FormData();
      formData.append('audio', audio, 'recording.wav');
      formData.append('sentence_id', sentenceId);

      const response = await fetch(
        `${config.public.backendApiUrl}/api/transcribe_sentence`,
        {
          method: 'POST',
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.message || `HTTP error! status: ${response.status}`
        );
      }

      const data = await response.json();

      // Validate response structure
      if (!data?.result?.accuracy) {
        throw new Error('Invalid response format from server');
      }

      return data;
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : 'An unknown error occurred';
      throw e;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    transcribeSentence,
    error,
    isLoading,
  };
}
