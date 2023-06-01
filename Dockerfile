# 使用官方的 Python 镜像作为基础镜像
FROM python:3.8
# 设置工作目录为 /app
WORKDIR /app
# 指定容器卷
VOLUME /app
# 复制依赖需求文件到工作目录
COPY requirements.txt .
# 安装依赖库
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple  --no-cache-dir -r requirements.txt

# 设置代理环境变量
ENV http_proxy=http://172.17.0.1:7890
ENV https_proxy=http://172.17.0.1:7890
ENV no_proxy=localhost,127.0.0.1
# 设置其他环境变量
ENV PYTHONUNBUFFERED=1
ENV ES_HOST=elasticsearch
# 设置 Django 服务启动时使用的命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

