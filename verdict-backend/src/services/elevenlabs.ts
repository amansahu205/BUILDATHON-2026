/**
 * ElevenLabs TTS/STT (ref: IMPLEMENTATION_PLAN Step 2.4, TECH_STACK §4)
 */
import { ElevenLabsClient } from 'elevenlabs';

export const eleven = new ElevenLabsClient({
  apiKey: process.env.ELEVENLABS_API_KEY!,
});

export const VOICES = {
  INTERROGATOR: process.env.ELEVENLABS_INTERROGATOR_VOICE_ID ?? '',
  COACH: process.env.ELEVENLABS_COACH_VOICE_ID ?? '',
};

export async function textToSpeech(text: string, voiceId: string) {
  return eleven.textToSpeech.convert(voiceId || VOICES.INTERROGATOR, {
    text,
    model_id: 'eleven_turbo_v2_5',
  });
}

export async function speechToText(audioBuffer: Buffer): Promise<string> {
  const blob = new Blob([audioBuffer], { type: 'audio/mpeg' });
  const result = await eleven.speechToText.convert({
    file: blob as Blob,
    model_id: 'scribe_v1',
  });
  const chunk = result as { text?: string };
  return chunk?.text ?? '';
}
