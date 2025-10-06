FROM nginx:alpine

# 静的ファイルをコピー
COPY static/ /usr/share/nginx/html/

# Nginx設定ファイルをコピー
COPY nginx.conf /etc/nginx/conf.d/default.conf

# ポート3000を公開
EXPOSE 3000

# Nginxを起動
CMD ["nginx", "-g", "daemon off;"]
