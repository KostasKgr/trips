# How to run

Create a virtual env and install requirements
```
vritualenv -p python3 .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the server, listens to port 5001:

```
python3 app.py
```


# Configuration

You can set the following environment variables to control the service behaviour.

| Environment variable             | Description                          |
|----------------------------------|--------------------------------------|
| SIMULATION_DELAY_SECONDS_MINIMUM | Minimum delay in position simulation |
| SIMULATION_DELAY_SECONDS_MAXIMUM | Maximum delay in position simulation |

