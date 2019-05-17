from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route("/")
def helloWorld():
    return "Hello World\n"

@app.route('/prefetch', methods=['GET', 'POST'])
def prefetch():
	url = request.args.get('url')
	command_prefetch = "/home/eugeneyu/prefetch.sh {0}".format(url)
	try:
		result = subprocess.check_output([command_prefetch], shell=True)
		return "Success"
	except subprocess.CalledProcessError as e:
		return "An error occurred while trying to fetch task status updates.", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80)