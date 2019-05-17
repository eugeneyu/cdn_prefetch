from flask import Flask, request
import asyncio
import subprocess

app = Flask(__name__)

KEY='~/.ssh/prefetch_key'
NODES=['35.194.113.217', '34.97.136.225']

global_loop = asyncio.new_event_loop()
asyncio.set_event_loop(global_loop)

async def bar(loop):
    # Disregard how simple this is, it's just for example
    s = await asyncio.create_subprocess_exec("ls", loop=loop)

async def prefetch_on_node(url, node_ip, loop):
	loop = asyncio.get_event_loop()
	cmd = "ssh -oStrictHostKeyChecking=no -i {0} prefetch@{1} {2} -o download 2>&1".format(KEY, node_ip, url)
	proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, loop=loop)
	stdout, stderr = await proc.communicate()

	print('[{0} exited with {1}]'.format(cmd, proc.returncode))
	if stdout:
		print('[stdout]\n{0}'.format(stdout.decode()))
	if stderr:
		print('[stderr]\n{0}'.format(stderr.decode()))

@app.route("/")
def helloWorld():
    return "Nothing here\n"

@app.route('/prefetch', methods=['GET', 'POST'])
def prefetch():
	url = request.args.get('url')
	new_loop = asyncio.new_event_loop()
	asyncio.set_event_loop(new_loop)
	loop = asyncio.get_event_loop()

	#loop = global_loop

	tasks = [
        asyncio.ensure_future(prefetch_on_node(url, NODES[0], loop)),
        asyncio.ensure_future(prefetch_on_node(url, NODES[1], loop)),
    ]
	loop.run_until_complete(asyncio.gather(*tasks))

	#global_loop.run_until_complete(asyncio.wait_for(bar(global_loop), 1000))
	loop.close()


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=80)