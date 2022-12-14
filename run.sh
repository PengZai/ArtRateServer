
# gunicorn -w 3 -k gthread --thread 4 -b 0.0.0.0:8001 -t 120 ArtRate_server.wsgi
gunicorn -w 2 -k gthread --thread 4 -b 10.206.0.13:8001 -t 120 ArtRate_server.wsgi