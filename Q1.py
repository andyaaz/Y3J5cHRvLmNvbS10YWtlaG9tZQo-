from collections import deque
from datetime import datetime
import re
from typing import TypedDict
from xmlrpc.client import Boolean


class Request(TypedDict):
    time: int
    url: str
    host: str


class RateLimiter:
    """
    Limit host requests with a queue within a time window and other options.
    Here is an example store:
    [
        "1.1.1.1": [<earilest_request_timestamp>, ..., <last_request_timestamp>],
        ...
    ]
    where we try to keep
        last_request_timestamp - earilest_request_timestamp < window
        and length of queue < limit
    otherwise host gets put in jail for ban_for specified time span.
    """

    def __init__(self, window: int, limit: int, ban_for: int, match_url: str) -> None:
        self.window = window
        self.limit = limit
        self.match_url = match_url
        self.ban_for = ban_for
        self.store = {}

    def add(
        self,
        host: Request["host"],
        time: Request["time"],
        url: Request["url"],
    ) -> None:
        if host not in self.store.keys():
            self.store[host] = deque([time])
        elif not self.match_url or url == self.match_url:
            self.store[host].append(time)

    def remove(self, host: Request["host"]) -> None:
        self.store.pop(host, None)

    def should_ban_for(self, host: Request["host"]) -> Boolean:
        if len(self.store[host]) > self.limit:
            return self.ban_for
        return False

    def pop_to_fit_window(self, host: Request["host"]) -> None:
        while self.store[host][-1] - self.store[host][0] > self.window:
            self.store[host].popleft()


class Jail:
    """
    banned hosts are here for duration specified when added
    """

    def __init__(self) -> None:
        self.store = {}

    def add(self, host: Request["host"], time: Request["time"], duration: int) -> None:
        self.store[host] = {"duration": duration, "banned_at": time}
        print(",".join([str(time), "BAN", host]))

    def is_in_jail(self, host: str) -> Boolean:
        return host in self.store.keys()

    def free_host_if_should(self, host: Request["host"], time: Request["time"]) -> None:
        if not self.is_in_jail(host):
            return None
        if time - self.store[host]["duration"] > self.store[host]["banned_at"]:
            self.store.pop(host)
            print(",".join([str(time), "UNBAN", host]))


def parse_line(line) -> Request:
    # https://www.seehuhn.de/blog/52.html
    PARTS = [
        r"(?P<host>\S+)",  # host %h
        r"\S+",  # indent %l (unused)
        r"(?P<user>\S+)",  # user %u
        r"\[(?P<time>.+)\]",  # time %t
        r'"(?P<req>.*)"',  # req "%r"
        r"(?P<status>[0-9]+)",  # status %>s
        r"(?P<size>\S+)",  # size %b (careful, can be '-')
        r'"(?P<referrer>.*)"',  # referrer "%{Referer}i"
        r'"(?P<agent>.*)"',  # user agent "%{User-agent}i"
    ]
    PATTERN = re.compile(r"\s+".join(PARTS) + r"\s*\Z")
    if not PATTERN.match(line):
        return None
    request = PATTERN.match(line).groupdict()
    time = int(datetime.strptime(request["time"], "%d/%b/%Y:%H:%M:%S %z").timestamp())
    url = request["req"].split()[1]
    return {"time": time, "url": url, "host": request["host"]}


if __name__ == "__main__":
    jail = Jail()
    rl1 = RateLimiter(window=60, limit=40, ban_for=600, match_url=None)
    rl2 = RateLimiter(window=600, limit=100, ban_for=3600, match_url=None)
    rl3 = RateLimiter(window=600, limit=20, ban_for=7200, match_url="/login")
    # TEST all rls
    rate_limiters = [rl3, rl2, rl1]
    # TEST rl1
    # rate_limiters = [rl1]
    # TEST rl2
    # rate_limiters = [rl2]
    # TEST rl3
    # rate_limiters = [rl3]
    with open("test_logs/TestQ1.log") as f:
        for line in f:
            request = parse_line(line)
            if request:
                # should_ban_for gets set when the first violation detected
                should_ban_for = False
                jail.free_host_if_should(host=request["host"], time=request["time"])
                if not jail.is_in_jail(request["host"]):
                    for rl in rate_limiters:
                        rl.add(**request)
                        rl.pop_to_fit_window(request["host"])
                        if not should_ban_for:
                            should_ban_for = rl.should_ban_for(request["host"])
                        if should_ban_for:
                            if not jail.is_in_jail(request["host"]):
                                jail.add(
                                    host=request["host"],
                                    time=request["time"],
                                    duration=should_ban_for,
                                )
                            rl.remove(request["host"])
