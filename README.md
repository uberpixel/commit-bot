A crude and simple post-receive hook that sends out commit notifications via Jabber/XMPP.

## Requirements
  * git
  * python
  * sleekxmpp

## Setup
Create a new file named `config.json` in the bots directory, and add a dictionary named `sender` with a `account` and `pass` keys containing the account name and password for the XMPP account that should deliver the notifications. Example:

	{
		"sender": {
			"account": "foo@bar.baz",
			"pass": "1234567890"
		}
	}
	
## Config.json
The `sender` dictionary is a **must**, additionally however, you can specify the following keys:

`recipients`: An array of XMPP accounts that should receive all notifications

`repositories`: An array of dictionaries for every repository. Each entry must at least have a key called `name` with the name of the repository as value. Additionally you can set a `recipients` array, which works just like the global one, except that it's constraint to this repository only. You can also set an `exclude` key which can be either `true`, to completely exclude the repository, or an array of strings containing the names of branches which should be excluded.

`whitelist`: Defaults to `false` if not set, however, if set to `true`, the bot will only send notifications about repositories that it finds in the `repositories` list and which are not explicitly excluded.

Example config.json:

	{
		"sender": {
			"account": "foo@bar.baz",
			"pass": "1234567890"
		},
		"whitelist": true,
		"recipients": [ "global@receiver" ],
		"repositories": [
			{
				"name": "some-repo",
				"exclude": true
			},
			{
				"name": "another-repo",
				"recipients": [ "local@receiver" ]
			},
			{
				"name": "third-repo",
				"exclude: [ "some-branch", "another-branch" ]
			}
		]
	}

## Usage
Simply symlink the post-receive script into the hooks directory of the git repositories you want to receive notifications for
	
## License
MIT license. See LICENSE.md for the complete licensing text