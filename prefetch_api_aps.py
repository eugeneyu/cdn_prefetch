from flask import Flask, request
import subprocess
import logging
import calendar
import time
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

LOG = "/var/log/prefetch.log"  
logging.basicConfig(filename=LOG, filemode="w", level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
console = logging.StreamHandler()  
console.setLevel(logging.DEBUG)  
logging.getLogger("").addHandler(console)
logger = logging.getLogger(__name__)


KEY = './prefetch_key'
#NODES = ['35.194.113.217', '34.97.136.225']

# Create nodes.txt with
# gcloud compute instances list --filter="name~'cdn-prefetch*'" --format="csv[no-heading](name,EXTERNAL_IP)" > nodes.txt
NODES = []
with open('nodes.txt') as f:
	for line in f:
		name, ip = line.partition(",")[::2]
		node = {}
		node['name'] = name.strip()
		node['ip'] = ip.strip()
		NODES.append(node)



def prefetch_on_node(url, node_ip):
	cmd = "ssh -oStrictHostKeyChecking=no -i {0} prefetch@{1} curl {2} -o download 2>&1".format(KEY, node_ip, url)
	#print(node_ip + ": " + cmd)
	logger.info(node_ip + ": " + cmd)
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	out, err = proc.communicate()
	#print(node_ip + ": " + out)
	logger.info(node_ip + ": " + out.decode("utf-8"))
	return out


@app.route("/")
def helloWorld():
    return "Nothing here\n"


@app.route('/prefetch', methods=['GET', 'POST'])
def prefetch():
	url = request.args.get('url')
	for node in NODES:
		app.apscheduler.add_job(func=prefetch_on_node, trigger='date', args=[url, node['ip']], 
			misfire_grace_time=20, id='ip-'+node['ip']+'-'+str(calendar.timegm(time.gmtime())))

	return 'Prefetch Started', 200


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=80)

