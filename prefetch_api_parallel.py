from flask import Flask, request
import subprocess
import gevent
from  gevent.pywsgi import WSGIServer

app = Flask(__name__)

KEY='/home/eugeneyu/.ssh/prefetch_key'
NODES=['35.194.113.217', '34.97.136.225']
printers = []
printers.append({'hostname':'www.google.com'})

def ping(hostname):
    command = ['ping', '-c', '1', '-W', '1', '-q', hostname]
    return subprocess.Popen(command, stdout=subprocess.PIPE)


def prefetch_on_node(url, node_ip):
	cmd = "ssh -oStrictHostKeyChecking=no -i {0} prefetch@{1} curl {2} -o download 2>&1".format(KEY, node_ip, url)
	print cmd
	return subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)


@app.route("/")
def helloWorld():
    return "Nothing here\n"

@app.route('/ping', methods=['GET', 'POST'])
def get_ping():
    site_id = 'x'
    pings = {printer['hostname']: ping(printer['hostname']) 
             for printer in printers}
    # Wait for all of them to complete
    gevent.wait(pings.values())
    for hostname in pings:
        response[site_id][hostname] = output_parser.ping(pings[hostname].stdout.read())
    return response


@app.route('/prefetch', methods=['GET', 'POST'])
def prefetch():
	url = request.args.get('url')
	prefetches = {
		node: prefetch_on_node(url, node)
		for node in NODES
	}

	gevent.wait(prefetches.values())
	for node in prefetches:
		response[node] = pings[node].stdout.read()

	return response


if __name__ == '__main__':
	#app.run(host='0.0.0.0',port=80)
	http_server = WSGIServer(('0.0.0.0', 80), app)
	http_server.serve_forever()

