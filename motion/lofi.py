#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lofi.py — موسيقى خلفية «تعليمية» هادئة (Lo-fi) مولّدة بالكود
==============================================================
موسيقى أصلية 100% (بدون حقوق) تناسب ريلز البرمجة والشروحات:
بيانو كهربائي بأكوردات دافئة + باص ناعم + إيقاع خفيف + خشخشة أسطوانة.

  python3 lofi.py -o music.wav --seconds 50
  python3 lofi.py -o music.wav --seconds 50 --bpm 76 --seed 4
ثم:
  python3 code_typer.py fahad.json -o reel.mp4 --music music.wav --music-volume 0.6
"""

import argparse
import os
import subprocess
import tempfile
import wave

import numpy as np

SR = 44100

# Fmaj7 → Em7 → Dm7 → Cmaj7 (تقدّم هادئ ومريح للتركيز)
PROGRESSION = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]
PENTA = [72, 74, 76, 79, 81, 84]   # سلّم خماسي للّحن


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n, attack, decay):
    t = np.arange(n) / SR
    a = np.clip(t / attack, 0, 1)
    return a * np.exp(-t / decay)


def rhodes(m, dur, vel):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = hz(m)
    tone = (np.sin(2 * np.pi * f * t)
            + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3)
            + 0.12 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 6)
            + 0.08 * np.sin(2 * np.pi * 7 * f * t) * np.exp(-t * 25))   # «ضربة» المطرقة
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.5 * t)
    return tone * trem * env(n, 0.006, dur * 0.55) * vel


def bell(m, dur, vel):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = hz(m)
    tone = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2.01 * f * t) * np.exp(-t * 4)
    return tone * env(n, 0.004, 0.45) * vel


def bass(m, dur, vel):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.tanh(1.6 * np.sin(2 * np.pi * hz(m) * t))
    return s * env(n, 0.01, dur * 0.7) * vel


def kick(rnd):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 45 + 75 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * 0.9


def snare(rnd):
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    noise = rnd.standard_normal(n)
    noise = noise - np.convolve(noise, np.ones(6) / 6, 'same')     # تخفيف الصوت المنخفض
    body = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 30)
    return (noise * 0.35 * np.exp(-t * 18) + body * 0.4) * 0.6


def hat(rnd, open_=False):
    n = int((0.12 if open_ else 0.05) * SR)
    t = np.arange(n) / SR
    noise = rnd.standard_normal(n)
    noise = np.diff(noise, prepend=0)                                # صوت عالٍ فقط
    return noise * np.exp(-t * (25 if open_ else 70)) * 0.12


def place(buf, sig, at):
    s = int(at * SR)
    e = min(len(buf), s + len(sig))
    if s < len(buf) and e > s:
        buf[s:e] += sig[:e - s]


def compose(seconds, bpm, seed):
    rnd = np.random.default_rng(seed)
    beat = 60.0 / bpm
    bar = beat * 4
    n = int((seconds + 2) * SR)
    keys = np.zeros(n)
    low = np.zeros(n)
    drums = np.zeros(n)
    lead = np.zeros(n)
    bars = int(seconds / bar) + 2
    swing = beat * 0.08
    for b in range(bars):
        t0 = b * bar
        chord = PROGRESSION[b % len(PROGRESSION)]
        # أكورد على الضربة 1 وعلى «و» الضربة 2 (أخف)
        for i, m in enumerate(chord):
            place(keys, rhodes(m, bar * 0.9, 0.16), t0 + i * 0.012)
            place(keys, rhodes(m + 12 if i == 3 else m, beat * 1.6, 0.07),
                  t0 + beat * 1.5 + swing + i * 0.01)
        place(low, bass(chord[0] - 12, beat * 1.8, 0.32), t0)
        place(low, bass(chord[0] - 12 + (7 if b % 2 else 0), beat * 1.4, 0.24), t0 + beat * 2.5 + swing)
        # الإيقاع يدخل بعد أول بارين
        if b >= 2:
            place(drums, kick(rnd), t0)
            place(drums, kick(rnd) * 0.7, t0 + beat * 2.5 + swing)
            if b % 4 == 3:
                place(drums, kick(rnd) * 0.5, t0 + beat * 3.5 + swing)
            place(drums, snare(rnd), t0 + beat)
            place(drums, snare(rnd), t0 + beat * 3)
            for k in range(8):
                off = swing if k % 2 else 0
                place(drums, hat(rnd, open_=(k == 7 and b % 2 == 1)) * (1 if k % 2 == 0 else 0.6),
                      t0 + k * beat / 2 + off)
        # لحن خفيف متقطّع بعد البار الرابع
        if b >= 4:
            for k in range(8):
                if rnd.random() < 0.28:
                    m = int(rnd.choice(PENTA))
                    place(lead, bell(m, beat, 0.09), t0 + k * beat / 2 + (swing if k % 2 else 0))
    # خشخشة أسطوانة
    crackle = np.zeros(n)
    idx = rnd.integers(0, n, int(seconds * 18))
    crackle[idx] = rnd.standard_normal(len(idx)) * 0.25
    hiss = np.convolve(rnd.standard_normal(n), np.ones(30) / 30, 'same') * 0.025
    mix = keys + low + drums * 0.8 + lead + crackle + hiss
    # ظهور واختفاء تدريجي
    fade_in, fade_out = int(1.5 * SR), int(2.5 * SR)
    total = int(seconds * SR)
    mix = mix[:total]
    mix[:fade_in] *= np.linspace(0, 1, fade_in)
    mix[-fade_out:] *= np.linspace(1, 0, fade_out)
    return mix / (np.max(np.abs(mix)) + 1e-9) * 0.8


def write_wav(path, x):
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32000).astype('<i2').tobytes())


def main():
    ap = argparse.ArgumentParser(description='موسيقى Lo-fi تعليمية هادئة')
    ap.add_argument('-o', '--out', default='music.wav')
    ap.add_argument('--seconds', type=float, default=50)
    ap.add_argument('--bpm', type=float, default=78)
    ap.add_argument('--seed', type=int, default=11)
    a = ap.parse_args()
    raw = os.path.join(tempfile.mkdtemp(), 'raw.wav')
    write_wav(raw, compose(a.seconds, a.bpm, a.seed))
    # دفء «lo-fi»: قص الترددات العالية + صدى غرفة خفيف + ستيريو بسيط
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', raw, '-af',
                    'lowpass=f=4200,highpass=f=35,aecho=0.8:0.6:45|90:0.18|0.10,'
                    'pan=stereo|c0=c0|c1=c0,aphaser=in_gain=0.9:out_gain=0.9:speed=0.15:decay=0.3,'
                    'loudnorm=I=-18:TP=-2', '-ar', '44100', a.out], check=True)
    print('✓', a.out)


if __name__ == '__main__':
    main()
