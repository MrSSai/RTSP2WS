概要
---
所有现代浏览器本体都不支持`RTSP（实时流协议）`流的播放，这是许多流行IP摄像头的通用格式。所以很长一段时间，如果你想在网页上显示你的`RTSP IP` 摄像头流，你必须使用中间转码服务器，它会接收`RTSP`流，解码并转变成浏览器接收的格式。
本项目将`RTSP`媒体流转码为`WebSocket`协议，前端页面使用`WebSocket`进行播放。
## 功能列表
- [x] RTSP媒体流
- [x] 多客户端
## 使用方法
### Docker
启动`WebSocket`服务端
```
docker run --name=websocket -it --rm -p 9001:9001 -p 80:80 624647769/websocket:v1.0
```
在浏览器输入服务端`IP`即可访问

你可以设置自己的`rtsp`流地址，例如：将自定义的rtsp流地址写在config.ini中
```editorconfig
[client]
rtsp_url=rtsp://admin:password@192.168.3.110:554/Streaming/Channels/1
```
启动Docker
```
docker run --name=websocket -it --rm \
 -p 9001:9001 \
 -p 80:80 \
 -v $PWD/config.ini:/app/config.ini \
 624647769/websocket:v1.0
```
在浏览器输入服务端`IP`即可访问
## 示例
![图片1](images/1.png)