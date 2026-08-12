# gen_story.py — build a multi-tier sci-fi story data.js (graded-reader style).
# Each tier restricts vocabulary to a frequency ceiling of the NGSL 1.2 list:
#   L1 = top 500 (≈A1), L2 = top 1000 (≈A2), L3 = top 1800 (≈B1), L4 = full 2809 (≈C1).
# Pipeline per tier:
#   1. narrative (N chapters) constrained to the tier's allowed word set.
#   2. leftover headwords (not present verbatim in narrative) -> 8 "Orion Archive" chapters
#      (only words within the tier ceiling), each word written verbatim in a framed log sentence.
#   3. vocab for ALL 2809 (word,zh,ex,exs,ch) using first occurrence across the FULL L4 story.
# Top-level data:
#   { storyTitle, totalNGSL:2809, rankedWords:[...by freq rank...],
#     stories:{ L1:{title,chapters,narrCount,ngsl}, ... L4 },
#     vocab:union(2809), ngslGloss:GLOSS, dict }
import json, re, random

GLOSS = json.load(open('ngsl_gloss.json', encoding='utf-8'))
RANKED = json.load(open('ngsl_ranked_words.json', encoding='utf-8'))  # rank-ordered words
old_raw = open('data.js', encoding='utf-8').read().replace('window.APP_DATA = ', '').rstrip().rstrip(';')
OLD = json.loads(old_raw)
DICT = OLD.get('dict', {})
for _k in ('aeloria', 'kael'):
    DICT.pop(_k, None)

# tier configs: (key, ceiling-size, narrative file)
TIERS = [
    ("L1", 500, "story_L1.json"),
    ("L2", 1000, "story_L2.json"),
    ("L3", 1800, "story_L3.json"),
    ("L4", 2809, "story_narrative.json"),
]

tok = re.compile(r"[A-Za-z][A-Za-z'\-]*")
random.seed(20260812)


def norm_key(s):
    s = s.lower()
    s = re.sub(r"'(s|re|ve|ll|t)?$", "", s)
    s = re.sub(r"[^a-z]", "", s)
    return s


def ceiling_set(n):
    # words from the true frequency ranking, intersected with GLOSS (drop case-oddities like 'I'/'TRUE')
    return set(w for w in RANKED[:n] if w in GLOSS)


# ---- build full vocab from the L4 (complete) story so every headword has occ ----
L4 = json.load(open("story_narrative.json", encoding='utf-8'))
l4_chapters = [{'title': c['title'], 'paras': list(c['paras'])} for c in L4['narrative']]
arch_titles = L4['archiveTitles']
# archive framing uses the Chinese gloss (zh) instead of English def (en) so that
# low-tier stories don't leak advanced vocabulary from the English definitions.
templates = [
    "In the Orion Archive, the word '{w}' means: {zh}.",
    "The book of Orion keeps the word '{w}': {zh}.",
    "Era wrote the word '{w}' so we may learn it: {zh}.",
    "When the signal came, the machine saved the word '{w}': {zh}.",
    "The old city kept '{w}' for the children: {zh}.",
    "A letter from the past named '{w}' and said: {zh}.",
    "The star map showed '{w}' with this meaning: {zh}.",
    "Teachers in the new home defined '{w}' for us: {zh}.",
]

# L4 leftover -> archive
l4_covered = set()
for c in L4['narrative']:
    for p in c['paras']:
        for m in tok.findall(p):
            k = norm_key(m)
            if k in GLOSS:
                l4_covered.add(k)
l4_leftover = sorted(w for w in GLOSS if w not in l4_covered)
N = len(arch_titles)
per = len(l4_leftover) // N + (1 if len(l4_leftover) % N else 0)
l4_arch = []
for i, t in enumerate(arch_titles):
    chunk = l4_leftover[i * per:(i + 1) * per]
    paras = ["These are the words Era salvaged from the silent edge of Orion, set down so the living may learn them."]
    for j, w in enumerate(chunk):
        tpl = templates[(i * 37 + j) % len(templates)]
        zh = (GLOSS[w].get('zh') or '').strip() or GLOSS[w].get('en', '')
        paras.append(tpl.replace('{w}', w).replace('{zh}', zh))
    l4_arch.append({'title': t, 'paras': paras})
l4_chapters += l4_arch

# full vocab from L4 chapters
occ = {}
for ci, ch in enumerate(l4_chapters):
    for p in ch['paras']:
        for m in tok.findall(p):
            k = norm_key(m)
            if k in GLOSS:
                if k not in occ:
                    occ[k] = (ci, [p])
                else:
                    _, exs = occ[k]
                    if p not in exs and len(exs) < 3:
                        exs.append(p)
vocab = {}
for w in GLOSS:
    ci, exs = occ[w]
    vocab[w] = {'word': w, 'zh': GLOSS[w].get('zh', ''), 'ex': exs[0], 'exs': exs, 'ch': ci}


# ---- per-tier assembly ----
stories = {}
for key, n, fn in TIERS:
    story = json.load(open(fn, encoding='utf-8'))
    narr = story['narrative']
    a_titles = story['archiveTitles']
    ce = ceiling_set(n)
    narr_chapters = [{'title': c['title'], 'paras': list(c['paras'])} for c in narr]
    covered = set()
    for c in narr:
        for p in c['paras']:
            for m in tok.findall(p):
                k = norm_key(m)
                if k in ce:
                    covered.add(k)
    leftover = sorted(w for w in ce if w not in covered)
    Na = len(a_titles)
    pa = len(leftover) // Na + (1 if leftover else 0)
    arch = []
    for i, t in enumerate(a_titles):
        chunk = leftover[i * pa:(i + 1) * pa]
        paras = ["These are the words Era salvaged from the silent edge of Orion, set down so the living may learn them."]
        for j, w in enumerate(chunk):
            tpl = templates[(i * 37 + j) % len(templates)]
            zh = (GLOSS[w].get('zh') or '').strip() or GLOSS[w].get('en', '')
            paras.append(tpl.replace('{w}', w).replace('{zh}', zh))
        arch.append({'title': t, 'paras': paras})
    chapters = narr_chapters + arch
    stories[key] = {
        'title': story['storyTitle'],
        'chapters': chapters,
        'narrCount': len(narr_chapters),
        'ngsl': {'total': len(ce), 'covered': len(ce), 'coveredWords': sorted(ce)},
    }

data = {
    'storyTitle': "猎户信号 · 分级故事集 (Orion Signal — Graded Readers)",
    'totalNGSL': 2809,
    'rankedWords': RANKED,
    'stories': stories,
    'vocab': vocab,
    'ngslGloss': GLOSS,
    'dict': DICT,
}

with open('data.js', 'w', encoding='utf-8') as f:
    f.write('window.APP_DATA = ')
    json.dump(data, f, ensure_ascii=False)
    f.write(';')

# ---- verify ----
allok = True
for key, n, fn in TIERS:
    s = stories[key]
    ch = s['chapters']
    cov = set()
    for c in ch:
        for p in c['paras']:
            for m in tok.findall(p):
                k = norm_key(m)
                if k in GLOSS:
                    cov.add(k)
    missing = [w for w in s['ngsl']['coveredWords'] if w not in cov]
    print(f"{key}: ceiling={s['ngsl']['total']} narr={s['narrCount']} chapters={len(ch)} "
          f"covered={len(cov)} ngsl.covered={s['ngsl']['covered']} missing_in_self={len(missing)}")
    if missing:
        allok = False
        print("   MISSING:", missing[:10])
print("vocab (union):", len(vocab), " rankedWords:", len(RANKED), " dict:", len(DICT))
print("ALL OK" if allok else "HAS ISSUES")
print("data.js bytes:", len(open('data.js', encoding='utf-8').read()))
