# Installation
0. make sure you have (`python`)[https://www.python.org/downloads/] installed - the version must be greater than `3.8`

1. package dependencies via. (`poetry`)[https://python-poetry.org/docs/]
    - install via. instructions on website, i used `curl -sSL https://install.python-poetry.org | python3 -`
        - follow the install page for any troubleshooting
    - inside this root folder `rag` execute `poetry install`
        - it will install the pkgs from the `pyproject.toml`
        - you can add new packages via. `poetry add {pkg}`
    - enter your virtual env by executing `poetry shell`
        - this has all your dependencies available
        - you may need to play around to associate this with your IDE (such as (`VSCode`)[https://code.visualstudio.com/docs/python/environments#_working-with-python-interpreters])
        - you can find the path to your virtual env interpreter using `poetry env list --full-path`
    - after initial setup:
        - whenever you pull from github execute `poetry install` or `poetry update` in case the `pyproject.toml` has changed
        - remember you are only in the virtual env after running `poetry shell`
            - the .venv files will then live inside the folder you ran the `poetry install` in
            - you can remove any envs using `poetry env remove {path|env-name}`
            - you can exit your virtual env using `deactivate`
