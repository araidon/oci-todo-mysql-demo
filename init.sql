CREATE TABLE IF NOT EXISTS todos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  done TINYINT(1) NOT NULL DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4;

-- サンプルデータの挿入
INSERT INTO todos (title, done) VALUES 
('サンプルタスク1', 0),
('サンプルタスク2', 1),
('サンプルタスク3', 0);
