const API_BASE = '';

function show(el) {
  el.hidden = false;
}
function hide(el) {
  el.hidden = true;
}

function get(id) {
  return document.getElementById(id);
}

async function fetchJson(url, options = {}) {
  const res = await fetch(API_BASE + url, {
    headers: { Accept: 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

function formatDate(iso) {
  if (!iso) return '—';
  try {
    const d = new Date(iso);
    return d.toLocaleString();
  } catch {
    return iso;
  }
}

function stateClass(state) {
  if (!state) return 'UNKNOWN';
  return state;
}

// --- List ---
const listLoading = get('listLoading');
const listError = get('listError');
const listEmpty = get('listEmpty');
const tableWrap = get('tableWrap');
const listBody = get('listBody');

async function loadList() {
  show(listLoading);
  hide(listError);
  hide(listEmpty);
  hide(tableWrap);
  try {
    const data = await fetchJson('/agent/status');
    hide(listLoading);
    if (!data.changes || data.changes.length === 0) {
      show(listEmpty);
      return;
    }
    show(tableWrap);
    listBody.innerHTML = data.changes.map((c) => `
      <tr data-change-id="${escapeAttr(c.changeId)}">
        <td><strong>${escapeHtml(c.changeId)}</strong></td>
        <td><span class="state-badge ${stateClass(c.state)}">${escapeHtml(c.state)}</span></td>
        <td>${escapeHtml(formatDate(c.updatedAt))}</td>
        <td><button type="button" class="btn btn-view" data-change-id="${escapeAttr(c.changeId)}">Open</button></td>
      </tr>
    `).join('');
    listBody.querySelectorAll('tr').forEach((row) => {
      row.addEventListener('click', (e) => {
        if (e.target.closest('.btn-view')) return;
        openDetail(row.dataset.changeId);
      });
    });
    listBody.querySelectorAll('.btn-view').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        openDetail(btn.dataset.changeId);
      });
    });
  } catch (err) {
    hide(listLoading);
    listError.textContent = err.message || 'Failed to load requests';
    show(listError);
  }
}

function escapeAttr(s) {
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML.replace(/"/g, '&quot;');
}
function escapeHtml(s) {
  if (s == null) return '';
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

// --- Detail ---
const detailSection = get('detailSection');
const detailTitle = get('detailTitle');
const detailLoading = get('detailLoading');
const detailError = get('detailError');
const detailContent = get('detailContent');
const detailChangeId = get('detailChangeId');
const detailState = get('detailState');
const detailUpdatedAt = get('detailUpdatedAt');
const detailManifest = get('detailManifest');
const detailArtifacts = get('detailArtifacts');
const deployBtn = get('deployBtn');
const closeDetailBtn = get('closeDetailBtn');

let currentChangeId = null;

function openDetail(changeId) {
  currentChangeId = changeId;
  detailTitle.textContent = `Request: ${changeId}`;
  show(detailSection);
  hide(detailError);
  hide(detailContent);
  show(detailLoading);
  loadDetail(changeId);
}

async function loadDetail(changeId) {
  try {
    const data = await fetchJson(`/agent/status/${encodeURIComponent(changeId)}`);
    hide(detailLoading);
    show(detailContent);
    detailChangeId.textContent = data.changeId;
    detailState.textContent = data.state;
    detailState.className = 'state-badge ' + stateClass(data.state);
    detailUpdatedAt.textContent = formatDate(data.updatedAt);
    const manifest = (data.artifacts && data.artifacts.manifest) || null;
    detailManifest.textContent = manifest
      ? JSON.stringify(manifest, null, 2)
      : 'No manifest stored for this request.';
    detailArtifacts.textContent = data.artifacts
      ? JSON.stringify(
          { gitPatch: data.artifacts.gitPatch, xsd: data.artifacts.xsd, tests: data.artifacts.tests },
          null,
          2
        )
      : 'No artifacts.';
    deployBtn.disabled = data.state === 'DEPLOYED';
  } catch (err) {
    hide(detailLoading);
    detailError.textContent = err.message || 'Failed to load request';
    show(detailError);
  }
}

async function deploy() {
  if (!currentChangeId) return;
  deployBtn.disabled = true;
  try {
    const data = await fetchJson(`/agent/status/${encodeURIComponent(currentChangeId)}/deploy`, {
      method: 'POST',
    });
    detailState.textContent = data.state;
    detailState.className = 'state-badge ' + stateClass(data.state);
    loadList();
  } catch (err) {
    deployBtn.disabled = false;
    alert(err.message || 'Deploy failed');
  }
}

closeDetailBtn.addEventListener('click', () => {
  hide(detailSection);
  currentChangeId = null;
});

deployBtn.addEventListener('click', deploy);

// Tabs
document.querySelectorAll('.tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach((t) => t.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach((p) => p.classList.remove('active'));
    tab.classList.add('active');
    const panel = get('tab' + tab.dataset.tab.charAt(0).toUpperCase() + tab.dataset.tab.slice(1));
    if (panel) panel.classList.add('active');
  });
});

get('refreshBtn').addEventListener('click', loadList);

loadList();
