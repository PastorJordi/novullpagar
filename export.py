import os
cwd = os.getcwd()


base_script = (
    '#!/bin/bash\n'
    f'source activate {os.environ["CONDA_DEFAULT_ENV"]}\n'
    f'python3 {os.path.join(cwd, "novullpagar.py")} "$@'
)

with open(os.path.join(cwd, 'novullpagar.sh'), 'w') as handle:
    handle.write(
        base_script
    )

export_str = f'alias novullpagar="{os.path.join(cwd, "novullpagar.sh")}"'

with open(os.path.expanduser("~/.bashrc"), "a") as handle:
    handle.write(export_str)