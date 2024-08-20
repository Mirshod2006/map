from django_cron import CronJobBase, Schedule
from .views import download_real

class RunFunctionEveryTenMinutes(CronJobBase):
    RUN_EVERY_MINS = 10  # Задаем интервал в минутах
    ALLOW_PARALLEL_RUNS = True
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'views.download_real'  # Идентификатор задачи
    def do(self):
        download_real()
