from github import Github
import json
import requests
from pandas.io.json import json_normalize
import pandas as pd
import numpy as np
import config

github_api = "https://api.github.com"
gh_session = requests.Session()
gh_session.auth = (config.USERNAME, config.TOKEN)

def commits_of_repo_github(repo, user, api):
    commits = []
    next = True
    i = 1
    while next == True:
        url = api + "/repos/{}/{}/commits?page={}&per_page=100".format(user, repo, i)
        commit_page = gh_session.get(url = url)
        commit_page_list = [dict(obj, **{"repo_name":"{}".format(repo)}) for obj in commit_page.json()]    
        commit_page_list = [dict(obj, **{"user":"{}".format(user)}) for obj in commit_page_list]
        commits = commits + commit_page_list
        if "Link" in commit_page.headers:
            if 'rel="next"' not in commit_page.headers["Link"]:
                next = False
        i = i + 1
    return commits

def create_commits_df(repo, user, api):
    commit_list = commits_of_repo_github(repo, user, api)
    return json_normalize(commit_list)

commits = create_commits_df("GitHubAPI, "swiercm", github_api)

commits.info()
