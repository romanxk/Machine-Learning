# ML 2017 hw3 Test CNN

import numpy as np
import csv
from sys import argv
from keras.models import load_model

np.set_printoptions(precision = 6, suppress = True)

def read_file(filename):

	data = []
	with open(filename, "r", encoding="big5") as f:

		for line in list(csv.reader(f))[1:]:
			data.append( [float(x) for x in line[1].split()] )

	return np.array(data), len(data)

def write_file(filename, result):

	with open(filename, "w", encoding="big5") as f:
		
		f.write("id,label\n")
		for i in range(len(result)):
			predict = np.argmax(result[i])
			f.write(repr(i) + "," + repr(predict) + "\n")

def main():
	
	print("read test data...")
	data, data_len = read_file(argv[1])

	print("reshape test data...")
	data = data / 255
	data = data.reshape(data.shape[0], 48, 48, 1)

	print("load model...")
	model = load_model(argv[3])

	print("predict...")
	result = model.predict(data, batch_size = 100, verbose = 1)

	print("output result...")
	write_file(argv[2], result)

if __name__ == "__main__":
	main()