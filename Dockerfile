FROM python:3.11-slim

# 安装运行基础依赖（FFmpeg, Node.js 等全平台解析支持）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    nodejs \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制项目所有文件
COPY . /app

# 安装 musicdl 及 WebUI 依赖
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir -r requirements.txt

# 默认下载保存路径
RUN mkdir -p /downloads
ENV MUSICDL_WORK_DIR=/downloads

# 开放 Web 端口
EXPOSE 5000

# 启动 WebUI 服务
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:app"]
