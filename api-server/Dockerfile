FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# 共通ライブラリをコピー
COPY ../shared/ /app/shared/

# 依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションをコピー
COPY app.py .

# ポート8000を公開
EXPOSE 8000

# アプリケーションを起動
CMD ["python", "app.py"]
