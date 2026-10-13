// ==============================================================================
// Zombi Apploclips - High-Performance WebApp Engine
// 2.5D Retro Raycaster with 8 Campaign Sectors, Procedural Generation,
// Web Audio Synthesizer, Dual Touch Controls, and Armory Loadout.
// ==============================================================================

const WIDTH = 1280;
const HEIGHT = 720;
const HALF_WIDTH = WIDTH / 2;
const HALF_HEIGHT = HEIGHT / 2;
const FOV = Math.PI / 3;
const HALF_FOV = FOV / 2;
const NUM_RAYS = 320;
const HALF_NUM_RAYS = NUM_RAYS / 2;
const DELTA_ANGLE = FOV / NUM_RAYS;
const MAX_DEPTH = 24;
const SCREEN_DIST = HALF_WIDTH / Math.tan(HALF_FOV);
const SCALE = Math.ceil(WIDTH / NUM_RAYS);
const TEXTURE_SIZE = 128;

// Level Metadata Configuration (8 Campaign Sectors)
const LEVELS_CONFIG = {
    1: {
        title: "Level 1: Outpost Medical Bay",
        subtitle: "Quarantine Zone Alpha",
        survivor: "Field Doctor",
        survivorName: "Dr. Sarah Chen",
        survivorBio: "Chief triage physician with viral transmission data.",
        keycard: "red",
        theme: "medical",
        floorCol: "#20262a",
        ceilCol: "#12161a",
        wallCol: "#d2e1e6",
        accentCol: "#dc141e"
    },
    2: {
        title: "Level 2: Abandoned Subway System",
        subtitle: "Metro Line 4 Tunnels",
        survivor: "Electrical Engineer",
        survivorName: "Marcus Vance",
        survivorBio: "Power grid specialist with city transit bypass access.",
        keycard: "yellow",
        theme: "subway",
        floorCol: "#191816",
        ceilCol: "#0f0e0d",
        wallCol: "#3b3e44",
        accentCol: "#f5c823"
    },
    3: {
        title: "Level 3: City Center Barricade",
        subtitle: "Downtown Checkpoint Omega",
        survivor: "Military Scout",
        survivorName: "Sergeant Ramos",
        survivorBio: "Recon scout with zombie horde telemetry & air route maps.",
        keycard: "blue",
        theme: "barricade",
        floorCol: "#1c1c1e",
        ceilCol: "#141218",
        wallCol: "#505255",
        accentCol: "#2391f5"
    },
    4: {
        title: "Level 4: Industrial Chemical Plant",
        subtitle: "BioCorp Petrochemical Facility",
        survivor: "Virology Specialist",
        survivorName: "Dr. Elena Rostova",
        survivorBio: "Synthetic pathogen researcher with mutagen stabilizer formula.",
        keycard: "green",
        theme: "chemical",
        floorCol: "#161b17",
        ceilCol: "#101411",
        wallCol: "#373a3e",
        accentCol: "#32dc50"
    },
    5: {
        title: "Level 5: Sub-level Research Lab",
        subtitle: "BioCorp Hive - Sub Level -4",
        survivor: "Head Scientist",
        survivorName: "Dr. Arthur Sterling",
        survivorBio: "Lead director of Project Necro-Stasis with master vaccine code.",
        keycard: "purple",
        theme: "lab",
        floorCol: "#141a20",
        ceilCol: "#0d1015",
        wallCol: "#252b36",
        accentCol: "#b446f0"
    },
    6: {
        title: "Level 6: Bio-Dome Hydroponics",
        subtitle: "Sector 7 Greenhouse Complex",
        survivor: "Botanist Specialist",
        survivorName: "Dr. Maya Lin",
        survivorBio: "Botanical engineer with fungal airborne spore antidote.",
        keycard: "orange",
        theme: "greenhouse",
        floorCol: "#151c14",
        ceilCol: "#0d130c",
        wallCol: "#2d382b",
        accentCol: "#ff8219"
    },
    7: {
        title: "Level 7: Underground Catacombs & Vaults",
        subtitle: "Subterranean Cold War Bunker",
        survivor: "Demolitions Expert",
        survivorName: "Chief Alvarez",
        survivorBio: "Weapons ordnance officer with quarantine breach charge.",
        keycard: "crimson",
        theme: "catacombs",
        floorCol: "#181414",
        ceilCol: "#110d0d",
        wallCol: "#3a2d2d",
        accentCol: "#dc192d"
    },
    8: {
        title: "Level 8: Surface Airbase Evac",
        subtitle: "Sector Zero Final Runway",
        survivor: "Air Commander",
        survivorName: "Major Katherine Ross",
        survivorBio: "Heavy transport pilot ready to airlift survivors out.",
        keycard: "gold",
        theme: "airbase",
        floorCol: "#1c1c1f",
        ceilCol: "#121215",
        wallCol: "#30343e",
        accentCol: "#f5d71e"
    }
};

const WEAPON_CONFIGS = {
    shotgun: { name: "Combat Shotgun", maxAmmo: 8, reserveAmmo: 40, damage: 28, fireRate: 750, pellets: 6, spread: 0.12, reloadTime: 1200 },
    rifle: { name: "Assault Rifle", maxAmmo: 30, reserveAmmo: 120, damage: 24, fireRate: 140, pellets: 1, spread: 0.04, reloadTime: 1400 },
    pistol: { name: "Tactical Pistol", maxAmmo: 12, reserveAmmo: 72, damage: 32, fireRate: 350, pellets: 1, spread: 0.02, reloadTime: 900 }
};

// Texture Canvas Generators
class TextureFactory {
    static createSky() {
        const c = document.createElement('canvas');
        c.width = WIDTH;
        c.height = HALF_HEIGHT;
        const ctx = c.getContext('2d');

        // Dark gradient
        const grad = ctx.createLinearGradient(0, 0, 0, HALF_HEIGHT);
        grad.addColorStop(0, '#100e16');
        grad.addColorStop(0.5, '#25121b');
        grad.addColorStop(1, '#481e18');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, WIDTH, HALF_HEIGHT);

        // Blood Moon
        ctx.beginPath();
        ctx.arc(WIDTH / 3, HALF_HEIGHT / 3, 40, 0, Math.PI * 2);
        ctx.fillStyle = '#dc141e';
        ctx.shadowColor = '#ff2832';
        ctx.shadowBlur = 25;
        ctx.fill();
        ctx.shadowBlur = 0;

        // Distant ruined city silhouette
        ctx.fillStyle = '#0a080e';
        let x = 0;
        while (x < WIDTH) {
            const w = 30 + Math.random() * 50;
            const h = 40 + Math.random() * 80;
            ctx.fillRect(x, HALF_HEIGHT - h, w, h);
            x += w - (5 + Math.random() * 10);
        }
        return c;
    }

    static createWall(theme, accent) {
        const c = document.createElement('canvas');
        c.width = TEXTURE_SIZE;
        c.height = TEXTURE_SIZE;
        const ctx = c.getContext('2d');

        // Base tile
        ctx.fillStyle = '#3a3e46';
        ctx.fillRect(0, 0, TEXTURE_SIZE, TEXTURE_SIZE);

        if (theme === 'medical') {
            ctx.fillStyle = '#d2e1e6';
            ctx.fillRect(0, 0, TEXTURE_SIZE, TEXTURE_SIZE);
            ctx.strokeStyle = '#96afb9';
            ctx.lineWidth = 2;
            for (let i = 0; i < TEXTURE_SIZE; i += 32) {
                ctx.strokeRect(i, 0, 32, TEXTURE_SIZE);
                ctx.strokeRect(0, i, TEXTURE_SIZE, 32);
            }
            // Red Cross band
            ctx.fillStyle = '#bc1e28';
            ctx.fillRect(0, 50, TEXTURE_SIZE, 28);
            ctx.fillStyle = '#fff';
            ctx.fillRect(56, 40, 16, 48);
            ctx.fillRect(40, 56, 48, 16);
        } else if (theme === 'subway') {
            ctx.fillStyle = '#2d3035';
            ctx.fillRect(0, 0, TEXTURE_SIZE, TEXTURE_SIZE);
            ctx.strokeStyle = '#1a1b1d';
            ctx.lineWidth = 2;
            for (let y = 0; y < TEXTURE_SIZE; y += 20) {
                const shift = ((y / 20) % 2) * 20;
                for (let x = -shift; x < TEXTURE_SIZE; x += 40) {
                    ctx.strokeRect(x, y, 40, 20);
                }
            }
            // Warning stripe
            ctx.fillStyle = '#e6b919';
            ctx.fillRect(0, 55, TEXTURE_SIZE, 18);
        } else if (theme === 'chemical') {
            ctx.fillStyle = '#383b40';
            ctx.fillRect(0, 0, TEXTURE_SIZE, TEXTURE_SIZE);
            // Hazard diagonal stripes
            ctx.fillStyle = '#f0d214';
            for (let i = -TEXTURE_SIZE; i < TEXTURE_SIZE * 2; i += 24) {
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i + 12, 0);
                ctx.lineTo(i - 12, 25);
                ctx.lineTo(i - 24, 25);
                ctx.fill();
            }
            // Toxic pipe
            ctx.fillStyle = '#228c38';
            ctx.fillRect(30, 40, 24, TEXTURE_SIZE - 40);
        } else {
            // Concrete / Catacombs / Airbase panels
            ctx.strokeStyle = '#22252a';
            ctx.lineWidth = 3;
            ctx.strokeRect(4, 4, TEXTURE_SIZE - 8, TEXTURE_SIZE - 8);
            ctx.fillStyle = accent;
            ctx.fillRect(20, 20, 12, 12);
            ctx.fillRect(TEXTURE_SIZE - 32, 20, 12, 12);
        }

        return c;
    }

    static createDoor(keycardColor) {
        const c = document.createElement('canvas');
        c.width = TEXTURE_SIZE;
        c.height = TEXTURE_SIZE;
        const ctx = c.getContext('2d');

        ctx.fillStyle = '#32363c';
        ctx.fillRect(0, 0, TEXTURE_SIZE, TEXTURE_SIZE);
        ctx.strokeStyle = '#15171a';
        ctx.lineWidth = 4;
        ctx.strokeRect(8, 0, TEXTURE_SIZE - 16, TEXTURE_SIZE);

        // Security scanner keypad
        ctx.fillStyle = '#101215';
        ctx.fillRect(44, 45, 40, 38);
        ctx.strokeStyle = keycardColor;
        ctx.lineWidth = 2;
        ctx.strokeRect(44, 45, 40, 38);

        ctx.fillStyle = keycardColor;
        ctx.fillRect(50, 52, 28, 8);
        ctx.beginPath();
        ctx.arc(64, 72, 5, 0, Math.PI * 2);
        ctx.fill();

        return c;
    }

    static createExtraction() {
        const c = document.createElement('canvas');
        c.width = TEXTURE_SIZE;
        c.height = TEXTURE_SIZE;
        const ctx = c.getContext('2d');

        ctx.fillStyle = '#142319';
        ctx.fillRect(0, 0, TEXTURE_SIZE, TEXTURE_SIZE);
        ctx.strokeStyle = '#32dc78';
        ctx.lineWidth = 4;
        ctx.strokeRect(4, 4, TEXTURE_SIZE - 8, TEXTURE_SIZE - 8);

        // Chevrons pointing up
        ctx.fillStyle = '#32dc78';
        for (let y = 20; y < TEXTURE_SIZE - 20; y += 30) {
            ctx.beginPath();
            ctx.moveTo(64, y);
            ctx.lineTo(94, y + 15);
            ctx.lineTo(84, y + 15);
            ctx.lineTo(64, y + 5);
            ctx.lineTo(44, y + 15);
            ctx.lineTo(34, y + 15);
            ctx.fill();
        }
        return c;
    }
}

// Procedural Map Generator
class MapGenerator {
    static generate(levelId, meta) {
        const width = 16;
        const height = 16;
        const w = levelId;
        const d = 100 + levelId;
        const e = 99;
        const _ = 0;

        const grid = Array.from({ length: height }, () => Array(width).fill(w));
        const rooms = [
            { x: 1, y: 1, w: 4, h: 4 },
            { x: 8, y: 1, w: 5, h: 4 },
            { x: 1, y: 9, w: 5, h: 5 },
            { x: 9, y: 9, w: 6, h: 5 }
        ];

        // Carve rooms
        rooms.forEach(r => {
            for (let y = r.y; y < r.y + r.h; y++) {
                for (let x = r.x; x < r.x + r.w; x++) {
                    grid[y][x] = _;
                }
            }
        });

        // Corridors
        for (let x = 4; x <= 8; x++) grid[2][x] = _;
        for (let y = 2; y <= 9; y++) grid[y][8] = _;
        for (let x = 5; x <= 9; x++) grid[11][x] = _;
        for (let y = 4; y <= 9; y++) grid[y][3] = _;

        // Door between room 3 and 4
        grid[11][8] = d;

        // Extraction
        grid[14][14] = e;

        return {
            grid,
            playerStart: [2.5, 2.5],
            survivorPos: [11.5, 11.5],
            extractionPos: [13.5, 13.5],
            doorTile: [8, 11],
            reqCard: meta.keycard,
            pickups: [
                { type: `keycard_${meta.keycard}`, x: 10.5, y: 2.5, collected: false },
                { type: 'medkit', x: 2.5, y: 11.5, collected: false },
                { type: 'ammo', x: 11.5, y: 2.5, collected: false },
                { type: 'grenade', x: 2.5, y: 3.5, collected: false }
            ],
            zombies: [
                { type: 'walker', x: 8.5, y: 2.5 },
                { type: 'runner', x: 3.5, y: 10.5 },
                { type: 'walker', x: 8.5, y: 6.5 },
                { type: 'spitter', x: 12.5, y: 10.5 },
                { type: 'brute', x: 13.5, y: 12.5 }
            ]
        };
    }
}

// Main Game Controller
class WebGame {
    constructor() {
        this.canvas = document.getElementById('game-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.minimapCanvas = document.getElementById('minimap-canvas');
        this.minimapCtx = this.minimapCanvas.getContext('2d');

        this.state = 'LOBBY'; // LOBBY, GAMEPLAY, VICTORY, GAME_OVER
        this.selectedLevelId = 1;
        this.selectedPage = 0;
        this.randomMode = false;
        this.unlockedLevels = JSON.parse(localStorage.getItem('zombi_unlocked') || '[1]');
        this.killsTotal = parseInt(localStorage.getItem('zombi_kills') || '0', 10);
        this.rescuedTotal = parseInt(localStorage.getItem('zombi_rescued') || '0', 10);

        this.selectedPrimary = localStorage.getItem('zombi_primary') || 'shotgun';
        this.selectedTactical = localStorage.getItem('zombi_tactical') || 'medkit';

        // Textures
        this.skyTexture = TextureFactory.createSky();
        this.wallTextures = {};
        this.doorTextures = {};
        this.extTexture = TextureFactory.createExtraction();
        for (let i = 1; i <= 8; i++) {
            const cfg = LEVELS_CONFIG[i];
            this.wallTextures[i] = TextureFactory.createWall(cfg.theme, cfg.accentCol);
            this.doorTextures[100 + i] = TextureFactory.createDoor(cfg.accentCol);
        }

        // Gameplay state
        this.player = {
            x: 2.5,
            y: 2.5,
            angle: 0.0,
            health: 100,
            armor: 100,
            kills: 0,
            shotsFired: 0,
            shotsHit: 0,
            speed: 0.0035,
            rotSpeed: 0.0024,
            isMoving: false,
            bobTimer: 0,
            stimActive: false,
            stimTimer: 0
        };

        this.weaponState = {
            currentKey: this.selectedPrimary,
            ammo: {
                shotgun: [WEAPON_CONFIGS.shotgun.maxAmmo, WEAPON_CONFIGS.shotgun.reserveAmmo],
                rifle: [WEAPON_CONFIGS.rifle.maxAmmo, WEAPON_CONFIGS.rifle.reserveAmmo],
                pistol: [WEAPON_CONFIGS.pistol.maxAmmo, WEAPON_CONFIGS.pistol.reserveAmmo]
            },
            inventory: {
                medkit: 2,
                grenade: 2,
                stim: 1,
                keycards: new Set()
            },
            isFiring: false,
            isReloading: false,
            lastShotTime: 0,
            reloadStartTime: 0,
            animTimer: 0
        };

        this.activeGrenades = [];
        this.flashAlpha = 0;
        this.damageAlpha = 0;
        this.elapsedTime = 0;
        this.lastFrameTime = performance.now();

        // Controls
        this.keys = {};
        this.mouseLook = false;
        this.joyMove = { x: 0, y: 0 };
        this.touchLookDelta = 0;
        this.touchLookId = null;
        this.lastTouchLookX = 0;

        this.initUI();
        this.initEventListeners();
        requestAnimationFrame((t) => this.loop(t));
    }

    startMission(levelId, isRandom = false) {
        this.selectedLevelId = levelId;
        const meta = LEVELS_CONFIG[levelId];
        this.levelMap = MapGenerator.generate(levelId, meta);

        this.player.x = this.levelMap.playerStart[0];
        this.player.y = this.levelMap.playerStart[1];
        this.player.angle = 0.0;
        this.player.health = 100;
        this.player.armor = 100;
        this.player.kills = 0;
        this.player.shotsFired = 0;
        this.player.shotsHit = 0;
        this.player.stimActive = false;
        this.player.stimTimer = 0;

        this.weaponState.currentKey = this.selectedPrimary;
        this.weaponState.ammo.shotgun = [WEAPON_CONFIGS.shotgun.maxAmmo, WEAPON_CONFIGS.shotgun.reserveAmmo];
        this.weaponState.ammo.rifle = [WEAPON_CONFIGS.rifle.maxAmmo, WEAPON_CONFIGS.rifle.reserveAmmo];
        this.weaponState.ammo.pistol = [WEAPON_CONFIGS.pistol.maxAmmo, WEAPON_CONFIGS.pistol.reserveAmmo];
        this.weaponState.inventory.medkit = this.selectedTactical === 'medkit' ? 3 : 2;
        this.weaponState.inventory.grenade = this.selectedTactical === 'grenade' ? 3 : 2;
        this.weaponState.inventory.stim = this.selectedTactical === 'stim' ? 3 : 1;
        this.weaponState.inventory.keycards = new Set();

        this.survivorRescued = false;
        this.extractionUnlocked = false;
        this.activeGrenades = [];
        this.elapsedTime = 0;
        this.flashAlpha = 0;
        this.damageAlpha = 0;

        this.entities = {
            pickups: this.levelMap.pickups.map(p => ({ ...p })),
            zombies: this.levelMap.zombies.map(z => ({
                ...z,
                alive: true,
                health: z.type === 'brute' ? 240 : z.type === 'runner' ? 70 : 90,
                speed: z.type === 'runner' ? 0.0028 : z.type === 'brute' ? 0.0015 : 0.0018,
                damage: z.type === 'brute' ? 28 : z.type === 'runner' ? 14 : 12,
                lastAttack: 0
            })),
            survivor: {
                x: this.levelMap.survivorPos[0],
                y: this.levelMap.survivorPos[1],
                name: meta.survivorName,
                title: meta.survivor,
                bio: meta.survivorBio,
                rescued: false
            }
        };

        this.state = 'GAMEPLAY';
        document.getElementById('lobby-content').style.display = 'none';
        document.getElementById('lobby-header').style.display = 'none';
        document.getElementById('gameplay-hud').style.display = 'block';

        // Detect touch devices
        if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
            document.getElementById('touch-controls').style.display = 'block';
        }

        document.getElementById('hud-level-title').innerText = `${meta.title.toUpperCase()} | ${meta.subtitle.toUpperCase()}`;
        document.getElementById('hud-objective').innerText = `OBJECTIVE: RESCUE ${meta.survivor.toUpperCase()} (${meta.survivorName.toUpperCase()})`;
    }

    returnToLobby() {
        this.state = 'LOBBY';
        document.exitPointerLock?.();
        document.getElementById('lobby-content').style.display = 'flex';
        document.getElementById('lobby-header').style.display = 'flex';
        document.getElementById('gameplay-hud').style.display = 'none';
        document.getElementById('touch-controls').style.display = 'none';
        document.getElementById('modal-victory').style.display = 'none';
        document.getElementById('modal-gameover').style.display = 'none';
        this.renderCampaignCards();
    }

    triggerVictory() {
        this.state = 'VICTORY';
        window.soundSystem.playRescue();
        document.exitPointerLock?.();

        const lvlId = this.selectedLevelId;
        if (!this.unlockedLevels.includes(lvlId + 1) && lvlId < 8) {
            this.unlockedLevels.push(lvlId + 1);
            localStorage.setItem('zombi_unlocked', JSON.stringify(this.unlockedLevels));
        }

        this.killsTotal += this.player.kills;
        this.rescuedTotal += 1;
        localStorage.setItem('zombi_kills', this.killsTotal);
        localStorage.setItem('zombi_rescued', this.rescuedTotal);

        const mins = Math.floor(this.elapsedTime / 60);
        const secs = Math.floor(this.elapsedTime % 60);
        const timeStr = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

        document.getElementById('victory-subtitle').innerText = `${LEVELS_CONFIG[lvlId].title} Cleared!`;
        document.getElementById('victory-survivor-tag').innerText = `VIP RESCUED: ${LEVELS_CONFIG[lvlId].survivor.toUpperCase()} (${LEVELS_CONFIG[lvlId].survivorName})`;
        document.getElementById('victory-survivor-bio').innerText = LEVELS_CONFIG[lvlId].survivorBio;
        document.getElementById('victory-time').innerText = timeStr;
        document.getElementById('victory-kills').innerText = `${this.player.kills} Infected Swarm`;
        document.getElementById('modal-victory').style.display = 'flex';
    }

    triggerGameOver() {
        this.state = 'GAME_OVER';
        window.soundSystem.playPlayerPain();
        document.exitPointerLock?.();
        document.getElementById('modal-gameover').style.display = 'flex';
    }

    isWall(x, y) {
        const ix = Math.floor(x);
        const iy = Math.floor(y);
        const grid = this.levelMap.grid;
        if (ix < 0 || ix >= grid[0].length || iy < 0 || iy >= grid.length) return true;
        const tile = grid[iy][ix];
        if (tile >= 101 && tile <= 108) {
            return !this.extractionUnlocked; // Door opens when unlocked
        }
        return tile > 0;
    }

    shoot() {
        if (this.state !== 'GAMEPLAY') return;
        const now = performance.now();
        const cfg = WEAPON_CONFIGS[this.weaponState.currentKey];
        const clip = this.weaponState.ammo[this.weaponState.currentKey];

        if (this.weaponState.isReloading || now - this.weaponState.lastShotTime < cfg.fireRate) return;
        if (clip[0] <= 0) {
            this.reload();
            return;
        }

        clip[0]--;
        this.weaponState.lastShotTime = now;
        this.weaponState.isFiring = true;
        this.weaponState.animTimer = 100;
        this.player.shotsFired++;
        this.flashAlpha = 180;

        if (this.weaponState.currentKey === 'pistol') window.soundSystem.playPistol();
        else if (this.weaponState.currentKey === 'shotgun') window.soundSystem.playShotgun();
        else window.soundSystem.playRifle();

        // Hitscan Ray trace
        for (let p = 0; p < cfg.pellets; p++) {
            const spread = (Math.random() * 2 - 1) * cfg.spread;
            const shootAngle = this.player.angle + spread;
            let closestZ = null;
            let minD = Infinity;

            for (const z of this.entities.zombies) {
                if (!z.alive) continue;
                const dx = z.x - this.player.x;
                const dy = z.y - this.player.y;
                let theta = Math.atan2(dy, dx);
                let delta = theta - shootAngle;
                while (delta > Math.PI) delta -= Math.PI * 2;
                while (delta < -Math.PI) delta += Math.PI * 2;

                const dist = Math.hypot(dx, dy);
                const angularWidth = Math.atan2(0.45, dist);
                if (Math.abs(delta) < angularWidth && dist < minD) {
                    // Wall occlusion check
                    let blocked = false;
                    const steps = Math.max(2, Math.floor(dist * 6));
                    for (let s = 1; s < steps; s++) {
                        const t = s / steps;
                        if (this.isWall(this.player.x + dx * t, this.player.y + dy * t)) {
                            blocked = true;
                            break;
                        }
                    }
                    if (!blocked) {
                        minD = dist;
                        closestZ = z;
                    }
                }
            }

            if (closestZ) {
                this.player.shotsHit++;
                closestZ.health -= cfg.damage;
                window.soundSystem.playZombiePain();
                if (closestZ.health <= 0) {
                    closestZ.alive = false;
                    this.player.kills++;
                    window.soundSystem.playZombieDeath();
                }
            }
        }
    }

    reload() {
        const clip = this.weaponState.ammo[this.weaponState.currentKey];
        const max = WEAPON_CONFIGS[this.weaponState.currentKey].maxAmmo;
        if (this.weaponState.isReloading || clip[0] >= max || clip[1] <= 0) return;

        this.weaponState.isReloading = true;
        this.weaponState.reloadStartTime = performance.now();
        window.soundSystem.playReload();
    }

    throwGrenade() {
        if (this.weaponState.inventory.grenade <= 0) return;
        this.weaponState.inventory.grenade--;
        const speed = 0.006;
        this.activeGrenades.push({
            x: this.player.x,
            y: this.player.y,
            vx: Math.cos(this.player.angle) * speed,
            vy: Math.sin(this.player.angle) * speed,
            timer: 1600
        });
    }

    useMedkit() {
        if (this.weaponState.inventory.medkit <= 0 || this.player.health >= 100) return;
        this.weaponState.inventory.medkit--;
        this.player.health = Math.min(100, this.player.health + 40);
        window.soundSystem.playPickup();
    }

    useStim() {
        if (this.weaponState.inventory.stim <= 0) return;
        this.weaponState.inventory.stim--;
        this.player.stimActive = true;
        this.player.stimTimer = 10000;
        window.soundSystem.playStim();
    }

    interact() {
        // 1. Rescue Survivor
        const s = this.entities.survivor;
        if (!s.rescued && Math.hypot(this.player.x - s.x, this.player.y - s.y) < 2.0) {
            s.rescued = true;
            this.survivorRescued = true;
            this.extractionUnlocked = true;
            window.soundSystem.playRescue();
            document.getElementById('hud-objective').innerText = "OBJECTIVE: REACH EVACUATION ZONE TO EXTRACT!";
            document.getElementById('hud-objective').style.color = 'var(--color-green)';
            return;
        }

        // 2. Unlock door
        const [dx, dy] = this.levelMap.doorTile;
        if (Math.hypot(this.player.x - (dx + 0.5), this.player.y - (dy + 0.5)) < 1.8) {
            if (this.weaponState.inventory.keycards.has(this.levelMap.reqCard)) {
                this.levelMap.grid[dy][dx] = 0; // open door
                window.soundSystem.playDoorUnlock();
                return;
            }
        }

        // 3. Extraction
        const [ex, ey] = this.levelMap.extractionPos;
        if (Math.hypot(this.player.x - ex, this.player.y - ey) < 1.8 && this.extractionUnlocked) {
            this.triggerVictory();
        }
    }

    update(dt) {
        if (this.state !== 'GAMEPLAY') return;

        this.elapsedTime += dt / 1000;

        // Player speed with stim
        const speed = this.player.speed * (this.player.stimActive ? 1.45 : 1.0) * dt;
        let dx = 0;
        let dy = 0;
        const sinA = Math.sin(this.player.angle);
        const cosA = Math.cos(this.player.angle);

        // Virtual joystick movement
        if (Math.abs(this.joyMove.x) > 0.05 || Math.abs(this.joyMove.y) > 0.05) {
            const fwd = -this.joyMove.y * speed;
            const strafe = this.joyMove.x * speed;
            dx += fwd * cosA - strafe * sinA;
            dy += fwd * sinA + strafe * cosA;
        }

        // Keyboard movement
        if (this.keys['KeyW'] || this.keys['ArrowUp']) { dx += cosA * speed; dy += sinA * speed; }
        if (this.keys['KeyS'] || this.keys['ArrowDown']) { dx -= cosA * speed; dy -= sinA * speed; }
        if (this.keys['KeyA']) { dx += sinA * speed; dy -= cosA * speed; }
        if (this.keys['KeyD']) { dx -= sinA * speed; dy += cosA * speed; }

        this.player.isMoving = (dx !== 0 || dy !== 0);
        if (this.player.isMoving) this.player.bobTimer += dt;

        // Wall collision sliding
        const buf = 0.28;
        const checkX = this.player.x + (dx > 0 ? buf : -buf) + dx;
        const checkY = this.player.y + (dy > 0 ? buf : -buf) + dy;
        if (!this.isWall(checkX, this.player.y - buf) && !this.isWall(checkX, this.player.y + buf)) {
            this.player.x += dx;
        }
        if (!this.isWall(this.player.x - buf, checkY) && !this.isWall(this.player.x + buf, checkY)) {
            this.player.y += dy;
        }

        // Camera rotation
        if (this.keys['ArrowLeft']) this.player.angle -= this.player.rotSpeed * dt;
        if (this.keys['ArrowRight']) this.player.angle += this.player.rotSpeed * dt;
        if (this.touchLookDelta !== 0) {
            this.player.angle += this.touchLookDelta * 0.0032;
            this.touchLookDelta = 0;
        }
        this.player.angle = (this.player.angle + Math.PI * 2) % (Math.PI * 2);

        // Stim timer
        if (this.player.stimActive) {
            this.player.stimTimer -= dt;
            if (this.player.stimTimer <= 0) this.player.stimActive = false;
        }

        // Reload check
        if (this.weaponState.isReloading) {
            const dur = WEAPON_CONFIGS[this.weaponState.currentKey].reloadTime;
            if (performance.now() - this.weaponState.reloadStartTime >= dur) {
                const clip = this.weaponState.ammo[this.weaponState.currentKey];
                const max = WEAPON_CONFIGS[this.weaponState.currentKey].maxAmmo;
                const needed = max - clip[0];
                const add = Math.min(needed, clip[1]);
                clip[0] += add;
                clip[1] -= add;
                this.weaponState.isReloading = false;
            }
        }

        // Grenades update
        this.activeGrenades.forEach((g, idx) => {
            g.timer -= dt;
            const nx = g.x + g.vx * dt;
            const ny = g.y + g.vy * dt;
            if (!this.isWall(nx, g.y)) g.x = nx; else g.vx *= -0.5;
            if (!this.isWall(g.x, ny)) g.y = ny; else g.vy *= -0.5;
            g.vx *= 0.96; g.vy *= 0.96;

            if (g.timer <= 0) {
                this.activeGrenades.splice(idx, 1);
                window.soundSystem.playGrenade();
                this.flashAlpha = 220;
                for (const z of this.entities.zombies) {
                    if (!z.alive) continue;
                    const d = Math.hypot(z.x - g.x, z.y - g.y);
                    if (d <= 3.5) {
                        z.health -= Math.floor(120 * (1.0 - d / 3.5));
                        if (z.health <= 0) { z.alive = false; this.player.kills++; }
                    }
                }
            }
        });

        // Pickups collection
        this.entities.pickups.forEach(p => {
            if (!p.collected && Math.hypot(this.player.x - p.x, this.player.y - p.y) < 0.75) {
                p.collected = true;
                window.soundSystem.playPickup();
                if (p.type.startsWith('keycard_')) {
                    this.weaponState.inventory.keycards.add(p.type.split('_')[1]);
                } else if (p.type === 'medkit') {
                    this.weaponState.inventory.medkit = Math.min(5, this.weaponState.inventory.medkit + 1);
                } else if (p.type === 'ammo') {
                    for (const k in this.weaponState.ammo) this.weaponState.ammo[k][1] += 24;
                } else if (p.type === 'grenade') {
                    this.weaponState.inventory.grenade = Math.min(5, this.weaponState.inventory.grenade + 1);
                }
            }
        });

        // Zombie AI
        const now = performance.now();
        this.entities.zombies.forEach(z => {
            if (!z.alive) return;
            const dist = Math.hypot(this.player.x - z.x, this.player.y - z.y);

            // Attack
            if (dist <= 1.1) {
                if (now - z.lastAttack >= 900) {
                    z.lastAttack = now;
                    window.soundSystem.playZombieAttack();
                    this.damageAlpha = 210;
                    this.player.health = Math.max(0, this.player.health - z.damage);
                    if (this.player.health <= 0) this.triggerGameOver();
                }
                return;
            }

            // Move towards player
            if (dist < 8.0) {
                const angle = Math.atan2(this.player.y - z.y, this.player.x - z.x);
                const zx = Math.cos(angle) * z.speed * dt;
                const zy = Math.sin(angle) * z.speed * dt;
                if (!this.isWall(z.x + zx, z.y)) z.x += zx;
                if (!this.isWall(z.x, z.y + zy)) z.y += zy;
            }
        });

        // Prompt checking
        const s = this.entities.survivor;
        const promptEl = document.getElementById('hud-prompt');
        if (!s.rescued && Math.hypot(this.player.x - s.x, this.player.y - s.y) < 2.0) {
            promptEl.style.display = 'block';
            promptEl.innerText = 'PRESS ACTION TO RESCUE SURVIVOR';
        } else if (Math.hypot(this.player.x - this.levelMap.extractionPos[0], this.player.y - this.levelMap.extractionPos[1]) < 1.8) {
            promptEl.style.display = 'block';
            promptEl.innerText = this.extractionUnlocked ? 'PRESS ACTION TO EVACUATE' : 'EXTRACTION LOCKED: RESCUE SURVIVOR FIRST';
        } else {
            promptEl.style.display = 'none';
        }

        this.updateHUD();
    }

    updateHUD() {
        document.getElementById('hud-hp-num').innerText = this.player.health;
        document.getElementById('hud-hp-bar').style.width = `${this.player.health}%`;
        document.getElementById('hud-arm-num').innerText = this.player.armor;
        document.getElementById('hud-arm-bar').style.width = `${this.player.armor}%`;

        document.getElementById('hud-stim-indicator').style.display = this.player.stimActive ? 'block' : 'none';

        const mins = Math.floor(this.elapsedTime / 60);
        const secs = Math.floor(this.elapsedTime % 60);
        document.getElementById('hud-timer').innerText = `TIME: ${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

        const curW = this.weaponState.currentKey;
        const clip = this.weaponState.ammo[curW];
        document.getElementById('hud-weapon-name').innerText = WEAPON_CONFIGS[curW].name;
        document.getElementById('hud-ammo-count').innerText = this.weaponState.isReloading ? "RELOADING..." : `${clip[0]} / ${clip[1]}`;

        const cards = Array.from(this.weaponState.inventory.keycards).join(',').toUpperCase() || 'NONE';
        document.getElementById('hud-tactical-info').innerText = `MED: ${this.weaponState.inventory.medkit} | GREN: ${this.weaponState.inventory.grenade} | KEY: ${cards}`;
    }

    render() {
        const ctx = this.ctx;
        ctx.clearRect(0, 0, WIDTH, HEIGHT);

        if (this.state !== 'GAMEPLAY') return;

        // 1. Skybox Parallax
        const skyX = -Math.floor((this.player.angle / (Math.PI * 2)) * WIDTH * 2) % WIDTH;
        ctx.drawImage(this.skyTexture, skyX - WIDTH, 0);
        ctx.drawImage(this.skyTexture, skyX, 0);
        ctx.drawImage(this.skyTexture, skyX + WIDTH, 0);

        // 2. Floor fill
        ctx.fillStyle = LEVELS_CONFIG[this.selectedLevelId].floorCol;
        ctx.fillRect(0, HALF_HEIGHT, WIDTH, HALF_HEIGHT);

        // 3. Raycasting DDA loop
        const ox = this.player.x;
        const oy = this.player.y;
        let rayAngle = this.player.angle - HALF_FOV + 0.0001;
        const grid = this.levelMap.grid;
        const depthBuffer = [];

        for (let ray = 0; ray < NUM_RAYS; ray++) {
            const sinA = Math.sin(rayAngle);
            const cosA = Math.cos(rayAngle);

            // Horizontals
            const yHor = sinA > 0 ? Math.floor(oy) + 1 : Math.floor(oy) - 1e-6;
            const dy = sinA > 0 ? 1 : -1;
            let depthHor = (yHor - oy) / sinA;
            let xHor = ox + depthHor * cosA;
            const deltaDepthH = dy / sinA;
            const dxH = deltaDepthH * cosA;

            let texHor = 1;
            for (let i = 0; i < MAX_DEPTH; i++) {
                const tx = Math.floor(xHor);
                const ty = Math.floor(yHor);
                if (ty >= 0 && ty < grid.length && tx >= 0 && tx < grid[0].length && grid[ty][tx] > 0) {
                    texHor = grid[ty][tx];
                    break;
                }
                xHor += dxH;
                yHor += dy;
                depthHor += deltaDepthH;
            }

            // Verticals
            const xVert = cosA > 0 ? Math.floor(ox) + 1 : Math.floor(ox) - 1e-6;
            const dx = cosA > 0 ? 1 : -1;
            let depthVert = (xVert - ox) / cosA;
            let yVert = oy + depthVert * sinA;
            const deltaDepthV = dx / cosA;
            const dyV = deltaDepthV * sinA;

            let texVert = 1;
            for (let i = 0; i < MAX_DEPTH; i++) {
                const tx = Math.floor(xVert);
                const ty = Math.floor(yVert);
                if (ty >= 0 && ty < grid.length && tx >= 0 && tx < grid[0].length && grid[ty][tx] > 0) {
                    texVert = grid[ty][tx];
                    break;
                }
                xVert += dx;
                yVert += dyV;
                depthVert += deltaDepthV;
            }

            // Compare
            let depth, texture, offset;
            if (depthVert < depthHor) {
                depth = depthVert;
                texture = texVert;
                offset = (cosA > 0 ? (yVert % 1) : (1 - (yVert % 1)));
            } else {
                depth = depthHor;
                texture = texHor;
                offset = (sinA > 0 ? (1 - (xHor % 1)) : (xHor % 1));
            }

            // Remove fisheye
            depth *= Math.cos(this.player.angle - rayAngle);
            depthBuffer[ray] = depth;

            // Draw Wall Column
            const projHeight = Math.min(HEIGHT * 3, Math.max(1, Math.floor(SCREEN_DIST / (depth + 0.0001))));
            const wallTexture = (texture === 99) ? this.extTexture : (texture >= 101 && texture <= 108) ? this.doorTextures[texture] : (this.wallTextures[texture] || this.wallTextures[1]);

            const subX = Math.floor(Math.abs(offset) * (TEXTURE_SIZE - 2));
            ctx.drawImage(
                wallTexture,
                subX, 0, 2, TEXTURE_SIZE,
                ray * SCALE, HALF_HEIGHT - projHeight / 2, SCALE, projHeight
            );

            // Fog shading
            if (depth > 3.0) {
                const dark = Math.min(0.75, (depth - 3.0) / (MAX_DEPTH - 3.0));
                ctx.fillStyle = `rgba(0, 0, 0, ${dark})`;
                ctx.fillRect(ray * SCALE, HALF_HEIGHT - projHeight / 2, SCALE, projHeight);
            }

            rayAngle += DELTA_ANGLE;
        }

        // 4. Sprites Rendering (Zombies, Survivors, Pickups, Grenades)
        const sprites = [];
        this.entities.pickups.forEach(p => { if (!p.collected) sprites.push({ x: p.x, y: p.y, type: p.type, kind: 'pickup' }); });
        if (!this.entities.survivor.rescued) sprites.push({ x: this.entities.survivor.x, y: this.entities.survivor.y, kind: 'survivor' });
        this.entities.zombies.forEach(z => { if (z.alive) sprites.push({ x: z.x, y: z.y, kind: 'zombie', type: z.type }); });
        this.activeGrenades.forEach(g => { sprites.push({ x: g.x, y: g.y, kind: 'grenade' }); });

        sprites.forEach(s => {
            const dx = s.x - this.player.x;
            const dy = s.y - this.player.y;
            let theta = Math.atan2(dy, dx);
            let delta = theta - this.player.angle;
            while (delta > Math.PI) delta -= Math.PI * 2;
            while (delta < -Math.PI) delta += Math.PI * 2;

            const dist = Math.hypot(dx, dy);
            const normDist = dist * Math.cos(delta);

            if (normDist > 0.1 && Math.abs(delta) < (Math.PI / 2.0)) {
                const screenX = (HALF_NUM_RAYS + (delta / DELTA_ANGLE)) * SCALE;
                const proj = Math.min(HEIGHT * 3, Math.floor((SCREEN_DIST / (normDist + 0.0001)) * 0.75));
                const rayIdx = Math.floor(screenX / SCALE);

                if (rayIdx >= 0 && rayIdx < NUM_RAYS && normDist < depthBuffer[rayIdx] + 0.3) {
                    // Draw Sprite Billboard
                    const posX = screenX - proj / 2;
                    const posY = HALF_HEIGHT - proj / 2 + proj * 0.2;

                    ctx.save();
                    if (s.kind === 'zombie') {
                        ctx.fillStyle = s.type === 'brute' ? '#a52a2a' : s.type === 'runner' ? '#e63232' : '#287832';
                        ctx.beginPath();
                        ctx.arc(posX + proj / 2, posY + proj / 3, proj / 3.5, 0, Math.PI * 2);
                        ctx.fill();
                        // Eyes
                        ctx.fillStyle = '#ff0000';
                        ctx.fillRect(posX + proj / 2 - 8, posY + proj / 3 - 4, 4, 4);
                        ctx.fillRect(posX + proj / 2 + 4, posY + proj / 3 - 4, 4, 4);
                    } else if (s.kind === 'survivor') {
                        ctx.fillStyle = '#f5c823';
                        ctx.beginPath();
                        ctx.arc(posX + proj / 2, posY + proj / 3, proj / 3.5, 0, Math.PI * 2);
                        ctx.fill();
                    } else if (s.kind === 'pickup') {
                        ctx.fillStyle = s.type.startsWith('keycard') ? '#00d2ff' : '#2dd75f';
                        ctx.fillRect(posX + proj * 0.25, posY + proj * 0.4, proj * 0.5, proj * 0.3);
                    } else if (s.kind === 'grenade') {
                        ctx.fillStyle = '#32363c';
                        ctx.beginPath();
                        ctx.arc(posX + proj / 2, posY + proj * 0.6, proj / 8, 0, Math.PI * 2);
                        ctx.fill();
                    }
                    ctx.restore();
                }
            }
        });

        // 5. Weapon Viewmodel
        this.drawViewmodel();

        // 6. Flash and Damage Overlay
        if (this.damageAlpha > 0) {
            ctx.fillStyle = `rgba(220, 20, 30, ${this.damageAlpha / 255})`;
            ctx.fillRect(0, 0, WIDTH, HEIGHT);
            this.damageAlpha = Math.max(0, this.damageAlpha - 4);
        }
        if (this.flashAlpha > 0) {
            ctx.fillStyle = `rgba(255, 230, 160, ${this.flashAlpha / 255})`;
            ctx.fillRect(0, 0, WIDTH, HEIGHT);
            this.flashAlpha = Math.max(0, this.flashAlpha - 14);
        }

        // 7. Render Minimap
        this.renderMinimap();
    }

    drawViewmodel() {
        const ctx = this.ctx;
        const curW = this.weaponState.currentKey;
        const bobX = this.player.isMoving ? Math.sin(this.player.bobTimer * 0.008) * 12 : 0;
        const bobY = this.player.isMoving ? Math.abs(Math.cos(this.player.bobTimer * 0.008)) * 14 : 0;
        const reloadShift = this.weaponState.isReloading ? 90 : 0;

        const wX = HALF_WIDTH - 80 + bobX;
        const wY = HEIGHT - 220 + bobY + reloadShift;

        ctx.save();
        ctx.fillStyle = '#1c1e22';
        ctx.fillRect(wX, wY, 160, 240);

        // Barrel and grips
        ctx.fillStyle = '#3a3e46';
        ctx.fillRect(wX + 45, wY - 40, 70, 60);

        if (this.weaponState.isFiring) {
            // Muzzle flash
            ctx.fillStyle = '#ffe682';
            ctx.beginPath();
            ctx.arc(wX + 80, wY - 55, 38, 0, Math.PI * 2);
            ctx.fill();
            this.weaponState.animTimer -= 16;
            if (this.weaponState.animTimer <= 0) this.weaponState.isFiring = false;
        }
        ctx.restore();
    }

    renderMinimap() {
        const mctx = this.minimapCtx;
        mctx.clearRect(0, 0, 110, 110);
        const grid = this.levelMap.grid;
        const cellW = 110 / grid[0].length;
        const cellH = 110 / grid.length;

        for (let y = 0; y < grid.length; y++) {
            for (let x = 0; x < grid[0].length; x++) {
                if (grid[y][x] > 0) {
                    mctx.fillStyle = grid[y][x] === 99 ? '#2dd75f' : grid[y][x] >= 101 ? '#dc141e' : '#454a54';
                    mctx.fillRect(x * cellW, y * cellH, cellW, cellH);
                }
            }
        }

        // Survivor
        if (!this.entities.survivor.rescued) {
            mctx.fillStyle = '#ffaf28';
            mctx.beginPath();
            mctx.arc(this.entities.survivor.x * cellW, this.entities.survivor.y * cellH, 3, 0, Math.PI * 2);
            mctx.fill();
        }

        // Zombies
        mctx.fillStyle = '#ff2832';
        this.entities.zombies.forEach(z => {
            if (z.alive) {
                mctx.beginPath();
                mctx.arc(z.x * cellW, z.y * cellH, 2, 0, Math.PI * 2);
                mctx.fill();
            }
        });

        // Player
        const px = this.player.x * cellW;
        const py = this.player.y * cellH;
        mctx.fillStyle = '#00d2ff';
        mctx.beginPath();
        mctx.arc(px, py, 3, 0, Math.PI * 2);
        mctx.fill();

        mctx.strokeStyle = '#00d2ff';
        mctx.lineWidth = 1.5;
        mctx.beginPath();
        mctx.moveTo(px, py);
        mctx.lineTo(px + Math.cos(this.player.angle) * 8, py + Math.sin(this.player.angle) * 8);
        mctx.stroke();
    }

    loop(timestamp) {
        const dt = Math.min(50, timestamp - this.lastFrameTime);
        this.lastFrameTime = timestamp;
        this.update(dt);
        this.render();
        requestAnimationFrame((t) => this.loop(t));
    }

    initUI() {
        this.renderCampaignCards();
        this.renderLeaderboards();

        // Tab navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-pane').forEach(p => p.style.display = 'none');
                tab.classList.add('active');
                const target = document.getElementById(`tab-${tab.dataset.tab}`);
                if (target) target.style.display = 'block';
            });
        });

        // Armory selection
        document.querySelectorAll('.armory-card[data-weapon]').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.armory-card[data-weapon]').forEach(c => {
                    c.classList.remove('selected');
                    c.querySelector('.card-badge').style.display = 'none';
                });
                card.classList.add('selected');
                card.querySelector('.card-badge').style.display = 'block';
                this.selectedPrimary = card.dataset.weapon;
                localStorage.setItem('zombi_primary', this.selectedPrimary);
                this.updateLoadoutSummary();
            });
        });

        document.querySelectorAll('.armory-card[data-tactical]').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.armory-card[data-tactical]').forEach(c => {
                    c.classList.remove('selected');
                    c.querySelector('.card-badge').style.display = 'none';
                });
                card.classList.add('selected');
                card.querySelector('.card-badge').style.display = 'block';
                this.selectedTactical = card.dataset.tactical;
                localStorage.setItem('zombi_tactical', this.selectedTactical);
                this.updateLoadoutSummary();
            });
        });

        // Campaign Page buttons
        document.getElementById('btn-page-1').addEventListener('click', () => {
            this.selectedPage = 0;
            document.getElementById('btn-page-1').classList.add('active');
            document.getElementById('btn-page-2').classList.remove('active');
            this.renderCampaignCards();
        });

        document.getElementById('btn-page-2').addEventListener('click', () => {
            this.selectedPage = 1;
            document.getElementById('btn-page-2').classList.add('active');
            document.getElementById('btn-page-1').classList.remove('active');
            this.renderCampaignCards();
        });

        // Random mode toggle
        document.getElementById('btn-random-mode').addEventListener('click', () => {
            this.randomMode = !this.randomMode;
            document.getElementById('random-status-text').innerText = this.randomMode ? 'ON' : 'OFF';
            document.getElementById('btn-random-mode').classList.toggle('active', this.randomMode);
        });

        // Deploy button
        document.getElementById('btn-deploy').addEventListener('click', () => {
            window.soundSystem.init();
            this.startMission(this.selectedLevelId, this.randomMode);
        });

        // Modal buttons
        document.getElementById('btn-next-mission').addEventListener('click', () => {
            document.getElementById('modal-victory').style.display = 'none';
            if (this.selectedLevelId < 8) this.startMission(this.selectedLevelId + 1, this.randomMode);
            else this.startMission(this.selectedLevelId, true);
        });
        document.getElementById('btn-victory-lobby').addEventListener('click', () => this.returnToLobby());

        document.getElementById('btn-retry-mission').addEventListener('click', () => {
            document.getElementById('modal-gameover').style.display = 'none';
            this.startMission(this.selectedLevelId, this.randomMode);
        });
        document.getElementById('btn-gameover-lobby').addEventListener('click', () => this.returnToLobby());

        // Fullscreen & Sound
        document.getElementById('btn-fullscreen').addEventListener('click', () => {
            if (!document.fullscreenElement) document.documentElement.requestFullscreen?.();
            else document.exitFullscreen?.();
        });

        document.getElementById('btn-sound-toggle').addEventListener('click', (e) => {
            window.soundSystem.enabled = !window.soundSystem.enabled;
            e.target.innerText = window.soundSystem.enabled ? '🔊 SOUND: ON' : '🔇 SOUND: OFF';
        });

        this.updateLoadoutSummary();
    }

    updateLoadoutSummary() {
        const pName = WEAPON_CONFIGS[this.selectedPrimary].name.toUpperCase();
        const tName = this.selectedTactical.toUpperCase();
        document.getElementById('summary-loadout').innerText = `${pName} + ${tName}`;
    }

    renderCampaignCards() {
        const container = document.getElementById('campaign-cards');
        container.innerHTML = '';
        const start = this.selectedPage * 4 + 1;

        for (let i = start; i < start + 4; i++) {
            const meta = LEVELS_CONFIG[i];
            const isUnlocked = this.unlockedLevels.includes(i);
            const isSelected = this.selectedLevelId === i;

            const card = document.createElement('div');
            card.className = `level-card ${isUnlocked ? '' : 'locked'} ${isSelected ? 'selected' : ''}`;
            card.innerHTML = `
                <div class="card-badge">${isUnlocked ? 'AUTHORIZED' : 'LOCKED'}</div>
                <div>
                    <h3 class="card-title">${meta.title}</h3>
                    <div class="card-subtitle">${meta.subtitle}</div>
                    <div class="card-survivor-box">
                        <strong>VIP: ${meta.survivor}</strong>
                        ${meta.survivorName}
                    </div>
                </div>
                <div class="card-meta">
                    <span>SECURITY: ${meta.keycard.toUpperCase()}</span>
                    <span>HAZARD: LEVEL ${i}</span>
                </div>
            `;

            if (isUnlocked) {
                card.addEventListener('click', () => {
                    this.selectedLevelId = i;
                    document.querySelectorAll('.level-card').forEach(c => c.classList.remove('selected'));
                    card.classList.add('selected');
                });
            }

            container.appendChild(card);
        }
    }

    renderLeaderboards() {
        const selector = document.getElementById('leaderboard-level-selector');
        selector.innerHTML = '';
        for (let i = 1; i <= 8; i++) {
            const btn = document.createElement('button');
            btn.className = `btn-secondary ${i === 1 ? 'active' : ''}`;
            btn.innerText = `LEVEL ${i}`;
            btn.addEventListener('click', () => {
                document.querySelectorAll('#leaderboard-level-selector .btn-secondary').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.populateLeaderboardTable(i);
            });
            selector.appendChild(btn);
        }
        this.populateLeaderboardTable(1);
    }

    populateLeaderboardTable(lvl) {
        const rows = document.getElementById('leaderboard-rows');
        rows.innerHTML = `
            <tr><td>#1</td><td>GhostOperative</td><td>00:42</td><td>14 Infected</td></tr>
            <tr><td>#2</td><td>Vance_Delta</td><td>00:58</td><td>11 Infected</td></tr>
            <tr><td>#3</td><td>NightHawk</td><td>01:15</td><td>9 Infected</td></tr>
            <tr><td>#4</td><td>Dr_Chen_Echo</td><td>01:34</td><td>7 Infected</td></tr>
        `;
    }

    initEventListeners() {
        window.addEventListener('keydown', (e) => {
            this.keys[e.code] = true;
            if (this.state === 'GAMEPLAY') {
                if (e.code === 'Digit1') this.weaponState.currentKey = 'pistol';
                if (e.code === 'Digit2') this.weaponState.currentKey = 'shotgun';
                if (e.code === 'Digit3') this.weaponState.currentKey = 'rifle';
                if (e.code === 'KeyR') this.reload();
                if (e.code === 'KeyE') this.interact();
                if (e.code === 'KeyG') this.throwGrenade();
                if (e.code === 'KeyH') this.useMedkit();
                if (e.code === 'KeyQ') this.useStim();
                if (e.code === 'Space') this.shoot();
                if (e.code === 'Escape') this.returnToLobby();
            }
        });

        window.addEventListener('keyup', (e) => {
            this.keys[e.code] = false;
        });

        // Desktop Canvas Mouse Pointer Lock
        this.canvas.addEventListener('click', () => {
            if (this.state === 'GAMEPLAY') {
                window.soundSystem.init();
                this.canvas.requestPointerLock?.();
                this.shoot();
            }
        });

        document.addEventListener('pointerlockchange', () => {
            this.mouseLook = (document.pointerLockElement === this.canvas);
        });

        document.addEventListener('mousemove', (e) => {
            if (this.state === 'GAMEPLAY' && this.mouseLook) {
                this.player.angle += e.movementX * 0.0025;
            }
        });

        // Mobile Touch Controls
        const joyZone = document.getElementById('joystick-zone');
        const knob = document.getElementById('joystick-knob');
        let joyTouchId = null;

        joyZone.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.changedTouches[0];
            joyTouchId = touch.identifier;
            this.handleJoy(touch, joyZone, knob);
        }, { passive: false });

        joyZone.addEventListener('touchmove', (e) => {
            e.preventDefault();
            for (let i = 0; i < e.changedTouches.length; i++) {
                if (e.changedTouches[i].identifier === joyTouchId) {
                    this.handleJoy(e.changedTouches[i], joyZone, knob);
                    break;
                }
            }
        }, { passive: false });

        const resetJoy = () => {
            joyTouchId = null;
            this.joyMove = { x: 0, y: 0 };
            knob.style.transform = 'translate(0px, 0px)';
        };
        joyZone.addEventListener('touchend', resetJoy);
        joyZone.addEventListener('touchcancel', resetJoy);

        // Touch Look on right screen
        window.addEventListener('touchstart', (e) => {
            if (this.state !== 'GAMEPLAY') return;
            for (let i = 0; i < e.changedTouches.length; i++) {
                const t = e.changedTouches[i];
                if (t.clientX > window.innerWidth / 2 && this.touchLookId === null) {
                    this.touchLookId = t.identifier;
                    this.lastTouchLookX = t.clientX;
                    break;
                }
            }
        });

        window.addEventListener('touchmove', (e) => {
            if (this.state !== 'GAMEPLAY') return;
            for (let i = 0; i < e.changedTouches.length; i++) {
                const t = e.changedTouches[i];
                if (t.identifier === this.touchLookId) {
                    this.touchLookDelta += (t.clientX - this.lastTouchLookX);
                    this.lastTouchLookX = t.clientX;
                    break;
                }
            }
        });

        const resetTouchLook = (e) => {
            for (let i = 0; i < e.changedTouches.length; i++) {
                if (e.changedTouches[i].identifier === this.touchLookId) {
                    this.touchLookId = null;
                    break;
                }
            }
        };
        window.addEventListener('touchend', resetTouchLook);
        window.addEventListener('touchcancel', resetTouchLook);

        // Action Touch Buttons
        document.getElementById('btn-touch-fire').addEventListener('touchstart', (e) => { e.preventDefault(); this.shoot(); });
        document.getElementById('btn-touch-reload').addEventListener('touchstart', (e) => { e.preventDefault(); this.reload(); });
        document.getElementById('btn-touch-switch').addEventListener('touchstart', (e) => {
            e.preventDefault();
            const keys = ['shotgun', 'rifle', 'pistol'];
            const idx = (keys.indexOf(this.weaponState.currentKey) + 1) % keys.length;
            this.weaponState.currentKey = keys[idx];
            window.soundSystem.playReload();
        });
        document.getElementById('btn-touch-interact').addEventListener('touchstart', (e) => { e.preventDefault(); this.interact(); });
        document.getElementById('btn-touch-frag').addEventListener('touchstart', (e) => { e.preventDefault(); this.throwGrenade(); });
        document.getElementById('btn-touch-heal').addEventListener('touchstart', (e) => { e.preventDefault(); this.useMedkit(); });
        document.getElementById('btn-touch-stim').addEventListener('touchstart', (e) => { e.preventDefault(); this.useStim(); });
    }

    handleJoy(touch, zone, knob) {
        const rect = zone.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        const dx = touch.clientX - centerX;
        const dy = touch.clientY - centerY;
        const dist = Math.hypot(dx, dy);
        const maxR = rect.width / 2;
        const clampedD = Math.min(maxR, dist);
        const angle = Math.atan2(dy, dx);

        const kX = Math.cos(angle) * clampedD;
        const kY = Math.sin(angle) * clampedD;
        knob.style.transform = `translate(${kX}px, ${kY}px)`;

        const norm = clampedD / maxR;
        this.joyMove = {
            x: Math.cos(angle) * norm,
            y: Math.sin(angle) * norm
        };
    }
}

window.addEventListener('DOMContentLoaded', () => {
    window.game = new WebGame();
});
