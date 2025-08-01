# 使用官方Python镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制应用文件
COPY . .

# 安装依赖
RUN pip install --no-cache-dir flask

# 创建存储目录
RUN mkdir -p /html_files

# 设置环境变量
ENV BASE_DIR=/html_files

# 暴露端口
EXPOSE 5000

# 运行应用
CMD ["python", "app.py"]