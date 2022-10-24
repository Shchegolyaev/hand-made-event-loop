import json
import os.path
import threading
import time

from calls import (DependenciesExistError, MaxCountJobError,
                   TimeNotComeException)
from job import Job
from logger import logging
from tasks import Tasks


class Scheduler:
    functions = [
        Tasks.generate_random_string,
        Tasks.get_five_random_user,
        Tasks.pipe,
        Tasks.target,
        Tasks.manage_folders_os,
        Tasks.source,
    ]

    def __init__(self, pool_size: int = 10):
        self._is_stopped = True
        self._is_running = False
        self.pool_size: int = pool_size
        self._job_queue: list[Job] = []
        self.tasks = {fn.__name__: fn for fn in self.functions}

    def schedule(self, job: Job):  # add task
        """
        Add job to queue scheduler.
        """
        if len(self._job_queue) == self.pool_size:
            raise MaxCountJobError("The scheduler supports " "no "
                                   "more than 10 tasks!")
        self._job_queue.append(job)
        logging.info(f"Add job: {job.id}")

    def check_screen_scheduler(self):
        name_file = "screen_scheduler.json"
        if not os.path.exists(name_file):
            return
        with open(name_file) as file:
            json_data = json.load(file)
        print(json_data)
        for job in json_data:
            json_data[job]["target"] = self.tasks[json_data[job]["target"]]
            self._job_queue.append(Job(**json_data[job]))
        os.remove(name_file)

    def run(self):
        """
        Start work scheduler.
        """
        self._is_running = True
        self._is_stopped = False

        self.check_screen_scheduler()
        while self._is_running:
            if not self._job_queue:  # check empty queue
                return None
            job = self._job_queue.pop(0)
            try:
                logging.info(f"Job {job.id} start.")
                job.run()  # run job
            except StopIteration:
                logging.info(f"Job {job.id} finished.")
                job.is_completed = True
                continue
            except TimeoutError:
                logging.error(f"Job {job.id} finished with TimeoutError.")
                continue
            except DependenciesExistError:
                logging.info(f"Job {job.id} wait for dependencies. "
                             f"Skipping...")
                if job.count_started >= job.tries:
                    logging.info(f"Job {job.id} exceeded the number "
                                 f"of restarts")
                    continue
            except TimeNotComeException:
                logging.info(
                    f"The time for completing the job {job.id} has not yet "
                    f"come. Skipping..."
                )
            except Exception as error:
                logging.info(f"In work job {job.id} happened error: {error}")
                if job.count_started >= job.tries:
                    logging.info(f"Job {job.id} exceeded the number "
                                 f"of restarts")
                    continue

            logging.info(f"Job {job.id} add to queue.")
            self._job_queue.append(job)
            time.sleep(1)
        logging.info("Scheduler is stop.")
        self._is_stopped = True

    def stop(self):
        self._is_running = False
        while not self._is_stopped:
            time.sleep(1)
        screen_scheduler: dict = {}
        for job in self._job_queue:
            data_for_job = job.__dict__
            data_for_job["target"] = job.target.__name__
            data_for_job.pop("coro")
            data_for_job.pop("time_start")
            data_for_job.pop("count_started")
            data_for_job.pop("is_completed")
            screen_scheduler[job.id] = data_for_job

        with open("screen_scheduler.json", "w") as fp:
            json.dump(screen_scheduler, fp, indent=4)


if __name__ == "__main__":
    scheduler = Scheduler(pool_size=10)

    #  work with file system
    # for i in range(1, 11):
    #     scheduler.schedule(Job(
    #             id=i,
    #             target=Tasks.generate_random_string,
    #             args=random.randint(100, 1000*1000)))

    # work with request
    for i in range(1, 10):
        scheduler.schedule(
            Job(id=i, target=Tasks.get_five_random_user, max_working_time=1)
        )

    #  dependencies example
    # job_source = Job(
    #     id=3,
    #     target=Tasks.source,
    #     max_working_time=10,
    #     dependencies=[]
    # )
    # job_pipe = Job(
    #     id=2,
    #     target=Tasks.pipe,
    #     max_working_time=10,
    #     dependencies=[job_source, ]
    # )
    # job_target = Job(
    #     id=1,
    #     target=Tasks.target,
    #     max_working_time=10,
    #     dependencies=[job_pipe, ]
    # )

    # scheduler.schedule(job_source)
    # scheduler.schedule(job_pipe)
    # scheduler.schedule(job_target)

    tread = threading.Thread(target=scheduler.run, name="Scheduler")
    tread.start()

    # Test with stop Scheduler
    time.sleep(5)
    scheduler.stop()
    # tread.join()
    # logging.info("Scheduler killed.")
    # time.sleep(5)
    #
    # logging.info("Scheduler start.")
    # tread = threading.Thread(target=scheduler.run, name="Scheduler")
    # tread.start()
