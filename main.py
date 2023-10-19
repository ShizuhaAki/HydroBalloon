from bs4 import BeautifulSoup
import requests
import schedule
import time
import re
import json
import browser_cookie3 as cookielib
from http.cookiejar import CookieJar

parsed_rids = set()
parsed_status = set()


class Record:
    uid: int
    pid: str

    def __init__(self, user, problem) -> None:
        self.uid = user.strip()
        self.pid = problem.strip()

    def __str__(self):
        return f"Problem: {self.pid}, User: {self.uid}"


def init(domain: str, contest_id: str, base_url: str, interval: int):
    url = f"{base_url}/d/{domain}/record?uidOrName=&pid=&tid={contest_id}&lang=&status=1"
    cookiejar = cookielib.firefox()
    schedule.every(interval).seconds.do(
        fetch_submissions, url=url, cookie=cookiejar, base_url=f'{base_url}/d/{domain}'
    )
    while True:
        schedule.run_pending()
        time.sleep(1)


def fetch_submissions(url: str, cookie: CookieJar, base_url: str) -> None:
    resp = requests.get(url, cookies=cookie)
    soup = BeautifulSoup(resp.content, features="html.parser")
    target_script = soup.body.findAll("script")
    for script in target_script:
        m = re.search(r"var UiContextNew = '\{(.*)\}'", str(script))
        if m:
            raw_resp = json.loads("{" + m.group(1) + "}")
            records = None
            if "rids" in raw_resp:
                records = raw_resp["rids"]
            for record in records:
                if not record in parsed_rids:
                    #    print(record)
                    status = parse_record(base_url, record, cookie)
                    parsed_rids.add(record)
                    if not str(status) in parsed_status:
                        # Only first AC should be added to jobs
                        parsed_status.add(str(status))
                        print(status)
                else:
                    break  # note that newer record IDs always come out on top
            break


def parse_record(base_url: str, record: str, cookie: CookieJar) -> Record:
    url = f"{base_url}/record/{record}"
    resp = requests.get(url, cookies=cookie)
    soup = BeautifulSoup(resp.content, features="html.parser")
    body = soup.body
    user = body.find("a", class_="user-profile-name")
    problem = body.find("a", href=re.compile("p/"))
    return Record(user=str(user.contents[0]), problem=str(problem.b.contents[0]))

conf = json.load('config.json')
domain = conf['domain']
contest_id = conf['contest_id']
base_url = conf['base_url']
delay = conf['delay']
init(domain, contest_id, base_url, delay)
