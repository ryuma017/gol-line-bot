import logging


format = "%(asctime)s: %(levelname)s: %(pathname)s: line %(lineno)s: %(message)s"
logging.basicConfig(filename='/var/log/intern2/flask.log', level=logging.DEBUG, format=format, datefmt='%Y-%m-%d %H:%M:%S')
