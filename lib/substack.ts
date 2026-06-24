const SUBSTACK_URL = "https://sproutingplant.substack.com";

export interface Post {
  id: number;
  slug: string;
  title: string;
  subtitle: string;
  cover_image: string | null;
  post_date: string;
  canonical_url: string;
  body_html: string;
  truncated_body_text: string;
  postTags: { id: string; name: string; slug: string }[];
}

export async function getPosts(limit = 20): Promise<Post[]> {
  try {
    const res = await fetch(`${SUBSTACK_URL}/api/v1/posts?limit=${limit}`, {
      cache: "no-store",
    });
    const text = await res.text();
    return JSON.parse(text);
  } catch (e) {
    console.error("getPosts error:", e);
    return [];
  }
}

export async function getPost(slug: string): Promise<Post | null> {
  try {
    const res = await fetch(`${SUBSTACK_URL}/api/v1/posts/${slug}`, {
      cache: "no-store",
    });
    const text = await res.text();
    return JSON.parse(text);
  } catch (e) {
    console.error("getPost error:", e);
    return null;
  }
}
