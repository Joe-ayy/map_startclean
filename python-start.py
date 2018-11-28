#!/usr/bin/env python


from gimpfu import *
import os

#delets yaml if one exsists to avoid confusion
#def delete_old_yaml(directory):
#	files=os.listdir(directory + "/")
#	for file in files:
#		if file.endswith(".yaml"):
#			os.remove(file)


#paints a circle around the park or dock location by makeing a bush and painting with it
def paint_hazard(drw,x,y):
	hazard_color = "yellow"
	hazard_radius = 27
	temp_brush = "b1"
	center = [x,y]
	og_background = pdb.gimp_context_get_background()
	og_foreground = pdb.gimp_context_get_foreground()
	pdb.gimp_context_set_foreground(hazard_color)
	temp_brush = pdb.gimp_brush_new(temp_brush)
	pdb.gimp_brush_set_shape(temp_brush, 0)
	pdb.gimp_brush_set_radius(temp_brush, 1000)
	pdb.gimp_context_set_brush_size(hazard_radius)
	pdb.gimp_brush_set_hardness(temp_brush, 100)
	pdb.gimp_context_set_opacity(50)
	pdb.gimp_pencil(drw, 2, center)
	pdb.gimp_context_set_background(og_background)
	pdb.gimp_context_set_foreground(og_foreground)
	pdb.gimp_brush_delete(temp_brush)
	pdb.gimp_context_set_opacity(100)

	
# check to see if there is enough clearance around the park and dock if not call to mark it
def check_clearence(drw, img, start_x, start_y, side_length):
	pdb.gimp_selection_none(img)
	pdb.gimp_image_select_ellipse(img, 0, start_x - 12, start_y - 13 , side_length - 1, side_length - 1)
	ratio, junk1, junk2, junk3, junk4, junk5 = pdb.gimp_drawable_histogram(drw, 0, 0, 1)
	black_pixel_ratio = 1 - (ratio / 255)
	pdb.gimp_selection_none(img)
	if black_pixel_ratio > 0:
		return False
	
	else:
		return True
		


def convert_meters_to_pixels(meters, ratio):
	return meters / ratio


def parse_x_y(line, x_y_list):
	# takes in a line and returns the x,y coordinates found in it
	pos1 = line.find(' ')
	x_meters_string = line[:pos1]
	pos2 = line.find(' ', pos1 + 1)
	y_meters_string = line[pos1 + 1:pos2]
	x_y_list.append(x_meters_string)
	x_y_list.append(y_meters_string)
	return


def get_start_stop_pixels(filename, ratio, offset_list):
# takes filename of .ply the ratio and the offset points returns the park and dock list "start and stop"
	start_and_stop_list = []
	park_x_y = []
	dock_x_y = []
	file = open(filename, 'r')
	line = file.readline()
	#hard code skip the header in the file
	for x in range(0, 14):
		line = file.readline()
		
	parse_x_y(line, park_x_y)
	#strip out the last line in the file
	line_list = []
	for lines in file:
		line_list.append(lines)
		
	last_line = line_list[len(line_list) - 1]
	parse_x_y(last_line, dock_x_y)
	#convert strings to float
	park_x_meters_string = park_x_y[0]
	park_x_meters_float = float(park_x_meters_string)
	park_y_meters_string = park_x_y[1]
	park_y_meters_float = float(park_y_meters_string)
	dock_x_meters_string = dock_x_y[0]
	dock_x_meters_float = float(dock_x_meters_string)
	dock_y_meters_string = dock_x_y[1]
	dock_y_meters_float = float(dock_y_meters_string)
	
	# convert from meters to pixels
	park_x_pixels_float = convert_meters_to_pixels(park_x_meters_float, ratio)
	park_y_pixels_float = convert_meters_to_pixels(park_y_meters_float, ratio)
	dock_x_pixels_float = convert_meters_to_pixels(dock_x_meters_float, ratio)
	dock_y_pixels_float = convert_meters_to_pixels(dock_y_meters_float, ratio)
	
	#round to nearest pixel because they are ints
	park_x_pixels_int = int(round(park_x_pixels_float))
	park_y_pixels_int = int(round(park_y_pixels_float))
	dock_x_pixels_int = int(round(dock_x_pixels_float))
	dock_y_pixels_int = int(round(dock_y_pixels_float))
	
	#get actual location in pixels by added offset
	park_x_pixels_int = park_x_pixels_int + offset_list[0]
	park_y_pixels_int = park_y_pixels_int + offset_list[1]
	dock_x_pixels_int = dock_x_pixels_int + offset_list[0]
	dock_y_pixels_int = dock_y_pixels_int + offset_list[1]
	
	# get actual location in meters for the file name
	park_x_meters_float = park_x_meters_float + offset_list[0] * ratio
	park_y_meters_float = park_y_meters_float + offset_list[1] * ratio
	dock_x_meters_float = dock_x_meters_float + offset_list[0] * ratio
	dock_y_meters_float = dock_y_meters_float + offset_list[1] * ratio
	
	# build the list 
	start_and_stop_list.append(park_x_pixels_int)
	start_and_stop_list.append(park_y_pixels_int)
	start_and_stop_list.append(dock_x_pixels_int)
	start_and_stop_list.append(dock_y_pixels_int)
	start_and_stop_list.append(park_x_meters_float)
	start_and_stop_list.append(park_y_meters_float)
	start_and_stop_list.append(dock_x_meters_float)
	start_and_stop_list.append(dock_y_meters_float)
	
	return start_and_stop_list


def get_pixel_ratio(file_name):
# take in file name and return the meters/pixels ratio as a float
	file = open(file_name, 'r')
	line = file.readline()
	for x in range(0,3):
		line = file.readline()
		
	delimiter_location1 = line.find(' ')
	delimiter_location2 = line.find('\n')
	ratio_string = line[delimiter_location1 + 1: delimiter_location2]
	ratio_float = float(ratio_string)
	file.close()
	return ratio_float

def get_pixel_offset(file_name):
# takes file name and returns the offset points in a list
	#parse out the needed info
	offset_list = []
	file = open(file_name, 'r')
	line = file.readline()
	for x in range(0, 5):
		line = file.readline()
		
	pos1 = line.find(": ")
	pos2 = line.find(' ', pos1 + 2)
	pos3 = line.find('\n', pos2 + 1)
	x_offset_string = line[pos1 + 2: pos2]
	y_offset_string = line[pos2 + 1: pos3]
	x_offset_int = int(x_offset_string)
	y_offset_int = int(y_offset_string)
	offset_list.append(x_offset_int)
	offset_list.append(y_offset_int)
	file.close()
	return offset_list

def parse_files(dir_path):
#takes the path to the directory and returns the park and dock list
	# look for .info and .ply file in the directory
	info_file_name = ""
	ply_filename = ""
	for file in os.listdir(dir_path):
		if file.endswith(".ply"):
			ply_filename = file
		if file.endswith(".info"):
			info_file_name = file

	info_file_name = dir_path + "/" + info_file_name
	ply_filename = dir_path + "/" + ply_filename
	ratio = get_pixel_ratio(info_file_name)
	x_y_offset = get_pixel_offset(info_file_name)
	start_stop_pixel_list = get_start_stop_pixels(ply_filename, ratio, x_y_offset)
	return start_stop_pixel_list
   
def draw_square(drw,x,y,color):
#take in center x,y and draw a 9 x  9 square around it
	for z in range(0,4):
		for w in range(0,4):
			pdb.gimp_drawable_set_pixel(drw,x + z,y + w,3,color)
			pdb.gimp_drawable_set_pixel(drw,x - z,y - w,3,color)
			pdb.gimp_drawable_set_pixel(drw,x + z,y - w,3,color)
			pdb.gimp_drawable_set_pixel(drw,x - z,y + w,3,color)
	

def python_start(img,drw):
	# init colors and image
	park_color = [204,0,0]
	dock_color = [0,0,204]
	img = gimp.image_list()[0]
	#get the full path of the image the user is currently working on
	file_path = pdb.gimp_image_get_filename(gimp.image_list()[0])
	clearance_diameter = 27
	yaml_lines = ["image: ","resolution: 0.050000\n","origin: [0.000000, 0.000000, 0.000000]\n","negate: 0\n","occupied_thresh: 0.65\n","free_thresh: 0.196\n", "\n"]
	
	# in gimp 0,0 is in top left but in fleet it is bottom left so the image is flipped to correspond with fleet
	# img is converted to rgb to color the spots
	pdb.gimp_image_flip(img, 1)
	pdb.gimp_image_convert_rgb(img)
	drw = pdb.gimp_image_get_active_drawable(img)
	
	#parse the file directory name from the path returned from file_path
	d1 = file_path.find("\\Documents\\")
	d2 = file_path.find('\\',d1 + 11)
	dir_path = file_path[:d2]
	gimp_filename = file_path[d1 + 11:d2] 
	dir_path = dir_path.replace('\\','/')
	
	
	#call to create the xy list of points and then draw those
	x_y_list = parse_files(dir_path)
	park_spot_clean_flag = check_clearence(drw,img,x_y_list[0],x_y_list[1],clearance_diameter)
	dock_spot_clear_flag = check_clearence(drw,img,x_y_list[2],x_y_list[3],clearance_diameter)
	
	if park_spot_clean_flag == False:
		paint_hazard(drw,x_y_list[0],x_y_list[1])
		
	if dock_spot_clear_flag == False:
		paint_hazard(drw,x_y_list[2],x_y_list[3])
	
	draw_square(drw,x_y_list[0],x_y_list[1],park_color)
	draw_square(drw,x_y_list[2],x_y_list[3],dock_color)
	
	#update the drawable and the image so that it reflects changes
	drw.update(x_y_list[0] - 3,x_y_list[1] - 3,7,7)
	drw.update(x_y_list[2] - 3,x_y_list[3] - 3,7,7)
	pdb.gimp_image_flip(img, 1)
	gimp.displays_flush()

	###No longer need to create text box layer because file is being saved with the coordinates in the name
	###txt_layer_string = "Park (meters): X-> " + '{0:.2f}'.format(x_y_list[4]) + " Y-> " + '{0:.2f}'.format(x_y_list[5]) + "\nDock (meters): X-> " + '{0:.2f}'.format(x_y_list[6]) + " Y-> " + '{0:.2f}'.format(x_y_list[7])
	##txt_layer = pdb.gimp_text_layer_new(img,txt_layer_string,"Sans",15,0)
	##img.add_layer(txt_layer,0)
	##pdb.gimp_text_layer_set_color(txt_layer,"BLACK")
	##pdb.gimp_text_layer_set_antialias(txt_layer,FALSE)
	
	# Format the x and y coordinates to 2 decimal places (the number you can see in fleet)
	# Also specify the values are in meters (also specified in fleet)
	# save a copy of the image .xcf with the points in the name
	short_gimp_filename = gimp_filename + "_P_" + '{0:.2f}'.format(x_y_list[4]) + "_" + '{0:.2f}'.format(x_y_list[5]) + "_D_" + '{0:.2f}'.format(x_y_list[6]) + "_" + '{0:.2f}'.format(x_y_list[7])
	gimp_filename = dir_path + "/" + short_gimp_filename + ".xcf"
	pdb.gimp_image_set_filename(img, gimp_filename)
	#next line is old way of saving .xcf file, 
	#pdb.gimp_file_save(img,drw,gimp_filename,"test.xcf")
	
	## create and save .yaml file, but first remove any yaml just in case wrong points were given
	#delete_old_yaml(dir_path)
	yaml_filename = gimp_filename.replace('.xcf','.yaml')
	yaml_file = open(yaml_filename, "w")
	yaml_lines[0] = yaml_lines[0] + short_gimp_filename + ".pgm\n"
	for line in yaml_lines:
		yaml_file.write(line)
		
	yaml_file.close()
	
	return 
   
register(
		"python_fu_start",
		"Start editing mapping",
		"Start editing the map",
		"Jair Pedroza",
		"JP",
		"2018",
		"<Image>/Tools/Transform Tools/_Start Clean-up",
		"RGB*, GRAY*",
		[],
		[],
		python_start)

main()