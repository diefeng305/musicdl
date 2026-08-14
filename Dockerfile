FROM python:3.11-slim

# 安装运行环境需要的基础软件（FFmpeg, Node.js 等）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    nodejs \
    git \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有源代码
COPY . /app

# 安装依赖及 musicdl 本身
RUN pip install --no-cache-dir -e .

# 创建默认挂载下载目录
WORKDIR /downloads

# 进入容器默认进入命令行模式
ENTRYPOINT ["musicdl"]
