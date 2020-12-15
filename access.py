from github import Github

g = Github("<access token>") #access token for user

print("{}'s repositries: ".format(g.get_user().login))
for repo in g.get_user().get_repos():
    print(repo.name)
