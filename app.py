from flask import Flask, request, jsonify, render_template_string
import pymysql
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 日本語をエスケープしない

# データベース接続設定
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': 3306,
    'charset': 'utf8mb4'
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

# HTMLテンプレート
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TODO管理アプリ - OCI コンテナ環境</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .todo-form { background: #ecf0f1; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .todo-form input[type="text"] { width: 70%; padding: 10px; border: 1px solid #bdc3c7; border-radius: 3px; }
        .todo-form button { padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 3px; cursor: pointer; margin-left: 10px; }
        .todo-form button:hover { background: #2980b9; }
        .todo-item { background: white; border: 1px solid #bdc3c7; padding: 15px; margin: 10px 0; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }
        .todo-item.completed { background: #d5f4e6; border-color: #27ae60; }
        .todo-item.completed .todo-title { text-decoration: line-through; color: #7f8c8d; }
        .todo-title { flex-grow: 1; margin-right: 15px; }
        .todo-actions button { padding: 5px 10px; margin: 0 5px; border: none; border-radius: 3px; cursor: pointer; }
        .toggle-btn { background: #f39c12; color: white; }
        .toggle-btn:hover { background: #e67e22; }
        .delete-btn { background: #e74c3c; color: white; }
        .delete-btn:hover { background: #c0392b; }
        .message { padding: 10px; margin: 10px 0; border-radius: 3px; }
        .success { background: #d5f4e6; color: #27ae60; border: 1px solid #27ae60; }
        .error { background: #fadbd8; color: #e74c3c; border: 1px solid #e74c3c; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📝 TODO管理アプリ</h1>
        <p>OCI 上のコンテナ環境（OKE 等）+ MySQL HeatWave で構築</p>
    </div>

    <div class="todo-form">
        <form id="todoForm">
            <input type="text" id="todoTitle" placeholder="新しいタスクを入力してください..." required>
            <button type="submit">追加</button>
        </form>
    </div>

    <div id="message"></div>

    <div id="todos">
        <h2>タスク一覧</h2>
        <div id="todoList">
            <!-- TODOリストがここに動的に挿入されます -->
        </div>
    </div>

    <script>
        // ページ読み込み時にTODOリストを取得
        loadTodos();

        // フォーム送信処理
        document.getElementById('todoForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const title = document.getElementById('todoTitle').value.trim();
            if (!title) return;

            try {
                const response = await fetch('/todos', {
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
                const response = await fetch('/todos');
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
                const response = await fetch(`/todos/${id}`, {
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
                const response = await fetch(`/todos/${id}`, {
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
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'TODO Management App'}), 200

@app.route('/todos', methods=['GET'])
def get_todos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM todos ORDER BY created_at DESC")
        todos = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(todos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/todos', methods=['POST'])
def create_todo():
    try:
        data = request.get_json()
        title = data.get('title')
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO todos (title, done) VALUES (%s, %s)", (title, 0))
        conn.commit()
        todo_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({'id': todo_id, 'title': title, 'done': 0}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    try:
        data = request.get_json()
        done = data.get('done')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE todos SET done = %s WHERE id = %s", (done, todo_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Todo updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Todo deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)


