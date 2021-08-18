#!/usr/bin/env python
import os
import requests
import yaml
import signal
from requests.auth import HTTPBasicAuth


class Config:
    def __init__(self, config_file):
        self.organisation = None
        self.repos_per_page = None
        self.basedir = None
        self.username = None
        self.password = None
        with open(config_file, "r") as stream:
            self.raw_config = yaml.safe_load(stream)
            self.organisation = self.raw_config["organisation"]
            self.username = self.raw_config["username"]
            self.password = self.raw_config["password"]
            self.basedir = self.raw_config["baseDir"]
            self.repos_per_page = self.raw_config["reposPerCall"]


config_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf")
config_file = os.path.join(config_dir, "config.yaml")
config = Config(config_file)

proceed = True
page = 1


def signal_handler(sig, frame):
    global proceed
    print('Aborting...')
    proceed = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

while proceed:
    response = requests.get(
        "https://api.github.com/orgs/{organisation}/repos?per_page={per_page}&page={page}"
            .format(organisation=config.organisation,
                    per_page=config.repos_per_page,
                    page=page),
        auth=HTTPBasicAuth(config.username, config.password))
    repositories = response.json()
    if response.status_code != 200 or isinstance(response.json(), str):
        print("api call failed: \n{response}".format(response=response.text))
        exit(1)
    else:
        page += 1
        if len(repositories) == 0:
            proceed = False
        else:
            for repo in repositories:
                if not proceed:
                    exit(1)
                ssh_url = repo.get("ssh_url")
                project = ssh_url.split("/")[-1].split(".")[0]
                fullpath = "{basedir}/{project}".format(basedir=config.basedir, project=project)
                if not os.path.exists(fullpath):
                    print("cloning {project}".format(project=project))
                    git_command = "git clone {url} {fullpath}".format(url=ssh_url, fullpath=fullpath)
                    os.system("echo {git_command}".format(git_command=git_command))
                    os.system(git_command)
                else:
                    print("updating {project}".format(project=project))
                    for command in ["fetch --all", "checkout master", "pull"]:
                        git_command = "git -C {fullpath} {command}".format(fullpath=fullpath, command=command)
                        os.system("echo {git_command}".format(git_command=git_command))
                        if 0 != os.system(git_command):
                            break
