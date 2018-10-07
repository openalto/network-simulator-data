#!/usr/bin/env python

import os
import sys
import json
from multiprocessing import Pool

import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

retry_requests = requests.Session()
retries = Retry(total=3,
                backoff_factor=0.1,
                status_forcelist=[ 500, 502, 503, 504 ])
retry_requests.mount('http://', HTTPAdapter(max_retries=retries))


def get_all_users():
    resp = requests.get("http://dashb-cms-job.cern.ch/dashboard/request.py/listusers-api",
                        headers={"Accept": "application/json"})
    content = json.loads(resp.content)
    users = [user["GridName"] for user in content["users"]]
    return users


def get_all_tasks(users, start=0, end=40):
    tasks = []
    count = start
    sum = len(users)
    results = Pool(200).imap_unordered(fetch_task, users[start:end])
    for user, content, error in results:
        if error is None:
            tasks.extend([task["TASKNAME"] for task in content["antasks"]])

            count += 1
            print("Users: %d/%d" % (count, sum))
        else:
            count += 1
            print("error fetching user: %s" % user)

        if count == sum:
            return

    return tasks


def fetch_task(user_name):
    try:
        url = "http://dashb-cms-job.cern.ch/dashboard/request.py/antasktable"
        params = {"user": user_name, "timerange": "lastWeek"}
        resp = requests.get(url, headers={"Accept": "application/json"}, params=params)
        content = json.loads(resp.content)
        return user_name, content, None
    except Exception as e:
        return user_name, None, e


def get_all_jobs(task_names):
    jobs = []
    count = 0
    sum = len(task_names)
    results = Pool(200).imap_unordered(fetch_job, task_names)
    for task_name, content, error in results:
        if error is None:
            jobs.extend([job for job in content["taskjobs"][0] if job["STATUS"] == "finished"])
            count += 1
            print("Tasks: %d/%d" % (count, sum))
        else:
            count += 1
            print("error fetching task: %s" % task_name)

        if count == sum:
            break
    return jobs


def fetch_job(task_name):
    try:
        url = "http://dashb-cms-job.cern.ch/dashboard/request.py/antasktable"
        params = {"taskname": task_name}
        # resp = requests.get(url, headers={"Accept": "application/json"}, params=params)
        resp = retry_requests.get(url, headers={"Accept": "application/json"},
                                  params=params, timeout=5)
        content = json.loads(resp.content)
        return task_name, content, None
    except Exception as e:
        return task_name, None, e


def get_all_files(jobs):
    count = 0
    sum = len(jobs)
    files = []

    results = Pool(200).imap_unordered(fetch_file, jobs)
    for job, part_files, error in results:
        if error is None:
            files.extend(part_files)

            count += 1
            print("Jobs: %d/%d" % (count, sum))
        else:
            count += 1
            print("error fetching job: %s" % job["TaskJobId"])

        if count % 3000 == 0:
            s = json.dumps(files, indent=4, sort_keys=True)
            # with open(os.path.join(sys.argv[1], "files_temp-%d.json" % int(count / 3000)), 'w') as f:
            with open(os.path.join(sys.argv[1], "files_temp.json"), 'w') as f:
                f.write(s)

        if count == sum:
            break
    return files


def fetch_file(job):
    files = []
    try:
        url = "http://dashb-cms-job.cern.ch/dashboard/request.py/fileaccessinfo2?schedulerJobId=%s" % (
        job["SchedulerJobId"])
        # params = {"schedulerJobId": job["SchedulerJobId"]}
        # resp = requests.get(url, headers={"Accept": "application/json"}, params=params)
        resp = retry_requests.get(url, headers={"Accept": "application/json"},
                                  timeout=5)
        content = json.loads(resp.content)
        for file_info in content["fileAccessInfo"]:
            file_info["site"] = job["Site"]
            file_info["jobId"] = job["JobId"]
            file_info["taskJobId"] = job["TaskJobId"]
            file_info["schedulerJobId"] = job["SchedulerJobId"]
            file_info["started"] = job["started"]
            file_info["finished"] = job["finished"]
            files.append(file_info)
        return job, files, None
    except Exception as e:
        return job, files, e


def main():
    users = get_all_users()
    tasks = get_all_tasks(users=users, start=int(sys.argv[2]), end=int(sys.argv[3]))
    jobs = get_all_jobs(task_names=tasks)
    j = json.dumps(jobs, indent=4, sort_keys=True)
    with open(os.path.join(sys.argv[1], "jobs.json"), 'w') as f:
        f.write(j)
    files = get_all_files(jobs)
    s = json.dumps(files, indent=4, sort_keys=True)
    with open(os.path.join(sys.argv[1], "files.json"), 'w') as f:
        f.write(s)
    os.remove(os.path.join(sys.argv[1], "files_temp.json"))


if __name__ == '__main__':
    main()
