import jpype
import csv 
import os
	
# Crea il file csv da dare in input al tool Mallet (con lo stemming).
#
# parametri:
#	input_file: nome del file csv da cui leggere, deve contenere i campi:
#			- 'PostId' - 'Body' stringa che contiene il corpo 
#			- output_file: nome del file csv sul quale scrivere, il file conterra' i campi:
#			- 'PostId' - 'Corpus' contenente 'Body' 
#			 dove a tutte le parole e' stata estratta la radice con l'algoritmo di Porter (tool Snowball)
def dataset_mallet_stem(input_file, output_file):
	jpype.startJVM("/usr/lib/jvm/java-7-openjdk-amd64/jre/lib/amd64/server/libjvm.so", "-ea", "-Djava.class.path="+os.path.abspath("."))
	
	Snowball = jpype.JClass("Snowball")
	
	stemmer = Snowball()
	dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';') # DELIMITER
	
	head = dict_reader.fieldnames
	f = ['PostId', 'Corpus']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f) # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	
	count = 0
	total = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		corpus = row['Body']	
		try:
			corpus = corpus.decode('unicode_escape').encode('ascii','ignore')
			r['Corpus'] = stemmer.extract_stem_corpus(corpus)
			count += 1
		except UnicodeDecodeError:
			try:
				corpus = unicode(corpus).encode('ascii', 'ignore')
				r['Corpus'] = stemmer.extract_stem_corpus(corpus)
				count += 1
			except Exception:
				corpus = unicode(corpus,errors='ignore')
				r['Corpus'] = stemmer.extract_stem_corpus(corpus)
				count += 1
			
		dict_writer.writerow(r)
		total += 1
		print count
	
	jpype.shutdownJVM()
	print "Initial posts ", total
	print 'Post processed: ', count
	return 'Done'
