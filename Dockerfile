FROM anasty17/mltb:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

# 安装 Alist（使用 curl 而不是 wget）
RUN mkdir -p /usr/src/alist
WORKDIR /usr/src/alist
# 使用 curl 下载（大多数基础镜像都预装了 curl）
RUN curl -L -o alist.tar.gz https://github.com/alist-org/alist/releases/download/v3.44.0/alist-linux-musl-amd64.tar.gz && \
    tar -xzvf alist.tar.gz && \
    chmod +x alist && \
    rm alist.tar.gz

# 返回主工作目录
WORKDIR /usr/src/app

RUN python3 -m venv mltbenv

COPY requirements.txt .
RUN mltbenv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

# 复制样本配置文件作为默认配置（如果不存在config.py）
RUN if [ ! -f config.py ]; then cp config_sample.py config.py; fi

CMD ["bash", "start.sh"]
