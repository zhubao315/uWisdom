---
title: 知识图谱
summary: uWisdom 知识库可视化图谱
permalink: /graph/
---

# 知识图谱

<div class="graph-controls">
  <div class="stat-cards" id="stat-cards">
    <div class="stat-card">
      <div class="stat-value" id="total-entries">--</div>
      <div class="stat-label">知识条目</div>
    </div>
    <div class="stat-card">
      <div class="stat-value" id="total-tags">--</div>
      <div class="stat-label">标签</div>
    </div>
    <div class="stat-card">
      <div class="stat-value" id="total-links">--</div>
      <div class="stat-label">关联关系</div>
    </div>
  </div>
  
  <div class="view-toggle">
    <button class="btn active" data-view="graph">关系图谱</button>
    <button class="btn" data-view="tagcloud">标签云</button>
    <button class="btn" data-view="timeline">时间线</button>
  </div>
</div>

## 知识网络

<div class="graph-container" id="graph-container">
  <div id="knowledge-graph"></div>
  <div class="graph-legend" id="graph-legend"></div>
</div>

<div class="tagcloud-container" id="tagcloud-container" style="display:none;">
  <div id="tag-cloud"></div>
</div>

<div class="timeline-container" id="timeline-container" style="display:none;">
  <div id="timeline"></div>
</div>

<style>
.graph-controls {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.stat-cards {
  display: flex;
  gap: 1rem;
}

.stat-card {
  background: linear-gradient(135deg, var(--sapphire) 0%, #1a5299 100%);
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  text-align: center;
  min-width: 120px;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  font-family: 'JetBrains Mono', monospace;
}

.stat-label {
  font-size: 0.875rem;
  opacity: 0.9;
}

.view-toggle {
  display: flex;
  gap: 0.5rem;
}

.view-toggle .btn {
  padding: 0.5rem 1rem;
  border: 2px solid var(--sapphire);
  background: white;
  color: var(--sapphire);
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.view-toggle .btn:hover {
  background: var(--slate-100);
}

.view-toggle .btn.active {
  background: var(--sapphire);
  color: white;
}

.graph-container {
  position: relative;
  background: var(--slate-900);
  border-radius: 16px;
  overflow: hidden;
  min-height: 600px;
}

#knowledge-graph {
  width: 100%;
  height: 600px;
}

.graph-legend {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  background: rgba(255,255,255,0.95);
  padding: 1rem;
  border-radius: 8px;
  font-size: 0.875rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.tagcloud-container {
  background: var(--slate-50);
  border-radius: 16px;
  padding: 2rem;
}

#tag-cloud {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  min-height: 400px;
}

.tag-item {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
  border: 2px solid transparent;
}

.tag-item:hover {
  transform: scale(1.1);
  border-color: var(--sapphire);
}

.tag-size-1 { font-size: 0.75rem; background: #E0E7FF; color: #3730A3; }
.tag-size-2 { font-size: 0.875rem; background: #C7D2FE; color: #4338CA; }
.tag-size-3 { font-size: 1rem; background: #A5B4FC; color: #4F46E5; }
.tag-size-4 { font-size: 1.125rem; background: #818CF8; color: #4338CA; }
.tag-size-5 { font-size: 1.25rem; background: #6366F1; color: white; }

.timeline-container {
  padding: 2rem;
}

#timeline {
  position: relative;
  padding-left: 2rem;
}

#timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, var(--sapphire), var(--teal));
}

.timeline-item {
  position: relative;
  padding: 1rem;
  margin-bottom: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: all 0.2s;
}

.timeline-item:hover {
  transform: translateX(8px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: -2rem;
  top: 1.5rem;
  width: 18px;
  height: 18px;
  background: white;
  border: 3px solid var(--sapphire);
  border-radius: 50%;
}

.timeline-date {
  font-size: 0.75rem;
  color: var(--slate-500);
  font-family: 'JetBrains Mono', monospace;
  margin-bottom: 0.25rem;
}

.timeline-title {
  font-weight: 600;
  color: var(--slate-900);
  margin-bottom: 0.25rem;
}

.timeline-title a {
  color: inherit;
  text-decoration: none;
}

.timeline-title a:hover {
  color: var(--sapphire);
}

.timeline-section {
  font-size: 0.75rem;
  color: var(--slate-500);
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  color: var(--slate-500);
}
</style>

<script>
async function loadVisualization() {
  try {
    const [vizResponse, searchResponse] = await Promise.all([
      fetch('/assets/visualization-data.json?v=' + Date.now()),
      fetch('/assets/search-index.json?v=' + Date.now())
    ]);
    
    const vizData = await vizResponse.json();
    const searchData = await searchResponse.json();
    
    // Update stats
    document.getElementById('total-entries').textContent = searchData.entries.length;
    document.getElementById('total-tags').textContent = vizData.tagCloud.length;
    document.getElementById('total-links').textContent = vizData.graph.links.length;
    
    // Render tag cloud
    renderTagCloud(vizData.tagCloud);
    
    // Render timeline
    renderTimeline(vizData.timeline);
    
    // Render graph (simplified D3-like visualization)
    renderGraph(vizData.graph);
    
    // Render legend
    renderLegend();
    
  } catch (error) {
    console.error('Failed to load visualization:', error);
  }
}

function renderTagCloud(tags) {
  const container = document.getElementById('tag-cloud');
  const maxCount = Math.max(...tags.map(t => t.count));
  
  tags.forEach(tag => {
    const size = Math.ceil((tag.count / maxCount) * 5);
    const item = document.createElement('a');
    item.className = `tag-item tag-size-${size}`;
    item.href = `/search/?q=${encodeURIComponent(tag.tag)}`;
    item.textContent = `${tag.tag} (${tag.count})`;
    container.appendChild(item);
  });
}

function renderTimeline(timeline) {
  const container = document.getElementById('timeline');
  
  timeline.forEach(item => {
    const div = document.createElement('div');
    div.className = 'timeline-item';
    div.innerHTML = `
      <div class="timeline-date">${item.updated}</div>
      <div class="timeline-title">
        <a href="${item.url}">${item.title}</a>
      </div>
      <div class="timeline-section">${item.section}</div>
    `;
    container.appendChild(div);
  });
}

function renderGraph(graph) {
  const container = document.getElementById('knowledge-graph');
  
  // Create SVG-based graph visualization
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('width', '100%');
  svg.setAttribute('height', '100%');
  svg.style.display = 'block';
  
  const colors = {
    'architect': '#133D72',
    'investor': '#059669',
    'lifelong-learner': '#7C3AED',
    'life-artist': '#DC2626',
    'default': '#6B7280'
  };
  
  // Simple force-directed layout simulation
  const width = container.clientWidth || 800;
  const height = container.clientHeight || 600;
  
  // Position nodes in a circle
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) * 0.35;
  
  const nodes = graph.nodes.map((node, i) => {
    const angle = (2 * Math.PI * i) / graph.nodes.length;
    return {
      ...node,
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
      vx: 0,
      vy: 0
    };
  });
  
  const nodeMap = {};
  nodes.forEach((n, i) => nodeMap[n.id] = i);
  
  // Simple force simulation
  for (let iter = 0; iter < 100; iter++) {
    // Repulsion between nodes
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const dx = nodes[j].x - nodes[i].x;
        const dy = nodes[j].y - nodes[i].y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const force = 5000 / (dist * dist);
        nodes[i].vx -= (dx / dist) * force;
        nodes[i].vy -= (dy / dist) * force;
        nodes[j].vx += (dx / dist) * force;
        nodes[j].vy += (dy / dist) * force;
      }
    }
    
    // Attraction along links
    graph.links.forEach(link => {
      const source = nodeMap[link.source];
      const target = nodeMap[link.target];
      if (source === undefined || target === undefined) return;
      
      const dx = nodes[target].x - nodes[source].x;
      const dy = nodes[target].y - nodes[source].y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const force = dist * 0.01;
      
      nodes[source].vx += (dx / dist) * force;
      nodes[source].vy += (dy / dist) * force;
      nodes[target].vx -= (dx / dist) * force;
      nodes[target].vy -= (dy / dist) * force;
    });
    
    // Apply velocity with damping
    for (let i = 0; i < nodes.length; i++) {
      nodes[i].x += nodes[i].vx * 0.1;
      nodes[i].y += nodes[i].vy * 0.1;
      nodes[i].vx *= 0.9;
      nodes[i].vy *= 0.9;
      
      // Keep within bounds
      nodes[i].x = Math.max(50, Math.min(width - 50, nodes[i].x));
      nodes[i].y = Math.max(50, Math.min(height - 50, nodes[i].y));
    }
  }
  
  // Draw links
  const linksGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  graph.links.forEach(link => {
    const sourceIdx = nodeMap[link.source];
    const targetIdx = nodeMap[link.target];
    if (sourceIdx === undefined || targetIdx === undefined) return;
    
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', nodes[sourceIdx].x);
    line.setAttribute('y1', nodes[sourceIdx].y);
    line.setAttribute('x2', nodes[targetIdx].x);
    line.setAttribute('y2', nodes[targetIdx].y);
    line.setAttribute('stroke', '#4B5563');
    line.setAttribute('stroke-width', '1');
    line.setAttribute('stroke-opacity', '0.4');
    linksGroup.appendChild(line);
  });
  svg.appendChild(linksGroup);
  
  // Draw nodes
  const nodesGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  nodes.forEach((node, i) => {
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('transform', `translate(${node.x}, ${node.y})`);
    g.style.cursor = 'pointer';
    
    const color = colors[node.identity] || colors.default;
    
    // Circle
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('r', node.tags.length > 0 ? '20' : '15');
    circle.setAttribute('fill', color);
    circle.setAttribute('opacity', '0.8');
    g.appendChild(circle);
    
    // Label
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('dy', node.tags.length > 0 ? '35' : '30');
    text.setAttribute('fill', '#E5E7EB');
    text.setAttribute('font-size', '11');
    text.setAttribute('font-family', 'Inter, sans-serif');
    text.textContent = node.title.length > 15 ? node.title.substring(0, 15) + '...' : node.title;
    g.appendChild(text);
    
    // Link wrapper
    const linkWrapper = document.createElementNS('http://www.w3.org/2000/svg', 'a');
    linkWrapper.setAttribute('href', node.id);
    
    g.addEventListener('click', () => {
      window.location.href = node.id;
    });
    
    g.addEventListener('mouseenter', () => {
      circle.setAttribute('opacity', '1');
      circle.setAttribute('r', (node.tags.length > 0 ? 24 : 18).toString());
    });
    
    g.addEventListener('mouseleave', () => {
      circle.setAttribute('opacity', '0.8');
      circle.setAttribute('r', (node.tags.length > 0 ? 20 : 15).toString());
    });
    
    nodesGroup.appendChild(g);
  });
  svg.appendChild(nodesGroup);
  
  container.appendChild(svg);
}

function renderLegend() {
  const legend = document.getElementById('graph-legend');
  const items = [
    { label: '架构师', color: '#133D72' },
    { label: '投资人', color: '#059669' },
    { label: '终身学习者', color: '#7C3AED' },
    { label: '生活艺术家', color: '#DC2626' },
    { label: '其他', color: '#6B7280' }
  ];
  
  legend.innerHTML = items.map(item => `
    <div class="legend-item">
      <span class="legend-dot" style="background: ${item.color}"></span>
      <span>${item.label}</span>
    </div>
  `).join('');
}

// View toggle
document.querySelectorAll('.view-toggle .btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.view-toggle .btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    
    const view = btn.dataset.view;
    document.getElementById('graph-container').style.display = view === 'graph' ? 'block' : 'none';
    document.getElementById('tagcloud-container').style.display = view === 'tagcloud' ? 'block' : 'none';
    document.getElementById('timeline-container').style.display = view === 'timeline' ? 'block' : 'none';
  });
});

document.addEventListener('DOMContentLoaded', loadVisualization);
</script>
