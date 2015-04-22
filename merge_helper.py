#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

import urllib2
import json
import re
from github import Github

YES_STRINGS = ['y', 'ye', 'yes', 'Y', 'YE', 'Ye', 'Yes', 'YES']
NO_STRINGS = ['n', 'no', 'No', 'NO']

def prompt(string):
    if(raw_input(string + ' [Y/n] ') in YES_STRINGS):
        return True
    else:
        return False

def load_config_file(path):
    data = ''
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def count_thumbs_up(pull_req):
    url = pull_req.comments_url
    data = urllib2.urlopen(url).read()
    data = json.loads(data)
    
    i = 0
    approved_by = set()
    while i < pull_req.comments:
        body = data[i]['body']
        if re.match(r'.*:\+1:.*', body, re.DOTALL):
            approved_by.add(data[i]['user']['login'])
        i+=1
    try:
        # Remove pull req sender from list - you can't approve yourself!
        #approved_by.remove(pull_req.user.login)
        pass
    except:
        pass

    return (len(approved_by),' (' + ','.join(approved_by) + ')')

config = load_config_file("config")
g = Github(config['user'], config['password'])

for repo in g.get_user().get_repos():
    repo.name

repos = g.get_user().get_repos()

for repo in repos:
    if repo.name not in map(str, config['my_repos']):
        continue
    pull_reqs = list()
    i = 0
    while len(repo.get_pulls().get_page(i)):
        j = 0
        for pr in repo.get_pulls().get_page(j):
            print 'Repo: '+ repo.full_name
            print 'PR#', pr.number, ': ', pr.title
            print 'Submitter: ', pr.user.name
            print 'Additions: ', pr.additions
            print 'Deletions: ', pr.deletions
            print 'Mergeable: ', str(pr.mergeable).upper()
            print 'URL: ', pr.html_url
            #print pr.default_branch
            (num_thumbs, approved_by) = count_thumbs_up(pr)
            print 'Thumbs up: ' + str(num_thumbs) + approved_by
            if(pr.mergeable and prompt('Merge PR# ' + str(pr.number) + '?')):
                pr.merge()
                if(pr.is_merged()):
                    print 'Merge successful.'
                else:
                    print 'Merge FAILED.'
            j += 1
            print '\n'
        i+=1
