# 使用官方Python镜像
FROM python:3.11-slim

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 设置工作目录
WORKDIR /app

# 更新包管理器并安装基本工具
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirments.txt .

# 安装Python依赖
RUN pip install --no-cache-dir --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir -r requirments.txt -i https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install gunicorn -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目文件
COPY . .

# 创建必要的目录和初始化数据库
RUN mkdir -p uploads && \
    chmod 755 uploads && \
    python -c "from database import init_db; init_db(); print('数据库初始化完成')" && \
    ls -la *.db || echo "数据库文件列表查看失败"

# 创建非root用户（安全考虑）
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 5000

# 健康检查 - 简化版本
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "main:app"]