/**
 * Meridian Web Audio Sound Engine
 * Uses pure Web Audio API synthesis — zero external mp3/wav files required,
 * completely immune to 404s, network latency, or browser asset caching issues.
 * Respects browser autoplay policies and user settings.
 */

export type SoundType = "gentle" | "reminder" | "focus" | "completion";

export interface SoundSettings {
  enabled: boolean;
  volume: number; // 0.0 to 1.0
  selectedSound: SoundType;
}

const STORAGE_KEY = "meridian_sound_settings";

const DEFAULT_SETTINGS: SoundSettings = {
  enabled: true,
  volume: 0.6,
  selectedSound: "gentle",
};

let audioCtx: AudioContext | null = null;

function getAudioContext(): AudioContext | null {
  if (typeof window === "undefined") return null;
  if (!audioCtx) {
    const AudioContextClass =
      window.AudioContext ||
      (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    if (AudioContextClass) {
      audioCtx = new AudioContextClass();
    }
  }
  if (audioCtx && audioCtx.state === "suspended") {
    audioCtx.resume().catch(() => {});
  }
  return audioCtx;
}

export function getSoundSettings(): SoundSettings {
  if (typeof window === "undefined") return DEFAULT_SETTINGS;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT_SETTINGS;
    return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) };
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export function saveSoundSettings(settings: Partial<SoundSettings>): SoundSettings {
  const current = getSoundSettings();
  const updated = { ...current, ...settings };
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch {}
  return updated;
}

/**
 * Plays a synthesized chime using Web Audio API
 */
export function playSound(type?: SoundType, overrideVolume?: number): void {
  const settings = getSoundSettings();
  if (!settings.enabled && overrideVolume === undefined) return;

  const ctx = getAudioContext();
  if (!ctx) return;

  const soundToPlay = type ?? settings.selectedSound;
  const masterVolume = Math.min(1, Math.max(0, overrideVolume ?? settings.volume));

  const now = ctx.currentTime;
  const masterGain = ctx.createGain();
  masterGain.gain.setValueAtTime(masterVolume, now);
  masterGain.connect(ctx.destination);

  switch (soundToPlay) {
    case "gentle": {
      // Warm marimba-like two-tone chime (F5 -> A5)
      playTone(ctx, masterGain, 698.46, now, 0.45, "sine", 0.3);
      playTone(ctx, masterGain, 880.0, now + 0.12, 0.6, "sine", 0.25);
      break;
    }
    case "reminder": {
      // Crisp crystal notification chime (C6 -> G6)
      playTone(ctx, masterGain, 1046.5, now, 0.35, "triangle", 0.35);
      playTone(ctx, masterGain, 1567.98, now + 0.08, 0.55, "sine", 0.3);
      break;
    }
    case "focus": {
      // Soft ambient meditation bell (E5 harmonic)
      playTone(ctx, masterGain, 659.25, now, 0.9, "sine", 0.4);
      playTone(ctx, masterGain, 1318.5, now + 0.02, 0.7, "sine", 0.15);
      break;
    }
    case "completion": {
      // Uplifting three-note resonant major chord (C5 -> E5 -> G5)
      playTone(ctx, masterGain, 523.25, now, 0.5, "sine", 0.25);
      playTone(ctx, masterGain, 659.25, now + 0.1, 0.55, "sine", 0.25);
      playTone(ctx, masterGain, 783.99, now + 0.2, 0.8, "sine", 0.3);
      break;
    }
  }
}

function playTone(
  ctx: AudioContext,
  destination: AudioNode,
  frequency: number,
  startTime: number,
  duration: number,
  type: OscillatorType,
  gainLevel: number
) {
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();

  osc.type = type;
  osc.frequency.setValueAtTime(frequency, startTime);

  // Smooth attack and exponential decay to prevent audio clicking
  gain.gain.setValueAtTime(0.0001, startTime);
  gain.gain.exponentialRampToValueAtTime(gainLevel, startTime + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

  osc.connect(gain);
  gain.connect(destination);

  osc.start(startTime);
  osc.stop(startTime + duration + 0.05);
}
