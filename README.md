Steps:

- Build container from Docker file as python:3.9 from the code folder
- Pull the rabbitmq container rabbitmq:3.12
- Test the rmq container loading, as there could be a delay in initial load.
- Install and enable docker-compose
- Run using docker-compose up -d
  - 3 containers should start on the default network.
- The main py will listen on port 80, send messages using http://<server>?msg=this is a test
-   The message classifiers are marked in main.py app route "/"
- The writer py will monitor rpalogs queue and push messages to logs/debug.log file. 
  - ToDO: Log rotate to be implemented.
- Writer code has a 30sec delay to enable rmq service load.
  - This can be improved to do service health check in docker compose.
- 