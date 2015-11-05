import os
import git


git_repo = 'git+https://github.com/openalea/'

def install(name):
    cmd_str = 'pip install -e %s'%(git_repo+name)
    print cmd_str

packages = """
deploy
sconsx
""".split()

def clone(url, path):
    return git.Repo.clone_from(url, path)

def tags(repository):
    return [t.name for t in repository.tags]

"""
url = 'https://github.com/scikit-learn/scikit-learn'
repo = git.Repo.clone_from(url, '.')

"""
