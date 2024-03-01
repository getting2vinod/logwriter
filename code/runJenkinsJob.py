import requests

# Jenkins configuration
jenkins_url = "http:///"
job_name = "Uipath Project Build and Deploy"
jenkins_user = "build"
jenkins_pwd = ""
token = "thisIstheLongToken"

jenkins_params = {'token': token}  # add 'Project_Name': project_name for paramaeters

try:
    auth = (jenkins_user, jenkins_pwd)
    crumb_data = requests.get("{0}/crumbIssuer/api/json".format(jenkins_url), auth=auth,
                              headers={'content-type': 'application/json'})
    if str(crumb_data.status_code) == "200":
        data = requests.get("{0}/job/{1}/build".format(jenkins_url, job_name),
                            auth=auth, params=jenkins_params,
                            headers={'content-type': 'application/json',
                                     'Jenkins-Crumb': crumb_data.json()['crumb']})

        if str(data.status_code) == "201":
            print("Jenkins job is triggered")

        else:
            print("Failed to trigger the Jenkins job")
    else:
        print("Couldn't fetch Jenkins-Crumb")

except Exception as e:
    print("Failed triggering the Jenkins job")
    print("Error: " + str(e))
