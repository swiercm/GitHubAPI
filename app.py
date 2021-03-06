from github import Github
import json
import requests
from pandas.io.json import json_normalize
import pandas as pd
import numpy as np
import config
import chart_studio.plotly as py
import plotly.graph_objs as graph_obj

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

commits = create_commits_df(config.REPO, config.USER, github_api)
                           
commits["date"] =  pd.to_datetime(commits["commit.committer.date"])
commits["date"] =  pd.to_datetime(commits["date"], utc=True)
commits["commit_date"] = commits["date"].dt.date
commits["commit_year"] = commits["date"].dt.year
commits["commit_hour"] = commits["date"].dt.hour
                            
#HOURLY COMMITS
commits_hour = commits.groupby("commit_hour")[["sha"]].count()
commits_hour = commits_hour.rename(columns = {"sha": "commit_count"})

fig = graph_obj.Figure([graph_obj.Bar(
    x=commits_hour.index, 
    y=commits_hour.commit_count,
    text=commits_hour.commit_count, 
    textposition="auto")])
fig.update_layout(title = "Hourly Commits", 
    xaxis_title = "Hour", 
    yaxis_title = "Commits", 
    xaxis_tickmode = "linear")
fig.show()

#COMMITS BY DATE
commits_day = commits.groupby("commit_date")[["sha"]].count()
commits_day = commits_day.rename(columns = {"sha": "commit_count"})

fig = graph_obj.Figure([graph_obj.Scatter(
    x=commits_day.index, 
    y=commits_day.commit_count, 
    text=commits_day.commit_count, 
    fill="tozeroy")])
fig.update_layout(
    title = "Commits by Date", 
    xaxis_title = "Date", 
    yaxis_title = "Commits ")
fig.show()

#AVERAGE DAILY COMMITS BY YEAR
commits_year = commits.groupby("commit_year")[["sha"]].count()
commits_year = commits_year.rename(columns = {"sha": "commits_count"})
commits_year["daily_avg"] = commits_year["commits_count"]/365

fig = graph_obj.Figure([graph_obj.Scatter(
    x=commits_year.index, 
    y=commits_year.daily_avg, 
    text=commits_year.daily_avg)])
fig.update_layout(
    title = "Average Daily Commits by Year", 
    xaxis_title = "Year", 
    yaxis_title = "Average Commits", 
    xaxis_tickmode = "linear")
fig.show()

#TOP COMMITTERS
commits_author = commits.groupby("author.login")[["sha"]].count()
commits_author = commits_author.rename(columns = {"sha": "commit_count"})
commits_author = commits_author.sort_values(by="commit_count", ascending=False)
top_authors = commits_author.head(30)

fig = graph_obj.Figure([graph_obj.Bar(
    x=top_authors.index, 
    y=top_authors.commit_count)])
fig.update_layout(
    title = "Top Committers", 
    xaxis_title = "Author", 
    yaxis_title = "Commits", 
    xaxis_tickmode = "linear",
    xaxis_tickangle=-40)
fig.show()
