/* ── Utility ── */
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
    return pathname.slice(baseurl.length) || "/";
  }
  return pathname;
}

async function fetchJson(path) {
  try {
    const response = await fetch(withBase(path));
    return response.ok ? response.json() : null;
  } catch {
    return null;
  }
}

/* ── Reading Progress ── */
function initReadingProgress() {
  const progress = document.getElementById("reading-progress");
  if (!progress) return;
  window.addEventListener("scroll", () => {
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    progress.style.width = scrolled + "%";
  });
}

/* ── TOC ── */
function initTOC() {
  const container = document.getElementById("toc-container");
  const article = document.querySelector(".main-article");
  if (!container || !article) return;

  const headings = Array.from(article.querySelectorAll("h2, h3"));
  if (headings.length < 2) {
    container.style.display = "none";
    return;
  }

  const tocHtml = headings.map((h, i) => {
    const id = h.id || `heading-${i}`;
    h.id = id;
    const level = h.tagName.toLowerCase();
    return `<a href="#${id}" class="toc-link toc-${level}" style="padding-left: ${level === 'h3' ? '1rem' : '0'}">${h.innerText}</a>`;
  }).join("");
  container.innerHTML = `<div class="eyebrow" style="margin-bottom: 0.5rem">On this page</div>` + tocHtml;

  // Active state on scroll
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        container.querySelectorAll(".toc-link").forEach(link => link.classList.remove("active"));
        const activeLink = container.querySelector(`[href="#${entry.target.id}"]`);
        if (activeLink) activeLink.classList.add("active");
      }
    });
  }, { rootMargin: "-100px 0px -70% 0px" });

  headings.forEach(h => observer.observe(h));
}

/* ── Search with Fuse.js ── */
function initSearch(indexData) {
  const root = document.querySelector("[data-search-root]");
  if (!root || !indexData) return;

  const entries = indexData.entries || [];
  const fuse = new Fuse(entries, {
    keys: [
      { name: "title", weight: 0.4 },
      { name: "summary", weight: 0.2 },
      { name: "tags", weight: 0.15 },
      { name: "content", weight: 0.25 }
    ],
    threshold: 0.35,
    includeMatches: true,
    useExtendedSearch: true
  });

  const resultsEl = document.getElementById("search-results");
  const countEl = document.getElementById("search-count");
  const queryInput = document.getElementById("search-query");

  const performSearch = () => {
    const query = queryInput.value.trim();
    if (!query) {
      resultsEl.innerHTML = "<p class='meta'>请输入关键词开始探索知识...</p>";
      countEl.textContent = `共 ${entries.length} 个条目`;
      return;
    }

    const fuseResults = fuse.search(query);
    countEl.textContent = `找到 ${fuseResults.length} 个匹配条目`;

    resultsEl.innerHTML = fuseResults.slice(0, 20).map(({ item, matches }) => {
      return `
        <article class="card search-result">
          <h3><a href="${withBase(item.url)}">${item.title}</a></h3>
          <p>${item.summary || ""}</p>
          <p class="search-meta">${item.domain || item.section} · ${item.version}</p>
          <div class="tag-list">${(item.tags || []).map(t => `<span class="tag">${t}</span>`).join("")}</div>
        </article>
      `;
    }).join("");
  };

  queryInput.addEventListener("input", performSearch);
  performSearch();
}

/* ── Global Map ── */
function initGlobalMap(indexData) {
  const container = document.getElementById("global-map");
  if (!container || !indexData) return;

  const entries = indexData.entries;
  const nodes = entries.map((e, i) => ({
    id: e.url,
    label: e.title,
    group: e.domain || e.section,
    title: e.summary
  }));

  const edges = [];
  const urlToId = {};
  entries.forEach(e => urlToId[e.url] = e.url);

  entries.forEach(e => {
    (e.links || []).forEach(link => {
      const target = link[1].replace(".html", "");
      if (urlToId[target]) {
        edges.push({ from: e.url, to: target });
      }
    });
  });

  const data = { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) };
  const options = {
    nodes: { shape: 'dot', size: 16, font: { size: 12, color: '#4B5563' }, borderWidth: 2 },
    edges: { color: '#D1D5DB', smooth: { type: 'continuous' } },
    groups: {
      '知识百科 / 领域': { color: { background: '#2DD4BF', border: '#133D72' } },
      '主题研究': { color: { background: '#FBBF24', border: '#133D72' } }
    },
    physics: { stabilization: true, barnesHut: { gravitationalConstant: -2000 } }
  };

  const network = new vis.Network(container, data, options);
  network.on("click", (params) => {
    if (params.nodes.length > 0) {
      window.location.href = withBase(params.nodes[0]);
    }
  });
}

/* ── Lucky Button ── */
function initLucky(indexData) {
  const btn = document.getElementById("lucky-button");
  if (!btn || !indexData) return;
  btn.addEventListener("click", () => {
    const entries = indexData.entries;
    const random = entries[Math.floor(Math.random() * entries.length)];
    window.location.href = withBase(random.url);
  });
}

/* ── Entry Graph (Mermaid) ── */
function renderEntryGraph(graphData) {
  const target = document.querySelector("[data-graph-target]");
  if (!target || !window.mermaid || !graphData) return;
  const current = normalizePath(stripBase(window.location.pathname));
  const graph = graphData.pages[current];
  if (!graph || !graph.mermaid) return;

  window.mermaid.render(`graph-${Math.random().toString(36).slice(2)}`, graph.mermaid)
    .then(({ svg }) => target.innerHTML = svg);
}

/* ── Init ── */
document.addEventListener("DOMContentLoaded", async () => {
  initReadingProgress();
  initTOC();
  if (window.hljs) window.hljs.highlightAll();

  const [graphData, indexData] = await Promise.all([
    fetchJson("/assets/graph.json"),
    fetchJson("/assets/search-index.json")
  ]);

  initLucky(indexData);
  renderEntryGraph(graphData);
  if (document.querySelector("[data-search-root]")) initSearch(indexData);
  if (document.getElementById("global-map")) initGlobalMap(indexData);
});
