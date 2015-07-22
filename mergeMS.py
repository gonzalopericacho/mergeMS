import os
import sys
import requests
import requests.packages.urllib3
import json

requests.packages.urllib3.disable_warnings()
TOKEN = os.getenv("GITHUB_TOKEN")

__author__ = 'gonzalopericacho'


def make_request(path,input={},method="GET"):
    url = "https://api.github.com%s" % path if not path.startswith("http") else path

    r = requests.request(method, url,data=json.dumps(input), headers={"Accept": "application/vnd.github.v3+json",
                                               "Authorization": "token %s" % TOKEN})

    r.raise_for_status()
    return r.json()


if __name__ == '__main__':

    if len(sys.argv) != 3:
        print "Usage: %s <repo> <version>" % sys.argv[0]
    else:
        repo = sys.argv[1]
        version = sys.argv[2]


        comp_branches = make_request("/repos/%s/compare/master...staging" % repo)

        if comp_branches["behind_by"] > 0:
            print "Staging needs rebasing"
            exit(1)
        elif comp_branches["ahead_by"] == 0:
            print "No commits to merge"
            exit(0)
        else:
            statuses = make_request("/repos/%s/commits/staging/status" % repo)["statuses"]
            for status in statuses:
                if status["state"] == "failure" or status["state"] == "pending":
                    print "Tests are not in success mode"
                    exit(1)
            print "Prepared to merge from staying to master"
            input = {"sha": comp_branches["commits"][0]["sha"]}
            make_request("/repos/%s/git/refs/heads/master" % repo, input, "PATCH")
            print "success!"
            print "Tagging..."
            input = {"tag_name": version,
                     "target_commitish": "master"}
            make_request("/repos/%s/releases" % repo, input, "POST")
            print "success!"
