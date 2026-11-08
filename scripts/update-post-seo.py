#!/usr/bin/env python3
"""
Update a Substack post's title and subtitle via the private API.

Usage:
  python3 scripts/update-post-seo.py --slug the-smart-persons-trap \
    --title "Why Smart People Can't Think Their Way to Peace" \
    --subtitle "How over-relying on intellect blocks emotional and spiritual growth"

Setup:
  1. Open sproutingplant.substack.com in Chrome while logged in
  2. Open DevTools (Cmd+Option+I) → Application → Cookies → sproutingplant.substack.com
  3. Copy the value of the cookie named "substack.sid"
  4. Set it as an environment variable:
       export SUBSTACK_SID="your_cookie_value_here"
  Or paste it into a .env file at the root of this project:
       SUBSTACK_SID=your_cookie_value_here
"""

import argparse
import http.cookiejar
import json
import os
import sys
import urllib.request
import urllib.error

SUBDOMAIN = "sproutingplant"
BASE_URL = f"https://{SUBDOMAIN}.substack.com"


def make_opener(session_sid: str):
    """Build an opener that sends the session cookie and handles CSRF automatically."""
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [
        ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"),
        ("Cookie", f"substack.sid={session_sid}"),
    ]
    return opener


def get_csrf_token(opener) -> str:
    """Fetch a CSRF token from Substack by hitting the user endpoint."""
    req = urllib.request.Request(f"{BASE_URL}/api/v1/user")
    try:
        with opener.open(req) as res:
            # Substack sets the CSRF token in a response header
            csrf = res.headers.get("X-CSRF-Token") or res.headers.get("x-csrf-token")
            if csrf:
                return csrf
    except urllib.error.HTTPError:
        pass

    # Fallback: try hitting the site root and read Set-Cookie for csrf token
    req = urllib.request.Request(BASE_URL)
    try:
        with opener.open(req) as res:
            for header, value in res.headers.items():
                if "csrf" in header.lower():
                    return value
    except Exception:
        pass

    return ""

POST_IDS = {
    "the-smart-persons-trap": 223013134,
    "youre-no-one-and-everyone": 222920992,
    "youre-not-half-human": 221433853,
    "feminism-my-journey": 205296330,
    "the-perfect-cube": 213960185,
    "the-fog-and-the-anchor": 213959604,
    "on-forgiveness-why-cruelty-is-never": 202324790,
    "my-journey-of-being-disliked": 202328055,
    "how-our-emotional-pangs-makes-us": 201916494,
    "why-your-healthy-boundaries-are-just": 201915000,
    "the-year-i-ditched-resolutions-and": 199769865,
    "why-assertiveness-is-a-divine-calling": 199672062,
    "understanding-the-kaparthy-loop": 199636033,
    "a-new-way-to-practice-positive-affirmations": 199637117,
    "how-i-got-claude-to-post-my-substack": 199534537,
    "notes-from-the-lion-king": 199503692,
    "i-wanted-to-be-a-bird": 194742217,
    "how-i-created-a-skill-on-claude-ai": 194821905,
    "what-being-an-ewe-lady-taught-me": 196569631,
    "who-decided-what-you-should-eat": 196144244,
}


def get_session_cookie():
    sid = os.environ.get("SUBSTACK_SID")
    if sid:
        return sid
    # Try loading from .env file
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("SUBSTACK_SID="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def update_post(post_id: int, slug: str, title: str | None, subtitle: str | None, session_sid: str):
    opener = make_opener(session_sid)

    # Fetch current post by slug (numeric ID doesn't work on public API)
    fetch_url = f"{BASE_URL}/api/v1/posts/{slug}"
    req = urllib.request.Request(fetch_url)
    try:
        with opener.open(req) as res:
            current = json.loads(res.read())
    except urllib.error.HTTPError as e:
        print(f"❌ Failed to fetch post: {e.code} {e.reason}")
        print("   Check that your SUBSTACK_SID cookie is correct and not expired.")
        sys.exit(1)

    print(f"   Current title:    {current.get('title')}")
    print(f"   Current subtitle: {current.get('subtitle')}")

    new_title = title if title else current.get("title")
    new_subtitle = subtitle if subtitle else current.get("subtitle", "")
    payload = {
        "title": new_title,
        "subtitle": new_subtitle,
        "draft_title": new_title,
        "draft_subtitle": new_subtitle,
    }
    data = json.dumps(payload).encode()

    # Try the write endpoints Substack uses internally
    endpoints = [
        f"{BASE_URL}/api/v1/drafts/{post_id}",
        f"https://substack.com/api/v1/posts/{post_id}",
        f"{BASE_URL}/api/v1/posts/{post_id}/update",
    ]

    for endpoint in endpoints:
        req = urllib.request.Request(
            endpoint, data=data, method="PUT",
            headers={
                "Content-Type": "application/json",
                "Referer": f"{BASE_URL}/publish/post/{post_id}",
                "Origin": BASE_URL,
            },
        )
        try:
            with opener.open(req) as res:
                result = json.loads(res.read())
                print(f"   Draft updated via {endpoint.split('/api/')[1]}")
                break
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"   tried {endpoint.split('/api/')[1]} → {e.code}: {body[:80]}")
    else:
        print("❌ All draft endpoints failed.")
        sys.exit(1)

    # Now publish the draft to make it live
    publish_endpoints = [
        f"{BASE_URL}/api/v1/posts/{post_id}/publish",
        f"{BASE_URL}/api/v1/drafts/{post_id}/publish",
        f"{BASE_URL}/api/v1/post/{post_id}/publish",
    ]
    publish_payload = json.dumps({"send": False, "share_automatically": False}).encode()

    for pub_endpoint in publish_endpoints:
        req = urllib.request.Request(
            pub_endpoint, data=publish_payload, method="POST",
            headers={
                "Content-Type": "application/json",
                "Referer": f"{BASE_URL}/publish/post/{post_id}",
                "Origin": BASE_URL,
            },
        )
        try:
            with opener.open(req) as res:
                result = json.loads(res.read())
                print(f"✅ Published via {pub_endpoint.split('/api/')[1]}")
                print(f"   New title:    {result.get('title', result.get('post', {}).get('title', '?'))}")
                print(f"   New subtitle: {result.get('subtitle', result.get('post', {}).get('subtitle', '?'))}")
                return
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"   publish tried {pub_endpoint.split('/api/')[1]} → {e.code}: {body[:120]}")

    print("❌ Draft updated but publish failed — open the editor and click Update now manually.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Update a Substack post title/subtitle")
    parser.add_argument("--slug", required=True, help="Post slug (from the URL)")
    parser.add_argument("--title", help="New title (omit to keep current)")
    parser.add_argument("--subtitle", help="New subtitle (omit to keep current)")
    args = parser.parse_args()

    if not args.title and not args.subtitle:
        print("❌ Provide at least --title or --subtitle")
        sys.exit(1)

    post_id = POST_IDS.get(args.slug)
    if not post_id:
        print(f"❌ Unknown slug: {args.slug}")
        print(f"   Known slugs: {', '.join(POST_IDS.keys())}")
        sys.exit(1)

    session_sid = get_session_cookie()
    if not session_sid:
        print("❌ No session cookie found.")
        print("   Set SUBSTACK_SID in your environment or in a .env file.")
        print("   See the instructions at the top of this script.")
        sys.exit(1)

    print(f"→ Updating post: {args.slug} (ID: {post_id})")
    update_post(post_id, args.slug, args.title, args.subtitle, session_sid)


if __name__ == "__main__":
    main()
