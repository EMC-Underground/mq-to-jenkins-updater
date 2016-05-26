import methods
from flask import Flask

# Globals
app = Flask(__name__)
scheduler = BackgroundScheduler()
port = int(os.getenv('VCAP_APP_PORT', 8080))

# Uncomment if you need to debug the site
# app.debug = True

# Routes
@app.route('/')
def index_route():
  return 'Welcome to the jenkins updater api'

if __name__ == '__main__':
  scheduler.add_job(methods.get_message_from_SQS, 'interval', seconds = 10)
  scheduler.add_listener(methods.error_listener, events.EVENT_JOB_EXECUTED | events.EVENT_JOB_ERROR)
  scheduler.start()

  try:
    app.run(host='0.0.0.0', port=port)

  except (KeyboardInterrupt, SystemExit):
    # Not strictly necessary if daemonic mode is enabled but should be done if possible
    scheduler.shutdown()
