import { getPosts } from "@/lib/substack";

export default async function sitemap() {
  const posts = await getPosts(50);

  const postUrls = posts.map((post) => ({
    url: `https://byflorence.net/posts/${post.slug}`,
    lastModified: new Date(post.post_date),
  }));

  return [
    { url: "https://byflorence.net", lastModified: new Date() },
    { url: "https://byflorence.net/about", lastModified: new Date() },
    ...postUrls,
  ];
}
