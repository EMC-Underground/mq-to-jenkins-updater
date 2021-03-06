import boto3
import xmltodict
import json
import requests
import os

# Assumptions:
# - All messages will have a X-GitHub-Event attribute
# Resources:
# - https://developer.github.com/v3/activity/events/types/
# - http://boto3.readthedocs.io/en/latest/guide/resources.html
def get_message_from_SQS():
  # Get the service resource
  sqs = boto3.resource('sqs')

  # Get the queue
  queue = sqs.get_queue_by_name(QueueName='emc-underground-github-events')

  # Process messages by printing out body and optional author name
  for message in queue.receive_messages(MessageAttributeNames=['GithubEvent']):
    print("We got a message")
    # Get the custom author message attribute if it was set
    eventType = ""
    if message.message_attributes is not None:
      eventType = message.message_attributes.get('GithubEvent').get('StringValue')
      print("The message was from github and it is a {0} event".format(eventType))
      event = json.loads(message.body)
      if eventType == "commit_comment":
        print('Someone commented on a commit!')
      elif eventType == "create":
        print('Someone created a branch or tag!')
      elif eventType == "delete":
        print('Someone deleted a branch or tag!')
      # elif eventType == "deployment":
      # elif eventType == "deployment_status":
      # elif eventType == "fork":
      # elif eventType == "gollum":
      # elif eventType == "issue_comment":
      # elif eventType == "member":
      # elif eventType == "membership":
      # elif eventType == "page_build":
      # elif eventType == "public":
      # elif eventType == "pull_request_review_comment":
      # elif eventType == "pull_request":
      elif eventType == "push":
        print('Someone has pushed to a repo!')
        repoName = event['repository']['full_name']
        check_for_jenkins_job(repoName)

      # elif eventType == "repository":
      # elif eventType == "release":
      # elif eventType == "status":
      # elif eventType == "team_add":
      # elif eventType ==   "watch":
      # elif eventType == "issues":
    # Let the queue know that the message is processed
    message.delete()

# Checks if jenkins maintains a project with a given Github repo name
# Params:
# + repoName - string - the name of the repoName
# Returns:
# + string|Null - returns the jenkins job url if found
def check_for_jenkins_job(repoName):
  # get the root jenkins object
  r = requests.get('http://10.4.44.127:8080/api/json')
  jenkins = r.json()

  # get the jobs from jenkins
  listOfJobs = jenkins['jobs']
  for job in listOfJobs:
    # get the config.xml
    jobRequest = requests.get('{0}config.xml'.format(job['url']))
    config = xmltodict.parse(jobRequest.text)
    githubURL = config['project']['properties']['com.coravy.hudson.plugins.github.GithubProjectProperty']['projectUrl']
    if repoName in githubURL:
      # Make the build!
      buildRequest = requests.post('{0}build'.format(job['url']))
      if buildRequest.status_code == requests.codes.created:
        requests.post('{0}hubot/jenkins'.format(os.getenv('HUBOT_URL')),data = {'message':'{0} has been updated in GitHub! Rebuilding...'.format(job['name'])})
      else:
        requests.post('{0}hubot/jenkins'.format(os.getenv('HUBOT_URL')),data = {'message':'{0} has been updated in GitHub! But the build request failed...'.format(job['name'])})
      return

  requests.post('{0}hubot/jenkins'.format(os.getenv('HUBOT_URL')),data = {'message':'{0} has been updated in GitHub but is not managed by Jenkins.'.format(repoName)})
# listener to give visibility into job completetion
def error_listener(event):
  if event.exception:
    print("The job failed...{0}".format(event.exception))
    print("{0}".format(event.traceback))
  else:
    print("The job worked!")
