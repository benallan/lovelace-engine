# Project Lovelace engine

Project Lovelace's automated tester of code submissions for computational science education.

## Set up


Build the engine docker file:

```
docker build -t lovelace-engine -f ./engine.Dockerfile .
```


Run the engine docker container:
```bash
docker run \
  -v "$(realpath ./engine):/app/engine" \
  -v "$(realpath ../lovelace-problems/problems):/app/problems" \
  -v "$(realpath ../lovelace-problems/resources):/app/resources" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 14714:14714 \
  lovelace-engine
```


Stop the engine container:
```bash
docker stop $(docker ps -q --filter ancestor=lovelace-engine)
```

TODO: clean up the code runner container(s) automatically when the engine container exits.
