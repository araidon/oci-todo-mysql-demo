# Container Instancesでの構築手順 - コマンド集

「第4章 コンテナアーキテクチャパターン」のContainer Instancesセクションで使用するコマンドをまとめたファイルです。
各セクションに対応するコマンドを順番に実行してください。

## 使用方法

1. このファイルを適切なサーバーにコピー
2. 必要な値を置き換える（`<xxx>`の部分）
3. 各セクションごとに実行

---

## セクション: 管理用Computeインスタンスの準備（オプション）

### 管理サーバへのSSH接続

書籍: `=== Container Instancesでの構築手順 > === 管理用Computeインスタンスの準備（オプション） > ==== ■2. 必要なツールのインストール`

```bash
ssh opc@<管理用ComputeのパブリックIP>
```

### 必要ツールのインストール

書籍: `=== Container Instancesでの構築手順 > === 管理用Computeインスタンスの準備（オプション） > ==== ■2. 必要なツールのインストール`

```bash
# システム更新
sudo dnf update -y

# MySQLクライアントのインストール
sudo dnf install mysql -y

# Dockerのインストール
sudo dnf install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker opc

# バージョン確認
mysql -v
docker -v
```

**注意**: Dockerグループへの追加を反映させるため、一度SSHセッションから抜けて再ログインしてください。

---

## セクション: アプリケーションの準備

### GitHubリポジトリのクローン

書籍: `=== Container Instancesでの構築手順 > === アプリケーションの準備 > ==== ■1. アプリケーションコードの準備 > ===== ・1. GitHubリポジトリのクローン`

```bash
# ホームディレクトリに移動
cd ~

# GitHubからリポジトリをクローン
git clone https://github.com/araidon/oci-todo-mysql-demo.git

# クローンしたディレクトリに移動
cd oci-todo-mysql-demo
```

### Dockerfileの内容確認

書籍: `=== Container Instancesでの構築手順 > === アプリケーションの準備 > ==== ■1. アプリケーションコードの準備 > ===== ・3. Dockerfileの確認`

```bash
cat Dockerfile
```

### Dockerイメージのビルド

書籍: `=== Container Instancesでの構築手順 > === アプリケーションの準備 > ==== ■2. コンテナイメージのビルド > ===== ・1. Dockerイメージのビルド`

```bash
# リポジトリディレクトリに移動（すでにいる場合は不要）
cd ~/oci-todo-mysql-demo

# Dockerイメージをビルド
docker image build -t todo-api:latest .
```

### OCIRへのログイン

書籍: `=== Container Instancesでの構築手順 > === アプリケーションの準備 > ==== ■3. Oracle Cloud Infrastructure Registry（OCIR）へのプッシュ > ===== ・2. OCIRへのログイン`

```bash
# <tenancy-namespace>: OCIテナンシー名（コンソール右上のプロファイルアイコンから確認可能）
# <username>: OCIユーザー名（oracleidentitycloudservice/<ユーザー名>の形式）
# <auth-token>: 認証トークンの生成で作成した認証トークン
# <region-key>: リージョンキー（例：nrt for 東京リージョン）

docker login <region-key>.ocir.io -u <tenancy-namespace>/<username>
# パスワード入力プロンプトで認証トークンを入力
```

### イメージのタグ付けとプッシュ

書籍: `=== Container Instancesでの構築手順 > === アプリケーションの準備 > ==== ■3. Oracle Cloud Infrastructure Registry（OCIR）へのプッシュ > ===== ・3. イメージのタグ付けとプッシュ`

```bash
# イメージにタグを付ける
docker image tag todo-api:latest \
  <region-key>.ocir.io/<tenancy-namespace>/todo-api:latest

# OCIRへプッシュ
docker push <region-key>.ocir.io/<tenancy-namespace>/todo-api:latest
```

---

## セクション: MySQL HeatWaveの構築

### MySQLへの接続

書籍: `=== Container Instancesでの構築手順 > === MySQL HeatWaveの構築 > ==== ■2. データベースとテーブルの作成 > ===== ・1. MySQLへの接続`

```bash
# MySQLへ接続
# <mysql-private-ip>: MySQL HeatWaveのプライベートIPアドレス
mysql -h <mysql-private-ip> -u admin -p
# パスワード入力プロンプトで、MySQL作成時に設定したパスワードを入力
```

### データベースとテーブルの作成

書籍: `=== Container Instancesでの構築手順 > === MySQL HeatWaveの構築 > ==== ■2. データベースとテーブルの作成 > ===== ・2. データベースの作成`

```sql
-- データベースの作成
CREATE DATABASE tododb;

-- データベースの選択
USE tododb;

-- テーブルの作成
CREATE TABLE todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    done TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 動作確認用のデータ挿入（オプション）
INSERT INTO todos (title, done) VALUES 
('OCIを学ぶ', 0),
('Container Instancesを試す', 0),
('TODO管理アプリを完成させる', 0);

-- データの確認
SELECT * FROM todos;

-- MySQLから切断
EXIT;
```

---

## セクション: Container Instanceの構築

### APIの動作確認

書籍: `=== Container Instancesでの構築手順 > === Container Instanceの構築 > ==== ■2. 動作確認 > ===== ・2. APIの動作確認`

Container Instanceの作成が完了し、プライベートIPアドレスを確認した後、以下のコマンドで動作確認します。

```bash
# タスク一覧の取得
# <container-private-ip>: Container InstanceのプライベートIPアドレス
curl -s http://<container-private-ip>:8000/todos

# 期待される結果: 上記で挿入したデータが返される
# [{"id":1,"title":"OCIを学ぶ","completed":false,...}]

# 新規タスクの作成
curl -X POST http://<container-private-ip>:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Network Load Balancerを設定する","completed":false}'

# 再度一覧を取得して確認
curl -s http://<container-private-ip>:8000/todos
```

---

## セクション: Network Load Balancer（NLB）の構築

### NLB経由でのAPI動作確認

書籍: `=== Container Instancesでの構築手順 > === Network Load Balancer（NLB）の構築 > ==== ■2. NLBのパブリックIPアドレスの確認` および `==== ■3. 動作確認`

NLBの作成が完了し、パブリックIPアドレスを確認した後、以下のコマンドで動作確認します。

```bash
# ヘルスチェックの確認
# <nlb-public-ip>: NLBのパブリックIPアドレス
curl -s http://<nlb-public-ip>/health

# タスク一覧の取得
curl -s http://<nlb-public-ip>/todos

# 新規タスクの作成
curl -X POST http://<nlb-public-ip>/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"NLB経由でアクセス成功"}'

# 再度一覧を取得
curl -s http://<nlb-public-ip>/todos
```

---

## セクション: 動作確認

### Webブラウザからの確認

書籍: `=== Container Instancesでの構築手順 > === 動作確認 > ==== ■1. Webブラウザからの確認 > ===== ・1. HTMLページへのアクセス`

Webブラウザから以下のURLにアクセスします。

```
http://<nlb-public-ip>/
```

### API直接アクセス

書籍: `=== Container Instancesでの構築手順 > === 動作確認 > ==== ■1. Webブラウザからの確認 > ===== ・2. API直接アクセス`

ブラウザまたはcurlコマンドで以下のURLにアクセスします。

```
http://<nlb-public-ip>/todos
```

