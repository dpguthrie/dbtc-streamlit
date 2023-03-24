# dbtc-streamlit

## Setup

Create a virtual environment

```
$ virtualenv .venv
```

Install required packages

```
$ pip install -r requirements.txt
```

## Run Streamlit

```
$ streamlit run Home.py
```

## Debuggin in vscode

This will allow you to run the streamlit server in debug mode and create breakpoints in your script.

```json
{
    "version": "0.1.0",
    "configurations": [
        {
            "name": "debug streamlit",
            "type": "python",
            "request": "launch",
            "program": "/.venv/bin/streamlit",
            "args": [
                "run",
                "Home.py"
            ]
        }
    ]
    }
```
