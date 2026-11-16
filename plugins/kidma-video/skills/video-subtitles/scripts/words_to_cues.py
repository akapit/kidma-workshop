#!/usr/bin/env python3
"""Turn a word-timed transcript into caption cues (one short group on screen at a time).

Input: JSON list of words [{"text": "...", "start": 0.18, "end": 0.38, "type": "word"}, ...]
       (ElevenLabs Scribe `words`, or any source with the same fields; also accepts
       {"words": [...]} or a Scribe result with "transcripts":[{"words":[...]}]).
Output: cues JSON [{"text": "...", "start": s, "end": e}, ...] to stdout or --out.

Rules (hyperframes captions reference): 3-5 words conversational, break at a sentence end
or a real pause, balanced splits of long sentences, cue opens just before its first word
and holds until the next cue (or a short tail after a pause). Never starts at exactly 0.
"""
import argparse, json, math, sys

END_PUNCT = (".", "?", "!", "…")


def load_words(path):
    d = json.load(open(path, encoding="utf-8"))
    if isinstance(d, dict):
        if "transcripts" in d:
            d = d["transcripts"][0]["words"]
        elif "words" in d:
            d = d["words"]
    words = [w for w in d if w.get("type", "word") == "word" and w.get("text", "").strip()]
    for w in words:
        w["text"] = w["text"].strip()
    return words


def sentences(words, pause):
    out, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["start"] - w["end"]) if nxt else 99
        if w["text"].endswith(END_PUNCT) or gap >= pause:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def split_balanced(sent, max_words):
    n = len(sent)
    if n <= max_words:
        return [sent]
    k = math.ceil(n / max_words)
    chunks, start = [], 0
    for c in range(1, k):
        ideal = round(c * n / k)
        best, best_score = ideal, -1
        for cut in range(max(start + 1, ideal - 1), min(n - 1, ideal + 1) + 1):
            prev = sent[cut - 1]
            gap = sent[cut]["start"] - prev["end"]
            # tiny gaps are timing noise: only a real pause (>=120ms) or a comma pulls the cut
            # away from the balanced midpoint; otherwise the cut closest to ideal wins
            score = (gap if gap >= 0.12 else 0) + (0.5 if prev["text"].endswith(",") else 0) - 0.05 * abs(cut - ideal)
            if score > best_score:
                best, best_score = cut, score
        chunks.append(sent[start:best])
        start = best
    chunks.append(sent[start:])
    return chunks


def build(words, max_words, pause, lead, tail, duration):
    groups = [g for s in sentences(words, pause) for g in split_balanced(s, max_words)]
    cues = []
    for i, g in enumerate(groups):
        start = max(0.12, g[0]["start"] - lead) if i == 0 else g[0]["start"] - lead
        cues.append({"text": " ".join(w["text"] for w in g), "start": start, "last_end": g[-1]["end"]})
    for i in range(1, len(cues)):  # pass 1: never open before the previous cue's last word ends
        cues[i]["start"] = max(cues[i]["start"], cues[i - 1]["last_end"])
    for i, c in enumerate(cues):   # pass 2: hold each cue to the next (no flicker) or a short tail
        if i + 1 < len(cues):
            nxt = cues[i + 1]["start"]
            c["end"] = nxt if nxt - c["last_end"] <= tail * 2 else c["last_end"] + tail
        else:
            c["end"] = duration if duration else c["last_end"] + tail
    # transcribers often drop the final period ("כל טוב" -> "כל טוב.")
    if cues and not cues[-1]["text"].endswith(END_PUNCT + (",",)):
        cues[-1]["text"] += "."
    return [{"text": c["text"], "start": round(c["start"], 2), "end": round(c["end"], 2)} for c in cues]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("words_json")
    ap.add_argument("--out")
    ap.add_argument("--max-words", type=int, default=5)
    ap.add_argument("--pause", type=float, default=0.6, help="gap (s) that ends a group")
    ap.add_argument("--lead", type=float, default=0.1, help="show cue this long before first word")
    ap.add_argument("--tail", type=float, default=0.35, help="hold after last word when a pause follows")
    ap.add_argument("--duration", type=float, help="video duration; last cue holds to it")
    a = ap.parse_args()
    cues = build(load_words(a.words_json), a.max_words, a.pause, a.lead, a.tail, a.duration)
    s = json.dumps(cues, ensure_ascii=False, indent=1)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(s + "\n")
    print(s)
