import io
import sys

from struct import pack, unpack, calcsize
#

import numpy as np
import matplotlib.pyplot as plt
import seaborn

#I <---> unsigned 32 bit int
struct_format = 'IdI'
struct_format_uint32  = 'I'
struct_format_doses   = 'd'
struct_format_indices = 'I'

y_slice = 70

def calculate_x_indices():
	x_bins = np.linspace(-26, 24, 126)
	low = np.min(np.where(x_bins > -2 ))
	high = np.max(np.where(x_bins < 7  ))
	print(x_bins[low], x_bins[high])
	return (low, high)

def slice_indices(lower_edge, upper_edge, lower_bound, upper_bound):
	return None

def calculate_z_indices():
	z_bins = np.linspace(-25, 25, 126)
	low = np.min(np.where(z_bins > -1 ))
	high = np.max(np.where(z_bins < 4  ))
	print(z_bins[low], z_bins[high])
	return (low, high)

def main():
	#so, now have the correct indices to slice out the parameters
	low_x, high_x  = calculate_x_indices()
	low_z, high_z  = calculate_z_indices()
	#
	read_count   = calcsize(struct_format_uint32)
	read_dose    = calcsize(struct_format_doses)
	read_indices = calcsize(struct_format_indices) 

	with open('beamlet1.dat', 'rb') as f:
		data = f.read(read_count)
		count, = unpack(struct_format_uint32, data)
		print(count)
		while True:
			list_doses   = []
			list_indices = []
			for i in range(count):
				data = f.read(read_dose)
				s, = unpack(struct_format_doses, data)
				list_doses.append(s)
			#print(s)
			for i in range(count):
				data = f.read(read_indices)
				s, = unpack(struct_format_indices, data)
				list_indices.append(s)
			#print(s)

			dose_grid = np.zeros((125,125,125))
			for dose, index in zip(list_doses, list_indices):
				dose_grid[np.unravel_index(index, dims=(125,125,125))] = dose
			
			print("argmax = ", np.argmax(dose_grid), np.unravel_index(np.argmax(dose_grid), dose_grid.shape))
			plt.figure()
			dose_max_slice = np.max(dose_grid[:, y_slice, :])
			plt.imshow(dose_grid[:, y_slice, :] / dose_max_slice, cmap=plt.get_cmap('cool'))
			ax = plt.gca()
			ax.grid(False)
			plt.show()

			sub_dose_grid = np.array(dose_grid[low_x:high_x+1, :, low_z:high_z+1])
			print("shape:      ", sub_dose_grid.shape)
			print("# elements: ", len(np.nonzero(sub_dose_grid.ravel())[0]))
			print("elements:   ", np.nonzero(sub_dose_grid.ravel()))


			elements = len(np.nonzero(sub_dose_grid.ravel())[0])
			non_zero_index = np.nonzero(sub_dose_grid.ravel())[0]
			sub_dose_grid_ravel = sub_dose_grid.ravel()
			with open('test_file_1.dat', 'wb') as out_file:
				out_file.write(pack('I', elements))
				for index_value in non_zero_index:
					out_file.write(pack('d', sub_dose_grid_ravel[index_value]))
				for index_value in non_zero_index:
					out_file.write(pack('I', index_value))

			with open('test_file_ascii_1.dat', 'w') as ascii_file:
				ascii_file.write(str(elements) + " ")
				for index_value in non_zero_index:
					ascii_file.write(str(sub_dose_grid_ravel[index_value]) + " ")
				for index_value in non_zero_index:
					ascii_file.write(str(index_value) + " ")

			# with open('test_file_full_ascii_1.dat', 'w') as ascii_file:
			# 	ascii_file.write(str(elements) + " ")
			# 	for index_value in non_zero_index:
			# 		ascii_file.write(str(sub_dose_grid_ravel[index_value]) + " ")
			# 	for index_value in non_zero_index:
			# 		ascii_file.write(str(index_value) + " ")

			#print(125**3)
			print("converting to numpy array")
			doses = np.array(list_doses)
			print(np.mean(doses))
			print(np.std(doses))
			print("done calculation")
			print(np.unravel_index(list_indices, (125,125,125)))

			plt.figure()
			ax = plt.subplot(111)
			plt.hist(doses, bins=1000)
			ax.set_yscale("log", nonposy='clip')
			plt.show()
			sys.exit(0)
			

			if not data:
				break
			s = unpack(struct_format, data)
			print(s)


if __name__ == '__main__':
	main()