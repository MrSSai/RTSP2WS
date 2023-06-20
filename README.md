概要
---
所有现代浏览器本体都不支持RTSP（实时流协议）流的播放，这是许多流行IP摄像头的通用格式。所以很长一段时间，如果你想在网页上显示你的RTSP IP 摄像头流，你必须使用中间转码服务器，它会接收RTSP流，解码并转变成浏览器接收的格式。
本项目将RTSP媒体流转码为WebSocket协议，前端页面使用WebSocket进行播放。
## 使用方法
#### Docker
启动WebSocket服务端
```
docker run --name=websocket -it --rm -p 9001:9001 624647769/websocket:v1.0
```
打开客户端
```angular2html
<!DOCTYPE html>
<html>
<head>
    <title>RTSP Stream</title>
    <style>
        #image-container {
            width: 100%;
            height: auto;
        }
    </style>
</head>
<body>
    <div id="image-container"></div>
    <script>
        const imageContainer = document.getElementById('image-container');
        // 请把 ip 设置为你的WebSocket服务端地址
        const socket = new WebSocket('ws://{ip}:9001');
        // 当收到消息时的处理逻辑
        socket.onmessage = function(event) {
            const imgData = event.data;

            // 创建图像元素
            const img = document.createElement('img');
            img.src = 'data:image/jpeg;base64,' + imgData;
            img.style.width = '100%';
            img.style.height = 'auto';

            // 清空图像容器，并添加新的图像
            imageContainer.innerHTML = '';
            imageContainer.appendChild(img);
        };

        // 当连接成功时的处理逻辑
        socket.onopen = function() {
            console.log('连接成功');
        };
        // 当连接关闭时的处理逻辑
        socket.onclose = function() {
            console.log('连接已关闭');
        };
		
    </script>
</body>
</html>
```
## 示例
![图片1](images/1.png)