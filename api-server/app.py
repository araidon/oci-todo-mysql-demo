from flask import Flask, request, jsonify
import sys
import os

# 共通ライブラリのパスを追加
sys.path.append('/app/shared')

from database import execute_query
from config import Config

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = Config.JSON_AS_ASCII

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'service': 'TODO API Server'}), 200

@app.route('/todos', methods=['GET'])
def get_todos():
    try:
        todos = execute_query("SELECT * FROM todos ORDER BY created_at DESC", fetch=True)
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
        
        todo_id = execute_query("INSERT INTO todos (title, done) VALUES (%s, %s)", (title, 0))
        
        return jsonify({'id': todo_id, 'title': title, 'done': 0}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    try:
        data = request.get_json()
        done = data.get('done')
        
        execute_query("UPDATE todos SET done = %s WHERE id = %s", (done, todo_id))
        
        return jsonify({'message': 'Todo updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        execute_query("DELETE FROM todos WHERE id = %s", (todo_id,))
        
        return jsonify({'message': 'Todo deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host=Config.API_HOST, port=Config.API_PORT, debug=Config.API_DEBUG)
