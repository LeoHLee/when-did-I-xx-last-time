const listEl = document.getElementById('list');
const skeleton = document.getElementById('skeleton');
const errorEl = document.getElementById('error');

const modal = document.getElementById('modal');
const modalSkeleton = document.getElementById('modalSkeleton');
const historyList = document.getElementById('historyList');

function format(sec) {
  return new Date(sec * 1000).toLocaleString();
}

function showSkeleton() {
  skeleton.hidden = false;
  skeleton.classList.add('show');
}

function hideSkeleton() {
  skeleton.classList.remove('show');
  skeleton.hidden = true;
}

async function loadItems() {
  showSkeleton();
  listEl.hidden = true;
  errorEl.hidden = true;

  try {
    const res = await fetch('/api/items');
    const items = await res.json();

    listEl.innerHTML = '';
    items.forEach(i => {
      const li = document.createElement('li');
        li.innerHTML = `
        <div class="item-info" data-id="${i.id}">
            <strong>${i.name}</strong>
            <span class="item-time">${i.last_time ? format(i.last_time) : '—'}</span>
        </div>
        <div>
            <button class="secondary" data-id="${i.id}" data-action="history">历史</button>
        </div>
        `;
      listEl.appendChild(li);
    });

    hideSkeleton();
    listEl.hidden = false;
  } catch {
    errorEl.textContent = '加载失败，请刷新页面';
    errorEl.hidden = false;
  }
}

listEl.addEventListener('click', async e => {
  const historyBtn = e.target.closest('button[data-action="history"]');
  if (historyBtn) {
    const id = historyBtn.dataset.id;
    openModal();
    modalSkeleton.hidden = false;
    historyList.hidden = true;

    const res = await fetch(`/api/items/${id}/history`);
    const data = await res.json();

    historyList.innerHTML = '';
    data.forEach(t => {
      const div = document.createElement('div');
      div.className = 'history-item';
      div.textContent = format(t);
      historyList.appendChild(div);
    });

    modalSkeleton.hidden = true;
    historyList.hidden = false;
    return;
  }

  const itemInfo = e.target.closest('.item-info');
  if (itemInfo) {
    const id = itemInfo.dataset.id;
    if (!confirm('确定刷新为当前时间？')) return;

    itemInfo.classList.add('loading');
    await fetch(`/api/items/${id}/refresh`, { method: 'POST' });
    loadItems();
  }
});

document.getElementById('addBtn').onclick = async () => {
  const input = document.getElementById('newItem');
  const name = input.value.trim();
  if (!name) return;

  await fetch('/api/items', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  });

  input.value = '';
  loadItems();
};

function openModal() {
  modal.hidden = false;
  modal.classList.add('show');
}

function closeModal() {
  modal.classList.remove('show');
  modal.hidden = true;
}

modal.onclick = e => {
  if (e.target === modal || e.target.classList.contains('close')) {
    closeModal();
  }
};

loadItems();
