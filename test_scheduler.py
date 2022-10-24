import datetime as dt

import pytest

from calls import (DependenciesExistError, MaxCountJobError,
                   TimeNotComeException)
from job import Job
from scheduler import Scheduler
from tasks import Tasks


class TestScheduler:
    instance_job = Job(
        id=1,
        target=Tasks.get_five_random_user,
        start_at="18:20",
        max_working_time=10,
        tries=0,
    )

    def test_max_count_job(self):
        scheduler = Scheduler()
        for i in range(10):
            self.instance_job.id = i
            scheduler.schedule(self.instance_job)
        with pytest.raises(MaxCountJobError):
            scheduler.schedule(self.instance_job)


class TestStartAt:
    def test_start_at(self):
        time = (dt.datetime.now() + dt.timedelta(hours=1)).time()
        job = Job(
            id=1,
            target=Tasks.get_five_random_user,
            start_at=f"{time.strftime('%H:%M')}",
        )
        with pytest.raises(TimeNotComeException):
            job.run()


class TestDependencies:
    def test_dependencies(self):
        one_job = Job(
            id=1,
            target=Tasks.get_five_random_user,
        )
        second_job = Job(
            id=1,
            target=Tasks.get_five_random_user,
            dependencies=[
                one_job,
            ],
        )
        with pytest.raises(DependenciesExistError):
            second_job.run()


class TestMaxWorkTime:
    def test_work_time(self):
        job = Job(id=1, target=Tasks.get_five_random_user, max_working_time=1)
        job.time_start = dt.datetime.now() - dt.timedelta(hours=1)
        with pytest.raises(TimeoutError):
            job.run()
