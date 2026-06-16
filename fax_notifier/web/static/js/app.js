let latestReceivedAt = null;
let selectedId = null;

async function loadFaxes() {
  const res = await fetch('/api/faxes');
  const faxes = await res.json();
  renderList(faxes);
  if (faxes.length > 0 && latestReceivedAt === null) {
    latestReceivedAt = faxes[0].received_at;
  }
}

function renderList(faxes) {
  const list = document.getElementById('fax-list');
  if (faxes.length === 0) {
    list.innerHTML = '<p class="loading">FAXはまだありません</p>';
    return;
  }
  list.innerHTML = faxes.map(f => `
    <div class="fax-item${f.id === selectedId ? ' active' : ''}" onclick="selectFax(${f.id}, '${escHtml(f.filename)}')">
      <div class="filename">${escHtml(f.filename)}</div>
      <div class="received-at">${formatDate(f.received_at)}</div>
    </div>
  `).join('');
}

async function selectFax(id, filename) {
  selectedId = id;
  const panel = document.getElementById('preview-panel');
  const ext = filename.split('.').pop().toLowerCase();

  document.querySelectorAll('.fax-item').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.fax-item').forEach(el => {
    if (el.querySelector('.filename').textContent === filename) {
      el.classList.add('active');
    }
  });

  if (ext === 'pdf') {
    panel.innerHTML = `<iframe src="/api/faxes/${id}/file"></iframe>`;
    return;
  }

  // TIFF: ページ数を取得してから全ページを縦並びで表示
  panel.innerHTML = '<p class="loading">読み込み中...</p>';
  const res = await fetch(`/api/faxes/${id}/pages`);
  const { total } = await res.json();

  const pages = Array.from({ length: total }, (_, i) =>
    `<img src="/api/faxes/${id}/file?page=${i}" alt="${escHtml(filename)} p.${i + 1}" loading="lazy">`
  ).join('');
  panel.innerHTML = `
    <div class="tiff-pages">
      <div class="tiff-page-count">${total}ページ</div>
      ${pages}
    </div>`;
}

async function pollNew() {
  if (latestReceivedAt === null) return;
  const res = await fetch(`/api/faxes/new?since=${encodeURIComponent(latestReceivedAt)}`);
  const newFaxes = await res.json();
  if (newFaxes.length === 0) return;

  latestReceivedAt = newFaxes[0].received_at;
  showBanner(`新しいFAXが${newFaxes.length}件届きました`);
  await loadFaxes();
}

function showBanner(message) {
  const banner = document.getElementById('banner');
  document.getElementById('banner-text').textContent = message;
  banner.classList.remove('hidden');
}

function closeBanner() {
  document.getElementById('banner').classList.add('hidden');
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function formatDate(iso) {
  return new Date(iso).toLocaleString('ja-JP');
}

loadFaxes();
setInterval(pollNew, POLLING_INTERVAL);
