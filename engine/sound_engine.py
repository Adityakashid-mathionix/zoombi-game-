"""
Sound Engine: Procedural 8-bit / retro sound synthesizer and Pygame audio manager.
Generates and plays sound effects for weapons, zombies, survivors, doors, and ambience.
"""
import math
import os
import random
import struct
import wave
import pygame as pg
from engine.settings import SOUND_VOLUME


class ProceduralSoundGenerator:
    """Generates authentic 8-bit / retro sound effects as in-memory or on-disk WAV files."""
    SAMPLE_RATE = 22050

    @classmethod
    def generate_wav(cls, filepath, sample_func, duration=0.3):
        """Write synthesized audio samples to a 16-bit mono WAV file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        num_samples = int(cls.SAMPLE_RATE * duration)
        with wave.open(filepath, 'w') as wav:
            wav.setnchannels(1)  # Mono
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(cls.SAMPLE_RATE)
            frames = bytearray()
            for i in range(num_samples):
                t = i / cls.SAMPLE_RATE
                val = sample_func(t, duration, i)
                val = max(-1.0, min(1.0, val))
                sample_int = int(val * 32767)
                frames.extend(struct.pack('<h', sample_int))
            wav.writeframes(frames)

    @classmethod
    def build_all_sfx(cls, base_dir="assets/sound"):
        """Synthesize all needed retro sound effects if they don't already exist."""
        os.makedirs(base_dir, exist_ok=True)

        # 1. Pistol Gunshot (Punchy noise pop + pitch drop)
        def pistol_sfx(t, dur, i):
            env = math.exp(-18 * t)
            freq = 600 * math.exp(-25 * t) + 120
            tone = math.sin(2 * math.pi * freq * t)
            noise = (random.random() * 2 - 1) * math.exp(-35 * t)
            return (tone * 0.4 + noise * 0.6) * env

        # 2. Shotgun Blast (Deep heavy boom + noise burst)
        def shotgun_sfx(t, dur, i):
            env = math.exp(-8 * t)
            freq = 180 * math.exp(-12 * t) + 60
            tone = math.sin(2 * math.pi * freq * t)
            noise = (random.random() * 2 - 1) * math.exp(-14 * t)
            return (tone * 0.5 + noise * 0.8) * env

        # 3. Assault Rifle High-Velocity Crack & Gunpowder Thump
        def rifle_sfx(t, dur, i):
            # Heavy low-end gunpowder punch / thump
            punch_env = math.exp(-60 * t)
            punch_f = 240 * math.exp(-70 * t) + 75
            punch = math.sin(2 * math.pi * punch_f * t) * punch_env

            # Metallic bolt / chamber crack
            crack_env = math.exp(-28 * t)
            crack_f = 620 * math.exp(-35 * t) + 190
            crack_tone = (math.sin(2 * math.pi * crack_f * t) + 
                          0.4 * math.sin(4 * math.pi * crack_f * t)) * crack_env

            # High-pressure supersonic shockwave noise
            noise_env = math.exp(-32 * t)
            noise = (random.random() * 2 - 1) * noise_env

            # Mechanical receiver metallic resonance ring
            ring_env = math.exp(-20 * t)
            ring = math.sin(2 * math.pi * 1450.0 * t) * 0.18 * ring_env

            return punch * 0.65 + crack_tone * 0.45 + noise * 0.70 + ring

        # 4. Frag Grenade Explosion (Low thunderous rumble + blast wave)
        def explosion_sfx(t, dur, i):
            env = math.exp(-3.5 * t)
            freq = 80 * math.exp(-4 * t) + 35
            tone = math.sin(2 * math.pi * freq * t)
            noise = (random.random() * 2 - 1) * math.exp(-5 * t)
            return (tone * 0.6 + noise * 0.7) * env

        # 5. Zombie Groan (Creepy low frequency modulated growl)
        def zombie_groan_sfx(t, dur, i):
            env = math.sin(math.pi * t / dur)
            mod = math.sin(2 * math.pi * 7 * t)
            freq = 120 + mod * 35 - t * 30
            tone = math.sin(2 * math.pi * freq * t)
            noise = (random.random() * 2 - 1) * 0.25
            return (tone * 0.75 + noise) * env

        # 6. Zombie Attack / Bite
        def zombie_attack_sfx(t, dur, i):
            env = math.exp(-12 * t)
            freq = 240 * math.exp(-10 * t) + 80
            tone = math.sin(2 * math.pi * freq * t)
            noise = (random.random() * 2 - 1) * math.exp(-15 * t)
            return (tone * 0.5 + noise * 0.5) * env

        # 7. Zombie Death (Splatter & falling gargle)
        def zombie_death_sfx(t, dur, i):
            env = math.exp(-5 * t)
            freq = 190 * math.exp(-8 * t) + 40
            tone = math.sin(2 * math.pi * freq * t)
            noise = (random.random() * 2 - 1) * math.exp(-7 * t)
            return (tone * 0.5 + noise * 0.6) * env

        # 8. Item Pickup Chime (Bright ascending arpeggio)
        def pickup_sfx(t, dur, i):
            env = math.exp(-7 * t)
            step = int(t * 16)
            freqs = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
            f = freqs[min(step, len(freqs) - 1)]
            tone = math.sin(2 * math.pi * f * t) + 0.3 * math.sin(4 * math.pi * f * t)
            return tone * 0.7 * env

        # 9. Door Unlock / Keycard Scan (High tech electronic double beep)
        def door_unlock_sfx(t, dur, i):
            env = math.exp(-10 * (t % 0.15))
            f = 1200 if t < 0.15 else 1800
            tone = math.sin(2 * math.pi * f * t)
            return tone * 0.6 * env

        # 10. Survivor Rescue Fanfare (Triumphant 8-bit fanfare)
        def rescue_sfx(t, dur, i):
            env = math.exp(-3 * t)
            notes = [440.0, 554.37, 659.25, 880.0]  # A, C#, E, A
            step = int(t * 5)
            f = notes[min(step, len(notes) - 1)]
            tone = (math.sin(2 * math.pi * f * t) + 
                    0.4 * math.sin(4 * math.pi * f * t) + 
                    0.2 * math.sin(6 * math.pi * f * t))
            return tone * 0.65 * env

        # 11. Player Pain
        def pain_sfx(t, dur, i):
            env = math.exp(-14 * t)
            f = 220 * math.exp(-20 * t) + 70
            tone = math.sin(2 * math.pi * f * t)
            return tone * 0.8 * env

        # 12. Adrenaline Boost (Rising resonance whoosh)
        def adrenaline_sfx(t, dur, i):
            env = math.sin(math.pi * t / dur)
            f = 200 + 700 * (t / dur) ** 2
            tone = math.sin(2 * math.pi * f * t)
            return tone * 0.7 * env

        # 13. Weapon Reload Click
        def reload_sfx(t, dur, i):
            env = math.exp(-25 * (t % 0.2))
            f = 800 if t < 0.2 else 1200
            tone = math.sin(2 * math.pi * f * t) + (random.random() * 2 - 1) * 0.4
            return tone * 0.5 * env

        # 14. Survivor "Help!" Distress Call (Urgent vocal alarm shout)
        def survivor_help_sfx(t, dur, i):
            env = math.exp(-4.5 * (t % 0.38))
            f = 460 + 380 * math.sin(2 * math.pi * 3.5 * t)
            tone = math.sin(2 * math.pi * f * t) + 0.35 * math.sin(3 * math.pi * f * t)
            noise = (random.random() * 2 - 1) * 0.12
            return (tone * 0.85 + noise) * env

        sfx_catalog = [
            ("pistol.wav", pistol_sfx, 0.25),
            ("shotgun.wav", shotgun_sfx, 0.55),
            ("rifle.wav", rifle_sfx, 0.20),
            ("grenade.wav", explosion_sfx, 0.90),
            ("zombie_groan.wav", zombie_groan_sfx, 0.80),
            ("zombie_attack.wav", zombie_attack_sfx, 0.35),
            ("zombie_death.wav", zombie_death_sfx, 0.60),
            ("pickup.wav", pickup_sfx, 0.35),
            ("door_unlock.wav", door_unlock_sfx, 0.35),
            ("rescue.wav", rescue_sfx, 0.85),
            ("pain.wav", pain_sfx, 0.28),
            ("adrenaline.wav", adrenaline_sfx, 0.60),
            ("reload.wav", reload_sfx, 0.45),
            ("survivor_help.wav", survivor_help_sfx, 0.75),
        ]

        for fname, func, dur in sfx_catalog:
            path = os.path.join(base_dir, fname)
            if not os.path.exists(path):
                try:
                    cls.generate_wav(path, func, dur)
                except Exception as e:
                    print(f"Warning: Failed to synthesize {fname}: {e}")


class SoundManager:
    """Manages playing and caching Pygame sound effects & background audio."""

    def __init__(self):
        self.sounds = {}
        self.enabled = True
        self.volume = SOUND_VOLUME

        # Ensure mixer is initialized with multi-profile fallback (critical on Android)
        if not pg.mixer.get_init():
            initialized = False
            for freq, buf in [(44100, 1024), (44100, 2048), (22050, 1024), (22050, 2048)]:
                try:
                    pg.mixer.init(frequency=freq, size=-16, channels=2, buffer=buf)
                    pg.mixer.set_num_channels(16)
                    initialized = True
                    break
                except Exception as e:
                    print(f"Pygame mixer init profile ({freq}, {buf}) failed: {e}")
            if not initialized:
                print("Warning: Audio mixer unavailable. Running in silent mode.")
                self.enabled = False
                return

        # Synthesize sound effects if not already present
        ProceduralSoundGenerator.build_all_sfx("assets/sound")

        # Load sounds into memory
        self.load_all_sounds()

    def load_all_sounds(self):
        sound_files = {
            "pistol": "assets/sound/pistol.wav",
            "shotgun": "assets/sound/shotgun.wav",
            "rifle": "assets/sound/rifle.wav",
            "grenade": "assets/sound/grenade.wav",
            "zombie_groan": "assets/sound/zombie_groan.wav",
            "zombie_attack": "assets/sound/zombie_attack.wav",
            "zombie_death": "assets/sound/zombie_death.wav",
            "pickup": "assets/sound/pickup.wav",
            "door_unlock": "assets/sound/door_unlock.wav",
            "rescue": "assets/sound/rescue.wav",
            "pain": "assets/sound/pain.wav",
            "adrenaline": "assets/sound/adrenaline.wav",
            "reload": "assets/sound/reload.wav",
            "survivor_help": "assets/sound/survivor_help.wav",
            "engineer_help": "assets/sound/engineer_help.wav",
            "engineer_rescued": "assets/sound/engineer_rescued.wav",
            "zombie_king_shout": "assets/sound/zombie_king_shout.wav",
            "zombie_king_laugh": "assets/sound/zombie_king_laugh.wav",
            "zombie_king_attack": "assets/sound/zombie_king_attack.wav",
            "zombie_king_death": "assets/sound/zombie_king_death.wav",
        }

        # Also check reference_doom sounds as alternatives
        alt_sounds = {
            "shotgun_alt": "reference_doom/resources/sound/shotgun.wav",
            "zombie_attack_alt": "reference_doom/resources/sound/npc_attack.wav",
            "zombie_death_alt": "reference_doom/resources/sound/npc_death.wav",
            "zombie_pain_alt": "reference_doom/resources/sound/npc_pain.wav",
            "player_pain_alt": "reference_doom/resources/sound/player_pain.wav",
        }

        for key, path in sound_files.items():
            if os.path.exists(path):
                try:
                    snd = pg.sound.Sound(path) if hasattr(pg, 'sound') and hasattr(pg.sound, 'Sound') else pg.mixer.Sound(path)
                    snd.set_volume(self.volume)
                    self.sounds[key] = snd
                except Exception as e:
                    print(f"Could not load {path}: {e}")

        for key, path in alt_sounds.items():
            if os.path.exists(path):
                try:
                    snd = pg.mixer.Sound(path)
                    snd.set_volume(self.volume)
                    self.sounds[key] = snd
                except Exception:
                    pass

    def play(self, name):
        if not self.enabled or not pg.mixer.get_init():
            return
        snd = self.sounds.get(name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def set_volume(self, vol):
        self.volume = max(0.0, min(1.0, vol))
        for snd in self.sounds.values():
            try:
                snd.set_volume(self.volume)
            except Exception:
                pass

    def play_pistol(self):
        self.play("pistol")

    def play_shotgun(self):
        if "shotgun_alt" in self.sounds:
            self.play("shotgun_alt")
        else:
            self.play("shotgun")

    def play_rifle(self):
        self.play("rifle")

    def play_grenade(self):
        self.play("grenade")

    def play_zombie_groan(self):
        self.play("zombie_groan")

    def play_zombie_attack(self):
        if "zombie_attack_alt" in self.sounds:
            self.play("zombie_attack_alt")
        else:
            self.play("zombie_attack")

    def play_zombie_pain(self):
        if "zombie_pain_alt" in self.sounds:
            self.play("zombie_pain_alt")
        else:
            self.play("pain")

    def play_zombie_death(self):
        if "zombie_death_alt" in self.sounds:
            self.play("zombie_death_alt")
        else:
            self.play("zombie_death")

    def play_player_pain(self):
        if "player_pain_alt" in self.sounds:
            self.play("player_pain_alt")
        else:
            self.play("pain")

    def play_pickup(self):
        self.play("pickup")

    def play_door_unlock(self):
        self.play("door_unlock")

    def play_rescue(self):
        self.play("rescue")

    def play_adrenaline(self):
        self.play("adrenaline")

    def play_reload(self):
        self.play("reload")

    def stop_voice(self):
        """Stop any playing survivor/engineer voices to prevent overlapping."""
        for key in ["survivor_help", "engineer_help", "engineer_rescued"]:
            snd = self.sounds.get(key)
            if snd:
                try:
                    snd.stop()
                except Exception:
                    pass

    def play_survivor_help(self):
        if "engineer_help" in self.sounds:
            self.play("engineer_help")
        elif "survivor_help" in self.sounds:
            self.play("survivor_help")
        else:
            self.play("rescue")

    def play_engineer_help(self):
        if "engineer_help" in self.sounds:
            self.play("engineer_help")
        elif "survivor_help" in self.sounds:
            self.play("survivor_help")
        else:
            self.play("rescue")

    def play_engineer_rescued(self):
        self.stop_voice()
        if "engineer_rescued" in self.sounds:
            self.play("engineer_rescued")
        else:
            self.play("rescue")

    def play_zombie_king_shout(self):
        self.play("zombie_king_shout")

    def play_zombie_king_laugh(self):
        self.play("zombie_king_laugh")

    def play_zombie_king_attack(self):
        self.play("zombie_king_attack")

    def play_zombie_king_death(self):
        self.play("zombie_king_death")

