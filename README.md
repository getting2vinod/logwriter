Steps (Logger):
Version 2.0
- Setup docker swarm
  - docker swarm init
- Build container from Docker file in code folder as pycode:2.0 from the code folder
  - Update the hostip.txt file with the ip address of the current host (used by jenkins build)
  - docker build . -t pycode:2.0
- The build will push the code folder into the image. This was done for web replicas was not starting. Can be enhanced.
- Pull the rabbitmq container rabbitmq:3.12
- Test the rmq container loading, as there could be a delay in initial load.
  - Create a folder named "tmp"
  - docker run -d --name rmq -v ${PWD}/rabbitmq:/tmp -v ${PWD}/mnesia:/mnesia rabbitmq:3.12
  - Attach to the container
    - docker exec -it rmq /bin/bash
    - cp -R /etc/rabbitmq /tmp
    - cp -R /var/lib/rabbitmq/mnesia /mnesia/. 
  - docker rm -f rmq 
-Build the nginx image
    - cd nginx
    - docker build . -t proxy:2.0
- On logwriter folder
  - chmod +x service.sh
  - Run service.sh
- The main py will listen on port 8081 , send messages using http://<server>?msg=this is a test
-   The message classifiers are marked in main.py app route "/"
- The writer py will monitor rpalogs queue and push messages to logs/debug<0-6>.log file. 
  - Log file is rotated weekly.
- Install the sumo collector on this box and set the folder from sumo cloud interface
  - code/logs/*.logs



Version 1.0
- Build container from Docker file as python:3.9 from the code folder
- Pull the rabbitmq container rabbitmq:3.12
- Test the rmq container loading, as there could be a delay in initial load.
- Install and enable docker-compose
- Run using docker-compose up -d
  - 3 containers should start on the default network.
- The main py will listen on port 8081 (port mapped to 80 through docker-compose), send messages using http://<server>?msg=this is a test
-   The message classifiers are marked in main.py app route "/"
- The writer py will monitor rpalogs queue and push messages to logs/debug<0-6>.log file. 
  - Log file is rotated weekly.
- Writer code has a 30sec delay to enable rmq service load.
  - This can be improved to do service health check in docker compose.
- Install the sumo collector on this box and set the folder from sumo cloud interface
  - logs/*.logs

Steps (Jenkins)
- Extract the backup file in "jenkins/jenkins-data/thinbackup/jenkinsThinkBackup.tar.gz"
  - tar –xvzf jenkins/jenkins-data/thinbackup/jenkinsThinkBackup.tar.gz
- Start  Jenkins using the docker-compose file in "jenkins" folder.
  - Note: Jenkins would be running independently 
- Install the jenkins plugin named "thinbackup"
- Set the thinbackup folder to "/var/jenkins_home/thinbackup"
- Use thinbackup to restore from the extracted backup
  - Select next build number and Restore plugins
- The backed up jobs should be visible now.
- In case there is a password change for the "build" user, update it in the main.py
- The build server is setup on dev instance, uipath cli needs to be setup (Should be setup automatically on the first run of the build.)
- The jenkins agent can be downloaded from this jenkins instance itself, for which java needs to be on the agent server.

Features:
- Ping on port 80 "/ping" will return the ip of the server. {"success": true,"ip":"<read from the hostip.txt>"}
  - This is done as the host ip could return the load balancer ip if picked up dynamically.