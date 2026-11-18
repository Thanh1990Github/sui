"""Synthesize a soft minimal-piano background bed (original, royalty-free).
usage: piano.py <out.wav> <seed> <bpm> <key_semitone> <seconds>"""
import sys
import numpy as np
import soundfile as sf

out, seed, bpm, key, secs = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])
SR = 44100
rng = np.random.default_rng(seed)
N = int(SR * (secs + 6))
L = np.zeros(N); R = np.zeros(N)

def midi_hz(m): return 440.0 * 2 ** ((m - 69) / 12)

def piano(f, dur, vel):
    n = int(SR * dur); t = np.arange(n) / SR
    tone = np.zeros(n)
    for h, a in [(1, 1.0), (2, 0.45), (3, 0.22), (4, 0.10), (5, 0.05), (6, 0.03)]:
        inh = 1 + 0.0004 * h * h  # slight inharmonicity
        tone += a * np.sin(2 * np.pi * f * h * inh * t + rng.uniform(0, 6.28)) * np.exp(-t * (1.1 + 0.9 * h))
    att = np.minimum(1, t / 0.006)
    return tone * att * vel

def pad(f, dur, vel):
    n = int(SR * dur); t = np.arange(n) / SR
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    s = sum(np.sin(2 * np.pi * f * d * t) for d in (1.0, 1.003, 0.997)) / 3
    return s * env * vel

def put(sig, start, pan=0.0):
    i = max(0, int(start * SR)); j = min(N, i + len(sig))
    if j <= i:
        return
    sig = sig[: j - i]
    L[i:j] += sig * (1 - pan) * 0.5
    R[i:j] += sig * (1 + pan) * 0.5

# chord progressions (scale degrees as semitones from key, minor-ish calm)
progs = [
    [[0, 3, 7, 10], [-4, 0, 3, 7], [-7, -3, 0, 5], [-2, 2, 5, 9]],   # i - VI - iv - VII
    [[0, 4, 7, 11], [-3, 0, 4, 9], [-7, -3, 0, 4], [-5, -1, 2, 7]],  # I - vi - IV - V
    [[0, 3, 7, 10], [-5, -2, 2, 5], [-4, 0, 3, 7], [-7, -3, 0, 3]],
]
prog = progs[seed % len(progs)]
beat = 60.0 / bpm; bar = 4 * beat
base = 57 + key  # around A3
t = 0.0; b = 0
while t < secs:
    ch = prog[b % len(prog)]
    # soft pad underneath
    for s in ch[:3]:
        put(pad(midi_hz(base - 12 + s), bar * 1.05, 0.035), t, rng.uniform(-0.3, 0.3))
    # bass note
    put(piano(midi_hz(base - 24 + ch[0]), bar * 1.2, 0.22), t, 0)
    # broken-chord arpeggio, sparse and gentle
    pattern = rng.choice([[0, 1, 2, 3, 2, 1, 2, 3], [0, 2, 1, 3, 0, 2, 3, 1], [0, 1, 2, 1, 3, 1, 2, 1]])
    for k, idx in enumerate(pattern):
        if rng.random() < 0.18 and k > 0:
            continue
        v = 0.11 + 0.04 * rng.random()
        put(piano(midi_hz(base + ch[idx]), 2.4, v), t + k * beat / 2 + rng.normal(0, 0.008), rng.uniform(-0.5, 0.5))
    # occasional high melody note
    if b % 2 == 1:
        put(piano(midi_hz(base + 12 + ch[rng.integers(0, 4)]), 3.0, 0.07), t + beat * rng.integers(1, 3), rng.uniform(-0.4, 0.4))
    t += bar; b += 1

# reverb: convolution with decaying noise impulse
ir_n = int(SR * 2.6); ti = np.arange(ir_n) / SR
def ir(): return rng.normal(0, 1, ir_n) * np.exp(-ti * 2.4)
def conv(x, h):
    m = len(x) + len(h) - 1; F = 1 << (m - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(h, F), F)[: len(x)]
wetL, wetR = conv(L, ir()), conv(R, ir())
wetL /= np.max(np.abs(wetL)) + 1e-9; wetR /= np.max(np.abs(wetR)) + 1e-9
dryL, dryR = L / (np.max(np.abs(L)) + 1e-9), R / (np.max(np.abs(R)) + 1e-9)
mix = np.stack([0.65 * dryL + 0.45 * wetL, 0.65 * dryR + 0.45 * wetR], axis=1)[: int(SR * secs)]
# fades + normalize to about -16 dBFS RMS
n = len(mix); fi, fo = int(SR * 2), int(SR * 4)
mix[:fi] *= np.linspace(0, 1, fi)[:, None]; mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix *= 10 ** (-16 / 20) / (np.sqrt(np.mean(mix ** 2)) + 1e-9)
mix = np.clip(mix, -0.95, 0.95)
sf.write(out, mix.astype(np.float32), SR)
print("ok", out, round(n / SR, 1), "s")
