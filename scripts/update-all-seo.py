#!/usr/bin/env python3
"""
Batch update all 20 posts with SEO-optimised titles and subtitles.
Run update-post-seo.py first to confirm it works on one post.

Usage:
  export SUBSTACK_SID="your_cookie_value"
  python3 scripts/update-all-seo.py

Add --dry-run to preview changes without applying them.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

SUBDOMAIN = "sproutingplant"
BASE_URL = f"https://{SUBDOMAIN}.substack.com"

UPDATES = [
    {
        "slug": "the-smart-persons-trap",
        "id": 223013134,
        "title": "Why Smart People Can't Think Their Way to Peace",
        "subtitle": "How over-relying on intellect blocks emotional and spiritual growth — and what to do instead",
    },
    {
        "slug": "youre-no-one-and-everyone",
        "id": 222920992,
        "title": "How to Stop Living Inside Your Head and Actually Take Action",
        "subtitle": "What neuroscience and spirituality agree on about breaking the mental loops that keep us stuck",
    },
    {
        "slug": "youre-not-half-human",
        "id": 221433853,
        "title": "You're Not Half Human: Why We Fragment Ourselves (and How to Stop)",
        "subtitle": "Reclaiming your emotional, spiritual, and physical self as one whole person",
    },
    {
        "slug": "feminism-my-journey",
        "id": 205296330,
        "title": "From Feminism to Trad Wife to Individualism: My Honest Journey",
        "subtitle": "What I learned moving through ideologies — and why I finally stopped choosing sides",
    },
    {
        "slug": "the-perfect-cube",
        "id": 213960185,
        "title": "Is AI Making Us Less Human? On Efficiency, Dependency, and Inner Stillness",
        "subtitle": "What happens to our inner life when we outsource thinking to machines",
    },
    {
        "slug": "the-fog-and-the-anchor",
        "id": 213959604,
        "title": "How to Reclaim Your Emotional Baseline After Burnout or Heartbreak",
        "subtitle": "A spiritual and somatic guide to finding your centre again when everything feels off",
    },
    {
        "slug": "on-forgiveness-why-cruelty-is-never",
        "id": 202324790,
        "title": "On Forgiveness: Why Cruelty Is Never Justified, Even When You Were Wronged",
        "subtitle": "How to release pain and find peace — without excusing what happened to you",
    },
    {
        "slug": "my-journey-of-being-disliked",
        "id": 202328055,
        "title": "What I Learned From Being Disliked: When Social Anxiety Looks Like Confidence",
        "subtitle": "How I discovered that my aloofness was really anxiety wearing a flight response",
    },
    {
        "slug": "how-our-emotional-pangs-makes-us",
        "id": 201916494,
        "title": "Why Your Emotions Make You Misread the People You Love Most",
        "subtitle": "The psychological loop that distorts how we see the people closest to us — and how to break it",
    },
    {
        "slug": "why-your-healthy-boundaries-are-just",
        "id": 201915000,
        "title": 'Why Your "Healthy Boundaries" Might Actually Be Fear in Disguise',
        "subtitle": "The difference between genuine limits and emotional armour — and how to tell them apart",
    },
    {
        "slug": "the-year-i-ditched-resolutions-and",
        "id": 199769865,
        "title": "What Happens When You Stop Setting Goals for a Year",
        "subtitle": "On ego deaths, surrender, and what the universe does when you stop forcing your life into a plan",
    },
    {
        "slug": "why-assertiveness-is-a-divine-calling",
        "id": 199672062,
        "title": "Why Assertiveness Is a Spiritual Practice, Not Just a Life Skill",
        "subtitle": "How speaking your truth and holding your ground is a form of creativity and self-expression",
    },
    {
        "slug": "understanding-the-kaparthy-loop",
        "id": 199636033,
        "title": "What Andrej Karpathy's AI Loop Taught Me About Getting Out of My Own Way",
        "subtitle": "How AI's auto-research feedback loops mirror the mental patterns that keep us stuck in life",
    },
    {
        "slug": "a-new-way-to-practice-positive-affirmations",
        "id": 199637117,
        "title": "Why Positive Affirmations Don't Work — and What to Do Instead",
        "subtitle": "A feeling-first approach to rewiring your mindset that actually sticks",
    },
    # 15: keeping as-is — already highly searchable
    # 16
    {
        "slug": "notes-from-the-lion-king",
        "id": 199503692,
        "title": "What The Lion King Taught Me About Guilt, Shame, and Showing Up Fully",
        "subtitle": "Simba's story is really about what happens when we run from ourselves — and what it costs us",
    },
    {
        "slug": "i-wanted-to-be-a-bird",
        "id": 194742217,
        "title": "What It Feels Like to Realise You Were Always Free",
        "subtitle": "On the moment you discover you are loved, limitless, and allowed to take up space",
    },
    {
        "slug": "how-i-created-a-skill-on-claude-ai",
        "id": 194821905,
        "subtitle": "How to build a custom AI writing assistant that knows your voice and writes in your style",
    },
    {
        "slug": "what-being-an-ewe-lady-taught-me",
        "id": 196569631,
        "title": "What My West African Heritage Taught Me About Power, Silence, and Self-Expression",
        "subtitle": "How I learned to name what I want by watching what the women before me never said",
    },
    {
        "slug": "who-decided-what-you-should-eat",
        "id": 196144244,
        "subtitle": "Breaking free from food rules — and other borrowed beliefs — that were never yours to begin with",
    },
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


def make_opener(session_sid):
    import http.cookiejar
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [
        ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"),
        ("Cookie", f"substack.sid={session_sid}"),
    ]
    return opener


def update_post(post_id, slug, title, subtitle, session_sid, dry_run):
    opener = make_opener(session_sid)

    # Fetch current by slug
    fetch_url = f"{BASE_URL}/api/v1/posts/{slug}"
    req = urllib.request.Request(fetch_url)
    try:
        with opener.open(req) as res:
            current = json.loads(res.read())
    except urllib.error.HTTPError as e:
        return False, f"fetch failed {e.code}"

    new_title = title if title else current.get("title")
    new_subtitle = subtitle if subtitle else current.get("subtitle", "")

    if dry_run:
        print(f"  [dry-run] title:    {new_title}")
        print(f"  [dry-run] subtitle: {new_subtitle}")
        return True, "dry-run"

    # Update draft
    draft_payload = json.dumps({
        "title": new_title, "subtitle": new_subtitle,
        "draft_title": new_title, "draft_subtitle": new_subtitle,
    }).encode()
    headers = {"Content-Type": "application/json", "Referer": f"{BASE_URL}/publish/post/{post_id}", "Origin": BASE_URL}
    req = urllib.request.Request(f"{BASE_URL}/api/v1/drafts/{post_id}", data=draft_payload, method="PUT", headers=headers)
    try:
        with opener.open(req) as res:
            json.loads(res.read())
    except urllib.error.HTTPError as e:
        return False, f"draft update failed {e.code}"

    # Publish draft
    pub_payload = json.dumps({"send": False, "share_automatically": False}).encode()
    req = urllib.request.Request(f"{BASE_URL}/api/v1/drafts/{post_id}/publish", data=pub_payload, method="POST", headers=headers)
    try:
        with opener.open(req) as res:
            json.loads(res.read())
        return True, "ok"
    except urllib.error.HTTPError as e:
        return False, f"publish failed {e.code} {e.read().decode()[:100]}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview without applying")
    args = parser.parse_args()

    session_sid = get_session_cookie()
    if not session_sid:
        print("❌ SUBSTACK_SID not set. See instructions in update-post-seo.py.")
        sys.exit(1)

    ok = 0
    fail = 0
    for post in UPDATES:
        slug = post["slug"]
        print(f"→ {slug}")
        success, msg = update_post(
            post["id"], post["slug"],
            post.get("title"), post.get("subtitle"),
            session_sid, args.dry_run
        )
        if success:
            print(f"  ✅ {msg}")
            ok += 1
        else:
            print(f"  ❌ {msg}")
            fail += 1
        time.sleep(0.5)  # be polite to the API

    print(f"\nDone: {ok} updated, {fail} failed")


if __name__ == "__main__":
    main()
