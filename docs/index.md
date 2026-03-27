---
title: 首页
summary: uWisdom 个人知识操作系统首页
---

<section class="hero">
  <div class="eyebrow">uWisdom</div>
  <h1>个人知识操作系统</h1>
  <p><strong>工程化可读，让知识成为可被 AI 调用的终身资产。</strong></p>
  <p class="meta">GitHub 原生托管 · Pages 一键发布 · 可持续演进 · 全维度检索 · Agent 原生适配</p>
  <p class="meta">知识百科 · 主题研究 · 人物志 · 工具 & Agent</p>
</section>

<section class="stats-bar" id="stats-bar">
  <div class="stat-item">
    <span class="stat-value" id="stat-total">-</span>
    <span class="stat-label">知识总条目</span>
  </div>
  <div class="stat-item">
    <span class="stat-value" id="stat-sections">-</span>
    <span class="stat-label">分类模块</span>
  </div>
  <div class="stat-item">
    <span class="stat-value" id="stat-domains">-</span>
    <span class="stat-label">核心领域</span>
  </div>
</section>

## 入口导航

<div class="grid">
  <article class="card">
    <h2><a href="{{ '/encyclopedia/' | relative_url }}">知识百科</a></h2>
    <p>体系化沉淀，搭建终身知识资产库。</p>
  </article>
  <article class="card">
    <h2><a href="{{ '/topic-research/' | relative_url }}">主题研究</a></h2>
    <p>锚定核心方向，深耕体系化研究。</p>
  </article>
  <article class="card">
    <h2><a href="{{ '/figures/' | relative_url }}">人物志</a></h2>
    <p>溯源智者思想，读懂核心影响力。</p>
  </article>
  <article class="card">
    <h2><a href="{{ '/tools-agent/' | relative_url }}">工具 & Agent</a></h2>
    <p>打通 AI 能力，让知识被精准调用。</p>
  </article>
  <article class="card">
    <h2><a href="{{ '/search/' | relative_url }}">全域搜索</a></h2>
    <p>自然语言提问，秒级定位知识。</p>
  </article>
  <article class="card">
    <h2><a href="{{ '/today/' | relative_url }}">今日精华</a></h2>
    <p>自动生成每日精选，唤醒知识价值。</p>
  </article>
</div>

## 四大身份 · 随机精选

<div class="identity-grid" id="identity-grid">
  <div class="identity-section" data-identity="architect">
    <h3>🏛️ 架构师</h3>
    <ul class="entry-list" id="architect-entries"></ul>
  </div>
  <div class="identity-section" data-identity="investor">
    <h3>📈 投资人</h3>
    <ul class="entry-list" id="investor-entries"></ul>
  </div>
  <div class="identity-section" data-identity="lifelong-learner">
    <h3>📚 终身学习者</h3>
    <ul class="entry-list" id="lifelong-learner-entries"></ul>
  </div>
  <div class="identity-section" data-identity="life-artist">
    <h3>🎨 生活艺术家</h3>
    <ul class="entry-list" id="life-artist-entries"></ul>
  </div>
</div>

<script>
fetch('{{ "/assets/homepage-featured.json" | relative_url }}')
  .then(r => r.json())
  .then(data => {
    const identities = data.identities;
    for (const [key, info] of Object.entries(identities)) {
      const ul = document.getElementById(`${key}-entries`);
      if (!ul) continue;
      for (const item of info.items) {
        const li = document.createElement('li');
        li.innerHTML = `<a href="${item.url}"><strong>${item.title}</strong><br><span class="summary">${item.summary}</span></a>`;
        ul.appendChild(li);
      }
    }
  });
</script>

<style>
.identity-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  margin: 2rem 0;
}
.identity-section {
  background: #f8fafc;
  border-radius: 8px;
  padding: 1.25rem;
  border-left: 4px solid #133D72;
}
.identity-section[data-identity="investor"] { border-left-color: #059669; }
.identity-section[data-identity="lifelong-learner"] { border-left-color: #7C3AED; }
.identity-section[data-identity="life-artist"] { border-left-color: #DC2626; }
.identity-section h3 { margin-top: 0; margin-bottom: 1rem; }
.entry-list { list-style: none; padding: 0; margin: 0; }
.entry-list li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #e2e8f0;
}
.entry-list li:last-child { border-bottom: none; }
.entry-list a { color: #334155; text-decoration: none; }
.entry-list a:hover { color: #133D72; }
.entry-list .summary { font-size: 0.85rem; color: #64748b; }
@media (max-width: 768px) {
  .identity-grid { grid-template-columns: 1fr; }
}
</style>

## 当前强化方向

- **导航重构**：四大模块为核心，优化知识流转路径
- **搜索升级**：自然语言 + 结构化筛选，精准触达
- **Agent 适配**：一键分享，无缝对接 AI 学习调用
- **知识图谱**：自动生成关联图谱，可视化知识脉络
- **每日精选**：自动产出当日精华，助力知识复用

> 锚定核心领域，深耕与探索并行，在迭代中与时代同频。成果源于主动挖掘机会，而非被动解决问题。
