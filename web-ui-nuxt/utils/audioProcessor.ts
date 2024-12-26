export async function processAudioForAPI(audioBlob: Blob): Promise<Blob> {
  const audioContext = new (window.AudioContext || window.webkitAudioContext)({
    sampleRate: 16000 // Force 16kHz sample rate
  });
  
  const arrayBuffer = await audioBlob.arrayBuffer();
  const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
  
  // Convert to mono if needed
  const monoBuffer = convertToMono(audioBuffer);
  
  // Convert to 16-bit PCM WAV
  const wavBuffer = audioBufferToWav(monoBuffer);
  return new Blob([wavBuffer], { type: 'audio/wav' });
}

function convertToMono(audioBuffer: AudioBuffer): AudioBuffer {
  const channels = audioBuffer.numberOfChannels;
  if (channels === 1) return audioBuffer;

  const monoBuffer = new AudioBuffer({
    length: audioBuffer.length,
    numberOfChannels: 1,
    sampleRate: audioBuffer.sampleRate
  });

  const monoData = monoBuffer.getChannelData(0);
  for (let i = 0; i < audioBuffer.length; i++) {
    let sum = 0;
    for (let channel = 0; channel < channels; channel++) {
      sum += audioBuffer.getChannelData(channel)[i];
    }
    monoData[i] = sum / channels;
  }

  return monoBuffer;
}

function audioBufferToWav(buffer: AudioBuffer): ArrayBuffer {
  const length = buffer.length * 2; // 16-bit samples
  const arrayBuffer = new ArrayBuffer(44 + length);
  const view = new DataView(arrayBuffer);
  const channels = 1; // Mono
  const sampleRate = buffer.sampleRate;

  // Write WAV header
  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + length, true);
  writeString(view, 8, 'WAVE');
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); // PCM format
  view.setUint16(22, channels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * channels * 2, true); // Byte rate
  view.setUint16(32, channels * 2, true); // Block align
  view.setUint16(34, 16, true); // Bits per sample
  writeString(view, 36, 'data');
  view.setUint32(40, length, true);

  // Write audio data
  const samples = buffer.getChannelData(0);
  let offset = 44;
  for (let i = 0; i < samples.length; i++) {
    const sample = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
    offset += 2;
  }

  return arrayBuffer;
}

function writeString(view: DataView, offset: number, string: string): void {
  for (let i = 0; i < string.length; i++) {
    view.setUint8(offset + i, string.charCodeAt(i));
  }
}