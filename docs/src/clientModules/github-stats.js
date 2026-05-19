// Fetches live star/fork counts from GitHub and injects them into the navbar
// chip rendered by the html nav item.
//
// Cached in localStorage for an hour so we don't burn through the unauthenticated
// GitHub API quota when readers click around.

const REPO = 'eidetic-labs/craik';
const CACHE_KEY = 'craik:gh-stats';
const CACHE_TTL_MS = 60 * 60 * 1000;

function format(n) {
  if (typeof n !== 'number' || !Number.isFinite(n)) return '—';
  if (n >= 10000) return Math.round(n / 1000) + 'k';
  if (n >= 1000) return (n / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
  return String(n);
}

function apply(stats) {
  if (!stats) return;
  document.querySelectorAll('[data-gh-stars]').forEach((el) => {
    el.textContent = format(stats.stars);
  });
  document.querySelectorAll('[data-gh-forks]').forEach((el) => {
    el.textContent = format(stats.forks);
  });
}

function readCache() {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (Date.now() - parsed.at > CACHE_TTL_MS) return null;
    return parsed;
  } catch {
    return null;
  }
}

function writeCache(stats) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(stats));
  } catch {
    /* storage unavailable — silently skip */
  }
}

async function fetchStats() {
  try {
    const res = await fetch(`https://api.github.com/repos/${REPO}`, {
      headers: { Accept: 'application/vnd.github+json' },
    });
    if (!res.ok) return null;
    const data = await res.json();
    return {
      stars: data.stargazers_count,
      forks: data.forks_count,
      at: Date.now(),
    };
  } catch {
    return null;
  }
}

async function load() {
  const cached = readCache();
  if (cached) apply(cached);

  const fresh = await fetchStats();
  if (fresh) {
    writeCache(fresh);
    apply(fresh);
  }
}

function whenReady(selector, run) {
  if (typeof document === 'undefined') return;
  if (document.querySelector(selector)) {
    run();
    return;
  }
  const obs = new MutationObserver(() => {
    if (document.querySelector(selector)) {
      obs.disconnect();
      run();
    }
  });
  obs.observe(document.body || document.documentElement, {
    childList: true,
    subtree: true,
  });
  // Stop watching after 8s if the target never appears.
  setTimeout(() => obs.disconnect(), 8000);
}

export function onRouteDidUpdate() {
  whenReady('[data-gh-stars]', load);
}

if (typeof window !== 'undefined') {
  whenReady('[data-gh-stars]', load);
}
