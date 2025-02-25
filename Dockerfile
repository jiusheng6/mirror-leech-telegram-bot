FROM anasty17/mltb:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

RUN python3 -m venv mltbenv

COPY requirements.txt .
RUN mltbenv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

# 下载 alist
RUN apt-get update && apt-get install -y wget \
    && wget https://github.com/alist-org/alist/releases/download/v3.42.0/alist-linux-musl-amd64.tar.gz \
    && tar -zxvf alist-linux-musl-amd64.tar.gz \
    && rm alist-linux-musl-amd64.tar.gz \
    && chmod +x alist \
    && apt-get remove -y wget \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*


CMD ["bash", "start.sh"]
