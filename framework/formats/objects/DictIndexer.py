# methods that index lists into dictionaries using various methods
class DictIndexer:

	@staticmethod
	def bySlot(list, slot, clean=False, index_type='flag', index_cell=0):
		dict = {}

		# get config
		index_first_row = index_type == 'row'
		index_rows = index_type == 'rows'
		index_cells = index_type == 'cell'

		for item in list:

			# get value, optionally clean it
			value = str(item[slot])
			if clean:
				value = value.strip().lower()

			# assemble full key
			key = value

			# index all matching rows if wanted
			if index_rows:
				if key not in dict:
					dict[key] = []
				dict[key].append(item)

			# index first matching row if wanted
			elif index_first_row:
				dict[key] = item

			# index last cell value if wanted
			elif index_cells:
				dict[key] = item[index_cell]

			# otherwise just index a flag
			else:
				dict[key] = True

		return dict

	@staticmethod
	def by2slots(list, slot1, slot2, clean=False, index_type='flag', index_cell=0):
		dict = {}

		# get config
		index_rows = index_type == 'rows'
		index_cells = index_type == 'cell'

		for item in list:

			# get values, optionally clean it
			value1 = str(item[slot1])
			value2 = str(item[slot2])
			if clean:
				value1 = value1.strip().lower()
				value2 = value2.strip().lower()

			# assemble full key
			key = value1 + "|" + value2

			# index all matching rows if wanted
			if index_rows:
				if key not in dict:
					dict[key] = []
				dict[key].append(item)

			# index last cell value if wanted
			elif index_cells:
				dict[key] = item[index_cell]

			# otherwise just index a flag
			else:
				dict[key] = True

		return dict

	@staticmethod
	def by3slots(list, slot1, slot2, slot3, clean=False, index_type='flag', index_cell=0):
		dict = {}

		# get config
		index_rows = index_type == 'rows'
		index_cells = index_type == 'cell'

		for item in list:

			# get values, optionally clean it
			value1 = str(item[slot1])
			value2 = str(item[slot2])
			value3 = str(item[slot3])
			if clean:
				value1 = value1.strip().lower()
				value2 = value2.strip().lower()
				value3 = value3.strip().lower()

			# assemble full key
			key = value1 + "|" + value2 + "|" + value3

			# index all matching rows if wanted
			if index_rows:
				if key not in dict:
					dict[key] = []
				dict[key].append(item)

			# index last cell value if wanted
			elif index_cells:
				dict[key] = item[index_cell]

			# otherwise just index a flag
			else:
				dict[key] = True

		return dict

	@staticmethod
	def by4slots(list, slot1, slot2, slot3, slot4, clean=False, index_type='flag', index_cell=0):
		dict = {}

		# get config
		index_rows = index_type == 'rows'
		index_cells = index_type == 'cell'

		for item in list:

			# get values, optionally clean it
			value1 = str(item[slot1])
			value2 = str(item[slot2])
			value3 = str(item[slot3])
			value4 = str(item[slot4])
			if clean:
				value1 = value1.strip().lower()
				value2 = value2.strip().lower()
				value3 = value3.strip().lower()
				value4 = value4.strip().lower()

			# assemble full key
			key = value1 + "|" + value2 + "|" + value3 + "|" + value4

			# index all matching rows if wanted
			if index_rows:
				if key not in dict:
					dict[key] = []
				dict[key].append(item)

			# index last cell value if wanted
			elif index_cells:
				dict[key] = item[index_cell]

			# otherwise just index a flag
			else:
				dict[key] = True

		return dict