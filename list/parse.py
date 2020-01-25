from  collections import OrderedDict

import rfc3986
import re
import json
import httpx
from . import model

INSTANCE_FILE = 'instances.yml'
TITLE_RE = re.compile('(add|remove)[ ]+(.+)', re.IGNORECASE)


def normalize_url(url):
    if url.startswith('http://'):
        return None

    if not url.startswith('https://'):
        url = 'https://' + url

    try:
        return rfc3986.normalize_uri(url)
    except:
        return None


def load_requests():
    requests = []
    with httpx.Client() as client:
        response = client.get('https://api.github.com/repos/dalf/searx-instances/issues?state=open')
        rjson = response.json()
        for issue in rjson:
            if len(list(filter(lambda label: label.get('name') == 'instance', issue['labels']))):
                r = re.search(TITLE_RE, issue.get('title'))
                issue_number = issue.get('number')
                command = r.group(1).lower()
                url = normalize_url(r.group(2))
                requests.append((issue_number, command, url))
    return requests


def apply_add_request(instances, request):
    new_instance = model.Instance(request[2], False, '', {})
    print(new_instance)
    instances.add(new_instance)


def apply_remove_request(instance, request):
    pass


def apply_requests(instance_list, requests):
    for request in requests:
        if request[1] in ['add']:
            apply_add_request(instance_list, request)
        elif request[1] in ['remove', 'delete', 'del']:
            apply_remove_request(instance_list, request)


def main():
    instance_list = model.Storage.load(INSTANCE_FILE)
    print(instance_list)
    requests = load_requests()
    # apply_requests(instance_list, requests)
    model.Storage.save(INSTANCE_FILE, instance_list)


if __name__ == "__main__":
    main()