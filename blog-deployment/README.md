# Blog Application Deployment

## 镜像缓存机制

+ 应用已经构造并上传到GHCR
+ 所有依赖都打包在镜像里
+ 不需要重新编译、安装依赖

## 系统要求

- Windows 10/11
- Docker Desktop 已安装并运行
- 网络连接

## 快速部署

1. **下载部署包**
   - 下载所有文件到同一文件夹

2. **运行部署脚本**
   - 双击 `deploy.bat`
   - 等待下载和启动完成

3. **访问应用**
   - 前端：http://localhost
   - 后端：http://localhost:5000

## 常用命令

```bash
# 启动应用
docker-compose up -d

# 停止应用
docker-compose down

# 查看日志
docker-compose logs -f

# 查看运行状态
docker-compose ps
```

## 故障排除

### 问题：端口被占用
```bash
# 检查端口占用
netstat -ano | findstr :80
netstat -ano | findstr :5000
```

### 问题：Docker未运行
- 启动 Docker Desktop
- 确保 Docker 状态为运行中

### 问题：下载失败
- 检查网络连接
- 重新运行 `deploy.bat`

## 清理应用

双击 `cleanup.bat` 完全移除应用

## 技术信息

- 前端：React + Vite
- 后端：Python Flask
- 代理：Nginx
- 容器化：Docker

## 支持

如有问题，请联系：[111]