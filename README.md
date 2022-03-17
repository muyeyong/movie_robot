功能介绍
=========================
定时自动从豆瓣电影的想看、在看、看过中获取影音信息，然后通过Sonarr、Radarr下载管理资源。

**注意，豆瓣读取和检索，未使用OpenAPI（如有任何合规问题请及时联系作者下架源码），但模拟请求的过程中，增加了随机延迟机制来保护网站。本工具只能用于学习和自己研究，禁止用作任何商业用途！**


环境要求
=========================
- 剧集管理：sonarr
- 电影管理：radarr
- BT下载工具：qbittorrent
- 种子管理：jackett

部署方式
=========================
- 本应用支持Docker形式启动，日常运行占资源非常低，无CPU消耗（linux crontab调度任务），常驻内存2MB左右；但因为使用了非OpenAPI的形式，所以没有提供打包好的docker镜像进行分享，请自行通过Dockerfile打包；
- 当然也可以下载源码，直接用NAS的定时任务运行，或者你的任何能够定时调度python程序的工具；

源码运行方式请先安装依赖：pip install -r requirements.txt

然后在执行命令：python3 douban_movie_download.py

配置文件
=========================
按注释源码的user_config.yml

制作成Docker(在项目根目录下运行)
=========================
制作镜像
 docker build -t movie_robot  . -f Dockerfile --platform linux/amd64
查看镜像
docker images 
运行镜像
docker run -it -v -v data:/放置user_config.yml的路径 movie_robot

参考博客： https://muyeyong.github.io/2022/01/06/zhe-teng-nas/


