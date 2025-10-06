import os

class Config:
    """アプリケーション設定"""
    
    # データベース設定
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'todos')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # API設定
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 8000))
    API_DEBUG = os.getenv('API_DEBUG', 'False').lower() == 'true'
    
    # Web UI設定
    WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
    WEB_PORT = int(os.getenv('WEB_PORT', 3000))
    
    # JSON設定
    JSON_AS_ASCII = False  # 日本語をエスケープしない
