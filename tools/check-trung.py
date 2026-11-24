#!/usr/bin/env python3
"""Kiểm tra trùng từ khóa / chủ đề / tiêu đề TRƯỚC KHI ĐĂNG.

Dùng:
  python3 tools/check-trung.py "<tiêu đề mới>" [--kw "<từ khóa chính>"] [--kenh UCxxxx]
  python3 tools/check-trung.py --dir kenh-okx/video-ngan/07-okx-promo-code

So với: mọi video đang có trên kênh YouTube (trang /videos, /shorts và RSS)
và mọi post.json trong kenh-*/ (video đã làm, kể cả chưa đăng).
Thoát mã 1 nếu có trùng → KHÔNG đăng, đổi từ khóa/tiêu đề trước.
"""
import json, re, sys, glob, os, urllib.request, html

CHANNEL = "UCWRCJ6cISKjXW7Gi-l97cuw"  # LifeProsper Hub
STOP = set("the a an and or of to in on for with your you is it what how why where which do does can i my new 2025 2026 2027 guide explained".split())


def norm(t):
    t = html.unescape(t).lower()
    t = re.sub(r"\(.*?\)", " ", t)
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return " ".join(t.split())


def core(t):
    """Cụm từ khóa ở đầu tiêu đề: phần trước dấu ':' hoặc '('."""
    t = html.unescape(t)
    return norm(re.split(r"[:(\-–|]", t)[0])


def toks(t):
    return {w for w in norm(t).split() if w not in STOP and w != "okx"}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")


def channel_titles(ch):
    out = {}
    try:
        x = get(f"https://www.youtube.com/feeds/videos.xml?channel_id={ch}")
        for vid, title in re.findall(r"<yt:videoId>(.*?)</yt:videoId>.*?<title>(.*?)</title>", x, re.S):
            out[vid] = html.unescape(title)
    except Exception as e:
        print(f"⚠ không đọc được RSS kênh: {e}")
    pats = {  # trang kênh: video dài (lockupViewModel) và Shorts (shortsLockupViewModel), id và tiêu đề theo cùng thứ tự
        "videos": (r'"contentId":"([\w-]{11})"', r'"lockupMetadataViewModel":\{"title":\{"content":"((?:[^"\\]|\\.)*)"'),
        "shorts": (r'"reelWatchEndpoint":\{"videoId":"([\w-]{11})"', r'"primaryText":\{"content":"((?:[^"\\]|\\.)*)"'),
    }
    for tab, (pid, ptitle) in pats.items():
        try:
            x = get(f"https://www.youtube.com/channel/{ch}/{tab}?hl=en")
            ids = list(dict.fromkeys(re.findall(pid, x)))
            titles = re.findall(ptitle, x)
            if len(ids) != len(titles):
                print(f"⚠ trang {tab}: {len(ids)} id nhưng {len(titles)} tiêu đề, chỉ lấy tiêu đề")
                ids = [f"{tab}-{i}" for i in range(len(titles))]
            for vid, t in zip(ids, titles):
                out.setdefault(vid, html.unescape(json.loads(f'"{t}"')))
        except Exception as e:
            print(f"⚠ không đọc được trang {tab}: {e}")
    if not out:
        print("✗ không lấy được danh sách video của kênh → KHÔNG đăng khi chưa kiểm được")
        sys.exit(1)
    return out


def local_titles(skip_dir=None):
    out = {}
    for p in glob.glob("kenh-*/video-*/*/post.json"):
        d = os.path.dirname(p)
        if skip_dir and os.path.abspath(d) == os.path.abspath(skip_dir):
            continue
        try:
            out[d] = json.load(open(p))["youtube"]["title"]
        except Exception:
            pass
    return out


def main():
    a = sys.argv[1:]
    kw = title = None
    ch, vdir = CHANNEL, None
    i = 0
    while i < len(a):
        if a[i] == "--kw": kw = a[i + 1]; i += 2
        elif a[i] == "--kenh": ch = a[i + 1]; i += 2
        elif a[i] == "--dir": vdir = a[i + 1]; i += 2
        else: title = a[i]; i += 1
    if vdir:
        post = json.load(open(os.path.join(vdir, "post.json")))
        title = post["youtube"]["title"]
        try: kw = kw or json.load(open(os.path.join(vdir, "plan.json")))["keyword"]
        except Exception: pass
        kw = kw or post["youtube"]["tags"][0]
    if not title:
        print(__doc__); sys.exit(2)
    kw = kw or core(title)
    nk, ct, tt = norm(kw), core(title), toks(title)
    print(f"Kiểm tra: “{title}”  · từ khóa: {kw}")
    hits = []
    for src, items in (("KÊNH", channel_titles(ch)), ("ĐÃ LÀM", local_titles(vdir))):
        for ref, t in items.items():
            why = []
            if core(t) == ct: why.append("trùng cụm từ khóa đầu tiêu đề")
            if nk and (core(t) == nk or norm(t).startswith(nk + " ") and len(nk.split()) >= 3): why.append("trùng từ khóa chính")
            ot = toks(t)
            if tt and ot and len(tt & ot) / len(tt | ot) >= 0.6: why.append("tiêu đề gần giống")
            if norm(t) == norm(title): why.append("trùng y hệt tiêu đề")
            if why:
                link = f"https://www.youtube.com/watch?v={ref}" if src == "KÊNH" else ref
                hits.append(f"  ✗ [{src}] “{t}” — {', '.join(dict.fromkeys(why))}\n      {link}")
    if hits:
        print("\n".join(hits))
        print("→ CÓ TRÙNG: đổi sang từ khóa chưa dùng và viết tiêu đề khác trước khi đăng.")
        sys.exit(1)
    print("✓ Không trùng từ khóa/tiêu đề với video trên kênh và video đã làm.")


if __name__ == "__main__":
    main()
