from dotenv import load_dotenv
import uuid, os, cmd

class ApiKeys(cmd.Cmd):
	intro = 'Console for controlling ApiKeys'
	prompt = 're_api>>'

	def do_create_key(self, arg):
		"""Creates an api key and returns the key
		syntax:
			re_api>> create_key
		"""
		print(uuid.uuid1())


if __name__ == '__main__':
	ApiKeys().cmdloop()