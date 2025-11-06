# OKE（OCI Kubernetes Engine）での構築手順 - コマンド集

本書「05-container-arai.re」のOKEセクションで使用するコマンドをまとめたファイルです。
各セクションに対応するコマンドを順番に実行してください。

## 使用方法

1. このファイルを適切なサーバーにコピー
2. 必要な値を置き換える（`<xxx>`の部分）
3. 各セクションごとに実行

---

## セクション: 管理用Computeインスタンスの準備

### 管理サーバへのSSH接続

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === 管理用Computeインスタンスの準備 > ==== ■2. 必要なツールのインストール`

```bash
ssh opc@<管理用ComputeのパブリックIP>
```

### 必要ツールのインストール

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === 管理用Computeインスタンスの準備 > ==== ■2. 必要なツールのインストール`

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

# OCI CLIのインストール
sudo dnf install python39-oci-cli -y

# kubectlのインストール
curl -LO "https://dl.k8s.io/release/$(curl -L -s \
  https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# バージョン確認
mysql -v
docker -v
oci --version
kubectl version --client
```

**注意**: Dockerグループへの追加を反映させるため、一度SSHセッションから抜けて再ログインしてください。

---

## セクション: MySQL HeatWaveの構築

### MySQLクライアントで接続

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === MySQL HeatWaveの構築 > ==== ■3. MySQLへの接続確認`

内部FQDNを設定した後、以下のコマンドで接続します。

```bash
mysql -h demo-mysql.dbsubnetprivate.demookecluster.oraclevcn.com \
  -u admin -p
```

パスワードを入力すると、MySQL HeatWaveに接続できます。

### スキーマとテーブルの作成

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === MySQL HeatWaveの構築 > ==== ■4. スキーマとテーブルの作成`

```sql
-- データベースの作成
CREATE DATABASE sampledb;

-- アプリ用DBユーザーを作成
CREATE USER 'appuser'@'%' IDENTIFIED BY 'your_secure_password_here';

-- 権限付与
GRANT ALL PRIVILEGES ON sampledb.* TO 'appuser'@'%';

-- 権限の反映
FLUSH PRIVILEGES;

-- データベースの選択
USE sampledb;

-- テーブルの作成
CREATE TABLE todos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    done TINYINT(1) NOT NULL DEFAULT 0,
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

## セクション: アプリケーションの準備

### GitHubリポジトリのクローン

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === アプリケーションの準備 > ==== ■1. アプリケーションコードの準備 > ===== ・1. GitHubリポジトリのクローン`

```bash
# ホームディレクトリに移動
cd ~

# GitHubからリポジトリをクローン
git clone https://github.com/araidon/oci-todo-mysql-demo.git

# クローンしたディレクトリに移動
cd oci-todo-mysql-demo
```

### OCIRへのDockerログイン

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === アプリケーションの準備 > ==== ■2. OCIRへのログイン > ===== ・1. 認証トークンの作成` および `===== ・2. OCIRへのログイン`

```bash
docker login <region-key>.ocir.io
Username: <tenancy-namespace>/<oci-username>
Password: <auth-token>
```

`<region-key>`は、リージョンに応じて以下の値を使用します：

- 東京リージョン: `nrt`
- 大阪リージョン: `kix`
- その他のリージョン: OCIドキュメントを参照

### コンテナイメージのビルドとプッシュ

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === アプリケーションの準備 > ==== ■3. コンテナイメージのビルドとプッシュ`

```bash
# イメージのビルド
docker image build -t <region-key>.ocir.io/<tenancy-namespace>/container-api:latest .

# イメージのプッシュ
docker image push <region-key>.ocir.io/<tenancy-namespace>/container-api:latest
```

---

## セクション: Kubernetesリソースのデプロイ

### kubeconfigの設定

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === Kubernetesリソースのデプロイ > ==== ■1. kubeconfigの設定`

OCIコンソールで、作成したOKEクラスタを選択し、「アクション」ボタンから「クラスタへのアクセス」を選択し、「ローカル・アクセス」タブを表示します。

管理用Computeインスタンスで、表示されたコマンドを順番に実行します。

**注意**: 
- コマンド3を実行すると、OCI CLIの初期設定が起動します。パブリック・エンドポイントを選択してください。
- コマンド成功後、もう一度同じコマンドを実行する必要があります。
- コマンド4は、コピーしたコマンドにバグがある場合があるため、`-`を`=`に書き換えて実行してください。

### 接続確認

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === Kubernetesリソースのデプロイ > ==== ■1. kubeconfigの設定`

```bash
kubectl get nodes

# 期待される結果例:
# NAME          STATUS   ROLES   AGE   VERSION
# 10.0.10.227   Ready    node    31h   v1.34.1
```

ノードが`Ready`状態であれば、kubectlの設定は完了です。

### OCIRアクセス用のSecretの作成

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === Kubernetesリソースのデプロイ > ==== ■2. OCIRアクセス用のSecretの作成`

```bash
kubectl create secret docker-registry ocir-secret \
  --docker-server=<region-key>.ocir.io \
  --docker-username='<tenancy-namespace>/<oci-username>' \
  --docker-password='<auth-token>'
```

### Secret/ConfigMapの作成

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === Kubernetesリソースのデプロイ > ==== ■3. アプリケーション用のSecret/ConfigMapの作成`

ファイル名: `secret-configmap.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-db-secret
  namespace: default
type: Opaque
stringData:
  DB_PASSWORD: "<appuser_password>"  # MySQLで作成したappuserのパスワード
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
data:
  DB_HOST: "demo-mysql.dbsubnetprivate.demookecluster.oraclevcn.com"
  DB_USER: "appuser"
  DB_NAME: "sampledb"
```

```bash
# Secret/ConfigMapの適用
kubectl apply -f secret-configmap.yaml
```

### Deploymentの作成

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === Kubernetesリソースのデプロイ > ==== ■4. Deploymentの作成`

ファイル名: `deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: container-api
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: container-api
  template:
    metadata:
      labels:
        app: container-api
    spec:
      imagePullSecrets:
        - name: ocir-secret
      containers:
        - name: api
          image: <region-key>.ocir.io/<tenancy-namespace>/container-api:latest
          imagePullPolicy: Always
          ports:
            - containerPort: 8000
          env:
            - name: DB_HOST
              valueFrom:
                configMapKeyRef:
                  name: app-config
                  key: DB_HOST
            - name: DB_USER
              valueFrom:
                configMapKeyRef:
                  name: app-config
                  key: DB_USER
            - name: DB_NAME
              valueFrom:
                configMapKeyRef:
                  name: app-config
                  key: DB_NAME
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: app-db-secret
                  key: DB_PASSWORD
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 20
```

```bash
# Deploymentの適用
kubectl apply -f deployment.yaml
```

### ServiceのNodePort公開

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === Kubernetesリソースのデプロイ > ==== ■5. ServiceのNodePort公開`

ファイル名: `service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: container-api-svc
  namespace: default
spec:
  type: NodePort
  ports:
    - name: http
      port: 80
      targetPort: 8000
      protocol: TCP
      nodePort: 30080
  selector:
    app: container-api
```

```bash
# Serviceの適用
kubectl apply -f service.yaml
```

### デプロイ状態の確認

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === Kubernetesリソースのデプロイ > ==== ■6. デプロイ状態の確認`

```bash
# Podの状態確認
kubectl get pods

# Deploymentの状態確認
kubectl get deployment

# Serviceの状態確認
kubectl get service

# 詳細情報確認
kubectl get pods -o wide
kubectl describe service container-api-svc

# Podのログ確認
kubectl logs -l app=container-api
```

### NodePort経由での動作確認

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === Kubernetesリソースのデプロイ > ==== ■6. デプロイ状態の確認`

```bash
# ノードのプライベートIPを確認
kubectl get nodes -o wide

# 管理サーバからNodePort経由でアクセス
# <ノードのプライベートIP>: kubectl get nodes -o wideで確認したIPアドレス
curl http://<ノードのプライベートIP>:30080/health
curl http://<ノードのプライベートIP>:30080/todos
```

---

## セクション: Network Load Balancer（NLB）の構築

### API動作確認

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === 動作確認 > ==== ■2. API直接アクセス`

NLBの作成が完了し、パブリックIPアドレスを確認した後、以下のコマンドで動作確認します。

```bash
# タスク一覧の取得
# <NLBのパブリックIP>: NLBのパブリックIPアドレス
curl -s http://<NLBのパブリックIP>/todos

# タスクの追加
curl -X POST http://<NLBのパブリックIP>/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "OKE quick test"}'

# 追加後のタスク一覧確認
curl -s http://<NLBのパブリックIP>/todos
```

---

## セクション: 動作確認

### Webブラウザからの確認

書籍: `== OKE（OCI Kubernetes Engine）での構築手順 > === 動作確認 > ==== ■1. Webブラウザからの確認`

NLBのパブリックIPアドレスをブラウザで開きます。

```
http://<NLBのパブリックIP>
```

TODO管理アプリのWebインターフェースが表示され、以下の操作ができることを確認します：
- タスクの追加（入力欄にタスクを入力して「追加」ボタンをクリック）
- タスク一覧の表示（データベースに登録されているタスクが表示される）
- タスクの完了/未完了切り替え（「完了」ボタンをクリック）
- タスクの削除（「削除」ボタンをクリック）

