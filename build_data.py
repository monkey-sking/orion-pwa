import json, re

SRC = "story_raw.json"
OUT = "data.js"

raw = json.load(open(SRC, encoding="utf-8"))
content = raw["data"]["document"]["content"]

# cut off author note / attachments
cut = content.find("作者注")
if cut != -1:
    content = content[:cut]

# story title from h2
m = re.search(r"<h2>(?:<b>)?(.*?)(?:</b>)?</h2>", content, re.S)
story_title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else "The Last Light of Aeloria"

parts = re.split(r"<h3>(.*?)</h3>", content, flags=re.S)
bodies = parts[1:]
# gloss: word immediately followed by full-width （zh）. Two patterns:
#  - lookahead letter  -> add a space after the word (fixes "solarcrystals")
#  - otherwise         -> no space
gloss_look = re.compile(r"([A-Za-z][A-Za-z'’\-]*)\（([^）]+)\）(?=[A-Za-z])")
gloss_plain = re.compile(r"([A-Za-z][A-Za-z'’\-]*)\（([^）]+)\）")
tag_re = re.compile(r"<[^>]+>")


def clean_text(p):
    s = gloss_look.sub(r"\1 ", p)
    s = gloss_plain.sub(r"\1", s)
    s = tag_re.sub("", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def to_html(p):
    s = gloss_look.sub(r'<span class="gw" data-w="\1" data-zh="\2">\1</span> ', p)
    s = gloss_plain.sub(r'<span class="gw" data-w="\1" data-zh="\2">\1</span>', s)
    s = s.replace("<b>", "<strong>").replace("</b>", "</strong>")
    s = s.replace("<em>", "<em>").replace("</em>", "</em>")
    s = tag_re.sub("", s)
    return s


vocab = {}
chapters = []
for i in range(0, len(bodies) - 1, 2):
    title = re.sub(r"<[^>]+>", "", bodies[i]).strip()
    body = bodies[i + 1]
    paras_raw = re.findall(r"<p>(.*?)</p>", body, flags=re.S)
    paras_html = []
    for p in paras_raw:
        if p.strip() == "":
            continue
        for wm in gloss_plain.finditer(p):
            key = wm.group(1).lower()
            c = clean_text(p)
            if key not in vocab:
                vocab[key] = {
                    "word": wm.group(1),
                    "zh": wm.group(2).strip(),
                    "ex": c,
                    "exs": [c],
                    "ch": len(chapters),
                }
            else:
                if c not in vocab[key]["exs"] and len(vocab[key]["exs"]) < 3:
                    vocab[key]["exs"].append(c)
        paras_html.append(to_html(p))
    if paras_html:
        chapters.append({"title": title, "paras": paras_html})

data = {
    "storyTitle": story_title,
    "totalNGSL": 2809,
    "chapters": chapters,
    "vocab": vocab,
}

with open(OUT, "w", encoding="utf-8") as f:
    f.write("window.APP_DATA = ")
    json.dump(data, f, ensure_ascii=False)
    f.write(";")

print("chapters:", len(chapters))
print("unique glossed words:", len(vocab))
print("sample:", list(vocab.items())[:3])
