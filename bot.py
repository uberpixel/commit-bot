#!/usr/bin/python

import sleekxmpp
import json
import os
import subprocess
import sys
import logging
from optparse import OptionParser

if sys.version_info < (3, 0):
	reload(sys)
	sys.setdefaultencoding('utf8')

logging.basicConfig()

try:
	basedir    = os.path.dirname(os.path.realpath(__file__))
	config     = json.load(open(os.path.join(basedir, 'config.json')))
except IOError:
	logging.error('Couldn\'t load config.json!')
	sys.exit()

recipients = []
repodir    = None
repository = None
branch     = None

class XMPPBot(sleekxmpp.ClientXMPP):

	def __init__(self, jid, password, msg):
		super(XMPPBot, self).__init__(jid, password)

		self.msg = msg
		self.add_event_handler('session_start', self.start)

		self.register_plugin('xep_0030')
		self.register_plugin('xep_0199')

	def start(self, event):
		self.send_presence()
		self.get_roster()

		for recipient in recipients:
			self.send_message(mto=recipient, mbody=self.msg)

		self.disconnect(wait=True)




def git_command(command):
	pipe = subprocess.Popen(command, shell=True, cwd=repodir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	(out, error) = pipe.communicate()
	pipe.wait()

	return out.strip()


def commit_data(since, until):
	data = git_command('git log {0}..{1} --format="%s - %an"'.format(since, until))
	result = data.strip()
	return result.split('\n')


def parse_commit(oldrev, revision):
	if revision == '0000000000000000000000000000000000000000':
		return 'deleted branch {0} from {1}'.format(branch, repository)

	author = git_command('git show --quiet --format="%an" {0}'.format(revision))

	if oldrev == '0000000000000000000000000000000000000000':
		return '{0} published branch {1}/{2}'.format(author, repository, branch)


	commits = commit_data(oldrev, revision)
	verb    = 'commit' if len(commits) == 1 else 'commits'
	message = '{0} pushed {1} {2} to {3}/{4}'.format(author, len(commits), verb, repository, branch)

	for commit in reversed(commits):
		message += '\n'
		message += commit

	return message




if __name__ == '__main__':
	optp = OptionParser()
	optp.add_option('-o', dest='oldrev', help='The old revision')
	optp.add_option('-n', dest='newrev', help='The new revision')
	optp.add_option('-g', dest='repo', help='The directry containing the repo')
	optp.add_option('-b', dest='branch', help='The branch')
	optp.add_option('-x', dest='name', help='The repo name')

	(opts, args) = optp.parse_args()

	repodir    = opts.repo
	branch     = opts.branch
	repository = opts.name
	whitelist  = False

	# Some basic validation
	if 'sender' not in config:
		logging.error('Invalid JSON! config.json requires sender')
		sys.exit()

	if 'account' not in config['sender'] or 'pass' not in config['sender']:
		logging.error('Invalid JSON! config.json requires account and pass in sender')
		sys.exit()

	if 'whitelist' in config:
		whitelist = config['whitelist']

	# Get the recipients
	if 'recipients' in config:
		recipients += config['recipients']

	# Get the repository info
	found = False

	try:
		if 'repositories' in config:
			for repo in config['repositories']:
				if repo['name'] == opts.name:
					found = True

					if 'exclude' in repo:
						exclude = repo['exclude']

						if type(exclude) is list:
							if branch in exclude:
								sys.exit()
						elif exclude == True:
							sys.exit()

					if 'recipients' in repo:
						recipients += repo['recipients']

					break
	except KeyError:
		pass

	if whitelist is True and found is False:
		sys.exit()

	# Parse the commit data
	message = parse_commit(opts.oldrev, opts.newrev)
	
	# Send the message
	if message is not None:
		xmpp = XMPPBot(config['sender']['account'], config['sender']['pass'], message)
	
		if xmpp.connect():
			xmpp.process(block=True)
		else:
			logging.error('Failed to connect to XMPP server')
