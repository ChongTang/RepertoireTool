#!/usr/bin/python
#file_dist.py: file_distribution involved in both porting 

import sys
import os
import csv
import re
import math
import operator

import clone
import config

file_rank_hash = {}
file_all_change_hash = {}
total_port = 0
total_change = 0

FREEBSD_RELEASE_DATES = "../../bsd_data/release_dates/freebsd.csv"
OPENBSD_RELEASE_DATES = "../../bsd_data/release_dates/openbsd.csv"
NETBSD_RELEASE_DATES = "../../bsd_data/release_dates/netbsd.csv"

#=====================================================================#
class fileStat:
	def __init__(self,rev,pcent_1,pcent_2,union,intersect,union_abs,total):
		self.rev = rev
		self.pcent_port1 = pcent_1
		self.pcent_port2 = pcent_2
		self.union = union
		self.intersect = intersect
		self.union_abs = union_abs
		self.total = total
#=====================================================================#

def cal_file_rank(rev,aset,pset1,pset2):

	global file_rank_hash
	global total_port
	global total_change

	file_union = pset1.union(pset2)
	total_port += len(file_union)
	total_change += len(aset)

	for i in file_union:
		diff_line_num = i[0]
		src_file_name = i[1]
#		temp_name = src_file_name.split("_")
#		src_dir = temp_name[0] + "/" + temp_name[1] + "/" + temp_name[2]
		if (file_rank_hash.has_key(src_file_name) == 0):
			file_rank_hash[src_file_name] = 0

		file_rank_hash[src_file_name] += 1
	
#=====================================================================#
def walk_dir(directory):

	global file_all_change_hash

	print "directory name = " + directory
	
	for fileName in os.listdir(directory):
		if (config.DEBUG == 1):
			print fileName
		fname = directory + "/" + fileName
		try:
			csvfile = open(fname,"r")
			reader = csv.reader(csvfile,delimiter=',')
			for row in reader:
				diff_line_num = row[0].strip()
				if diff_line_num.startswith("src"):
					pass
				else:
					srcFileName = row[2]
					if(file_all_change_hash.has_key(srcFileName) == 0):
						file_all_change_hash[srcFileName] = 0
					file_all_change_hash[srcFileName] += 1
			
					f, extn = os.path.splitext(fileName)
					year = config.release_dates[f]
					config.src_file_hash[(f,year,diff_line_num)] = srcFileName
					if (config.all_srcFile_by_rev.has_key(year) == 0):
						config.all_srcFile_by_rev[year] = []
					config.all_srcFile_by_rev[year].append((diff_line_num,srcFileName))
	
		
		except IOError as e:
			print fileName + " doesnot exist"
#print config.all_srcFile_by_rev
#=====================================================================#
#=====================================================================#

if (len(sys.argv) < 5):
	 print "Usage: filedist.py input1.txt input2.txt conv_dir output"
	 print "inputN.txt is the output from repertoire"
	 print "conv_dir contains all files that is generated by parsing diff files: usually in the form of conv_dev"
	 print "format: diff_line_no | source_file_line_no| source_file_name"
	 print "output is the output file"
	 sys.exit(2)

in_file1 = sys.argv[1]
in_file2 = sys.argv[2]
dir_name = sys.argv[3]
conv_file = sys.argv[4] 


print "Input Files : " + in_file1 + "," + in_file2
print "Output Files : " + conv_file 

outf = open(conv_file,"w")

config.hash_release_dates(FREEBSD_RELEASE_DATES)
config.hash_release_dates(OPENBSD_RELEASE_DATES)
config.hash_release_dates(NETBSD_RELEASE_DATES)


walk_dir(dir_name)
clone.process_rep_output(in_file1,1)
clone.process_rep_output(in_file2,2)

printLine = "source files , all edits, ported edits , non-ported edits\n"
outf.write(printLine)

if (config.DEBUG > 0):
	print "======= config.all_srcFile_by_rev ==========="
	print config.all_srcFile_by_rev
	print " ===== config.clone_by_rev1 =========="
	print config.clone_by_rev1
	print " ===== config.clone_by_rev2 =========="
	print config.clone_by_rev2


for key in config.clone_by_rev1.iterkeys():
#	print key
	clone_set1 = set()
	clone_set2 = set()
	ported_files = set()
	all_set = set()

	clone_set1 = set(config.clone_by_rev1[key])

	if (config.clone_by_rev2.has_key(key)):
		clone_set2 = set(config.clone_by_rev2[key])
		
	all_set = set(config.all_srcFile_by_rev[key])
	
	cal_file_rank(key,all_set,clone_set1,clone_set2)
	
file_rank_ported = sorted(file_rank_hash.iteritems())
file_rank_all = sorted(file_all_change_hash.iteritems())

for key in file_rank_hash:
	if(file_all_change_hash.has_key(key) != 0):
		all_edits = file_all_change_hash[key]
		ported_edits = file_rank_hash[key]
		non_ported_edits = int(all_edits) - int(ported_edits) 
#		print str(key) + "," + str(all_edits) + "," + str(ported_edits) + "," + str(non_ported_edits)
		outf.write(str(key) + "," + str(all_edits) + "," + str(ported_edits) + "," + str(non_ported_edits) + "\n")
