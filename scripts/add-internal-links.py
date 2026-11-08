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
    # Emotional pangs → Fog and anchor ("storm")
    (
        "how-our-emotional-pangs-makes-us", 201916494,
        "the-fog-and-the-anchor",
        "storm",
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


def inject_link_into_prosemirror(doc, anchor_phrase, target_url):
    """
    Walk a ProseMirror JSON doc and wrap the FIRST occurrence of anchor_phrase
    (case-insensitive) in a text node with a link mark.
    Returns (modified_doc, matched_text | None).
    """
    pattern = re.compile(re.escape(anchor_phrase), re.IGNORECASE)
    matched = [None]

    def walk(node):
        if matched[0]:
            return node
        if node.get("type") == "html" and not matched[0]:
            html_content = node.get("attrs", {}).get("html", "")
            m = pattern.search(html_content)
            if m:
                matched[0] = m.group(0)
                replacement = f'<a href="{target_url}">{m.group(0)}</a>'
                new_html = html_content[:m.start()] + replacement + html_content[m.end():]
                return {**node, "attrs": {**node["attrs"], "html": new_html}}
            return node
        if node.get("type") == "text" and not matched[0]:
            # Skip if already has a link mark
            marks = node.get("marks", [])
            if any(m.get("type") == "link" for m in marks):
                return node
            text = node.get("text", "")
            m = pattern.search(text)
            if m:
                matched[0] = m.group(0)
                before = text[:m.start()]
                anchor = m.group(0)
                after = text[m.end():]
                result = []
                if before:
                    result.append({**node, "text": before})
                link_node = {
                    "type": "text",
                    "text": anchor,
                    "marks": marks + [{"type": "link", "attrs": {"href": target_url, "target": "_blank"}}],
                }
                result.append(link_node)
                if after:
                    result.append({**node, "text": after})
                return result  # signal: replace this node with list
        if "content" in node:
            new_content = []
            for child in node["content"]:
                result = walk(child)
                if isinstance(result, list):
                    new_content.extend(result)
                else:
                    new_content.append(result)
            return {**node, "content": new_content}
        return node

    new_doc = walk(doc)
    return new_doc, matched[0]


def fetch_draft(opener, post_id):
    url = f"{BASE_URL}/api/v1/drafts/{post_id}"
    try:
        with opener.open(urllib.request.Request(url)) as res:
            return json.loads(res.read())
    except urllib.error.HTTPError as e:
        return None


def update_post(opener, post_id, slug, anchor_phrase, target_url, dry_run):
    if dry_run:
        # For dry-run, just check body_html from public post for the phrase
        post = fetch_post(opener, slug)
        if not post:
            return False, None, "could not fetch post"
        body = post.get("body_html", "")
        m = re.search(re.escape(anchor_phrase), body, re.IGNORECASE)
        return True, m.group(0) if m else None, "dry-run"

    # Fetch draft (has draft_body as ProseMirror JSON)
    draft = fetch_draft(opener, post_id)
    if not draft:
        return False, None, "could not fetch draft"

    draft_body_str = draft.get("draft_body", "")
    if not draft_body_str:
        return False, None, "no draft_body"

    try:
        doc = json.loads(draft_body_str)
    except Exception:
        return False, None, "draft_body not valid JSON"

    # Check if link already present
    if target_url in draft_body_str:
        return True, None, "link already present"

    new_doc, matched_text = inject_link_into_prosemirror(doc, anchor_phrase, target_url)
    if not matched_text:
        return False, None, f"phrase {anchor_phrase!r} not found in draft_body"

    new_draft_body = json.dumps(new_doc)
    headers = {
        "Content-Type": "application/json",
        "Referer": f"{BASE_URL}/publish/post/{post_id}",
        "Origin": BASE_URL,
    }
    draft_payload = json.dumps({
        "draft_title": draft.get("draft_title", ""),
        "draft_subtitle": draft.get("draft_subtitle", ""),
        "draft_body": new_draft_body,
    }).encode()
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
        return False, None, f"draft PUT failed {e.code}"

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
        return True, matched_text, "ok"
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

        success, matched, msg = update_post(
            opener, source_id, source_slug, anchor_phrase, target_url, args.dry_run
        )
        if msg == "link already present":
            print(f"  ✓ link already present")
            skip += 1
        elif matched is None and success:
            print(f"  ⚠ {msg}")
            skip += 1
        elif success:
            print(f"  {'[dry-run] ' if args.dry_run else ''}✅ linked: \"{matched}\"")
            ok += 1
        else:
            print(f"  ❌ {msg}")
            fail += 1

        time.sleep(0.6)

    print(f"\nDone: {ok} linked, {skip} skipped, {fail} failed")


if __name__ == "__main__":
    main()
