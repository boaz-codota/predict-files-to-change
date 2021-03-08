import requests
import json
from requests_oauthlib import OAuth1
import sys
import pathlib
import os
import git
import glob

# Usage example: python3 kaki.py my_out_dir https://api.github.com/repos/y2kappa/timed

if len(sys.argv) != 3:
    print(
        "Usage: python3 kaki.py <output_dir> <repo> (https://api.github.com/repos/<user>/repo)"
    )

path = str(sys.argv[1])
repo_for_api = "https://api.github.com/repos/" + str(sys.argv[2])
repo_for_clone = "https://github.com/" + str(sys.argv[2]) + ".git"
folder_for_clone = str(sys.argv[2]).replace("/", "_")

pathlib.Path(path).mkdir(parents=True, exist_ok=True)
output_file = path + "/" + repo_for_api.replace("/", "_") + ".json"
repo = git.Repo.clone_from(repo_for_clone, folder_for_clone)

print("Scanning " + repo_for_api + " -> " + output_file + "\n=============")


def request_to_github(url):
    result = requests.get(
        url,
        headers={"Accept": "application/vnd.github.v3+"},
        auth=OAuth1("8477dcc5255b6d701da96123d516bf14ca59664a"),
    ).json()
    # print(str(result))
    return result


def get_all_untouched_files(commit):
    repo.git.checkout(commit)

    return [
        filename
        for filename in glob.iglob(folder_for_clone + "/**/*", recursive=True)
        if not os.path.isdir(filename)
    ]


def get_content(file_name):
    text = ""
    try:
        with open(file_name, "r") as f:
            text = f.read()
    except (UnicodeDecodeError, FileNotFoundError):
        print("ignoring " + file_name)
    return text


data = []
i = 1
cur_page = request_to_github(
    repo_for_api + "/pulls?state=closed&per_page=100&page=" + str(i)
)

try:
    while len(cur_page) > 0:
        for pr in cur_page:
            pull = {}
            files_of_pull = request_to_github(
                str(pr["_links"]["self"]["href"]) + "/files"
            )

            untouched_files = get_all_untouched_files(
                pr.get("merge_commit_sha", pr["head"]["sha"])
            )
            pull["title"] = pr["title"]
            pull["body"] = pr["body"]
            pull["changed_files"] = list(
                map(
                    lambda x: {
                        "name": x["filename"],
                        "content": get_content(folder_for_clone + "/" + x["filename"]),
                    },
                    files_of_pull,
                )
            )
            pull["unchanged_files"] = list(
                map(
                    lambda name: {
                        "name": name[len(folder_for_clone + "/") :],
                        "content": get_content(name),
                    },
                    filter(lambda x: x not in pull["changed_files"], untouched_files),
                )
            )
            print("Pull: " + pull["title"] + "\n")
            data.append(pull)
        i += 1
        cur_page = request_to_github(
            repo_for_api + "/pulls?state=closed&per_page=100&page=" + str(i)
        )
except:
    pass

with open(output_file, "w") as f:
    f.write(json.dumps(data))
