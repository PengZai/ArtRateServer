pythonpath='/var/www/html/ArtRate/ArtRate_server'
# bind = '118.195.135.213:8000'
# bind = 'localhost:8001'
bind = '0.0.0.0:8001'

workers = 2


# reference web
# https://www.zmrenwu.com/courses/hellodjango-blog-tutorial/materials/74/
# comment
# gunicorn ArtRate_server.wsgi -w 2 -k gthread 4 -b 0.0.0.0:8001 -t 16


# command
# gunicorn -c gunicorn_conf.py ArtRate_server.wsgi
# nohup gunicorn -c gunicorn_conf.py ArtRate_server.wsgi &> /dev/null &

# 查看是否成功启动
# ps -ef | grep python |grep gunicorn_conf |grep -v grep