// APIサーバーのベースURL（環境変数から取得、デフォルトは相対パス）
const API_BASE_URL = window.location.origin.replace(':3000', ':8000') || 'http://localhost:8000';

// ページ読み込み時にTODOリストを取得
loadTodos();

// フォーム送信処理
document.getElementById('todoForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const title = document.getElementById('todoTitle').value.trim();
    if (!title) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/todos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title })
        });

        if (response.ok) {
            document.getElementById('todoTitle').value = '';
            loadTodos();
            showMessage('タスクが追加されました！', 'success');
        } else {
            showMessage('エラーが発生しました', 'error');
        }
    } catch (error) {
        showMessage('接続エラーが発生しました', 'error');
    }
});

// TODOリストの読み込み
async function loadTodos() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/todos`);
        const todos = await response.json();
        displayTodos(todos);
    } catch (error) {
        showMessage('TODOリストの読み込みに失敗しました', 'error');
    }
}

// TODOリストの表示
function displayTodos(todos) {
    const todoList = document.getElementById('todoList');
    if (todos.length === 0) {
        todoList.innerHTML = '<p>タスクがありません。新しいタスクを追加してください。</p>';
        return;
    }

    todoList.innerHTML = todos.map(todo => `
        <div class="todo-item ${todo.done ? 'completed' : ''}">
            <div class="todo-title">${todo.title}</div>
            <div class="todo-actions">
                <button class="toggle-btn" onclick="toggleTodo(${todo.id}, ${todo.done})">
                    ${todo.done ? '未完了に戻す' : '完了'}
                </button>
                <button class="delete-btn" onclick="deleteTodo(${todo.id})">削除</button>
            </div>
        </div>
    `).join('');
}

// TODOの完了/未完了切り替え
async function toggleTodo(id, currentDone) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/todos/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ done: currentDone ? 0 : 1 })
        });

        if (response.ok) {
            loadTodos();
            showMessage('タスクが更新されました！', 'success');
        } else {
            showMessage('更新に失敗しました', 'error');
        }
    } catch (error) {
        showMessage('接続エラーが発生しました', 'error');
    }
}

// TODOの削除
async function deleteTodo(id) {
    if (!confirm('このタスクを削除しますか？')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/todos/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadTodos();
            showMessage('タスクが削除されました！', 'success');
        } else {
            showMessage('削除に失敗しました', 'error');
        }
    } catch (error) {
        showMessage('接続エラーが発生しました', 'error');
    }
}

// メッセージ表示
function showMessage(message, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.innerHTML = `<div class="message ${type}">${message}</div>`;
    setTimeout(() => {
        messageDiv.innerHTML = '';
    }, 3000);
}
