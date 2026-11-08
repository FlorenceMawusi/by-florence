#!/usr/bin/env python3
"""
Add internal links between related posts on Substack.

Each entry defines a source post, a target post, and ONE phrase in the source
post's body that should become a hyperlink to the target post.

Usage:
  export SUBSTACK_SID="your_cookie_value"
  python3 scripts/add-internal-links.py           # live run
  python3 scripts/add-internal-links.py --dry-run # preview only
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

SUBDOMAIN = "sproutingplant"
BASE_URL = f"https://{SUBDOMAIN}.substack.com"
SITE_URL = "https://byflorence.net"

# ---------------------------------------------------------------------------
# Internal link map
# Each tuple: (source_slug, source_id, target_slug, anchor_phrase)
# anchor_phrase is a substring to find in the HTML and wrap with <a href>.
# Keep one link per source post to stay natural.
# ---------------------------------------------------------------------------
LINKS = [
    # Boundaries post → Assertiveness post ("the truth is...")
    (
        "why-your-healthy-boundaries-are-just", 201915000,
        "why-assertiveness-is-a-divine-calling",
        "truth",
    ),
    # Assertiveness post → Boundaries post ("Boundaries")
    (
        "why-assertiveness-is-a-divine-calling", 199672062,
        "why-your-healthy-boundaries-are-just",
        "Boundaries",
    ),
    # Smart person's trap → Stop living in your head ("stuck")
    (
        "the-smart-persons-trap", 223013134,
        "youre-no-one-and-everyone",
        "stuck",
    ),
    # Emotional pangs → Fog and anchor ("feeling")
    (
        "how-our-emotional-pangs-makes-us", 201916494,
        "the-fog-and-the-anchor",
        "feeling",
    ),
    # Fog and anchor → Emotional pangs ("emotions")
    (
        "the-fog-and-the-anchor", 213959604,
        "how-our-emotional-pangs-makes-us",
        "emotions",
    ),
    # Forgiveness → Being disliked ("fight-or-flight")
    (
        "on-forgiveness-why-cruelty-is-never", 202324790,
        "my-journey-of-being-disliked",
        "flight",
    ),
    # Being disliked → Forgiveness ("pain")
    (
        "my-journey-of-being-disliked", 202328055,
        "on-forgiveness-why-cruelty-is-never",
        "pain",
    ),
    # Karpathy loop → The perfect cube ("AI")
    (
        "understanding-the-kaparthy-loop", 199636033,
        "the-perfect-cube",
        "AI",
    ),
    # Lion King → Forgiveness ("wrong")
    (
        "notes-from-the-lion-king", 199503692,
        "on-forgiveness-why-cruelty-is-never",
        "wrong",
    ),
    # I wanted to be a bird → Not half human ("whole")
    (
        "i-wanted-to-be-a-bird", 194742217,
        "youre-not-half-human",
        "whole",
    ),
    # West African heritage → Assertiveness ("power")
    (
        "what-being-an-ewe-lady-taught-me", 196569631,
        "why-assertiveness-is-a-divine-calling",
        "power",
    ),
    # Who decided what you eat → Feminism journey ("borrowed")
    (
        "who-decided-what-you-should-eat", 196144244,
        "feminism-my-journey",
        "borrowed",
    ),
    # Stop living in your head → Smart person's trap ("trap")
    (
        "youre-no-one-and-everyone", 222920992,
        "the-smart-persons-trap",
        "trap",
    ),
]


def get_session_cookie():
    sid = os.environ.get("SUBSTACK_SID")
    if sid:
        return sid
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("SUBSTACK_SID="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def make_opener(sid):
    opener = urllib.request.build_opener()
    opener.addheaders = [
        ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"),
        ("Cookie", f"substack.sid={sid}"),
    ]
    return opener


def fetch_post(opener, slug):
    url = f"{BASE_URL}/api/v1/posts/{slug}"
    try:
        with opener.open(urllib.request.Request(url)) as res:
            return json.loads(res.read())
    except urllib.error.HTTPError as e:
        print(f"  ❌ fetch failed {e.code} for {slug}")
        return None


def inject_link(body_html, anchor_phrase, target_url):
    """
    Find the FIRST occurrence of anchor_phrase (case-insensitive, outside existing <a> tags)
    and wrap it with a link. Returns (new_html, matched_text | None).
    """
    # Build a pattern that matches the phrase but only if NOT already inside an <a ...>
    # Strategy: split on <a ...>...</a> blocks, inject only into text segments.
    parts = re.split(r'(<a\s[^>]*>.*?</a>)', body_html, flags=re.DOTALL | re.IGNORECASE)
    injected = False
    result = []
    matched_text = None
    for part in parts:
        if not injected and not part.startswith('<a'):
            pattern = re.compile(re.escape(anchor_phrase), re.IGNORECASE)
            m = pattern.search(part)
            if m:
                matched_text = m.group(0)
                replacement = f'<a href="{target_url}">{matched_text}</a>'
                part = part[:m.start()] + replacement + part[m.end():]
                injected = True
        result.append(part)
    return ''.join(result), matched_text


def update_post(opener, post_id, slug, new_body, dry_run):
    if dry_run:
        return True, "dry-run"

    # Fetch current draft fields to avoid overwriting anything
    post = fetch_post(opener, slug)
    if not post:
        return False, "could not re-fetch post"

    draft_payload = json.dumps({
        "draft_title": post.get("title", ""),
        "draft_subtitle": post.get("subtitle", ""),
        "draft_body": new_body,
    }).encode()
    headers = {
        "Content-Type": "application/json",
        "Referer": f"{BASE_URL}/publish/post/{post_id}",
        "Origin": BASE_URL,
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/v1/drafts/{post_id}",
        data=draft_payload,
        method="PUT",
        headers=headers,
    )
    try:
        with opener.open(req) as res:
            json.loads(res.read())
    except urllib.error.HTTPError as e:
        return False, f"draft PUT failed {e.code}"

    pub_payload = json.dumps({"send": False, "share_automatically": False}).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/api/v1/drafts/{post_id}/publish",
        data=pub_payload,
        method="POST",
        headers=headers,
    )
    try:
        with opener.open(req) as res:
            json.loads(res.read())
        return True, "ok"
    except urllib.error.HTTPError as e:
        return False, f"publish failed {e.code} {e.read().decode()[:120]}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sid = get_session_cookie()
    if not sid:
        print("❌ SUBSTACK_SID not set.")
        sys.exit(1)

    opener = make_opener(sid)
    ok = fail = skip = 0

    for source_slug, source_id, target_slug, anchor_phrase in LINKS:
        target_url = f"{SITE_URL}/posts/{target_slug}"
        print(f"→ {source_slug}  [{anchor_phrase!r} → /posts/{target_slug}]")

        post = fetch_post(opener, source_slug)
        if not post:
            fail += 1
            continue

        body = post.get("body_html") or post.get("draft_body") or ""
        if not body:
            print("  ⚠ no body_html, skipping")
            skip += 1
            continue

        # Skip if link already exists
        if target_url in body:
            print("  ✓ link already present")
            skip += 1
            continue

        new_body, matched = inject_link(body, anchor_phrase, target_url)
        if not matched:
            print(f"  ⚠ phrase {anchor_phrase!r} not found in body, skipping")
            skip += 1
            continue

        print(f"  {'[dry-run] ' if args.dry_run else ''}linking: \"{matched}\" → {target_url}")

        success, msg = update_post(opener, source_id, source_slug, new_body, args.dry_run)
        if success:
            print(f"  ✅ {msg}")
            ok += 1
        else:
            print(f"  ❌ {msg}")
            fail += 1

        time.sleep(0.6)

    print(f"\nDone: {ok} linked, {skip} skipped, {fail} failed")


if __name__ == "__main__":
    main()
