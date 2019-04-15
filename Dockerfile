# FROM python:3
# WORKDIR /usr/src/app

# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .
# CMD [ "python", "auto_restart.py" ]

FROM artifactory.tusimple.ai/docker-base/service/base-without-tsrpc:latest

WORKDIR /sync-auto-restart

RUN echo "10.130.8.53 artifactory.tusimple.ai" >> /etc/hosts && /bin/bash -c "source /root/.bashrc" && pip3 install -i https://artifactory.tusimple.ai/artifactory/api/pypi/pypi/simple ts_rpc

COPY . .

CMD python3 auto_restart.py