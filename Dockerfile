# 使用轻量级 Python 镜像作为基础镜像
FROM python:3.11-slim

# 设置环境变量，防止生成 pyc 文件和缓冲输出
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# 设置工作目录
WORKDIR /app

# 安装系统依赖（如 ffmpeg 和 nodejs 等底层解密/转码依赖）
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ffmpeg \
    nodejs \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 复制当前仓库内容到容器内
COPY . /app

# 安装 Python 项目依赖及本项目
# 如果仓库内有 requirements.txt 优先安装，随后执行安装本包
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi \
    && pip install --no-cache-dir .

# 创建默认的音乐下载目录
RUN mkdir -p /downloads

# 设置容器启动时的默认下载保存目录环境变量
ENV MUSICDL_DOWNLOAD_DIR=/downloads

# 设置容器入口点
ENTRYPOINT ["musicdl"]
CMD ["--help"]
