# Wraps the skill's audio.py: same mix, but the music bed fades out under the Qur'an verse.
import sys, json, os, numpy as np
M = '/root/.claude/plugins/synced/71a1fc52-e708-48e6-814c-cd380002c539_1613d6aa-cae0-4f11-a495-525925ad275d/majed-video/video-ad-editor/motion'
sys.path.insert(0, M); os.chdir(M)
import audio
proj = sys.argv[1]
tl = json.load(open(os.path.join(proj, 'timeline.json')))
sc = {s['id']: s for s in tl['scenes']}
A, B, F = sc['s6']['start'] - 0.4, sc['s6']['end'] + 0.2, 0.8      # silent window + fade length
orig = audio.build_bed
def quiet(tl_, music, dur, seed=7):
    bed = orig(tl_, music, dur, seed=seed); SR = audio.SR
    t = np.arange(len(bed)) / SR
    g = np.clip(np.maximum((A - t) / F, (t - B) / F), 0, 1)       # 1 → 0 before A, 0 → 1 after B
    print(f'  🔇 الموسيقى تسكت تحت الآية: {A:.2f}s → {B:.2f}s')
    return bed * g[:, None]
audio.build_bed = quiet
sys.argv = ['audio.py', proj]
audio.main()
