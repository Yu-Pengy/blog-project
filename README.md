# Blog Application Deployment

这是一个武大大一学生的第三学期项目，前端基于vue框架，后端基于flask框架，数据库采用sqlite，虽然代码基本都是ai写的，但是仍然是一个全栈 + DevOps的成功尝试

## 镜像缓存机制

+ 应用已经构造并上传到GHCR
+ 所有依赖都打包在镜像里
+ 不需要重新编译、安装依赖

## 系统要求

- Windows 10/11
- Docker Desktop 已安装并运行
- 网络连接

## 想体验这个项目..  快速部署

1. **下载部署包**
	- 下载blog-deployment文件夹

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

- **前端**：Vue.js 3 + Vite 
- **后端**：Python Flask
- **数据库**：SQLite
- **Web服务器**：Nginx
- **容器化**：Docker + Docker Compose
- **CI/CD**：GitHub Actions
- **镜像仓库**：GitHub Container Registry (GHCR)

## 支持

如有问题，请联系：[123456]


## 开发者CI/CD流程

### **自动化部署流程**
1. **代码提交**：修改代码后提交到 `test` 分支
2. **自动触发**：GitHub Actions 自动检测到推送并触发构建
3. **镜像构建**：自动构建 Docker 镜像并推送到 GitHub Container Registry (GHCR)
4. **本地更新**：通过以下命令更新到最新版本

### **更新步骤**
```bash
# 拉取最新镜像
docker-compose pull

# 重启服务应用更新
docker-compose down 
docker-compose up -d

# 或使用强制重建（确保使用新镜像）
docker-compose up -d --force-recreate
```

### **构建时间**
- 平均构建时间：2-3分钟
- 构建状态查看：[GitHub Actions](https://github.com/yu-pengy/project/actions)
+ 修改代码后提交到test分支，自动触发CI流程
+ 自动构建docker镜像并部署到GHCR上
+ 通过docker-compose pull指令拉取最新镜像
+ docker-compose up -d启动即可看到最新更改后的镜像
