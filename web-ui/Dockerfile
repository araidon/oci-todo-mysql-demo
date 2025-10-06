FROM nginx:alpine

# 静的ファイルをコピー
COPY static/ /usr/share/nginx/html/

# Nginx設定ファイルをテンプレートとしてコピー
COPY nginx.conf /etc/nginx/templates/default.conf.template

# ポート3000を公開
EXPOSE 3000

# 環境変数をNginxに渡して起動
CMD ["sh", "-c", "envsubst '${API_SERVER_HOST}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
