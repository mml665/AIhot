// ===== State =====
let allNews = [];
let currentFilter = 'all';
let searchQuery = '';
const API_BASE = window.location.origin;

// ===== DOM Elements =====
const newsGrid = document.getElementById('newsGrid');
const searchInput = document.getElementById('searchInput');
const themeToggle = document.getElementById('themeToggle');
const totalNewsEl = document.getElementById('totalNews');
const totalCategoriesEl = document.getElementById('totalCategories');
const newsCountEl = document.getElementById('newsCount');
const emptyState = document.getElementById('emptyState');
const navBtns = document.querySelectorAll('.nav-btn');
const refreshBtn = document.getElementById('refreshBtn');

// ===== Init =====
async function init() {
  loadTheme();
  await loadNews();
  renderNews();
  updateStats();
  bindEvents();
}

// ===== Load News from API =====
async function loadNews() {
  try {
    const res = await fetch(`${API_BASE}/api/news`);
    const data = await res.json();
    allNews = data.items || [];
  } catch {
    // Fallback: try loading from local JSON
    try {
      const res = await fetch('data/news.json');
      allNews = await res.json();
    } catch {
      allNews = [];
    }
  }
}

// ===== Render News Cards =====
function renderNews() {
  const filtered = filterNews();
  newsCountEl.textContent = `${filtered.length} 条`;

  if (filtered.length === 0) {
    newsGrid.innerHTML = '';
    emptyState.style.display = 'block';
    return;
  }

  emptyState.style.display = 'none';
  newsGrid.innerHTML = filtered.map((item, i) => `
    <article class="news-card" style="animation-delay: ${i * 0.05}s" onclick="openNews('${item.url}')">
      <div class="card-header">
        <span class="card-category">${item.category}</span>
        ${item.tag ? `<span class="card-tag ${item.tag}">${item.tag === 'hot' ? '🔥 热门' : '✨ 最新'}</span>` : ''}
      </div>
      <h3 class="card-title">${highlightText(item.title)}</h3>
      <p class="card-summary">${highlightText(item.summary)}</p>
      <div class="card-footer">
        <span class="card-source">${item.source}</span>
        <span class="card-time">${item.time}</span>
      </div>
    </article>
  `).join('');
}

// ===== Filter News =====
function filterNews() {
  return allNews.filter(item => {
    const matchFilter = currentFilter === 'all' || item.category === currentFilter;
    const matchSearch = !searchQuery ||
      item.title.toLowerCase().includes(searchQuery) ||
      item.summary.toLowerCase().includes(searchQuery) ||
      item.category.toLowerCase().includes(searchQuery);
    return matchFilter && matchSearch;
  });
}

// ===== Highlight Search Text =====
function highlightText(text) {
  if (!searchQuery) return text;
  const regex = new RegExp(`(${escapeRegex(searchQuery)})`, 'gi');
  return text.replace(regex, '<mark style="background:#fef08a;padding:0 2px;border-radius:2px;">$1</mark>');
}

function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ===== Update Stats =====
function updateStats() {
  const categories = new Set(allNews.map(n => n.category));
  animateNumber(totalNewsEl, allNews.length);
  totalCategoriesEl.textContent = categories.size;
}

function animateNumber(el, target) {
  let current = 0;
  const step = Math.ceil(target / 20);
  const timer = setInterval(() => {
    current += step;
    if (current >= target) {
      current = target;
      clearInterval(timer);
    }
    el.textContent = current;
  }, 30);
}

// ===== Open News =====
function openNews(url) {
  if (url) window.open(url, '_blank');
}

// ===== Theme Toggle =====
function loadTheme() {
  const saved = localStorage.getItem('aihot-theme');
  if (saved === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
  }
}

function toggleTheme() {
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  if (isDark) {
    document.documentElement.removeAttribute('data-theme');
    localStorage.setItem('aihot-theme', 'light');
  } else {
    document.documentElement.setAttribute('data-theme', 'dark');
    localStorage.setItem('aihot-theme', 'dark');
  }
}

// ===== Bind Events =====
function bindEvents() {
  // Search
  let debounceTimer;
  searchInput.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      searchQuery = e.target.value.trim().toLowerCase();
      renderNews();
    }, 200);
  });

  // Category filter
  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      navBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.filter;
      renderNews();
    });
  });

  // Theme toggle
  themeToggle.addEventListener('click', toggleTheme);

  // Refresh
  refreshBtn.addEventListener('click', refreshNews);
}

// ===== Refresh News =====
async function refreshNews() {
  refreshBtn.classList.add('spinning');
  try {
    await fetch(`${API_BASE}/api/refresh`, { method: 'POST' });
    await loadNews();
    renderNews();
    updateStats();
  } catch {
    // Silently fail
  }
  refreshBtn.classList.remove('spinning');
}

// ===== Start =====
init();
