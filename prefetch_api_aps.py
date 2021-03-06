from flask import Flask, request
import subprocess
import logging
import sys
import calendar
import time
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

LOG = "/var/log/prefetch.log"  
logging.basicConfig(filename=LOG, filemode="w", level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
#console = logging.StreamHandler()  
#console.setLevel(logging.DEBUG)  
#logging.getLogger("").addHandler(console)
#logger = logging.getLogger(__name__)

class LessThanFilter(logging.Filter):
    def __init__(self, exclusive_maximum, name=""):
        super(LessThanFilter, self).__init__(name)
        self.max_level = exclusive_maximum

    def filter(self, record):
        #non-zero return means we log this message
        return 1 if record.levelno < self.max_level else 0

#Get the root logger
logger = logging.getLogger(__name__)
#Have to set the root logger level, it defaults to logging.WARNING
logger.setLevel(logging.NOTSET)

logging_handler_out = logging.StreamHandler(sys.stdout)
logging_handler_out.setLevel(logging.DEBUG)
logging_handler_out.addFilter(LessThanFilter(logging.WARNING))
logger.addHandler(logging_handler_out)

logging_handler_err = logging.StreamHandler(sys.stderr)
logging_handler_err.setLevel(logging.WARNING)
logger.addHandler(logging_handler_err)


KEY = '/etc/prefetch-key/prefetch_key'
#NODES = ['35.194.113.217', '34.97.136.225']

# Create nodes.txt with
# gcloud compute instances list --filter="name~'cdn-prefetch*'" --format="csv[no-heading](name,EXTERNAL_IP)" > nodes.txt
NODES_LIST_FILE = './nodes.txt'



def prefetch_on_node(url, node_ip):
	cmd = "ssh -oStrictHostKeyChecking=no -i {0} prefetch@{1} curl {2} 2>&1".format(KEY, node_ip, url)
	#print(node_ip + ": " + cmd)
	logger.info(node_ip + " CMD: " + cmd)
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	out, err = proc.communicate()
	#print(node_ip + ": " + out)
	logger.info(node_ip + " OUT bytes: " + str(len(out)))
	if err:
		logger.error(node_ip + " ERR: " + err)
	return out


@app.route("/")
def helloWorld():
    return "Nothing here\n"


@app.route('/prefetch', methods=['GET', 'POST'])
def prefetch():
	url = request.args.get('url')
	nodes = []
	with open(NODES_LIST_FILE) as f:
		for line in f:
			name, ip = line.partition(",")[::2]
			node = {}
			node['name'] = name.strip()
			node['ip'] = ip.strip()
			nodes.append(node)
	for node in nodes:
		app.apscheduler.add_job(func=prefetch_on_node, trigger='date', args=[url, node['ip']], 
			misfire_grace_time=20, id='ip-'+node['ip']+'-'+str(calendar.timegm(time.gmtime())))

	return 'Prefetch Started', 200


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=80)

