

docker service create \
--name rmq \
--mount type=bind,source="${PWD}"/rabbitmq,destination=/etc/rabbitmq \
--mount type=bind,source="${PWD}"/mnesia,destination=/var/lib/rabbitmq/mnesia \
--hostname rmq \
--publish 5672:5672 \
--network rpalognet \
rabbitmq:3.12

docker service create \
--name writer \
--mount type=bind,source="${PWD}"/logs,destination=/code/logs \
--hostname writer \
--network rpalognet \
pycode:latest python /code/write.py

docker service create \
--name web \
--replicas 4 \
--mount type=bind,source="${PWD}"/code/logs,destination=/code/logs \
--hostname web \
--publish 8081:8081 \
--network rpalognet \
pycode:latest /bin/bash /code/start.sh


docker service create \
  --name proxy \
  --mount type=bind,source="${PWD}"/nginx/nginx.conf,destination=/etc/nginx/nginx.conf \
  --mount type=bind,source="${PWD}"/nginx,destination=/var/cache/nginx \
  --mount type=bind,source="${PWD}"/nginx/logs,destination=/var/log/nginx \
  --network rpalognet \
  -p "80:80" \
   proxy:latest