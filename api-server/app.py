from flask import Flask, request, jsonify
import pymysql
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 日本語をエスケープしない

# データベース接続設定（sharedの内容を統合）
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': 3306,
    'charset': 'utf8mb4'
}

def get_db_connection():
    """データベース接続を取得する"""
    return pymysql.connect(**DB_CONFIG)

def execute_query(query, params=None, fetch=False):
    """クエリを実行する"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.lastrowid if cursor.lastrowid else None
        
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'TODO API Server'}), 200

@app.route('/api/todos', methods=['GET'])
def get_todos():
    try:
        todos = execute_query("SELECT * FROM todos ORDER BY created_at DESC", fetch=True)
        return jsonify(todos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos', methods=['POST'])
def create_todo():
    try:
        data = request.get_json()
        title = data.get('title')
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        todo_id = execute_query("INSERT INTO todos (title, done) VALUES (%s, %s)", (title, 0))
        
        return jsonify({'id': todo_id, 'title': title, 'done': 0}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    try:
        data = request.get_json()
        done = data.get('done')
        
        execute_query("UPDATE todos SET done = %s WHERE id = %s", (done, todo_id))
        
        return jsonify({'message': 'Todo updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        execute_query("DELETE FROM todos WHERE id = %s", (todo_id,))
        
        return jsonify({'message': 'Todo deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
