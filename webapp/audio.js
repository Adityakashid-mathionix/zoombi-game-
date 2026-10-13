// Web Audio API Synthesizer for Zombi Apploclips
class SoundSystem {
    constructor() {
        this.ctx = null;
        this.volume = 0.8;
        this.enabled = true;
    }

    init() {
        if (!this.ctx) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            this.ctx = new AudioContext();
        }
        if (this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    createNoiseBuffer(duration = 0.5) {
        if (!this.ctx) return null;
        const bufferSize = this.ctx.sampleRate * duration;
        const buffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const data = buffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            data[i] = Math.random() * 2 - 1;
        }
        return buffer;
    }

    playPistol() {
        if (!this.enabled) return;
        this.init();
        const t = this.ctx.currentTime;

        // Punchy tone drop
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(650, t);
        osc.frequency.exponentialRampToValueAtTime(110, t + 0.12);

        gain.gain.setValueAtTime(0.6 * this.volume, t);
        gain.gain.exponentialRampToValueAtTime(0.01, t + 0.14);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t);
        osc.stop(t + 0.15);

        // Noise snap
        const noise = this.ctx.createBufferSource();
        noise.buffer = this.createNoiseBuffer(0.12);
        const nGain = this.ctx.createGain();
        nGain.gain.setValueAtTime(0.7 * this.volume, t);
        nGain.gain.exponentialRampToValueAtTime(0.01, t + 0.12);
        noise.connect(nGain);
        nGain.connect(this.ctx.destination);
        noise.start(t);
    }

    playShotgun() {
        if (!this.enabled) return;
        this.init();
        const t = this.ctx.currentTime;

        // Sub bass boom
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(220, t);
        osc.frequency.exponentialRampToValueAtTime(45, t + 0.35);

        gain.gain.setValueAtTime(0.85 * this.volume, t);
        gain.gain.exponentialRampToValueAtTime(0.01, t + 0.38);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t);
        osc.stop(t + 0.4);

        // Heavy blast noise
        const noise = this.ctx.createBufferSource();
        noise.buffer = this.createNoiseBuffer(0.35);
        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(1800, t);
        filter.frequency.exponentialRampToValueAtTime(400, t + 0.35);

        const nGain = this.ctx.createGain();
        nGain.gain.setValueAtTime(0.9 * this.volume, t);
        nGain.gain.exponentialRampToValueAtTime(0.01, t + 0.35);

        noise.connect(filter);
        filter.connect(nGain);
        nGain.connect(this.ctx.destination);
        noise.start(t);
    }

    playRifle() {
        if (!this.enabled) return;
        this.init();
        const t = this.ctx.currentTime;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'square';
        osc.frequency.setValueAtTime(450, t);
        osc.frequency.exponentialRampToValueAtTime(140, t + 0.08);

        gain.gain.setValueAtTime(0.45 * this.volume, t);
        gain.gain.exponentialRampToValueAtTime(0.01, t + 0.09);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t);
        osc.stop(t + 0.1);

        const noise = this.ctx.createBufferSource();
        noise.buffer = this.createNoiseBuffer(0.09);
        const nGain = this.ctx.createGain();
        nGain.gain.setValueAtTime(0.5 * this.volume, t);
        nGain.gain.exponentialRampToValueAtTime(0.01, t + 0.09);
        noise.connect(nGain);
        nGain.connect(this.ctx.destination);
        noise.start(t);
    }

    playGrenade() {
        if (!this.enabled) return;
        this.init();
        const t = this.ctx.currentTime;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(90, t);
        osc.frequency.exponentialRampToValueAtTime(30, t + 0.7);

        gain.gain.setValueAtTime(1.0 * this.volume, t);
        gain.gain.exponentialRampToValueAtTime(0.01, t + 0.75);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t);
        osc.stop(t + 0.8);

        const noise = this.ctx.createBufferSource();
        noise.buffer = this.createNoiseBuffer(0.7);
        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(900, t);
        filter.frequency.exponentialRampToValueAtTime(180, t + 0.7);

        const nGain = this.ctx.createGain();
        nGain.gain.setValueAtTime(0.95 * this.volume, t);
        nGain.gain.exponentialRampToValueAtTime(0.01, t + 0.7);

        noise.connect(filter);
        filter.connect(nGain);
        nGain.connect(this.ctx.destination);
        noise.start(t);
    }

    playZombieGroan() {
        if (!this.enabled) return;
        this.init();
        const t = this.ctx.currentTime;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(110, t);
        osc.frequency.linearRampToValueAtTime(145, t + 0.25);
        osc.frequency.exponentialRampToValueAtTime(75, t + 0.6);

        gain.gain.setValueAtTime(0.01, t);
        gain.gain.linearRampToValueAtTime(0.4 * this.volume, t + 0.15);
        gain.gain.exponentialRampToValueAtTime(0.01, t + 0.6);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t);
        osc.stop(t + 0.65);
    }

    playZombieAttack() {
        if (!this.enabled) return;
        this.init();
        const t = this.ctx.currentTime;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(260, t);
        osc.frequency.exponentialRampToValueAtTime(90, t + 0.2);

        gain.gain.setValueAtTime(0.55 * this.volume, t);
        gain.gain.exponentialRampToValueAtTime(0.01, t + 0.22);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t);
        osc.stop(t + 0.25);
    }

    playZombiePain() {
        if (!this.enabled) return;
        this.init();
        const t = this.ctx.currentTime;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(190, t);
        osc.frequency.exponentialRampToValueAtTime(80, t + 0.18);

        gain.gain.setValueAtTime(0.5 * this.volume, t);
        gain.gain.exponentialRampToValueAtTime(0.01, t + 0.2);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t);
        osc.stop(t + 0.22);
    }

    playZombieDeath() {
        if (!this.enabled) return;
        this.init();
        const t = this.ctx.currentTime;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(140, t);
        osc.frequency.exponentialRampToValueAtTime(35, t + 0.45);

        gain.gain.setValueAtTime(0.65 * this.volume, t);
        gain.gain.exponentialRampToValueAtTime(0.01, t + 0.5);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t);
        osc.stop(t + 0.55);
    }

    playPlayerPain() {
        if (!this.enabled) return;
        this.init();
        const t = this.ctx.currentTime;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(170, t);
        osc.frequency.exponentialRampToValueAtTime(65, t + 0.2);

        gain.gain.setValueAtTime(0.6 * this.volume, t);
        gain.gain.exponentialRampToValueAtTime(0.01, t + 0.22);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t);
        osc.stop(t + 0.25);
    }

    playPickup() {
        if (!this.enabled) return;
        this.init();
        const t = this.ctx.currentTime;

        // Bright 3-note arpeggio chord
        [523.25, 659.25, 783.99].forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(freq, t + idx * 0.06);

            gain.gain.setValueAtTime(0.01, t);
            gain.gain.setValueAtTime(0.4 * this.volume, t + idx * 0.06);
            gain.gain.exponentialRampToValueAtTime(0.01, t + idx * 0.06 + 0.16);

            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(t + idx * 0.06);
            osc.stop(t + idx * 0.06 + 0.18);
        });
    }

    playDoorUnlock() {
        if (!this.enabled) return;
        this.init();
        const t = this.ctx.currentTime;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(320, t);
        osc.frequency.setValueAtTime(480, t + 0.08);

        gain.gain.setValueAtTime(0.4 * this.volume, t);
        gain.gain.exponentialRampToValueAtTime(0.01, t + 0.2);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t);
        osc.stop(t + 0.22);
    }

    playRescue() {
        if (!this.enabled) return;
        this.init();
        const t = this.ctx.currentTime;

        [440, 554.37, 659.25, 880].forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(freq, t + idx * 0.09);

            gain.gain.setValueAtTime(0.45 * this.volume, t + idx * 0.09);
            gain.gain.exponentialRampToValueAtTime(0.01, t + idx * 0.09 + 0.28);

            osc.connect(gain);
            gain.connect(this.ctx.destination);
            osc.start(t + idx * 0.09);
            osc.stop(t + idx * 0.09 + 0.3);
        });
    }

    playStim() {
        if (!this.enabled) return;
        this.init();
        const t = this.ctx.currentTime;

        const noise = this.ctx.createBufferSource();
        noise.buffer = this.createNoiseBuffer(0.3);
        const filter = this.ctx.createBiquadFilter();
        filter.type = 'bandpass';
        filter.frequency.setValueAtTime(2200, t);
        filter.frequency.exponentialRampToValueAtTime(3800, t + 0.25);

        const gain = this.ctx.createGain();
        gain.gain.setValueAtTime(0.55 * this.volume, t);
        gain.gain.exponentialRampToValueAtTime(0.01, t + 0.28);

        noise.connect(filter);
        filter.connect(gain);
        gain.connect(this.ctx.destination);
        noise.start(t);
    }

    playReload() {
        if (!this.enabled) return;
        this.init();
        const t = this.ctx.currentTime;

        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(340, t);
        osc.frequency.exponentialRampToValueAtTime(180, t + 0.07);

        gain.gain.setValueAtTime(0.4 * this.volume, t);
        gain.gain.exponentialRampToValueAtTime(0.01, t + 0.09);

        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(t);
        osc.stop(t + 0.1);
    }
}

window.soundSystem = new SoundSystem();
