# --- 阶段 1: 构建阶段 (Build Stage) ---
# 使用官方Node.js镜像
FROM node:16 AS build-stage

# 在容器内创建一个工作目录
WORKDIR /app

# 仅复制 package.json 和 package-lock.json (如果存在)
# 这一步是为了充分利用 Docker 的缓存机制。只要这两个文件没变，就不会重新安装依赖。
COPY package*.json ./

# 设置 npm 使用国内的淘宝镜像源，可以极大加速依赖下载速度
RUN npm config set registry https://registry.npmmirror.com/

# 安装所有依赖项。
# 注意：这里必须是 'npm install'，而不是 'npm ci --only=production'。
# 因为像 vite 这样的构建工具是开发依赖 (devDependencies)，必须被安装才能执行构建。
RUN npm install

# 降级到更稳定的版本组合，解决 crypto 兼容性问题
# 这个版本组合在 Docker 环境中非常稳定
RUN npm install vite@5.4.10 @vitejs/plugin-vue@5.1.4 --save-dev

# 复制你项目中的所有源代码到容器的工作目录
COPY . .

# 设置环境变量解决 crypto 相关问题，并执行构建
# NODE_OPTIONS 增加内存限制，GENERATE_SOURCEMAP=false 减少构建时间
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV GENERATE_SOURCEMAP=false
ENV NODE_ENV=production

# 执行 package.json 中定义的 "build" 脚本，也就是 'vite build'
# 这会把你的 Vue 应用打包成静态文件，并输出到 /app/dist 目录
RUN npm run build

# --- 阶段 2: 生产阶段 (Production Stage) ---
# 使用官方Nginx镜像
FROM nginx:stable-alpine

# 将上一个“构建阶段”生成的静态文件（在 /app/dist）
# 复制到 Nginx 用于托管网站的默认目录 (/usr/share/nginx/html)
# 这是多阶段构建最核心的步骤，确保了最终镜像只包含运行所需的文件，体积很小。
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制自定义的 Nginx 配置文件。
# 这个文件非常重要，它能解决 Vue Router 的 history 模式导致的404问题，并能配置API代理。
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 告诉 Docker，这个容器在运行时会监听 80 端口
EXPOSE 80

# Nginx 镜像已经包含了启动自身的默认命令，所以我们不需要再写 CMD 或 ENTRYPOINT