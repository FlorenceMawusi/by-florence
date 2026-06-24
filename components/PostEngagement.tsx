"use client";

import { useState, useEffect } from "react";

function HeartIcon({ filled }: { filled: boolean }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill={filled ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
    </svg>
  );
}

function CommentIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
    </svg>
  );
}


interface Props {
  slug: string;
  substackUrl: string;
}

export default function PostEngagement({ slug, substackUrl }: Props) {
  const [liked, setLiked] = useState(false);

  useEffect(() => {
    const likes = JSON.parse(localStorage.getItem("liked-posts") || "[]");
    setLiked(likes.includes(slug));
  }, [slug]);

  function toggleLike() {
    const likes: string[] = JSON.parse(localStorage.getItem("liked-posts") || "[]");
    let updated: string[];
    if (liked) {
      updated = likes.filter((s) => s !== slug);
    } else {
      updated = [...likes, slug];
    }
    localStorage.setItem("liked-posts", JSON.stringify(updated));
    setLiked(!liked);
  }

  return (
    <div className="mt-12 pt-8 border-t flex flex-wrap gap-3" style={{ borderColor: "rgba(26,16,8,0.1)" }}>
      <button
        onClick={toggleLike}
        className="flex items-center gap-2 px-4 py-2 rounded-full text-sm transition-all border"
        style={{
          borderColor: liked ? "var(--accent)" : "rgba(26,16,8,0.15)",
          color: liked ? "var(--accent)" : "var(--foreground)",
          background: liked ? "rgba(232,68,10,0.06)" : "transparent",
        }}
      >
        <HeartIcon filled={liked} />
        {liked ? "Liked" : "Like this post"}
      </button>

      <a
        href={`${substackUrl}#comments`}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-2 px-4 py-2 rounded-full text-sm border transition-all hover:opacity-80"
        style={{ borderColor: "rgba(26,16,8,0.15)", color: "var(--foreground)" }}
      >
        <CommentIcon />
        Comment on Substack
      </a>

    </div>
  );
}
