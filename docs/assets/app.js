function normalizePath(pathname) {
  return pathname.replace(/\/+$/, "") || "/";
}

function withBase(path) {
  const baseurl = document.body.dataset.baseurl || "";
  return `${baseurl}${path}`;
}

function stripBase(pathname) {
  const baseurl = document.body.dataset.baseurl || "";
  if (baseurl && pathname.startsWith(baseurl)) {
    const trimmed = pathname.slice(baseurl.length);
    return trimmed || "/";
  }
  return pathname;
}

async function fetchJson(path) {
  try {
    const response = await fetch(withBase(path));
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

/* ── Mobile menu toggle ── */
function initMobileMenu() {
  const toggle = document.querySelector("[data-menu-toggle]");
  const nav = document.querySelector("[data-nav]");
  if (!toggle || !nav) return;
  toggle.addEventListener("click", () => {
    nav.classList.toggle("open");
    const isOpen = nav.classList.contains("open");
    toggle.setAttribute("aria-label", isOpen ? "关闭导航" : "打开导航");
  });
  // Close menu when clicking a link
  nav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => nav.classList.remove("open"));
  });
}

/* ── Copy agent link ── */
function initCopyButton() {
  const button = document.querySelector("[data-copy-agent]");
  if (!button) return;
  button.addEventListener("click", async () => {
    const text = `${window.location.href}\n请学习这条 uWisdom 知识，并结合上下游关系理解它。`;
    try {
      await navigator.clipboard.writeText(text);
      button.textContent = "已复制，可直接发给 Agent";
    } catch {
      // Fallback for non-HTTPS
      const ta = document.createElement("textarea");
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      button.textContent = "已复制，可直接发给 Agent";
    }
    window.setTimeout(() => {
      button.textContent = "复制链接，让你的 Agent 学习这条知识";
    }, 2200);
  });
}

/* ── Knowledge graph rendering ── */
function renderGraph(graphData) {
  const target = document.querySelector("[data-graph-target]");
  if (!target || !window.mermaid || !graphData) return;
  const current = normalizePath(stripBase(window.location.pathname));
  const graph = graphData.pages[current];
  if (!graph || !graph.mermaid) {
    target.innerHTML = "<p class='meta'>当前条目暂未生成关系图。</p>";
    return;
  }
  const id = `graph-${Math.random().toString(36).slice(2)}`;
  window.mermaid
    .render(id, graph.mermaid)
    .then(({ svg }) => {
      target.innerHTML = svg;
    })
    .catch(() => {
      target.innerHTML = "<p class='meta'>关系图渲染失败。</p>";
    });
}

/* ── Search ── */
function buildOptionList(values, emptyLabel) {
  return [`<option value="">${emptyLabel}</option>`]
    .concat(values.map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`))
    .join("");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function scoreEntry(entry, query) {
  if (!query) return 1;
  const q = query.toLowerCase();
  const tokens = q.split(/\s+/).filter(Boolean);
  let score = 0;
  const haystacks = [
    [entry.title || "", 8],
    [entry.summary || "", 5],
    [(entry.tags || []).join(" "), 4],
    [entry.domain || "", 4],
    [entry.content || "", 2],
    [entry.author || "", 3],
    [entry.book || "", 3],
  ];
  haystacks.forEach(([text, weight]) => {
    const source = String(text).toLowerCase();
    tokens.forEach((token) => {
      if (source.includes(token)) score += weight;
    });
  });
  return score;
}

function highlightText(text, query) {
  if (!query || !text) return escapeHtml(text);
  const tokens = query.toLowerCase().split(/\s+/).filter(Boolean);
  let result = escapeHtml(text);
  tokens.forEach((token) => {
    const regex = new RegExp(`(${token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
    result = result.replace(regex, '<span class="search-highlight">$1</span>');
  });
  return result;
}

function initSearch(indexData) {
  const root = document.querySelector("[data-search-root]");
  if (!root || !indexData) return;

  const entries = indexData.entries || [];
  const filters = indexData.filters || {};
  root.innerHTML = `
    <section class="search-panel card">
      <div class="search-grid">
        <input id="search-query" type="search" placeholder="输入问题、概念、人物、主题..." autofocus />
        <select id="filter-domain">${buildOptionList(filters.domain || [], "全部领域")}</select>
        <select id="filter-tag">${buildOptionList(filters.tag || [], "全部标签")}</select>
        <select id="filter-version">${buildOptionList(filters.version || [], "全部版本")}</select>
        <select id="filter-book">${buildOptionList(filters.book || [], "全部书籍")}</select>
        <select id="filter-author">${buildOptionList(filters.author || [], "全部作者")}</select>
      </div>
      <p class="meta" style="margin-top:12px">站点内提供结构化检索；语义检索通过 OpenAI embeddings + FAISS 离线管线生成，可供 Agent 或本地工具调用。</p>
    </section>
    <p id="search-count" class="meta"></p>
    <section id="search-results"></section>
  `;

  const results = root.querySelector("#search-results");
  const countEl = root.querySelector("#search-count");
  const controls = {
    query: root.querySelector("#search-query"),
    domain: root.querySelector("#filter-domain"),
    tag: root.querySelector("#filter-tag"),
    version: root.querySelector("#filter-version"),
    book: root.querySelector("#filter-book"),
    author: root.querySelector("#filter-author"),
  };

  // Restore from URL params
  const params = new URLSearchParams(window.location.search);
  controls.query.value = params.get("q") || "";
  controls.domain.value = params.get("domain") || "";
  controls.tag.value = params.get("tag") || "";
  controls.version.value = params.get("version") || "";
  controls.book.value = params.get("book") || "";
  controls.author.value = params.get("author") || "";

  const renderResults = () => {
    const query = controls.query.value.trim();
    const domain = controls.domain.value;
    const tag = controls.tag.value;
    const version = controls.version.value;
    const book = controls.book.value;
    const author = controls.author.value;

    // Update URL
    const nextParams = new URLSearchParams();
    if (query) nextParams.set("q", query);
    if (domain) nextParams.set("domain", domain);
    if (tag) nextParams.set("tag", tag);
    if (version) nextParams.set("version", version);
    if (book) nextParams.set("book", book);
    if (author) nextParams.set("author", author);
    const newUrl = `${window.location.pathname}${nextParams.toString() ? `?${nextParams}` : ""}`;
    window.history.replaceState({}, "", newUrl);

    const matched = entries
      .map((entry) => ({ entry, score: scoreEntry(entry, query) }))
      .filter(({ entry, score }) => {
        if (query && score <= 0) return false;
        if (domain && entry.domain !== domain) return false;
        if (tag && !(entry.tags || []).includes(tag)) return false;
        if (version && entry.version !== version) return false;
        if (book && entry.book !== book) return false;
        if (author && entry.author !== author) return false;
        return true;
      })
      .sort((a, b) => b.score - a.score)
      .slice(0, 30);

    countEl.textContent = query ? `找到 ${matched.length} 个匹配条目` : `共 ${entries.length} 个知识条目`;

    if (!matched.length) {
      results.innerHTML = "<p class='meta'>没有找到匹配条目。可以换一个问题表达，或降低过滤条件。</p>";
      return;
    }

    results.innerHTML = matched
      .map(({ entry }) => `
        <article class="card search-result">
          <h3><a href="${entry.url}">${query ? highlightText(entry.title, query) : escapeHtml(entry.title)}</a></h3>
          <p>${entry.summary ? (query ? highlightText(entry.summary, query) : escapeHtml(entry.summary)) : ""}</p>
          <p class="search-meta">${[entry.section, entry.domain, entry.version, entry.author, entry.book].filter(Boolean).map(escapeHtml).join(" · ")}</p>
          <div class="tag-list">${(entry.tags || []).map((item) => `<span class="tag">${escapeHtml(item)}</span>`).join("")}</div>
        </article>
      `)
      .join("");
  };

  Object.values(controls).forEach((control) => {
    control.addEventListener("input", renderResults);
    control.addEventListener("change", renderResults);
  });
  renderResults();
}

/* ── Init ── */
document.addEventListener("DOMContentLoaded", async () => {
  initMobileMenu();
  initCopyButton();
  const [graphData, indexData] = await Promise.all([
    fetchJson("/assets/graph.json"),
    fetchJson("/assets/search-index.json"),
  ]);
  renderGraph(graphData);
  initSearch(indexData);
});
