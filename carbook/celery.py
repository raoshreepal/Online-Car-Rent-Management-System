# from celery import Celery

# app = Celery('test', broker='redis://localhost:6379/0')

# try:
#     app.connection().connect()
#     print("Celery can connect to Redis!")
# except Exception as e:
#     print("Celery cannot connect to Redis:", e)




import os
from celery import Celery

# Set default settings for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carbook.settings")

app = Celery("carbook")

# Load task modules from all registered Django apps.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from installed Django apps.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
