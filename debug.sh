docker build --no-cache -t sync-auto-restart .
docker run -it --network=host sync-auto-restart