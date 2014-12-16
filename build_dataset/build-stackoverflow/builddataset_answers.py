
import MySQLdb
import sqlite3
import csv
import os
import datetime
import time
import re
import string
import operator
import threading
from HTMLParser import HTMLParser
from builddataset import text_length,clean_body,link_count,del_code,execute_param_query

# commenti di tutti gli utenti ad una risposta PostId prima della data di accettazione Date
def getCommentsBeforeAccDate(postid, vote_date):
	return "SELECT Id, text FROM Comments WHERE creationDate < \'" + vote_date + "\' AND PostId = " + postid

# commenti di tutti gli utenti ad una risposta PostId
def getComments(postid):
	return "SELECT Id, text FROM Comments WHERE PostId = " + postid


# edits di tutti gli utenti ad una risposta PostId prima di una certa data Date */

def getBodyEditsBeforeAccDate(postid, vote_date):
	return "SELECT Id FROM PostHistory WHERE posthistorytypeid = 5 AND creationDate < \'" + vote_date + "\' AND PostId = " + postid


# edits di tutti gli utenti ad una risposta PostId
def getBodyEdits(postid):
	return "SELECT Id FROM PostHistory WHERE posthistorytypeid = 5 AND PostId = " + postid


# Estrae il numero di upvotes, prima di una certa data Date, su una risposta ansid  */
def getAnswUpVotesBeforeAccDate(ansid, date):
	return "SELECT u_postID as AnswerID, count(u_voteID) as UpVotesAnsw FROM answerupvotes_mv WHERE u_postID = " + ansid + " AND 

uts_voteDate < date(\'" + date + "\')"
	
# Estrae il numero di downvotes, prima di una certa data (@Date), ottenuti dalle risposte postate da un certo utente (@User) */
def getAnswDownVotesBeforeAccDate(ansid, date):
	return "SELECT d_postID as AnswerID, count(d_voteID) as AnswerDownvotesScore FROM answerdownvotes_mv WHERE d_postID = " + ansid + " 

AND dts_voteDate < date(\'" + date + "\')"


# Estrae il numero di upvotes, su una risposta ansid */
def getAnswUpVotes(ansid):
	return "SELECT u_postID as AnswerID, count(u_voteID) as UpVotesAnsw FROM answerupvotes_mv WHERE u_postID = " + ansid 
	
# Estrae il numero di downvotes, su una risposta ansid */
def getAnswDownVotes(ansid):
	return "SELECT d_postID as AnswerID, count(d_voteID) as AnswerDownvotesScore FROM answerdownvotes_mv WHERE d_postID = " + ansid 

# Esegue la query sul database (mysql), passati in input, e ritorna il result set
#
# parametri:
#	database: stringa con il nome del database che si vuole interrogare (es.: 'stackoverflow')
#	query: stringa con la query (in sql) da eseguire sul database
#
# output:
#	result set 
#def execute_param_query(database, query):
#	conn = MySQLdb.connect(host="127.0.0.1", port=3307, user='root',passwd='ettadb',db=database)
#	c = conn.cursor()
#	c.execute(query)
#	c.fetchall()
#	return c


#provvisoria
def cutfile(inputfile,output_file):

	dict_reader = csv.DictReader(open(inputfile, 'r'), delimiter=';')
	head = dict_reader.fieldnames
	
	dict_writer = csv.DictWriter(open(output_file, 'w'),delimiter=';', fieldnames=head)
	dict_writer.writerow(dict((fn,fn) for fn in head))
	count=0
	for row in dict_reader:
		#if count > 12326500 :
		if count < 100:
			dict_writer.writerow(row)
		count += 1

	return 'done'

#provvisoria
def merge2(file_name_input, file_name_metric, output_file):
	
	f1=open(file_name_input, 'r')
	f2=open(file_name_metric, 'r')
	dict_reader_1 = csv.DictReader(f1, delimiter=';')
	dict_reader_2 = csv.DictReader(f2, delimiter=';')

	head = dict_reader_1.fieldnames
	head_2 = dict_reader_2.fieldnames
	for h in head_2:
		if h != 'PostId':
			head.append(h)
	f2.close()
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=head)
	dict_writer.writerow(dict((fn,fn) for fn in head))
	c=0
	for row_1 in dict_reader_1:
		f2= open(file_name_metric, 'r')
		dict_reader_2 = csv.DictReader(f2, delimiter=';')
		for row_2 in dict_reader_2:
			if row_2['PostId'] == row_1['PostId']:
				for h in head_2:
					if h != 'PostId':
						row_1[h] = row_2[h]
				c+=1
				dict_writer.writerow(row_1)
				f2.close()
				break
	print 'Post processed: ', c
	return 'Done'

 #provvisoria
def clean_topic(file_name_input, output_file):
	dict_reader_1 = csv.DictReader(open(file_name_input, 'r'), delimiter=';')
	head = dict_reader_1.fieldnames
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=head)
	dict_writer.writerow(dict((fn,fn) for fn in head))
	c=0
	c1=0
	for row_1 in dict_reader_1:
		c+=1
		if row_1['PostId']!= '':
			c1+=1
			dict_writer.writerow(row_1)
	print 'Post writed: ', c1
	print 'Post processed: ', c
	return 'Done' 	

#provvisoria

def ins_topicQdb( input_file, output_sql_file):

	dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';')
	head = dict_reader.fieldnames

	out_file = open(output_sql_file, 'w')
	c=0
	for row in dict_reader:
		postQ = str(row['PostId'])
		topicQ = str(row['TopicQ'])
		query="INSERT INTO topic_questions_mv (t_postID, t_topic) VALUES ("+ postQ +"," + topicQ + ");"
		out_file.write(query+"\n")
		c+=1
	out_file.close()
	print 'Create!'
	return 'Done'

# Definiamo, per ogni risposta, i commenti che tutti gli utenti hanno 
# aggiunto prima della data di accettazione di una risposta alla discussione. Nel caso non ci fosse
# una risposta accettata vengono considerati tutti i commenti che tutti hanno 
# aggiunto alla risposta in questione.
# La funzione calcola il numero ed il testo di tali commenti.
#
# parametri:
#	database: nome del database da interrogare
#	output_file: nome del file csv su cui scrivere i risultati, conterra' i campi:
#			- 'PostId'
#			- 'NumberOfUsersComments' numero di commenti
#			- 'TextOfUsersComments' testo dei commenti trovati
def allcommentsonanswers_dataset(database, inputfile, output_file):
	
	dict_reader = csv.DictReader(open(inputfile, 'r'),delimiter=';')
	head = dict_reader.fieldnames
	
	# Inizializza il csv da scrivere
	fieldnames = ['PostId' , 'NumberOfUsersComments', 'TextOfUsersComments']
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=fieldnames) # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in fieldnames)) #Scrive gli header

	# Query per ottenere tutte le domande con la relativa data di accettazione della risposta nel caso ci sia
	#query_answers_questions_voteDate = "select * from (select a.a_postid as ansid, q.postId, q.ts_voteDate from answers_mv a inner join 

questwithacceptedanswer_mv q on a.a_QuestionId=q.postid union select a.a_postid as ansid, q.q_postID as postId, null from answers_mv a inner 

join questions_mv q on a.a_QuestionId=q.q_postid) questions group by ansid, postId"
	#answers_questions = execute_param_query(database, query_answers_questions_voteDate)
	
	
	for row in dict_reader:
		# row[0] = answId
		# row[1] = postId
		# row[2] = ts_voteDate

		comments = []
		w_row = {}
		w_row['PostId'] = row['PostId']
		if str(row['Date']) != 'None':
			comments = execute_param_query(database, getCommentsBeforeAccDate(str(row['PostId']), str(row['Date'])))
		else:
			comments = execute_param_query(database, getComments(str(row['PostId'])))

		
		w_row['NumberOfUsersComments'] = str(comments.rowcount)
		w_row['TextOfUsersComments'] = str()
		for comm in comments:
			# comm[0] = c_Id
			# comm[1] = c_text
			w_row['TextOfUsersComments'] += ' ' + comm[1]
			#w_row['TextOfUsersComments'] += ' ' + unicode(comm[1], errors='ignore')
		
		dict_writer.writerow(w_row)




# Funzione che calcola, per ogni risposta, il numero di edits effettuati sulla risposta  
# prima della data di accettazione di una risposta alla discussione. Nel caso non ci fosse
# una risposta accettata vengono considerati tutti gli edit effettuati.
# La funzione calcola il numero ed il numero di tali edit.
#
# parametri:
#	database: nome del database da interrogare
#	output_file: nome del file csv su cui scrivere i risultati, conterra' i campi:
#			- 'PostId'
#			- 'NumberOfEdits' numero di edit
#			 

def n_edits(database, inputfile, output_file):
	
	dict_reader = csv.DictReader(open(inputfile, 'r'), delimiter=';')
	head = dict_reader.fieldnames
	# Inizializza il csv da scrivere
	fieldnames = ['PostId' , 'NumberOfEdits']
	count=0
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=fieldnames) # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in fieldnames)) #Scrive gli header

	# Query per ottenere tutte le domande con la relativa data di accettazione della risposta nel caso ci sia
	#query_answers_questions_voteaccDate = "select * from (select a.a_postid as ansid, q.postId, q.ts_voteDate from answers_mv a inner 

join questwithacceptedanswer_mv q on a.a_QuestionId=q.postid union select a.a_postid as ansid, q.q_postID as postId, null from answers_mv a 

inner join questions_mv q on a.a_QuestionId=q.q_postid) questions group by ansid, postId"
	#answers_questions = execute_param_query(database, query_answers_questions_voteaccDate)
	
	
	for row in dict_reader:
		# row[0] = answId
		# row[1] = postId
		# row[2] = ts_voteDate

		edits = []
		w_row = {}
		w_row['PostId'] = row['PostId']
		if str(row['Date']) != 'None':
			bodyedits  = execute_param_query(database, getBodyEditsBeforeAccDate(str(row['PostId']), str(row['Date'])))
		else:
			
			bodyedits  = execute_param_query(database, getBodyEdits(str(row['PostId'])))

		
		w_row['NumberOfEdits'] = str(bodyedits.rowcount)
		dict_writer.writerow(w_row)
		count+=1

	print 'Processed',count
	return 'Done'


#funzione che permette di salvare in un file csv: 
#	-idrisposta
#	-idquestion
#	-data di accettazione di una risposta alla discussione idquestion

def save_date_accepted(db, output_file):
	f = ['PostId','PostQuestion', 'Date']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0

	query_answers_questions_voteaccDate = "select * from (select a.a_postid as ansid, q.postId, q.ts_voteDate from answers_mv a inner join 

	questwithacceptedanswer_mv q on a.a_QuestionId=q.postid union select a.a_postid as ansid, q.q_postID as postId, null from answers_mv a 

inner join questions_mv q on a.a_QuestionId=q.q_postid) questions group by ansid, postId"
	answers_questions = execute_param_query(db, query_answers_questions_voteaccDate)
	
	for row in answers_questions:
		# row[0] = answId
		# row[1] = postId
		# row[2] = ts_voteDate
		r = {}
		r['PostQuestion'] = row[1]
		r['PostId'] = str(row[0])
		r['Date'] = str(row[2])
		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed: ', count
	return 'Done'



# Calcola lo score delle risposte fornite in input come il numero degli up vote meno il numero di down 
# vote prima della data di accettazione di una risposta
#
# parametri:
#	db: stringa con il nome del database da cui leggere
#	file_name: nome del file csv da cui leggere, deve contenere #almeno i campi:
#			- 'PostId' : id della risposta
#			- 'Date': data di accettazione di una risposta
#
#	output_file: nome del file csv su cui scrivere i risultati, contiene i campi:
#			- 'PostId'
#			- 'AnswerScore' numero degli up vote meno il numero dei down vote della 
#				risposta prima della data di accettazione 'Date'

def scoreanswer(db,inputfile, output_file):
	dict_reader = csv.DictReader(open(inputfile, 'r'), delimiter=';')
	head = dict_reader.fieldnames

	f = ['PostId', 'AnswerScore']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		# row[0] = answId
		# row[1] = postId
		# row[2] = ts_voteDate
		r = {}
		#r['PostId'] = row[1]
		answid = row['PostId']
		date = row['Date']
		if str(date) != 'None':
			result_set6 = execute_param_query(db, getAnswUpVotesBeforeAccDate(answid, date))
			result_set7 = execute_param_query(db, getAnswDownVotesBeforeAccDate(answid, date))
		else:
			result_set6 = execute_param_query(db, getAnswUpVotes(answid))
			result_set7 = execute_param_query(db, getAnswDownVotes(answid))
			
		
		#print "end queries"
		
		for tup in result_set6:
			a_up = tup[1]
		for tup in result_set7:
			a_down = tup[1]
		
		a_score = a_up - a_down
		r['PostId']=answid
		r['AnswerScore'] = a_score

		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed: ', count
	return 'Done'


# Calcola il numero di upvote della risposta
# prima della data di accettazione di una risposta
#
# parametri:
#	db: stringa con il nome del database da cui leggere
#	file_name: nome del file csv da cui leggere, deve contenere almeno i campi:
#			- 'PostId': id della risposta
#			- 'Date': data di accettazione di una risposta alla discussione in formato '2014-01-30 21:30'
#	output_file: nome del file csv su cui scrivere i risultati, contiene i campi:
#			- 'PostId'
#			- 'AnswerUpVotes' numero degli up vote della #risposta prima della data in 'Date'
def scoreaup(db,inputfile, output_file):
	dict_reader = csv.DictReader(open(inputfile, 'r'), delimiter=';')
	head = dict_reader.fieldnames

	f = ['PostId', 'AnswerUpVotes']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		
		r = {}
		answid = row['PostId']
		date = row['Date']
		if str(date) != 'None':
			result_set6 = execute_param_query(db, getAnswUpVotesBeforeAccDate(answid, date))
		else:
			result_set6 = execute_param_query(db, getAnswUpVotes(answid))
			
		
		for tup in result_set6:
			a_up = tup[1]
		

		r['PostId']=answid
		r['AnswerUpVotes'] = a_up

		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed: ', count
	return 'Done'

# Calcola il numero dei downvote della risposta
# prima della data di accettazione di una risposta
#
# parametri:
#	db: stringa con il nome del database da cui leggere
#	file_name: nome del file csv da cui leggere, deve contenere almeno i campi:
#			- 'PostId': id della risposta
#			- 'Date': data di accettazione di una risposta alla discussione in formato '2014-01-30 21:30'
#	output_file: nome del file csv su cui scrivere i risultati, contiene i campi:
#			- 'PostId'
#			- 'AnswerDownVotes' numero degli up vote della #risposta prima della data in 'Date'

def scoreadown(db,inputfile, output_file):
	dict_reader = csv.DictReader(open(inputfile, 'r'), delimiter=';')
	head = dict_reader.fieldnames

	f = ['PostId', 'AnswerDownVotes']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:

		r = {}

		answid = row['PostId']
		date = row['Date']
		if str(date) != 'None':
			result_set7 = execute_param_query(db, getAnswDownVotesBeforeAccDate(answid, date))
		else:
			result_set7 = execute_param_query(db, getAnswDownVotes(answid))

		for tup in result_set7:
			a_down = tup[1]
		
		r['PostId']=answid
		r['AnswerDownVotes'] = a_down

		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed: ', count
	return 'Done'


# Calcola lo score delle risposte
#
# parametri:
#	file_name: nome del file csv da cui leggere, deve contenere almeno i campi:
#		- 'PostId' :id della risposta
#		- 'AnswerUpVotes' numero degli up vote della risposta
#			prima della data di accettazione della domanda
#		- 'AnswerDownVotes'	numero dei down vote della #risposta prima della data di accettazione di una risposta
#	output_file: nome del file csv su cui scrivere i risultati e contiene i campi:
#		- 'PostId'
#		- 'AnswerScore' risultato della sottrazione tra il campo 'AnswerUpVotes' e il
#			campo 'AnswerDownVotes'
def calculate_answ_score(file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';')
	
	head = dict_reader.fieldnames
	f = ['PostId', 'AnswerScore']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		a_up = row['AnswerUpVotes']
		a_down = row['AnswerDownVotes']

		a_score = int(a_up) - int(a_down)
			
		r['AnswerScore'] = a_score

		dict_writer.writerow(r)
	
	return 'Done'



# Salva il result set calcolando la lunghezza del titolo e del corpo
#
# parametri:
#	result_set: oggetto ritornato dalla funzione execute_param_query, tale
#		result set deve contenere almeno il campo 'Body'
#	filename: nome del file in formato csv su cui scrivere il result_set,
#		il file conterra': 
#			- gli stessi campi del result set con il campo 'Body' ripulito 
#				dai tag html e dal code snippet
#			- il campo 'TitleLength' con il numero di parole del campo Title
#			- il campo 'BodyLength' con il numero di parole del campo Body
def save_csv_body_title_len(result_set, filename):
	
	f = open(filename, 'w')
	writer = csv.writer(f)
	
	#writer = csv.writer(f, delimiter=';')
	#print result_set

	desc = result_set.description # Prende i campi della tabella

	i = 0
	body_field = 0
	fields = [] # crea il vettore che contiene gli header da scrivere nel csv di output
	for d in desc:
		if 'Body' in d[0]:
			body_field = i # conserva l'indice del campo Body
		if 'Title' in d[0]:
			title_field = i # conserva l'indice del campo Title
		fields = fields + [d[0]]
		i += 1
	fields.append('TitleLength')
	fields.append('BodyLength')
	print fields
	writer.writerow(fields) # scrive gli header sul csv
	total = 0
	count = 0
	for row in result_set: # Cicla sui record della tabella
		total += 1
		row_to_write = []
		i = 0
		
		blen = 0
		tlen = 0
		for c in row:				
			if i == body_field:
				body = ''
				try:
					body = c.decode('unicode_escape').encode('ascii','ignore')
				except UnicodeDecodeError:
					try:
						body = unicode(c).encode('ascii', 'ignore')
					except Exception:
						body = unicode(c, errors='ignore')

				body_cleaned = clean_body(body) 
				blen = text_length(body_cleaned)

				row_to_write = row_to_write + [body_cleaned]
				print body_cleaned
				print row_to_write
				count += 1

			elif i == title_field:
				try:
					tlen = text_length(c)
					row_to_write = row_to_write + [c]
				except Exception:
					tlen = 0
					row_to_write = row_to_write + ['']
				
			else:
				row_to_write = row_to_write + [str(c)]
			i += 1
		row_to_write = row_to_write + [str(tlen)]
		row_to_write = row_to_write + [str(blen)]
		print row_to_write
		writer.writerow(row_to_write)
	

	print "Total post",total
	print "Post processed ",count
	return 'Done'

# Funzione che associa ad uno score di reputazione la rispettiva cateogria (nome e numero)
#
# parametri:
#	file_name: nome del file in formato csv che deve contenere #almeno i campi:
#			- PostId: id della risposta
#			- ReputationAnsw: score di reputazione 
#					dell'autore della risposta	
#			- ReputationQuest: score di reputazione 
#					dell'autore della domanda	
#	filename: nome del file in formato csv su cui scrivere l'output
#il file conterra': 
#			- PostId
#			- i campi #'ReputationCategoryNameAnsw'e
#			  'ReputationCategoryNumberAnsw' contenenti rispettivamente nome e numero di categoria di 
#			   reputazione dell'autore della risposta
#			- i campi #'ReputationCategoryNameQuest'e
#			   'ReputationCategoryNumberQuest' contenenti rispettivamente nome e numero di categoria di 
#			   reputazione dell'autore della domanda


def reputation_csv(file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';') # DELIMITER
	
	head = dict_reader.fieldnames
	f = ['PostId', 

'ReputationCategoryNameAnsw','ReputationCategoryNumberAnsw','ReputationCategoryNameQuest','ReputationCategoryNumberQuest']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)  # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		repScoreAnswStr = row['ReputationAnsw']
		repScoreAnsw = int(repScoreAnswStr)
		#print repScore
		if (repScoreAnsw<10):
			categoryname='Inactive'
			categorynumber=int(0)
		if (repScoreAnsw>9 and repScoreAnsw<100):
			categoryname='Low'
			categorynumber=int(1)
		if (repScoreAnsw>99 and repScoreAnsw<20000):
			categoryname='Medium'
			categorynumber=int(2)
		if (repScoreAnsw>19999):
			categoryname='High'
			categorynumber=int(3)

		r['ReputationCategoryNameAnsw']=categoryname
		r['ReputationCategoryNumberAnsw']=categorynumber

		repScoreQuestStr = row['ReputationQuest']
		repScoreQuest = int(repScoreQuestStr)
		#print repScore
		if (repScoreQuest<10):
			categoryname='Inactive'
			categorynumber=int(0)
		if (repScoreQuest>9 and repScoreQuest<100):
			categoryname='Low'
			categorynumber=int(1)
		if (repScoreQuest>99 and repScoreQuest<20000):
			categoryname='Medium'
			categorynumber=int(2)
		if (repScoreQuest>19999):
			categoryname='High'
			categorynumber=int(3)

		r['ReputationCategoryNameQuest']=categoryname
		r['ReputationCategoryNumberQuest']=categorynumber

		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed for reputation_csv: ', count
	return 'Done'



# Funzione che calcola il tempo intercorso tra il post della #risposta e quello della rispettiva domanda
#
# parametri:
#	file_name: nome del file in formato csv che deve contenere #almeno i campi:
#			- PostId: id della risposta
#			- PostCreationDate: data di creazione della 
#					risposta (formato date)	
#			- QuestionCreationDate: data di creazione della #domanda	
#	filename: nome del file in formato csv su cui scrivere l'output
#		il file conterra': 
#			- PostId
#			- espressione in vari modi della differenza di #tempo intercorso



def timeResponse_csv(file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';') # DELIMITER
	
	head = dict_reader.fieldnames
	f = ['PostId','RespTimeInHoursDays','RespTimeInMinsDays','RespTimeInSecsDays', 

'RespDays','RespTimeHours','RespTimeMins','RespTimeSecs']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)  # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		date_answer = datetime.datetime.strptime(row['PostCreationDate'],"%Y-%m-%d %H:%M:%S")
		#datetime.datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S.%f")
		date_question = datetime.datetime.strptime(row['QuestionCreationDate'],"%Y-%m-%d %H:%M:%S")
		diff = date_answer - date_question
		hours = diff.seconds / 3600
		min = diff.seconds / 60
		min2 = (diff.seconds % 3600) / 60
		sec2 = (diff.seconds % 3600) % 60
                #print hour
		#print min
		#print sec
		#time = datetime.time(hours,min,sec)
	
		
		r['RespTimeInHoursDays'] = hours + (diff.days*24)
		r['RespTimeInMinsDays'] = min + (diff.days*(60 *24))
		r['RespTimeInSecsDays'] = diff.seconds + (diff.days*(60*60*24))
		r['RespDays'] = diff.days	
		r['RespTimeHours'] = hours
		r['RespTimeMins'] = min2
		#r['RespTimeSecs'] = diff.seconds
		r['RespTimeSecs'] = sec2

		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed for timeresponse.csv : ', count
	return 'Done'

# test per vedere se un post è una risposta accettata 
def testAccepted(post):
	return "SELECT postid AS pid FROM acceptedanswer_mv WHERE postid = " + post + ""


# Funzione che valuta se una risposta è una risposta accettata o no
#
# parametri:
#	file_name: nome del file in formato csv che deve contenere almeno i campi:
#			- PostId: id della risposta
#			
#	filename: nome del file in formato csv su cui scrivere l'output
#		il file conterra': 
#			- PostId
#			- i campi Accepted, Not Accepted che dicono se una risposta è una risposta accettata o meno


def accepted(file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';')  # DELIMITER
	
	head = dict_reader.fieldnames
	f = ['PostId', 'Accepted', 'NotAccepted']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)  # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		postid= row['PostId']
		accepted = 'no'
		notaccepted = 'yes'
		

		result_set5 = execute_param_query('stackoverflow', testAccepted(postid))
		tot_tuple = long(result_set5.rowcount)

		if tot_tuple > 0:
			accepted = 'yes'
			notaccepted = 'no'
		
		r['Accepted'] = accepted
		r['NotAccepted'] = notaccepted
		
		dict_writer.writerow(r)
		count += 1

	print 'Post processed for accepted: ', count
	return 'Done'


# Funzione che valuta se una risposta è la prima risposta postata #alla relativa domanda
#
# parametri:
#	file_name: nome del file in formato csv che deve contenere #almeno i campi:
#			- PostId: id della risposta
#			- PostCreationDate: data di creazione della 
#					risposta (formato date)	
#			- QuestionCreationDate: data di creazione della #domanda	
#	filename: nome del file in formato csv su cui scrivere l'output
#		il file conterra': 
#			- PostId 
#			- IsFirstAnswer che dice se una risposta è la prima postata alla relativa domanda o meno

def isfirstanswer(db, input_file, output_file):

	dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';')
	head = dict_reader.fieldnames

	f = ['PostId', 'IsFirstAnswer']
	writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f) # DELIMITER
	writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header

	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		postid= row['PostId']
		#idquestion = str(row['QuestionId'])
		idquestion = row['QuestionId']

		result_set2 = execute_param_query(db,"SELECT a_PostId AS PostFirst, MIN(a_postdate) AS DateFirst FROM answers_mv WHERE 

a_QuestionId = " + idquestion + "")
 			
		idfirstanswer=0
		for tup in result_set2:
			idfirstanswer = tup[0]
	
		isfirst = 'no' 
		#print 'PostLetto = ', postid, 'Postfirst = ', idfirstanswer 
		if (str(postid)==str(idfirstanswer)):
			#print 'is first!'
			isfirst = 'yes'
			
		r['IsFirstAnswer'] = isfirst
		
		writer.writerow(r)
		count += 1

	print 'Post processed for isfirst: ', count
	return 'Done'


# Funzione che ricava il ranking delle risposte in una discussione considerando tutte quelle della specifica discussione
#
# parametri:
#	file_name: nome del file in formato csv che deve contenere #almeno i campi:
#			- PostId: id della risposta
#			- QuestionId : id della relativa domanda
#	filename: nome del file in formato csv su cui scrivere l'output
#		il file conterra': 
#			- PostId 
#			- Ranking che conserva linformazione sull'ordine di arrivo della risposta


def rankinganswers(db, input_file, output_file):

	dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';')
	head = dict_reader.fieldnames

	f = ['PostId', 'Ranking']
	writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f) # DELIMITER
	writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header

	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		postid= row['PostId']
		#idquestion = str(row['QuestionId'])
		idquestion = row['QuestionId']

		result_set2 = execute_param_query(db,"Select a.a_postid AS AnsId, a.a_postdate, a.a_QuestionId from  answers_mv a where 

a.a_QuestionId=" + idquestion + " order by a.a_postdate ASC");

 		idpost=0
		rank=1
		for tup in result_set2:
			
			idanswer = tup[0]
			isfirst = 'no' 
			#print 'PostLetto = ', postid, 'Postfirst = ', idfirstanswer 
			if (str(postid)==str(idanswer)):
			#print 'is first!'
				r['Ranking'] = rank
			else:
				rank+=1
		
		writer.writerow(r)
		count += 1

	print 'Post processed for ranking answers: ', count
	return 'Done'



# Funzione che valuta l'allineamento della reputation tra autore della risposta e quello della domanda
#
# parametri:
#	file_name: nome del file in formato csv che deve contenere almeno i campi:
#			- PostId: id della risposta
#			- ReputationAnsw: score di reputazione 
#					dell'autore della risposta	
#			- ReputationQuest: score di reputazione 
#					dell'autore della domanda	
#			- ReputationCategoryNumberAnsw : categoria di
# 			  reputazione dell'autore della risposta
#			- ReputationCategoryNumberQuest : categoria di 
# 			  reputazione dell'autore della domanda
#	filename: nome del file in formato csv su cui scrivere l'output
#		il file conterra': 
#			- PostId
#			- i campi 'Align_on_category','Align_on_score contenenti rispettivamente 
#			  l'allineamento calcolato sia tra le categorie che tra gli score

def reputation_align(file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';') # DELIMITER
	
	head = dict_reader.fieldnames
	f = ['PostId', 'Align_on_category','Align_on_score']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)  # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		repScoreAnswStr = row['ReputationAnsw']
		repScoreQuesStr = row['ReputationQuest']
		repCatAnsw   = row['ReputationCategoryNumberAnsw']
		repCatQuest  = row['ReputationCategoryNumberQuest']
		
		repScoreAnsw = int(repScoreAnswStr)
		repScoreQuest= int(repScoreQuesStr)
		#print repScore
		if (repCatAnsw<repCatQuest):
			alignCat='Lower'
		if (repCatAnsw>repCatQuest):
			alignCat='Higher'
		if (repCatAnsw==repCatQuest):
			alignCat='Equal'
			
		if (repScoreAnsw<repScoreQuest):
			alignScore='Lower'
		if (repScoreAnsw>repScoreQuest):
			alignScore='Higher'
		if (repScoreAnsw==repScoreQuest):
			alignScore='Equal'
			

		r['Align_on_category']=alignCat
		r['Align_on_score']=alignScore

		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed for rep align: ', count
	return 'Done'


#provvisoria

def onlymyanswers(db, input_file, output_file):

	dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';')
	head = dict_reader.fieldnames

	f = ['PostId', 'Topic']
	writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f) # DELIMITER
	writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header

	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		postid= row['PostId']

		result_set2 = execute_param_query(db,"SELECT a_PostId AS PostFirst, MIN(a_postdate) AS DateFirst FROM answers_mv WHERE 

a_QuestionId = " + idquestion + "")
 			

		result_set5 = execute_param_query('academia', "SELECT a_postID AS PostId FROM answers_mv WHERE a_postDate > date('2014-04-20') 

")
		tot_tuple = long(result_set5.rowcount)

		if tot_tuple > 0:
			accepted = 'yes'
			notaccepted = 'no'

		idfirstanswer=0
		for tup in result_set2:
			idfirstanswer = tup[0]
	
		isfirst = 'no' 
		print 'PostLetto = ', postid, 'Postfirst = ', idfirstanswer 
		if (str(postid)==str(idfirstanswer)):
			print 'is first!'
			isfirst = 'yes'
			
		r['IsFirstAnswer'] = isfirst
		
		writer.writerow(r)
		count += 1

	print 'Post processed: ', count
	return 'Done'


# Calcola il numero di link presenti in ogni post.
#
# parametri:
#	database: nome del database da interrogare
#	output_file: nome del file csv su cui scrivere i risultati, conterra' i campi:
#			- 'PostId'
#			- 'URL' numero di link identificati nel corpo del post corrispondente
def n_of_link(database, output_file):
	
	f = ['PostId', 'URL']
	writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f) # DELIMITER
	writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header

	answers_body= "SELECT a_postID AS PostId, a_body AS Body FROM answers_mv order by PostId asc"
	#questions_body = "SELECT q_postID AS PostId, q_body AS Body FROM questions_mv"
	result_set = execute_param_query(database, answers_body)
	desc = result_set.description # Prende i campi della tabella

	i = 0
	body_field = 0
	fields = [] # crea il vettore che contiene gli header da scrivere nel csv di output
	for d in desc:
		if 'Body' in d[0]:
			body_field = i # conserva l'indice del campo Body
		if 'PostId' in d[0]:
			postid_field = i # conserva l'indice del campo Title
		fields = fields + [d[0]]
		i += 1
	
	total = 0
	count = 0
	for row in result_set: # Cicla sui record della tabella
		total += 1
		row_to_write = {}
		row_to_write['URL'] = str(0)
		i = 0
		
		for c in row:				
			if i == body_field:
				body = ''
				try:
					body = c.decode('unicode_escape').encode('ascii','ignore')
				except UnicodeDecodeError:
					try:
						body = unicode(c).encode('ascii', 'ignore')
					except Exception:
						body = unicode(c, errors='ignore')

				n_link = link_count(del_code(body))

				row_to_write['URL'] = str(n_link)
				count += 1

			elif i == postid_field:
				row_to_write['PostId'] = str(c)
				
			i += 1
		
		writer.writerow(row_to_write)
	

	print "Total post for links",total
	print "Post processed for links",count
	return 'Done'





all_answers_query = "SELECT a_postID AS PostId, a_title AS Title, a_body AS Body, a_tags AS Tags, a_postDate AS PostCreationDate, a_score AS 

Score, a_ownerID AS UserId, a_ownerReputation AS ReputationAnsw, a_QuestionId AS QuestionId, a_user_quest_id AS UserQuest, 

a_user_quest_reputation AS ReputationQuest, a_DateQuestion AS QuestionCreationDate FROM answers_mv order by PostId asc"


#answer_query = "SELECT a_postID AS PostId, a_title AS Title, a_body AS Body, a_tags AS Tags, a_postDate AS PostCreationDate, a_score AS 

Score, a_ownerID AS UserId, a_ownerReputation AS ReputationAnsw, a_QuestionId AS QuestionId, a_user_quest_id AS UserQuest, 

a_user_quest_reputation AS ReputationQuest, a_DateQuestion AS QuestionCreationDate FROM answers_mv WHERE a_postDate > date('2014-04-20')"
