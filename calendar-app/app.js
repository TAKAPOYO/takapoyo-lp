// =====================================================
//  カレンダーアプリ
//  - LocalStorage でデータ保存
//  - File System Access API で Obsidian Vault 連携
// =====================================================

// ── 状態管理 ──────────────────────────────────────

const state = {
  currentYear: new Date().getFullYear(),
  currentMonth: new Date().getMonth(), // 0-indexed
  selectedDate: null,     // "YYYY-MM-DD"
  vaultHandle: null,      // FileSystemDirectoryHandle
  vaultName: null,
  memoSaveTimer: null,
};

// ── データ操作 (LocalStorage) ──────────────────────

function storageKey(dateStr) {
  return `cal_${dateStr}`;
}

function loadDayData(dateStr) {
  const raw = localStorage.getItem(storageKey(dateStr));
  if (!raw) return { todos: [], memo: '' };
  try { return JSON.parse(raw); } catch { return { todos: [], memo: '' }; }
}

function saveDayData(dateStr, data) {
  localStorage.setItem(storageKey(dateStr), JSON.stringify(data));
}

// ── 日付ユーティリティ ────────────────────────────

function toDateStr(year, month, day) {
  return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

function todayStr() {
  const d = new Date();
  return toDateStr(d.getFullYear(), d.getMonth(), d.getDate());
}

const WEEKDAY_JA = ['日曜日', '月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日'];
const MONTH_STR  = (m) => `${m + 1}月`;

// ── Markdown 変換 (Obsidian 互換) ─────────────────

function dataToMarkdown(dateStr, data) {
  const todoLines = data.todos.map(t =>
    `- [${t.done ? 'x' : ' '}] ${t.text}`
  ).join('\n');

  const parts = [`---\ndate: ${dateStr}\n---\n`];
  if (data.todos.length > 0) {
    parts.push(`## Todo\n${todoLines}`);
  }
  if (data.memo.trim()) {
    parts.push(`## メモ\n${data.memo.trim()}`);
  }
  return parts.join('\n\n') + '\n';
}

function markdownToData(md) {
  const data = { todos: [], memo: '' };

  // Todo パース
  const todoSection = md.match(/## Todo\n([\s\S]*?)(?=\n## |\n---|\s*$)/);
  if (todoSection) {
    const lines = todoSection[1].trim().split('\n');
    for (const line of lines) {
      const m = line.match(/^- \[( |x)\] (.+)$/);
      if (m) {
        data.todos.push({ id: crypto.randomUUID(), text: m[2], done: m[1] === 'x' });
      }
    }
  }

  // メモ パース
  const memoSection = md.match(/## メモ\n([\s\S]*?)(?=\n## |\s*$)/);
  if (memoSection) {
    data.memo = memoSection[1].trim();
  }

  return data;
}

// ── Obsidian Vault (File System Access API) ────────

async function selectVault() {
  if (!window.showDirectoryPicker) {
    alert('このブラウザはFile System Access APIに対応していません。\nChrome または Edge をお使いください。');
    return;
  }
  try {
    const handle = await window.showDirectoryPicker({ mode: 'readwrite' });
    state.vaultHandle = handle;
    state.vaultName = handle.name;
    updateVaultUI();
    // 現在選択中の日付があれば読み込み直す
    if (state.selectedDate) {
      await loadFromVault(state.selectedDate);
    }
  } catch (e) {
    if (e.name !== 'AbortError') console.error(e);
  }
}

async function getOrCreateCalendarDir() {
  if (!state.vaultHandle) return null;
  try {
    return await state.vaultHandle.getDirectoryHandle('Calendar', { create: true });
  } catch (e) {
    console.error('Calendarフォルダの作成に失敗:', e);
    return null;
  }
}

async function loadFromVault(dateStr) {
  const dir = await getOrCreateCalendarDir();
  if (!dir) return;
  try {
    const fileHandle = await dir.getFileHandle(`${dateStr}.md`);
    const file = await fileHandle.getFile();
    const text = await file.text();
    const data = markdownToData(text);
    saveDayData(dateStr, data); // LocalStorage にも保存
    if (state.selectedDate === dateStr) renderPanel(dateStr);
  } catch (e) {
    if (e.name !== 'NotFoundError') console.error(e);
    // ファイルがなければ何もしない
  }
}

async function saveToVault(dateStr) {
  const dir = await getOrCreateCalendarDir();
  if (!dir) return;
  try {
    const data = loadDayData(dateStr);
    const md = dataToMarkdown(dateStr, data);
    const fileHandle = await dir.getFileHandle(`${dateStr}.md`, { create: true });
    const writable = await fileHandle.createWritable();
    await writable.write(md);
    await writable.close();
  } catch (e) {
    console.error('Vault書き込みエラー:', e);
  }
}

function openInObsidian(dateStr) {
  if (!state.vaultName) return;
  const path = `Calendar/${dateStr}.md`;
  const uri = `obsidian://open?vault=${encodeURIComponent(state.vaultName)}&file=${encodeURIComponent(path)}`;
  window.location.href = uri;
}

// ── カレンダー描画 ─────────────────────────────────

function renderCalendar() {
  const { currentYear: y, currentMonth: m } = state;

  document.getElementById('month-title').textContent =
    `${y}年 ${MONTH_STR(m)}`;

  const grid = document.getElementById('calendar-grid');
  grid.innerHTML = '';

  const firstDay = new Date(y, m, 1).getDay(); // 0=Sun
  const daysInMonth = new Date(y, m + 1, 0).getDate();
  const daysInPrevMonth = new Date(y, m, 0).getDate();

  const today = todayStr();
  const cells = [];

  // 前月の日
  for (let i = firstDay - 1; i >= 0; i--) {
    cells.push({ day: daysInPrevMonth - i, month: m - 1, year: m === 0 ? y - 1 : y, otherMonth: true });
  }
  // 当月の日
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push({ day: d, month: m, year: y, otherMonth: false });
  }
  // 次月の日 (6行埋め)
  const remaining = 42 - cells.length;
  for (let d = 1; d <= remaining; d++) {
    cells.push({ day: d, month: m + 1, year: m === 11 ? y + 1 : y, otherMonth: true });
  }

  for (const cell of cells) {
    const adjustedMonth = cell.month < 0 ? 11 : cell.month > 11 ? 0 : cell.month;
    const adjustedYear = cell.month < 0 ? cell.year - 1 : cell.month > 11 ? cell.year + 1 : cell.year;
    const dateStr = toDateStr(adjustedYear, adjustedMonth, cell.day);
    const weekday = new Date(adjustedYear, adjustedMonth, cell.day).getDay();

    const el = document.createElement('div');
    el.className = 'day-cell';
    if (cell.otherMonth) el.classList.add('other-month');
    if (dateStr === today) el.classList.add('today');
    if (dateStr === state.selectedDate) el.classList.add('selected');
    if (weekday === 0) el.classList.add('sunday');
    if (weekday === 6) el.classList.add('saturday');

    // データ確認
    const data = loadDayData(dateStr);
    const hasTodos = data.todos.length > 0;
    const hasMemo  = data.memo.trim().length > 0;
    if (hasTodos || hasMemo) el.classList.add('has-data');

    // 日付数字
    const numEl = document.createElement('div');
    numEl.className = 'day-number';
    numEl.textContent = cell.day;
    el.appendChild(numEl);

    // バッジ
    if (hasTodos || hasMemo) {
      const badgeEl = document.createElement('div');
      badgeEl.className = 'day-badges';
      if (hasTodos) {
        const done = data.todos.filter(t => t.done).length;
        const total = data.todos.length;
        const b = document.createElement('span');
        b.className = `badge-todo${done === total ? ' all-done' : ''}`;
        b.textContent = `✓ ${done}/${total}`;
        badgeEl.appendChild(b);
      }
      if (hasMemo) {
        const b = document.createElement('span');
        b.className = 'badge-memo';
        b.textContent = '📝';
        badgeEl.appendChild(b);
      }
      el.appendChild(badgeEl);
    }

    if (!cell.otherMonth) {
      el.addEventListener('click', () => selectDate(dateStr));
    }

    grid.appendChild(el);
  }
}

// ── パネル開閉 ────────────────────────────────────

function isMobile() {
  return window.innerWidth < 768;
}

function openPanel() {
  const panel = document.getElementById('side-panel');
  panel.classList.remove('panel-hidden');

  if (isMobile()) {
    const backdrop = document.getElementById('backdrop');
    backdrop.classList.remove('hidden');
    // スクロール防止
    document.body.style.overflow = 'hidden';
  } else {
    document.getElementById('empty-panel').classList.add('hidden');
  }
}

function closePanel() {
  const panel = document.getElementById('side-panel');
  panel.classList.add('panel-hidden');
  state.selectedDate = null;

  if (isMobile()) {
    document.getElementById('backdrop').classList.add('hidden');
    document.body.style.overflow = '';
  } else {
    document.getElementById('empty-panel').classList.remove('hidden');
  }

  renderCalendar();
}

async function selectDate(dateStr) {
  state.selectedDate = dateStr;

  // Vault があれば最新を読み込む
  if (state.vaultHandle) {
    await loadFromVault(dateStr);
  }

  renderCalendar();
  renderPanel(dateStr);
  openPanel();
}

function renderPanel(dateStr) {
  const [y, mo, d] = dateStr.split('-').map(Number);
  const dateObj = new Date(y, mo - 1, d);
  const weekday = WEEKDAY_JA[dateObj.getDay()];

  const monthDay = `${mo}月${d}日`;
  document.getElementById('panel-date-label').textContent = `${y}年 ${monthDay}`;
  document.getElementById('panel-weekday-label').textContent = weekday;

  // Obsidianで開くボタン
  const obsBtn = document.getElementById('btn-open-obsidian');
  if (state.vaultHandle) {
    obsBtn.classList.remove('hidden');
    obsBtn.onclick = () => openInObsidian(dateStr);
  } else {
    obsBtn.classList.add('hidden');
  }

  const data = loadDayData(dateStr);
  renderTodoList(dateStr, data.todos);

  const memoInput = document.getElementById('memo-input');
  memoInput.value = data.memo;
}

// ── Todo ──────────────────────────────────────────

function renderTodoList(dateStr, todos) {
  const list = document.getElementById('todo-list');
  const empty = document.getElementById('todo-empty');
  list.innerHTML = '';

  if (todos.length === 0) {
    empty.classList.remove('hidden');
    return;
  }
  empty.classList.add('hidden');

  for (const todo of todos) {
    const li = document.createElement('li');
    li.className = `todo-item${todo.done ? ' done' : ''}`;
    li.dataset.id = todo.id;

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = todo.done;
    checkbox.addEventListener('change', () => toggleTodo(dateStr, todo.id));

    const textEl = document.createElement('span');
    textEl.className = 'todo-text';
    textEl.contentEditable = 'true';
    textEl.textContent = todo.text;
    textEl.addEventListener('blur', () => editTodoText(dateStr, todo.id, textEl.textContent.trim()));
    textEl.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') { e.preventDefault(); textEl.blur(); }
    });

    const delBtn = document.createElement('button');
    delBtn.className = 'btn-delete-todo';
    delBtn.textContent = '✕';
    delBtn.addEventListener('click', () => deleteTodo(dateStr, todo.id));

    li.appendChild(checkbox);
    li.appendChild(textEl);
    li.appendChild(delBtn);
    list.appendChild(li);
  }
}

function addTodo(dateStr) {
  const input = document.getElementById('todo-input');
  const text = input.value.trim();
  if (!text) return;

  const data = loadDayData(dateStr);
  data.todos.push({ id: crypto.randomUUID(), text, done: false });
  saveDayData(dateStr, data);
  input.value = '';
  renderTodoList(dateStr, data.todos);
  renderCalendar();
  syncToVault(dateStr);
}

function toggleTodo(dateStr, id) {
  const data = loadDayData(dateStr);
  const todo = data.todos.find(t => t.id === id);
  if (todo) todo.done = !todo.done;
  saveDayData(dateStr, data);
  renderTodoList(dateStr, data.todos);
  renderCalendar();
  syncToVault(dateStr);
}

function editTodoText(dateStr, id, newText) {
  if (!newText) { deleteTodo(dateStr, id); return; }
  const data = loadDayData(dateStr);
  const todo = data.todos.find(t => t.id === id);
  if (todo && todo.text !== newText) {
    todo.text = newText;
    saveDayData(dateStr, data);
    syncToVault(dateStr);
  }
}

function deleteTodo(dateStr, id) {
  const data = loadDayData(dateStr);
  data.todos = data.todos.filter(t => t.id !== id);
  saveDayData(dateStr, data);
  renderTodoList(dateStr, data.todos);
  renderCalendar();
  syncToVault(dateStr);
}

// ── メモ ──────────────────────────────────────────

function onMemoInput(dateStr) {
  const memo = document.getElementById('memo-input').value;
  const data = loadDayData(dateStr);
  data.memo = memo;
  saveDayData(dateStr, data);
  renderCalendar();

  // 保存ステータス
  const status = document.getElementById('memo-save-status');
  status.textContent = '保存中...';
  clearTimeout(state.memoSaveTimer);
  state.memoSaveTimer = setTimeout(async () => {
    await syncToVault(dateStr);
    status.textContent = '保存済み ✓';
    setTimeout(() => { status.textContent = ''; }, 2000);
  }, 800);
}

// ── Vault 同期 ────────────────────────────────────

async function syncToVault(dateStr) {
  if (state.vaultHandle) {
    await saveToVault(dateStr);
  }
}

function updateVaultUI() {
  const icon  = document.getElementById('vault-icon');
  const label = document.getElementById('vault-label');
  if (state.vaultHandle) {
    icon.textContent = '✅';
    label.textContent = state.vaultName;
  } else {
    icon.textContent = '📁';
    label.textContent = 'Vaultを選択';
  }
}

// ── イベント初期化 ────────────────────────────────

function initEvents() {
  // 月ナビゲーション
  document.getElementById('btn-prev').addEventListener('click', () => {
    state.currentMonth--;
    if (state.currentMonth < 0) { state.currentMonth = 11; state.currentYear--; }
    renderCalendar();
  });

  document.getElementById('btn-next').addEventListener('click', () => {
    state.currentMonth++;
    if (state.currentMonth > 11) { state.currentMonth = 0; state.currentYear++; }
    renderCalendar();
  });

  // パネルを閉じる
  document.getElementById('btn-close-panel').addEventListener('click', closePanel);

  // バックドロップをタップして閉じる (モバイル)
  document.getElementById('backdrop').addEventListener('click', closePanel);

  // Vault選択
  document.getElementById('btn-vault').addEventListener('click', selectVault);

  // Todo 追加
  document.getElementById('btn-add-todo').addEventListener('click', () => {
    if (state.selectedDate) addTodo(state.selectedDate);
  });
  document.getElementById('todo-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && state.selectedDate) addTodo(state.selectedDate);
  });

  // メモ入力
  document.getElementById('memo-input').addEventListener('input', () => {
    if (state.selectedDate) onMemoInput(state.selectedDate);
  });
}

// ── 起動 ──────────────────────────────────────────

function init() {
  initEvents();
  renderCalendar();

  // PC のみ今日を自動選択 (スマホは手動で開く方が自然)
  if (!isMobile()) {
    selectDate(todayStr());
  }
}

init();
