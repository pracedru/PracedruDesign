import json
import zlib
import base64

__author__ = 'mamj'

text_formats_endings = ['.json', '.jadoc', '.jobj', '.jgeom', '.inp', '.si_mpl', '.ts']


def complex_handler(Obj):
	if hasattr(Obj, 'serialize_json'):
		#try:
			return Obj.serialize_json()
		#except TypeError as e:
		#	print(str(e))
	else:
		raise Exception('Object of type %s with value of %s is not JSON serializable' % (type(Obj), repr(Obj)))


def read_text_from_disk(file_path):
	with open(file_path) as data_file:
		data = data_file.read()
	return data


def read_lines_from_disk(file_path):
	with open(file_path) as data_file:
		data = data_file.readlines()
	return data


def read_json_data_from_disk(file_path):
	is_binary = True
	for ending in text_formats_endings:
		if ending in file_path.lower():
			is_binary = False
	if not is_binary:
		with open(file_path) as data_file:
			data = json.load(data_file)
	else:
		with open(file_path, "rb") as data_file:
			S = data_file.read()
			data_string = zlib.decompress(S)
			data = json.loads(data_string.decode("UTF-8"))
	return data


def write_data_to_disk(file_path, data):
	is_binary = True
	for ending in text_formats_endings:
		if ending in file_path.lower():
			is_binary = False
	if not is_binary:
		text_file = open(file_path, "w")
		text_file.write(data)
		text_file.close()
	else:
		code = zlib.compress(bytes(data, 'UTF-8'))
		text_file = open(file_path, "wb")
		text_file.write(code)
		text_file.close()


def get_uids(idobject_list):
	uids = []
	for idobject in idobject_list:
		uids.append(idobject.uid)
	return uids
