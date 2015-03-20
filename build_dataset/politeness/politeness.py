import csv
import string
import jpype
import os
import nltk
from model import score

#body_test = "The worldwide diffusion of social media has profoundly changed the way we communicate and access information. Increasingly, people try to solve domain-specific problems through interaction on social online Question and Answer (Q&A) sites. The enormous success of Stack Overflow, a community of 2.9 million programmers asking and providing answers about code development, attests this increasing trend. One of the biggest drawbacks of communication through social media is to appropriately convey sentiment through text. While display rules for emotions exist and are widely accepted for traditional face-to-face interaction, people might not be prepared for effectively dealing with the barriers of social media to non-verbal communication. Though, emotions matter, especially in the context of online Q&A communities where social reputation is a key factor for successful knowledge sharing. As a consequence, the design of systems and mechanisms for fostering emotional awareness in computer-mediated communication is becoming an important technical and social challenge for research in computer-supported collaborative work and social computing."


# Calcola il valore di politeness per il testo che si vuole
# analizzare.
#
# parametri:
#	text: testo che si vuole analizzare
#
# output:
#	restituisce una stringa con il risultato della fasei parser applicata sul testo di input
def get_parser(text):
	parsing_text = parser_o.parsing(text)
	return parsing_text


#Script che divide il testo di input in frasi
#parametri:
#	text: testo che si vuole analizzare
#
#output:
#	restituisce l'elenco delle frasi che costituiscono il testo di input 

def get_sentences(text=''):
    #nltk.download('punkt')    #da abilitare solo alla prima esecuzione
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentences = tokenizer.tokenize(text)
    
    return sentences


# JVM utilities
def start_JVM(path_libjvm='/usr/lib/jvm/java-7-openjdk-amd64/jre/lib/amd64/server/libjvm.so'):
	jpype.startJVM(path_libjvm, "-ea", "-Djava.class.path="+os.path.abspath("."))

def stop_JVM():
	jpype.shutdownJVM()
###############


# Calcola i valori di politeness per ogni testo contenuto 
# nel file di input.
#
# parametri:
#	file_name: nome del file csv contenente i testi da analizzare, deve contenere almeno:
#			- 'PostId'
#			- il campo con il testo da analizzare
#	output_file: nome del file csv su cui scrivere i risultati, conterra' i campi:
#			- 'PostId'
#			- 'Polite' espresso come valore nell'intervallo [0,1], conterra' valore
#				'0' se il calcolo non va a buon fine
#			- 'Impolite' espresso come valore nell'intervallo [0,1] (precisamente 1-polite), conterra' valore
#				'0' se il calcolo non va a buon fine
#	text_field: nome del campo che contiene il testo che si vuole analizzare
def politeness(file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';')
	
	f = ['PostId', 'Polite', 'Impolite']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	total = 0
	count = 0
	ski= 0
	count_ok=0
	skipped_ecc = 0
	print 'New' 
	for row in dict_reader:
		total += 1
		print total
		print 'Post esaminato : ', row['PostId']
		text = row['Body']
		print 'lunghezza testo:',len(text)
		if (len(text)>1):
			try:
				r = {}
				r['PostId'] = row['PostId']
				r['Polite'] = str('0')
				r['Impolite'] = str('0')   
			
				#calcolare le frasi e per ogni frase chiama parsing
				sentences = get_sentences(text)
				dictionary = {}
				dictionary['text']=text
				listasentences=[]
				listaparselem=[]
			
				for sentence in sentences:
					listasentences.append(sentence)	
					array_parser = get_parser(sentence)
					print 'fine parser'
					listaparselem_parz=[] 
					for el_pars_p in array_parser:
						listaparselem_parz.append(el_pars_p)
					
					listaparselem.append(listaparselem_parz)
				

				dictionary['sentences']=listasentences
				dictionary['parses']=listaparselem
				#print dictionary
				print 'calcolo probs, postid:',row['PostId'] 		
				probs = score(dictionary)

				r['Polite'] = probs['polite']
				r['Impolite'] = probs['impolite']
				#dict_writer.writerow(r)
				count_ok += 1
			except Exception:
				print 'Eccezione'
				skipped_ecc+=1
				r['PostId']= row['PostId']
				r['Polite']= str('0')
				r['Impolite']=str('0')		
				dict_writer.writerow(r)
				continue		
		else:
			r['PostId'] = row['PostId']
			r['Polite'] = str('0')
			r['Impolite'] = str('0')
			ski += 1
			
		dict_writer.writerow(r)
		count+=1

	stop_JVM()
	print "Initial posts ", total
	print "Post processed ", count
	print 'Ski vuota', ski
	print "Skipped_ecc: ", skipped_ecc
	print "Gest_ok", count_ok
	return 'Done'




def politeness_test():
	#dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';')
	
	#f = ['PostId', 'Polite', 'Impolite']
	
	#dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	#dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	total = 0
	count = 0
	skipped = 0
	#for row in dict_reader:
	total += 1
	#text = row['Body']
	#text = 'Have you found the answer for your question? If yes would you please share it?'
	#text = "Sorry :) I dont want to hack the system!! :) is there another way?"
        text = "What are you trying to do?  Why can't you just store the \"Range\"? "
        #text = "This was supposed to have been moved to &lt;url&gt; per the cfd. why wasn't it moved?"

	if (text!=' '):
		#r = {}
		#r['PostId'] = row['PostId']
		#r['Polite'] = str('None')
		#r['Impolite'] = str('None')   
			#calcolare le frasi e per ogni frase chiama parsing
		sentences = get_sentences(text)
		print sentences
		dictionary = {}
		dictionary['text']=text
		listasentences=[]
		listaparselem_parz=[]
		listaparselem=[]
	
		
		for sentence in sentences:
			print sentence
			listasentences.append(sentence)		
			array_parser = get_parser(sentence)
			
			for el_pars_p in array_parser:
				listaparselem_parz.append(el_pars_p)
				
			listaparselem.append(listaparselem_parz)
			

		dictionary['sentences']=listasentences
		dictionary['parses']=listaparselem
		
			
		probs = score(dictionary)

		print 'Polite : ', probs['polite']
		print 'Impolite: ',probs['impolite']
		count += 1
		
		
	else:
		print 'ERRORE'
		#r = {}
		#r['PostId'] = row['PostId']
		#r['Polite'] = str('0')
		#r['Impolite'] = str('0') 

		
			
	#dict_writer.writerow(r)

	stop_JVM()
	print "Initial posts ", total
	print "Post processed ", count
	print "Skipped: ", skipped
	return 'Done'


# Avvia la JVM nel momento in cui viene importato il file come libreria, si puo' commentare tale riga e avviarla solo quando necessario
start_JVM()

# P = carica la classe PolitenessParserTesi
P = jpype.JClass('ParserPol')

# parser_o = oggetto della classe Politeness
parser_o = P()
