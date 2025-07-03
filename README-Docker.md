# 博客项目 Docker 部署指南

## 快速部署

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd project
```

### 2. 一键部署
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 访问应用
- **前端**: http://localhost (或 http://localhost:8080)
- **后端API**: http://localhost:5000

## 管理命令

### 启动服务
```bash
# 后台运行
docker-compose up -d

# 前台运行（查看日志）
docker-compose up
```

### 停止服务
```bash
# 停止所有服务
docker-compose down

# 停止并删除所有数据卷（慎用）
docker-compose down -v
```

### 重新构建
```bash
# 重新构建所有镜像
docker-compose build

# 重新构建并启动
docker-compose up -d --build
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f blog-backend
docker-compose logs -f blog-frontend
```

## 数据持久化

- **上传文件**: 存储在 `blog-uploads` 命名卷中
- **数据库**: 存储在 `blog-database` 命名卷中

## 端口说明

- **80**: 前端主端口
- **8080**: 前端备用端口
- **5000**: 后端API端口

## 故障排除

### 检查服务状态
```bash
docker-compose ps
```

### 查看详细日志
```bash
docker-compose logs -f
```

### 重启服务
```bash
docker-compose restart
```

### 进入容器调试
```bash
# 进入后端容器
docker-compose exec blog-backend sh

# 进入前端容器
docker-compose exec blog-frontend sh
```

## 系统要求

- Docker >= 20.10
- Docker Compose >= 2.0
- 可用内存 >= 2GB
- 可用磁盘空间 >= 1GB
