Notes réalisation serveur :
	Modèle d'une requête :
		[c] Dans tx :
		|[
			def tx(self,req):
				loop = asyncio.get_running_loop()
				jss  = req.to_json()
				fut  = loop.create_future()

				# Determine seq_num and store message
				seq_num            = self.__seq_num_get()
				self.msgs[seq_num] = fut

				# Await the future object
				await fut
				if fut.result() == ("error",_):
					raise Request_Error(...)

			# ... #
			def line_received(self, line):
				try:
					dd = json.loads(line)
					
					# Parse various messages types, etc.
					if seq_num in self.msgs:
						fut = self.msgs[seq_num]
						del selfs.msgs[seq_num] # Unref in message list
						#...#
						fut.set_result()

				except JsonParseError as e:
					# ... #
		|]
