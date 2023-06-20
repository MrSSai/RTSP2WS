# 使用 ubuntu:20.04 作为基础镜像
FROM ubuntu:20.04

# 设置工作目录
WORKDIR /app

# 复制本地的 config.ini, main.py, requirements.txt 到容器中
COPY . .

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装依赖包
RUN sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && sed -i 's/archive.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && sed -i 's/security.ubuntu.com/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y python3.8 python3.8-dev ffmpeg python3-pip supervisor nginx && \
    rm -rf /var/lib/apt/lists/* && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1 && \
    update-alternatives --set python /usr/bin/python3.8

# 安装 Python 依赖包
RUN pip3 install -r requirements.txt -i https://pypi.douban.com/simple/
RUN cp nginx/nginx.conf /etc/nginx/nginx.conf

# 暴露 9001 端口
EXPOSE 9001
EXPOSE 80
#启动命令
#docker run --name=doctor-websocket --restart=always -d -p 9001:9001 -p 80:80 --net=doctor-docker_doctor_net  624647769/websocket:v1.0
# 运行 main.py
#CMD ["python","main.py"]
CMD ["supervisord","-c","/app/supervisord.conf"]