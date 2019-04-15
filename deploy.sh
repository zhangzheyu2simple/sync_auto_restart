docker build -t sync-auto-restart .
docker tag sync-auto-restart:latest artifactory.tusimple.ai/docker-data-pipeline/sync/autorestart
sudo docker push artifactory.tusimple.ai/docker-data-pipeline/sync/autorestart:latest