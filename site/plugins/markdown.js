// Vite plugin that pre-renders source Markdown files into a page's <main>
// at build time (and on dev requests). Each page's index.html declares its
// source with a comment:
//
//   <main class="prose"><!-- render-markdown: ../hide-and-seek/rules.md --></main>
//
// At build time the comment is replaced with the rendered HTML, so search
// engines and no-JS clients see a fully populated page. Source .md files
// live in the repo (not duplicated under site/) — single source of truth.
//
// Relative .md links inside the source are rewritten to in-site routes
// where a corresponding page exists; remaining repo-relative links fall
// back to canonical GitHub URLs.
//
// Conditional content: source files may include audience-specific blocks
// fenced by HTML comments. On the site build, repo-only blocks are
// stripped and site-only fences are unwrapped (the content stays). On
// GitHub, both blocks render literally — HTML comments are invisible but
// the markdown between them is normal markdown. Use sparingly; prefer
// context-neutral wording when possible.
//
//   <!-- repo-only -->
//   Stuff that only makes sense when reading the file in the repo.
//   <!-- /repo-only -->
//
//   <!-- site-only -->
//   Stuff that only makes sense on the site (also visible on GitHub).
//   <!-- /site-only -->

import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import MarkdownIt from "markdown-it";
import anchor from "markdown-it-anchor";

const HERE = dirname(fileURLToPath(import.meta.url));
const SITE_DIR = resolve(HERE, "..");
const REPO_ROOT = resolve(SITE_DIR, "..");
const GH_TREE = "https://github.com/ramblin-dev/rural-jet-lag/blob/main";

// Map repo-relative source paths → in-site routes.
const ROUTE_MAP = {
  "README.md": "/",
  "vehicle-stations.md": "/vehicle-stations/",
  "hide-and-seek/rules.md": "/rules/",
  "hide-and-seek/setup.md": "/setup/",
};

const md = new MarkdownIt({ html: true, linkify: true, typographer: false });
md.use(anchor, { permalink: anchor.permalink.headerLink() });

function rewriteLink(href, sourcePath) {
  if (/^[a-z]+:\/\//i.test(href) || href.startsWith("#") || href.startsWith("mailto:")) {
    return href;
  }
  // Split off any #fragment.
  const hashIdx = href.indexOf("#");
  const path = hashIdx >= 0 ? href.slice(0, hashIdx) : href;
  const hash = hashIdx >= 0 ? href.slice(hashIdx) : "";
  // Resolve the link relative to the source markdown's directory, then
  // make it repo-relative.
  const absolute = resolve(dirname(sourcePath), path);
  const repoRel = absolute.startsWith(REPO_ROOT + "/")
    ? absolute.slice(REPO_ROOT.length + 1)
    : null;
  if (repoRel && ROUTE_MAP[repoRel]) {
    return ROUTE_MAP[repoRel] + hash;
  }
  if (repoRel) {
    // Fall back to GitHub for repo files we don't render in-site
    // (reference/, stations-generator/, license files, …).
    return `${GH_TREE}/${repoRel}${hash}`;
  }
  return href;
}

function rewriteLinksInHtml(html, sourcePath) {
  return html.replace(/href="([^"]+)"/g, (match, href) => {
    const next = rewriteLink(href, sourcePath);
    return `href="${next}"`;
  });
}

function applyConditionalsForSite(text) {
  // Strip repo-only blocks (markers + content + trailing newline if any).
  let out = text.replace(
    /[ \t]*<!--\s*repo-only\s*-->[\s\S]*?<!--\s*\/repo-only\s*-->[ \t]*\n?/g,
    "",
  );
  // Unwrap site-only blocks (keep content, drop just the markers).
  out = out.replace(/[ \t]*<!--\s*\/?site-only\s*-->[ \t]*\n?/g, "");
  return out;
}

function renderMarkdownFile(mdPath) {
  const text = readFileSync(mdPath, "utf8");
  const processed = applyConditionalsForSite(text);
  const html = md.render(processed);
  return rewriteLinksInHtml(html, mdPath);
}

const TOKEN_RE = /<!--\s*render-markdown:\s*([^\s-][^\s]*)\s*-->/g;

export function markdownPagesPlugin() {
  return {
    name: "rural-jet-lag-markdown-pages",
    transformIndexHtml: {
      order: "pre",
      handler(html, ctx) {
        const pageDir = ctx?.filename ? dirname(ctx.filename) : SITE_DIR;
        return html.replace(TOKEN_RE, (_match, rel) => {
          const mdPath = resolve(pageDir, rel);
          return renderMarkdownFile(mdPath);
        });
      },
    },
    handleHotUpdate(ctx) {
      if (ctx.file.endsWith(".md")) {
        ctx.server.ws.send({ type: "full-reload" });
        return [];
      }
    },
  };
}
