# oci-todo-mysql-demo

OCI 上の Kubernetes(OKE) や任意のコンテナ環境で動作する、マイクロサービス構成の TODO アプリ。

## 機能
- タスクの追加 / 完了切替 / 削除
- レスポンシブなシングルページ UI（Nginx + 静的ファイル）
- REST API サーバー（Flask）
- ヘルスチェック `/health`

## 構成
```
container-api/
├── web-ui/              # Web UI専用コンテナ
│   ├── Dockerfile
│   ├── nginx.conf
│   └── static/
│       ├── index.html
│       ├── style.css
│       └── script.js
├── api-server/          # API専用コンテナ  
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── shared/              # 共通ライブラリ
│   ├── database.py
│   └── config.py
├── docker-compose.yml   # 統合構成
└── init.sql            # データベース初期化
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

## ローカル実行（Docker Compose）
```bash
# 全サービスを起動
docker-compose up --build

# バックグラウンドで起動
docker-compose up -d --build
```

- Web UI: `http://localhost:3000`
- API Server: `http://localhost:8000`
- ヘルスチェック: `http://localhost:8000/health`
- MySQL: `localhost:3306`

## 個別実行（Docker）
```bash
# API Server のみ
cd api-server
docker build -t todo-api .
docker run --rm -p 8000:8000 \
  -e DB_HOST=your-mysql-host \
  -e DB_USER=your-user \
  -e DB_PASSWORD=your-password \
  -e DB_NAME=your-db \
  todo-api

# Web UI のみ
cd web-ui
docker build -t todo-web .
docker run --rm -p 3000:3000 todo-web
```

## GitHub への公開手順（例）
```bash
git init

git add .

git commit -m "Add OKE-ready TODO app"

git branch -M main

git remote add origin git@github.com:<your-account>/oci-todo-mysql-demo.git

git push -u origin main
```
