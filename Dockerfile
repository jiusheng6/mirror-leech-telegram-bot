FROM anasty17/mltb:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

# 安装必要的工具
RUN apt-get update && apt-get install -y wget curl && apt-get clean

# 安装 Alist
RUN mkdir -p /usr/src/alist
WORKDIR /usr/src/alist
RUN wget https://github.com/alist-org/alist/releases/download/v3.44.0/alist-linux-musl-amd64.tar.gz && \
    tar -xzvf alist-linux-musl-amd64.tar.gz && \
    chmod +x alist && \
    rm alist-linux-musl-amd64.tar.gz

# 返回主工作目录
WORKDIR /usr/src/app

RUN python3 -m venv mltbenv

COPY requirements.txt .
RUN mltbenv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash", "start.sh"]
