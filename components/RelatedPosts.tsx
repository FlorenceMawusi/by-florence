import { getPosts, Post } from "@/lib/substack";
import Image from "next/image";
import Link from "next/link";

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function getRelated(current: Post, all: Post[]): Post[] {
  const currentTags = new Set(current.postTags?.map((t) => t.slug) ?? []);
  const others = all.filter((p) => p.slug !== current.slug);

  const scored = others.map((p) => {
    const shared = p.postTags?.filter((t) => currentTags.has(t.slug)).length ?? 0;
    return { post: p, score: shared };
  });

  scored.sort((a, b) => b.score - a.score || new Date(b.post.post_date).getTime() - new Date(a.post.post_date).getTime());
  return scored.slice(0, 3).map((s) => s.post);
}

export default async function RelatedPosts({ current }: { current: Post }) {
  const all = await getPosts(50);
  const related = getRelated(current, all);
  if (related.length === 0) return null;

  return (
    <section className="mt-16 pt-10 border-t" style={{ borderColor: "rgba(26,16,8,0.12)" }}>
      <h2 className="text-sm font-semibold uppercase tracking-widest mb-6" style={{ color: "var(--accent)", letterSpacing: "0.1em" }}>
        Keep Reading
      </h2>
      <div className="grid gap-6 sm:grid-cols-3">
        {related.map((post) => (
          <Link
            key={post.slug}
            href={`/posts/${post.slug}`}
            className="group block no-underline"
          >
            {post.cover_image && (
              <div className="overflow-hidden rounded-lg mb-3" style={{ aspectRatio: "16/9" }}>
                <Image
                  src={post.cover_image}
                  alt={post.title}
                  width={400}
                  height={225}
                  className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                />
              </div>
            )}
            <time className="text-xs" style={{ color: "var(--accent)" }}>
              {formatDate(post.post_date)}
            </time>
            <p className="text-sm font-medium mt-1 leading-snug group-hover:opacity-70 transition-opacity" style={{ color: "var(--foreground)" }}>
              {post.title}
            </p>
          </Link>
        ))}
      </div>
    </section>
  );
}
