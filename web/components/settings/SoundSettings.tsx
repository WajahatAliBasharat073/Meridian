"use client";

import { useEffect, useState } from "react";
import { Bell, Volume2, Play } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  getSoundSettings,
  playSound,
  saveSoundSettings,
  type SoundSettings,
  type SoundType,
} from "@/lib/soundEngine";
import {
  getNotificationSettings,
  saveNotificationSettings,
  type NotificationSettings,
} from "@/lib/notifications";

export function SoundSettingsSection() {
  const [sound, setSound] = useState<SoundSettings>(getSoundSettings());
  const [notif, setNotif] = useState<NotificationSettings>(getNotificationSettings());

  useEffect(() => {
    setSound(getSoundSettings());
    setNotif(getNotificationSettings());
  }, []);

  const updateSound = (partial: Partial<SoundSettings>) => {
    const updated = saveSoundSettings(partial);
    setSound(updated);
  };

  const updateNotif = (partial: Partial<NotificationSettings>) => {
    const updated = saveNotificationSettings(partial);
    setNotif(updated);
  };

  return (
    <Card className="p-5 space-y-5">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Volume2 size={18} className="text-accent-strong" />
          <h3 className="text-sm font-semibold text-text">Notification Sounds & Chimes</h3>
        </div>
        <p className="text-xs text-text-muted">
          Crystal-clear synthesizer chimes generated via Web Audio API. Respects browser autoplay
          restrictions.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 gap-4 pt-2 border-t border-border">
        {/* Master Sound Switch */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-text">Sound Effects</p>
            <p className="text-[11px] text-text-faint">Play chimes on activity transitions</p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={sound.enabled}
            onClick={() => updateSound({ enabled: !sound.enabled })}
            className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${
              sound.enabled ? "bg-accent-strong" : "bg-surface-2 border border-border"
            }`}
          >
            <div
              className={`bg-surface w-4 h-4 rounded-full shadow-md transform transition-transform ${
                sound.enabled ? "translate-x-5 bg-bg" : "translate-x-0"
              }`}
            />
          </button>
        </div>

        {/* Master Notifications Switch */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-text">In-App Alerts</p>
            <p className="text-[11px] text-text-faint">Show toasts for upcoming blocks & routines</p>
          </div>
          <button
            type="button"
            role="switch"
            aria-checked={notif.enabled}
            onClick={() => updateNotif({ enabled: !notif.enabled })}
            className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors ${
              notif.enabled ? "bg-accent-strong" : "bg-surface-2 border border-border"
            }`}
          >
            <div
              className={`bg-surface w-4 h-4 rounded-full shadow-md transform transition-transform ${
                notif.enabled ? "translate-x-5 bg-bg" : "translate-x-0"
              }`}
            />
          </button>
        </div>
      </div>

      {/* Sound Selection & Volume */}
      {sound.enabled && (
        <div className="space-y-3 pt-3 border-t border-border">
          <div className="grid sm:grid-cols-2 gap-4 items-center">
            <div>
              <label className="text-xs font-medium text-text block mb-1.5">Chime Tone</label>
              <select
                value={sound.selectedSound}
                onChange={(e) => updateSound({ selectedSound: e.target.value as SoundType })}
                className="w-full h-9 rounded-lg border border-border bg-surface-2 px-3 text-xs text-text"
              >
                <option value="gentle">Gentle Marimba</option>
                <option value="reminder">Crystal Reminder</option>
                <option value="focus">Binaural Focus Bell</option>
                <option value="completion">Major Chord Completion</option>
              </select>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-medium text-text">Volume</label>
                <span className="text-xs text-text-faint tabular-nums">
                  {Math.round(sound.volume * 100)}%
                </span>
              </div>
              <input
                type="range"
                min="0.1"
                max="1"
                step="0.05"
                value={sound.volume}
                onChange={(e) => updateSound({ volume: parseFloat(e.target.value) })}
                className="w-full"
              />
            </div>
          </div>

          <div className="flex justify-end pt-1">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => playSound(sound.selectedSound, sound.volume)}
              className="gap-1.5"
            >
              <Play size={13} />
              Test Sound
            </Button>
          </div>
        </div>
      )}

      {/* Alert Categories */}
      {notif.enabled && (
        <div className="pt-3 border-t border-border space-y-2">
          <p className="text-xs font-medium uppercase tracking-wide text-text-faint mb-2">
            Smart Alert Categories
          </p>
          <div className="grid sm:grid-cols-2 gap-2 text-xs">
            <label className="flex items-center gap-2 cursor-pointer p-2 rounded-lg bg-surface-2/60 hover:bg-surface-2">
              <input
                type="checkbox"
                checked={notif.activityReminders}
                onChange={(e) => updateNotif({ activityReminders: e.target.checked })}
                className="rounded border-border"
              />
              <span className="text-text">Activity start (10 min before & start)</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer p-2 rounded-lg bg-surface-2/60 hover:bg-surface-2">
              <input
                type="checkbox"
                checked={notif.hydrationAlerts}
                onChange={(e) => updateNotif({ hydrationAlerts: e.target.checked })}
                className="rounded border-border"
              />
              <span className="text-text">Hydration (water prompts)</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer p-2 rounded-lg bg-surface-2/60 hover:bg-surface-2">
              <input
                type="checkbox"
                checked={notif.mealAlerts}
                onChange={(e) => updateNotif({ mealAlerts: e.target.checked })}
                className="rounded border-border"
              />
              <span className="text-text">Meal windows (lunch & dinner)</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer p-2 rounded-lg bg-surface-2/60 hover:bg-surface-2">
              <input
                type="checkbox"
                checked={notif.breakReminders}
                onChange={(e) => updateNotif({ breakReminders: e.target.checked })}
                className="rounded border-border"
              />
              <span className="text-text">Focus break reminders</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer p-2 rounded-lg bg-surface-2/60 hover:bg-surface-2">
              <input
                type="checkbox"
                checked={notif.windDownReminder}
                onChange={(e) => updateNotif({ windDownReminder: e.target.checked })}
                className="rounded border-border"
              />
              <span className="text-text">Evening wind-down</span>
            </label>
          </div>
        </div>
      )}
    </Card>
  );
}
