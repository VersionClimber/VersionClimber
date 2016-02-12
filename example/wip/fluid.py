from __future__ import unicode_literals
from rpaths import PosixPath, Path
import yaml
from reprounzip.common import File, Package, read_files, read_packages

fn = 'marsalt/.reprozip-trace/config.yml'

def load_config(filename):
    with filename.open(encoding='utf-8') as fp:
        config = yaml.safe_load(fp)
    
    keys_ = set(config)
    runs = config.get('runs', [])
    packages = read_packages(config.get('packages', []), File, Package)
    other_files = read_files(config.get('other_files', []), File)

    # Adds 'input_files' and 'output_files' keys to runs
    for run in runs:
        if 'input_files' not in run:
            run['input_files'] = {}
        if 'output_files' not in run:
            run['output_files'] = {}

    return runs, packages, other_files

def main():
    config = load_config(Path(fn))
    runs, packages, other_files = config
    for p in packages:
        print p.name


