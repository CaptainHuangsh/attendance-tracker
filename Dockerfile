FROM docker.m.daocloud.io/ubuntu:22.04

# Version: 1.2.2
# 使用国内apt源
RUN sed -i 's/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list

WORKDIR /app

# 安装Python和系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    python3.11-venv \
    iputils-ping \
    net-tools \
    iproute2 \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 设置时区为上海
RUN ln -fs /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone

# 创建符号链接
RUN ln -s /usr/bin/python3.11 /usr/local/bin/python

# 安装Python依赖
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制代码
COPY main.py .
COPY static/ ./static/

# 创建数据目录
RUN mkdir -p /app/data && chmod 777 /app/data && touch /app/data/app.log && chmod 666 /app/data/app.log

# 暴露端口
EXPOSE 10170

# 启动命令（使用root运行以确保日志可写）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10170"]
