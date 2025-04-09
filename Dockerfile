FROM anasty17/mltb:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

# 安装 Alist - 优先使用 curl (确认基础镜像有curl)
RUN mkdir -p /usr/src/alist
WORKDIR /usr/src/alist

# 使用 curl 下载 Alist
RUN curl -L -o alist-linux-musl-amd64.tar.gz https://github.com/alist-org/alist/releases/download/v3.44.0/alist-linux-musl-amd64.tar.gz && \
    tar -xzvf alist-linux-musl-amd64.tar.gz && \
    chmod +x alist && \
    rm alist-linux-musl-amd64.tar.gz

# 返回主工作目录
WORKDIR /usr/src/app

RUN python3 -m venv mltbenv

COPY requirements.txt .
RUN mltbenv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

# 复制样本配置文件作为默认配置（如果不存在config.py）
RUN if [ ! -f config.py ]; then cp config_sample.py config.py; fi

CMD ["bash", "start.sh"]
