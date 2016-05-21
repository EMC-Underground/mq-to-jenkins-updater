import boto3
import xmltodict
import json

def get_message_from_SQS():
  # Get the service resource
  sqs = boto3.resource('sqs')

  # Get the queue
  queue = sqs.get_queue_by_name(QueueName='emc-underground-github-events')

  # Process messages by printing out body and optional author name
  for message in queue.receive_messages(MessageAttributeNames=['Source']):
    # Get the custom author message attribute if it was set
    eventSource = ''
    if message.message_attributes is not None:
      eventSource = message.message_attributes.get('Source').get('StringValue')
      if eventSource:
        if eventSource == "Github"
          print('We got something from Github!')
          event = message.body
          repoName = event['repository']['full_name']
          if check_for_jenkins_job(repoName):
            a
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
      return job['url']
