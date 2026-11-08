import { getPost, getPosts } from "@/lib/substack";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import PostEngagement from "@/components/PostEngagement";
import type { Metadata } from "next";

function cleanBodyHtml(html: string): string {
  return html.replace(/<div class="captioned-image-container">[\s\S]*?<\/figure><\/div>/, "");
}

export async function generateStaticParams() {
  const posts = await getPosts(50);
  return posts.map((p) => ({ slug: p.slug }));
}

export async function generateMetadata(
  { params }: { params: Promise<{ slug: string }> }
): Promise<Metadata> {
  const { slug } = await params;
  const post = await getPost(slug);
  if (!post) return {};

  const description = post.subtitle || post.description || "An essay by Florence on AI & Spirituality.";
  const image = post.cover_image || "https://byflorence.net/og-image.png";
  const url = `https://byflorence.net/posts/${slug}`;

  return {
    title: `${post.title} — By Florence`,
    description,
    openGraph: {
      title: post.title,
      description,
      url,
      siteName: "By Florence",
      images: [{ url: image, width: 1200, height: 630 }],
      type: "article",
      publishedTime: post.post_date,
    },
    twitter: {
      card: "summary_large_image",
      title: post.title,
      description,
      images: [image],
    },
  };
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export default async function PostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await getPost(slug);
  if (!post) notFound();

  return (
    <article className="max-w-2xl mx-auto px-6 py-12">
      <Link href="/" className="text-sm mb-8 inline-block" style={{ color: "var(--accent)" }}>
        ← All posts
      </Link>

      {post.cover_image && (
        <Image
          src={post.cover_image}
          alt={post.title}
          width={720}
          height={400}
          className="w-full rounded-lg object-cover mb-8"
          style={{ maxHeight: "400px" }}
        />
      )}

      <header className="mb-10">
        <time className="text-sm" style={{ color: "var(--accent)" }}>
          {formatDate(post.post_date)}
        </time>
        <h1 className="text-3xl font-medium mt-2 mb-3 leading-tight" style={{ color: "var(--foreground)" }}>
          {post.title}
        </h1>
        {post.subtitle && (
          <p className="text-lg italic" style={{ color: "var(--foreground)", opacity: 0.65 }}>
            {post.subtitle}
          </p>
        )}
        {post.postTags?.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-4">
            {post.postTags.map((tag) => (
              <span
                key={tag.id}
                className="text-xs px-3 py-1 rounded-full"
                style={{ background: "rgba(232,68,10,0.1)", color: "var(--accent)" }}
              >
                {tag.name}
              </span>
            ))}
          </div>
        )}
      </header>

      <div
        className="prose-content leading-relaxed"
        style={{ color: "var(--foreground)" }}
        dangerouslySetInnerHTML={{ __html: cleanBodyHtml(post.body_html) }}
      />

      <PostEngagement slug={slug} substackUrl={post.canonical_url} />
    </article>
  );
}
