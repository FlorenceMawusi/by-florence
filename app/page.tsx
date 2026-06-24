import Link from "next/link";
import Image from "next/image";
import { getPosts } from "@/lib/substack";

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export default async function HomePage() {
  const posts = await getPosts(20);

  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      <div className="mb-12">
        <h1 className="text-4xl font-medium mb-3" style={{ color: "var(--foreground)" }}>
          AI &amp; Spirituality
        </h1>
        <p className="text-lg" style={{ color: "var(--foreground)", opacity: 0.6 }}>
          Writing at the intersection of artificial intelligence and spiritual growth.
        </p>
      </div>

      <div className="flex flex-col gap-10">
        {posts.map((post) => (
          <article key={post.id} className="flex flex-col sm:flex-row gap-6 pb-10 border-b" style={{ borderColor: "rgba(26,16,8,0.1)" }}>
            {post.cover_image && (
              <Link href={`/posts/${post.slug}`} className="shrink-0">
                <Image
                  src={post.cover_image}
                  alt={post.title}
                  width={200}
                  height={140}
                  className="rounded-md object-cover w-full sm:w-[200px] h-[140px]"
                />
              </Link>
            )}
            <div className="flex flex-col gap-2">
              <time className="text-xs" style={{ color: "var(--accent)" }}>
                {formatDate(post.post_date)}
              </time>
              <Link href={`/posts/${post.slug}`} className="no-underline">
                <h2 className="text-xl font-medium leading-snug hover:underline" style={{ color: "var(--foreground)" }}>
                  {post.title}
                </h2>
              </Link>
              {post.subtitle && (
                <p className="text-base italic" style={{ color: "var(--foreground)", opacity: 0.65 }}>
                  {post.subtitle}
                </p>
              )}
              <p className="text-sm leading-relaxed line-clamp-3" style={{ color: "var(--foreground)", opacity: 0.55 }}>
                {post.truncated_body_text}
              </p>
              <Link
                href={`/posts/${post.slug}`}
                className="text-sm mt-1 self-start"
                style={{ color: "var(--accent)" }}
              >
                Read more →
              </Link>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
