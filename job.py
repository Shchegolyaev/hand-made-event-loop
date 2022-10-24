import datetime as dt

from calls import DependenciesExistError, TimeNotComeException


class Job:
    def __init__(
        self,
        id: int,
        target,
        start_at: str = "",
        max_working_time: int = -1,
        tries: int = 0,
        dependencies: list = [],
        args=0,
    ):
        self.time_start = None
        self.id = id
        self.start_at = start_at
        self.max_working_time = max_working_time  # in seconds
        self.tries = tries
        self.dependencies: [Job] = dependencies
        self.target = target
        self.args = args
        self.is_completed = False
        self.count_started = 0
        if args != 0:
            self.coro = self.target(self.args)
        else:
            self.coro = self.target()

    def run(self):

        #  check for tries
        self.count_started += 1

        #  check for dependencies
        if self.dependencies:
            for depend in self.dependencies:
                if depend.is_completed is False:
                    raise DependenciesExistError()

        #  check for start_at
        if self.start_at != "":
            start_at_time = dt.datetime.strptime(self.start_at, "%H:%M").time()
            time_now = dt.datetime.now().time()
            if time_now < start_at_time:
                raise TimeNotComeException()

        #  check for max_working_time
        if self.time_start is None:
            self.time_start = dt.datetime.now()
        if self.max_working_time != -1:
            if (
                int((dt.datetime.now() - self.time_start).total_seconds())
                > self.max_working_time
            ):
                raise TimeoutError()

        #  start coro
        result = next(self.coro)

        return result

    def pause(self):
        pass

    def stop(self):
        pass
