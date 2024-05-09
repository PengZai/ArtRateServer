pythonpath='/var/www/html/ArtRate/ArtRate_server'
# bind = '118.195.135.213:8000'
# bind = 'localhost:8001'
bind = '0.0.0.0:8001'

workers = 2


# reference web
# https://www.zmrenwu.com/courses/hellodjango-blog-tutorial/materials/74/
# comment
# gunicorn ArtRate_server.wsgi -w 2 -k gthread 4 -b 0.0.0.0:8001 -t 16


# kill gunicorn
# ps -ax | grep <process name> | grep -v grep | awk '{print $1}' | xargs kill
# ps -ax | grep gunicorn | grep -v grep | awk '{print $1}' | xargs kill


# command
# gunicorn -c gunicorn_conf.py ArtRate_server.wsgi
# nohup gunicorn -c gunicorn_conf.py ArtRate_server.wsgi &> /dev/null &
# nohup bash run.sh > log.txt 2>&1 &


# 查看是否成功启动
# ps -ef | grep python |grep gunicorn_conf |grep -v grep
# ps -ax | grep gunicorn

# 管理员页面
# http://118.195.135.213:8001/admin/login