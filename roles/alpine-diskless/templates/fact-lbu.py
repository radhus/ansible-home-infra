#!{{ ansible_python.executable }}

import subprocess
import json

def main():
    lbu_list = subprocess.check_output(['lbu', 'list'])
    tracked_files = lbu_list.decode().strip().split('\n')

    lbu_status = subprocess.check_output(['lbu', 'status'])
    modified_files = [
        line.strip().split(' ')[1]
        for line in lbu_status.decode().strip().split('\n')
        if len(line) > 0
    ]
    dirty = len(modified_files) > 0

    output = {
        "tracked": tracked_files,
        "modified": modified_files,
        "dirty": dirty,
    }
    print(json.dumps(output))

if __name__ == '__main__':
    main()