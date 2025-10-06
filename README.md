# oci-todo-mysql-demo

OCI Container Instances で動作する、独立したコンテナ構成の TODO アプリ。

## 機能
- タスクの追加 / 完了切替 / 削除
- レスポンシブなシングルページ UI（Nginx + 静的ファイル）
- REST API サーバー（Flask）
- ヘルスチェック `/health`
- 外部MySQLデータベース対応

## 構成
```
container-api/
├── web-ui/              # Web UI専用コンテナ（独立動作）
│   ├── Dockerfile
│   ├── nginx.conf
│   └── static/
│       ├── index.html
│       ├── style.css
│       └── script.js
└── api-server/          # API専用コンテナ（独立動作）
    ├── Dockerfile
    ├── app.py
    └── requirements.txt
```

## Container Instances での実行

### 1. Web UI Container Instance
```bash
# イメージをビルド
cd web-ui
docker build -t todo-web-ui .

# ローカルでテスト
docker run --rm -p 3000:3000 \
  -e API_SERVER_HOST=localhost \
  todo-web-ui
```

### 2. API Server Container Instance
```bash
# イメージをビルド
cd api-server
docker build -t todo-api-server .

# ローカルでテスト
docker run --rm -p 8000:8000 \
  -e DB_HOST=your-mysql-host \
  -e DB_USER=your-user \
  -e DB_PASSWORD=your-password \
  -e DB_NAME=todos \
  todo-api-server
```

## 事前準備（DB）
MySQL に `todos` テーブルを作成してください。

```sql
CREATE TABLE todos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  done TINYINT(1) NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4;
```

## 環境変数
- `DB_HOST`: MySQL ホスト名
- `DB_USER`: MySQL ユーザー
- `DB_PASSWORD`: パスワード
- `DB_NAME`: データベース名

## ローカル実行（独立コンテナ）

### 1. API Server を起動
```bash
cd api-server
docker build -t todo-api-server .
docker run --rm -p 8000:8000 \
  -e DB_HOST=your-mysql-host \
  -e DB_USER=your-user \
  -e DB_PASSWORD=your-password \
  -e DB_NAME=todos \
  todo-api-server
```

### 2. Web UI を起動
```bash
cd web-ui
docker build -t todo-web-ui .
docker run --rm -p 3000:3000 \
  -e API_SERVER_HOST=localhost \
  todo-web-ui
```

### アクセス
- Web UI: `http://localhost:3000`
- API Server: `http://localhost:8000`
- ヘルスチェック: `http://localhost:8000/health`

## OCI Container Instances での実行

### 1. イメージをOCIRにプッシュ
```bash
# API Server
cd api-server
docker build -t icn.ocir.io/your-namespace/todo-api-server:latest .
docker push icn.ocir.io/your-namespace/todo-api-server:latest

# Web UI
cd web-ui
docker build -t icn.ocir.io/your-namespace/todo-web-ui:latest .
docker push icn.ocir.io/your-namespace/todo-web-ui:latest
```

### 2. Container Instances を作成
- **API Server Container Instance**: ポート8000を公開
- **Web UI Container Instance**: ポート3000を公開、環境変数`API_SERVER_HOST`にAPI ServerのプライベートIPを設定

## GitHub への公開手順（例）
```bash
git init

git add .

git commit -m "Add OKE-ready TODO app"

git branch -M main

git remote add origin git@github.com:<your-account>/oci-todo-mysql-demo.git

git push -u origin main
```
