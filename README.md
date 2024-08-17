# GitHub release watcher


## Dev

```bash
# edit main.py and set the CACHE_FILE to the debug value

# run the app
python main.py

# example outout: Running on http://127.0.0.1:5000

```

## Deploy using Docker

To build and deploy to a local docker instance

```bash
chmod +x deploy.sh

# replace 8080 with desired port to deploy on (default is 5000)
./deploy.sh 8080

```