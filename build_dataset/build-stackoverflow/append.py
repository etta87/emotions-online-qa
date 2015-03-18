import csv


#script che effettua l'operazione di append tra due file csv aventi la stessa struttura
#input: - file_1: primo file da considerare
#       - file_2: secondo file da considerare
#output:- output_file: file che concatena file_1 e file_2

def append(file_1, file_2, output_file):
	dict_reader_1 = csv.DictReader(open(file_name_1, 'r'), delimiter=';') # DELIMITER
	dict_reader_2 = csv.DictReader(open(file_name_2, 'r'), delimiter=';') # DELIMITER

	head = dict_reader_1.fieldnames

	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=head) # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in head)) #Scrive gli header
	
	count1=0
	for row_1 in dict_reader_1:
		dict_writer.writerow(row_1)
		count1=count1+1

	count2=0
	for row_2 in dict_reader_2:
		dict_writer.writerow(row_2)
		count2=count2+1
	
	tot=count1+count2
	print 'Total first file', count1
	print 'Total second file', count2
	print 'Total posts processed',tot
	print 'Done'

	return 'Done'



#script che effettua l'operazione di differenza tra due file csv
#input: - file_1: primo file da considerare
#       - file_2: secondo file da considerare
#output:- output_file: file che effettua l'operazione di  file_1-file_2

def difference_two_files(first_file, second_file, output_file):
	dict_reader = csv.DictReader(open(first_file, 'r'), delimiter=';')
	list_first_file=[]
	for row in dict_reader:
		list_first_file.append(row['PostId'])
	
	dict_reader2= csv.DictReader(open(second_file, 'r'), delimiter=';')

	head = dict_reader2.fieldnames
      
        dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=head) # DELIMITER
        dict_writer.writerow(dict((fn,fn) for fn in head)) #Scrive gli heade

	cont=1
	conta_scritti=0
	for row2 in dict_reader2:
		if row2['PostId'] not in lista1:
			dict_writer.writerow(row2)
			conta_scritti+=1
		cont+=1

	print 'Done'
	print 'Post totali : ', cont
	print 'Post del file di output : ',conta_scritti 
	return 'Done'
                	
