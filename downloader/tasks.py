from celery import Celery

app = Celery('downloader', broker='pyamqp://guest@localhost//')

@app.task
def add(x, y):
    return x + y
