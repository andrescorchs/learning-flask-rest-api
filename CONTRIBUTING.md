# CONTRIBUTING

## How to build the Dockerfile image locally

```
docker build -t IMAGE_NAME DOCKERFILE_DIR
```

## How to run the Dockerfile locally

```
docker run -dp 5000:5000 -w /app -v "$(pwd):/app" IMAGE_NAME sh -c "flask run"
```