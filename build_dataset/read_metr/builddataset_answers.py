

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
#from datetime import datetime
from fractions import Fraction
from HTMLParser import HTMLParser
#from builddataset import text_length,clean_body,link_count,del_code,execute_param_query
from readability import Readability
import utils




# Crea il file csv da dare in input alle funzioni che calcolano lo score di
# sentiment.
#
# parametri:
#       input_file: nome del file csv da cui leggere, deve contenere almeno i campi:
#                       - 'PostId'
#                       - 'Body' corpo del post
#       output_file: nome del file csv su cui scrivere, conterra' i campi:
#                       - 'PostId'
#                       - 'Corpus' con il campo 'Body'
def dataset_liwc_senti(input_file, output_file):
        dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';') # DELIMITER

        head = dict_reader.fieldnames
        f = ['PostId', 'Corpus']

        dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f) # DELIMITER
        dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header

        count = 0
        for row in dict_reader:
                r = {}
                r['PostId'] = row['PostId']
                corpus = row['Body']

                try:
                        #corpus = title + " " + body

                        try:
                                r['Corpus'] = corpus.decode('unicode_escape').encode('ascii','ignore')
                        except UnicodeDecodeError:
                                print r['PostId']
                                try:
                                        r['Corpus'] = unicode(corpus).encode('ascii', 'ignore')
                                except Exception:
                                        r['Corpus'] = unicode(corpus, errors='ignore')


                except Exception:
                        dict_writer.writerow(r)
                        continue
                dict_writer.writerow(r)
        print 'Post processed: ', count
        return 'Done'



#Script che effettua il calcolo delle metriche di readability
#INPUT: -input_file: file csv che contiene le osservazioni
#OUTPUT:-output_file: file csv che contiene le metriche di readability calcolate

def readability_metrics(input_file, output_file):
        dict_reader = csv.DictReader(open(input_file,'r'),delimiter=';')
        head = dict_reader.fieldnames

        f =['PostId','AutomatedReadingIndex','FleschReadingEase','FleschKincaidGradeLevel','GunningFogIndex','SMOGIndex','ColemanLiauIndex','NSentences','NWords','NChars','NSyllables','NComplexWords','AvgWordsPSentence','AvgUpperCharsPPost']
        dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
        dict_writer.writerow(dict((fn,fn) for fn in f))

        count = 0
        skippAri = 0
        skippFRE = 0
        skippFKGL = 0
        skipGFI = 0
        skipSMOG = 0
        skipCLI = 0
        upperchars = 0
        c=0
        for row in dict_reader:
                r={}
                c+=1
                r['PostId']= row['PostId']
                text = row['Body']
                if(len(text)>1):
                        rd = Readability(text)
                        try:
                                r['AutomatedReadingIndex'] = float(rd.ARI())
                        except Exception:
                                r['AutomatedReadingIndex'] = float(rd.ARI())
                                skippAri += 1
                                continue
                        try:
                                r['FleschReadingEase'] = float(rd.FleschReadingEase())
                        except Exception:
                                r['FleschReadingEase'] = 0
                                skippFRE += 1
                                continue
                        try:
                                r['FleschKincaidGradeLevel']= float(rd.FleschKincaidGradeLevel())
                        except Exception:
                                r['FleschKincaidGradeLevel']= 0
                                skippFKGL +=1
                                continue
                        try:
                                r['GunningFogIndex'] = float(rd.GunningFogIndex())
                        except Exception:
                                r['GunningFogIndex'] = 0
                                skipGFI += 1
                                continue
                        try:
                                r['SMOGIndex'] = float(rd.SMOGIndex())
                        except Exception:
                                r['SMOGIndex'] = 0
                                skipSMOG += 1
                                r['SMOGIndex'] = 0
                                skipSMOG += 1
                                continue
                        try:
                                r['ColemanLiauIndex'] = float(rd.ColemanLiauIndex())
                        except Exception:
                                r['ColemanLiauIndex'] = 0
                                skipCLI += 1
                                continue

                        upperchars= utils.metric_upperchar(text)
                        r['NSentences'] = int(rd.getSentenceCount())
                        r['NWords'] = int(rd.getWordCount())
                        r['NChars'] = int(rd.getCharCount())
                        r['NSyllables'] = int(rd.getSyllableCount())
                        r['NComplexWords'] = int(rd.getComplexWordsCount())
                        r['AvgWordsPSentence'] = float(rd.getAvgWordsPSentence())
                        r['AvgUpperCharsPPost'] = upperchars
                else:
                        print 'Riga Vuota'
                        r['AutomatedReadingIndex'] = 0
                        r['FleschReadingEase'] = 'NONE'
                        r['FleschKincaidGradeLevel'] = 0
                        r['GunningFogIndex'] = 0
                        r['SMOGIndex'] = 0
                        r['ColemanLiauIndex'] = 0
                        r['NSentences'] = 0
                        r['NWords'] = 0
                        r['NChars'] = 0
                        r['NSyllables'] = 0
                        r['NComplexWords'] = 0
                        r['AvgWordsPSentence'] = 0
                        r['AvgUpperCharsPPost'] = 0
                dict_writer.writerow(r)
                count+=1
        print 'Post processed for readability metrics: ', count
        return 'Done'






#Script che crea il file .sql per riempire la vista che contiene le coppie id_domanda - topic 
#soluzione utilizzata per accelerare i tempi di esecuzione
#INPUT: - input_file: file csv contenente le informazioni circa l'id della domanda ed il topic della domanda
#OUTPUT:- output_file: file .sql che eseguito in mysql riempie la tabella topic_questions_mv 

def ins_topicQdb( input_file, output_sql_file):

        dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';')
        head = dict_reader.fieldnames

        out_file = open(output_sql_file, 'w')
        c=0
        for row in dict_reader:
                postQ = str(row['PostId'])
                topicQ = str(row['Topic'])
                query="INSERT INTO topic_questions_mv (t_postID, t_topic) VALUES ("+ postQ +"," + topicQ + ");"
                out_file.write(query+"\n")
                c+=1
        out_file.close()
        print 'Create!'
        return 'Done'



#Script che isola le risposte scritte prima del post della risposta successivamente dichiarata accettata
#INPUT : - inputfile: file csv che per ogni risposta contiene: ID della risposta,ID della domanda a cui fa capo,
#          Data di pubblicazione della risposta e Data di pubblicazione della risposta accettata
#OUTPUT: - output_file: file csv che conserva gli id delle risposte scritte prima di quelle che poi sono state accettate
#	   ed ovviamente le risposte accettate. NB: Nel caso la discussione non abbia una risposta accettata (valore None),
#	   vengono conservate tutte le risposte di quella discussione


def filtra_non_n(inputfile,output_file):

        dict_reader = csv.DictReader(open(inputfile, 'r'), delimiter=';')
        head = dict_reader.fieldnames

        dict_writer = csv.DictWriter(open(output_file, 'w'),delimiter=';', fieldnames=head)
        dict_writer.writerow(dict((fn,fn) for fn in head))

        count=0
        scritti=0
        tagliati =0
        for row in dict_reader:
                if(str(row['DataPostRispAccettata'])==str('None')):
                        dict_writer.writerow(row)
                        scritti+=1
                else:
                        if (datetime.strptime(row['DataPostRispAccettata'],"%Y-%m-%d %H:%M:%S")>= datetime.strptime(row['CreationDateDiPostId'],"%Y-%m-%d %H:%M:%S")):
                                dict_writer.writerow(row)
                                scritti+=1
                        else:
                                tagliati+=1

                count += 1
        print 'scritti: ',scritti
        print 'esamiati: ', count
        print 'tagliati',tagliati
        return 'done'


#Script che per ogni risposta, recupera l'id della domanda a cui fa capo, la data di pubblicazione della risposta e la data di pubblicazione della risposta
#accettata della discussione di cui fa parte. PS: Per tempi di elaborazione si è ristretto lo script alla sola fetta di risposte più recenti che includeva 
#tutte le risposte dell'ultimo mese del dump [condizione PostID > 24000000]
#INPUT: -Nome del db 
#	-input_file:file contenente le risposte, è sufficiente che il file contenga almeno il campo 'PostId'
#OUTPUT:-file csv che per ogni risposta recupera: ID risposta, ID domanda a cui fa riferimento, Data di creazione della risposta e data di creazione della 
#	 risposta che poi è diventata la risposta accettata. NB: Se la discussione non ha una risposta accettata viene utilizzato il valore 'None'

def trova_data(db,input_file,output_file):

        dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';')
        head = dict_reader.fieldnames
        fieldnames=['PostId','QuestId','DataPostRispAccettata','CreationDateDiPostId']

        dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=fieldnames) # DELIMITER
        dict_writer.writerow(dict((fn,fn) for fn in fieldnames)) #Scrive gli header

        scritti=0
        tot=0
        for row in dict_reader:
                if(int(row['PostId'])>int(24000000)):
                        if ((row['Date'])=='None'):
                                r={}
                                r['PostId']=row['PostId']
                                r['QuestId']=row['PostQuestion']
                                r['DataPostRispAccettata']='None'
                                r['CreationDateDiPostId']='None'
                                dict_writer.writerow(r)
                                scritti+=1
                        else:
                                quest=row['PostQuestion']
                                query= "select answ_acc from questwithacceptedanswer2_mv where postID=" + str(quest)
                                q1 = execute_param_query(db,query)
                                for an in q1:
                                        id=an[0]

                                query2= "select creationdate from Posts where id=" + str(id)
                                q2 = execute_param_query(db,query2)
                                for an2 in q2:
                                        date=str(an2[0])


                                query3= "select creationdate from Posts where id=" + str(row['PostId'])
                                q3 = execute_param_query(db,query3)
                                for an3 in q3:
                                        datePost=str(an3[0])
                                r={}
                                r['PostId']= row['PostId']
                                r['QuestId']= row['PostQuestion']
                                r['DataPostRispAccettata']=date
                                r['CreationDateDiPostId']=datePost
                                dict_writer.writerow(r)
                                scritti+=1
                        tot+=1
        print 'scritti :',scritti
        print 'analizzati : ',tot
        return 'Done'




# commenti di tutti gli utenti ad una risposta (@PostId) prima della data di accettazione (@Date)
def getCommentsBeforeAccDate(postid, vote_date):
	return "SELECT Id, text FROM Comments WHERE creationDate < \'" + vote_date + "\' AND PostId = " + postid

# commenti di tutti gli utenti ad una risposta (@PostId)
def getComments(postid):
	return "SELECT Id, text FROM Comments WHERE PostId = " + postid


# commenti dell'autore della risposta ad una propria risposta (@PostId) prima della data di accettazione (@Date)
def getUsersCommentsBeforeAccDate(postid, vote_date):
        return "SELECT ca_Id, ca_text FROM userscommentsanswers_mv WHERE ca_ts_creationDate < \'" + vote_date + "\' AND qa_Id = " + postid

# commenti dell'autore della risposta ad una propria risposta (@PostId)
def getUsersComments(postid):
        return "SELECT ca_Id, ca_text FROM userscommentsanswers_mv WHERE qa_Id = " + postid


# edits di un utente ad un post (@PostId). NB:Nel mio caso id di risposte
def getBodyAuthEdits(postid,aut):
        return "SELECT Id FROM PostHistory WHERE posthistorytypeid = 5 AND PostId = " + postid + " AND UserId= "+ aut

# tutti gli edits fatti su un post prima della data di accettazione
def getBodyEditsBeforeAccDate(postid, vote_date):
	return "SELECT Id FROM PostHistory WHERE posthistorytypeid = 5 AND creationDate < \'" + vote_date + "\' AND PostId = " + postid


# tutti gli edits fatti su un post (@PostId)
def getBodyEdits(postid):
	return "SELECT Id FROM PostHistory WHERE posthistorytypeid = 5 AND PostId = " + postid


# Estrae il numero di upvotes, prima di una certa data (@Date), ottenuti dalle risposte postate da un certo utente (@User) */
def getAnswUpVotesBeforeAccDate(ansid, date):
	return "SELECT u_postID as AnswerID, count(u_voteID) as UpVotesAnsw FROM answerupvotes_mv WHERE u_postID = " + ansid + " AND uts_voteDate < date(\'" + date + "\')"
	
# Estrae il numero di downvotes, prima di una certa data (@Date), ottenuti dalle risposte postate da un certo utente (@User) */
def getAnswDownVotesBeforeAccDate(ansid, date):
	return "SELECT d_postID as AnswerID, count(d_voteID) as AnswerDownvotesScore FROM answerdownvotes_mv WHERE d_postID = " + ansid + " AND dts_voteDate < date(\'" + date + "\')"


# Estrae il numero di upvotes, ottenuti dalle risposte postate da un certo utente (@User) */
def getAnswUpVotes(ansid):
	return "SELECT u_postID as AnswerID, count(u_voteID) as UpVotesAnsw FROM answerupvotes_mv WHERE u_postID = " + ansid 
	
# Estrae il numero di downvotes, ottenuti dalle risposte postate da un certo utente (@User) */
def getAnswDownVotes(ansid):
	return "SELECT d_postID as AnswerID, count(d_voteID) as AnswerDownvotesScore FROM answerdownvotes_mv WHERE d_postID = " + ansid 




#query che recupera il datetime del primo commento scritto dall'autore della risposta, sulla sua risposta 
def getTimeFirstAuthorComments(postid):
        return "SELECT MIN(c_ts_creationDate) FROM authorcommentsanswers_mv WHERE a_Id = " + postid

#query che recupera il datetime dell'ultimo commento scritto dall'autore della risposta, sulla sua risposta
def getTimeLastAuthorComments(postid):
        return "SELECT MAX(c_ts_creationDate) FROM authorcommentsanswers_mv WHERE a_Id = " + postid


#Script che provvede a recuperare per ogni risposta, la data di pubblicazione della risposta, la data del primo e dell'ultimo commento scritto dall'autore 
#della risposta su quella sua risposta,la differenza in secondi del tempo intercorso tra il momento del post della risposta ed il post del primo commento
#dell'autore alla sua risposta e la differenza in secondi del tempo intercorso tra il momento del post della risposta ed il post dell'ultimo commento dell'autore
#alla sua risposta.
#INPUT:- nome del db
#      - inputfile: file che contiene le risposte su cui eseguire lo script NB: anche in questo caso, per tempi di elaborazione, si è ristretto lo script alla sola
#        fetta di risposte più recenti che includeva tutte le risposte dell'ultimo mese del dump [condizione PostID > 24000000] 
#OUTPUT:- output_file: file contenente postid della risposta, data di pubblicazione della risposta, data del primo commento dell'autore (se non c'è viene utilizzato
#	  il 'None'), data dell'ultimo commento dell'autore (se non c'è viene utilizzato il 'None') e le rispettive differenze in secondi. 
 
def timeauthorcomment(database, inputfile, output_file):

        dict_reader = csv.DictReader(open(inputfile, 'r'),delimiter=';')
        head = dict_reader.fieldnames

        # Inizializza il csv da scrivere
        fieldnames = ['PostId' ,'DateAnswer', 'DateFirstAuthorComment','DateLastAuthorComment','SecsTimeFirstAutComment','SecsTimeLastAutComment']
        dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=fieldnames) # DELIMITER
        dict_writer.writerow(dict((fn,fn) for fn in fieldnames)) #Scrive gli header

        t=0
        for row in dict_reader:

                w_row = {}
                w_row['PostId'] = row['PostId']
                t=0
                if ((int(row['PostId']))>int(24000000)):
                        comments = execute_param_query(database, getUsersComments(str(row['PostId'])))
                        #print 'tot:commenti: ',comments.rowcount
			if (int(comments.rowcount)==0):
				w_row['DateAnswer']=row['PostCreationDate']
                                w_row['DateFirstAuthorComment'] = str('None')
                                w_row['DateLastAuthorComment'] = str('None')
                                w_row['SecsTimeFirstAutComment'] = int('0')
                                w_row['SecsTimeLastAutComment'] = int('0')
                        else:
				w_row['DateAnswer']=row['PostCreationDate']
                                first = execute_param_query(database, getTimeFirstAuthorComments(str(row['PostId'])))
				for rowsf in first:
					w_row['DateFirstAuthorComment']=rowsf[0]
					#print rowsf[0]
                                last = execute_param_query(database, getTimeLastAuthorComments(str(row['PostId'])))
				#print row['PostId']
				#print first.rowcount
          			for rowsl in last:
					w_row['DateLastAuthorComment']=rowsl[0]
                                        #print rowsl[0]

                                date_answer = datetime.datetime.strptime(row['PostCreationDate'],"%Y-%m-%d %H:%M:%S")
                                date_first_comment = datetime.datetime.strptime(str(w_row['DateFirstAuthorComment']),"%Y-%m-%d %H:%M:%S")
                                date_last_comment = datetime.datetime.strptime(str(w_row['DateLastAuthorComment']),"%Y-%m-%d %H:%M:%S")


                                diff_f = date_first_comment - date_answer

                                w_row['SecsTimeFirstAutComment'] = diff_f.seconds + (diff_f.days*(60*60*24))

                                diff_l = date_last_comment - date_answer
                                w_row['SecsTimeLastAutComment'] = diff_l.seconds + (diff_l.days*(60*60*24))

                        dict_writer.writerow(w_row)
                        t+=1
        print 'Post scritti:',t
        return 'Done'

#Script che calcola: - il tempo medio intercorso tra quando un utente pubblica una risposta e posta il suo primo commento 
#		     - il tempo medio intercorso tra quando un utente pubblica una risposta e posta il suo ultimo commento
# INPUT: - input_file: file che deve contenere: postid della risposta, differenza in secondi tra il post della risposta ed il post del primo commento dell'autore
#          della risposta a quella risposta, differenza in secondi tra il post della risposta ed il post dell'ultimo commento dell'autore della risposta a quella risposta   
# OUTPUT: - stampa a video delle due medie.

def media_first_last_time_comment(input_file):

        dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';') # DELIMITER
        c=0
        acc_first=0
        acc_last=0
        media_first=0
        media_last=0
        val_first=0
        val_last=0
        tot_first=0
        tot_last=0
        for row in dict_reader:
		c+=1
                print row['PostId']
                if(str(row['SecsTimeFirstAutComment'])!= '0')and(str(row['SecsTimeLastAutComment'])!= '0'):
          
                        val_first = decimal.Decimal(row['SecsTimeFirstAutComment'])
                        val_first= val_first*1

                        tot_first+=1
                        acc_first= acc_first+val_first

                        val_last = decimal.Decimal(row['SecsTimeLastAutComment'])
                        val_last= val_last*1

                        tot_last+=1
                        acc_last= acc_last+val_last


        print 'fine accumulatore'
        media_first=acc_first/tot_first
        media_last=acc_last/tot_last
        mf= decimal.Decimal(media_first)
        decimal.getcontext().prec = 2
        decimal.getcontext().rounding = getattr(decimal,'ROUND_HALF_EVEN')

        mf= mf*1
        print 'Somma first : ', acc_first
        print 'Tot first: ', tot_first
        print 'media first: ', mf

        ml= decimal.Decimal(media_last)
        decimal.getcontext().prec = 2
        decimal.getcontext().rounding = getattr(decimal,'ROUND_HALF_EVEN')
        print 'Somma last : ', acc_last
        print 'Tot last: ', tot_last
        print 'media last: ', ml
	print 'totali: ',c
        return 'Done'



#Script che determina l'allineamento topic tra domanda e risposta. 
#INPUT: -nome del db
#       -input_file: file che contiene postid della risposta, topic della risposta, id della domanda a cui la risposta fa riferimento 
#OUTPUT: -output_file: file csv che contiene id della risposta, topic della risposta, id della domanda e campo issametopic che vale yes se il topic della
#	  domanda e quello della risposta sono uguali.
#NB: I topic delle domande sono caricati in una tabella all'interno della base di dati per velocizzare l'esecuzione della metrica 

def topic_align(db,input_file,output_file):

	dict_reader = csv.DictReader(open(input_file, 'r'),delimiter=';')
	head = dict_reader.fieldnames

	f = ['PostId', 'Topic','TopicQuestion','IsSameTopic']
	writer = csv.DictWriter(open(output_file, 'w'), delimiter=';',fieldnames=f)
	writer.writerow(dict((fn,fn) for fn in f))	

	count=0
	topicq=0
	idquestion=0

	for row in dict_reader:
		r={}
		r['PostId'] = row['PostId']
		postid=row['PostId']
		topicAns=row['Topic']
		r['Topic']= row['Topic']
		idquestion = row['QuestionId']
		result_set2 = execute_param_query(db,"SELECT t_topic FROM topic_questions_mv WHERE t_postID = " + str(idquestion) )
	
		for tup in result_set2:
			topicq = tup[0]
		isSametopic = 'no'
		if(str(topicAns) == str(topicq)):
			isSametopic = 'yes'

		r['TopicQuestion'] = topicq
		r['IsSameTopic'] = isSametopic
		
		writer.writerow(r)
		count+=1

	print 'Post processed for topic_align: ', count
	return 'Done'	


#Script che provvede a creare lo script .sql con il codice SQL per l'inserimetno degli id delle domande chiuse all'interno della 
# apposita tabella nella base di dati.   

def ins_questions_closeddb( input_file, output_sql_file):

        dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';')
        head = dict_reader.fieldnames

        out_file = open(output_sql_file, 'w')
        c=0
        for row in dict_reader:
                postQ = str(row['PostId'])
                query="INSERT INTO questions_closed_mv (qc_questID) VALUES ("+ postQ +");"
                out_file.write(query+"\n")
                c+=1
        out_file.close()
        print 'Create!'
        return 'Done'





# Definiamo, per ogni risposta, i commenti che tutti gli utenti hanno 
# aggiunto prima della data di accettazione della risposta. Nel caso non ci fosse
# una risposta accettata vengono considerati tutti i commenti che tutti hanno 
# aggiunto alla risposta in questione.
# La funzione calcola il numero ed il testo di tali commenti.
#
# parametri:
#	database: nome del database da interrogare
#       inputfile: file che contiene postid delle risposte,data dell'eventuale voto di accettazione (qualora non ci sia un voto di accettazione la data vale 'None') 
#	output_file: nome del file csv su cui scrivere i risultati, conterra' i campi:
#			- 'AnswersId'
#			- 'NumberOfUsersComments' numero di commenti
#			- 'TextOfUsersComments' testo dei commenti trovati
def allcommentsonanswers_dataset(database, inputfile, output_file):
	
	dict_reader = csv.DictReader(open(inputfile, 'r'),delimiter=';')
	head = dict_reader.fieldnames
	
	# Inizializza il csv da scrivere
	fieldnames = ['PostId' , 'NumberOfUsersComments', 'TextOfUsersComments']
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=fieldnames) # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in fieldnames)) #Scrive gli header	
	
	for row in dict_reader:
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
			w_row['TextOfUsersComments'] += ' ' + comm[1]
			
		
		dict_writer.writerow(w_row)
	return 'done'


#Script che per ogni risposta conta il numero di edit eseguiti sul post prima della data di accettazione (Se la data di accettazione non è presente vengono 
#conteggiati tutti gli edit)
#INPUT: - database:nome del db
#	- inputfile: file csv contenente gli id dei post e le date del voto di accettazione della discussione
#OUTPUT:- output_file: file che contiene, per ogni risposta il numero di edits su quella risposta prima della data di accettazione

def n_edits(database, inputfile, output_file):
	
	dict_reader = csv.DictReader(open(inputfile, 'r'), delimiter=';')
	head = dict_reader.fieldnames
	# Inizializza il csv da scrivere
	fieldnames = ['PostId' , 'NumberOfEdits']
	count=0
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=fieldnames) # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in fieldnames)) #Scrive gli header

	
	for row in dict_reader:
	
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


#Script che, per ogni risposta,conserva l'id della domanda a cui fa riferimento la risposta e la data dell'eventuale voto di accettazione di una risposta nella 
#discussione.
#INPUT: - db : nome del db
#OUTPUT:- output_file: file che conserva, dopo l'esecuzione di una query sulla base di dati, per tutte le risposte dell'ultimo mese, l'id della domanda e la data 
#	  dell'eventuale voto di accettazione ('None' qualora non ci sia una risposta accettata nella discussione)
 
def save_date_accepted(db, output_file):
	f = ['PostId','PostQuestion', 'Date']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0

	query_answers_questions_voteaccDate = "select * from (select a.al2_postid as ansid, q.postId, q.ts_voteDate from answers_last_30days2_mv a inner join 	questwithacceptedanswer_mv q on a.al2_QuestionId=q.postid union select a.al2_postid as ansid, q.q_postID as postId, null from answers_last_30days2_mv a inner join questions_mv q on a.al2_QuestionId=q.q_postid) questions group by ansid, postId"
	answers_questions = execute_param_query(db, query_answers_questions_voteaccDate)
	
	for row in answers_questions:
		r = {}
		r['PostQuestion'] = row[1]
		r['PostId'] = str(row[0])
		r['Date'] = str(row[2])
		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed: ', count
	return 'Done'



# Calcola lo score delle risposte come il numero degli up vote meno il numero di down 
# vote prima della data di accettazione di una risposta
#
# parametri:
#	db: stringa con il nome del database da cui leggere
#	file_name: nome del file csv da cui leggere, deve contenere almeno i campi:
#			- 'PostId'
#			- 'UserId' id dell'utente che ha postato la risposta
#			- 'PostCreationDate' data di creazione del post in formato '2014-01-30 21:30'
#	output_file: nome del file csv su cui scrivere i risultati, contiene i campi:
#			- 'PostId'
#			- 'AnswerScore' numero degli up vote meno il numero dei down vote delle 
#				risposte dell'utente prima della data in 'PostCreationDate'
def scoreanswer(db,inputfile, output_file):
	dict_reader = csv.DictReader(open(inputfile, 'r'), delimiter=';')
	head = dict_reader.fieldnames

	f = ['PostId', 'AnswerScore']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		r = {}
		answid = row['PostId']
		date = row['Date']
		if str(date) != 'None':
			result_set6 = execute_param_query(db, getAnswUpVotesBeforeAccDate(answid, date))
			result_set7 = execute_param_query(db, getAnswDownVotesBeforeAccDate(answid, date))
		else:
			result_set6 = execute_param_query(db, getAnswUpVotes(answid))
			result_set7 = execute_param_query(db, getAnswDownVotes(answid))
			
		
		
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


# Calcola il numero degli up vote sulle risposte scritte da un particolare utente prima della data di accettazione di una risposta
#
# parametri:
#	db: stringa con il nome del database da cui leggere
#	file_name: nome del file csv da cui leggere, deve contenere almeno i campi:
#			- 'PostId'
#			- 'UserId' id dell'utente che ha postato la risposta
#			- 'PostCreationDate' data di creazione del post in formato '2014-01-30 21:30'
#	output_file: nome del file csv su cui scrivere i risultati, contiene i campi:
#			- 'PostId'
#			- 'AnswerUpVotes' numero degli up vote ottenuti dalle risposte scritte da un 
#			   dall'utente che ha postato la risposta prima della data in 'PostCreationDate'
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

# Calcola il numero di down vote ricevuti dalle risposte di un utente prima della data di accettazione di una risposta
#
# parametri:
#	db: stringa con il nome del database da cui leggere
#	file_name: nome del file csv da cui leggere, deve contenere almeno i campi:
#			- 'PostId'
#			- 'UserId' id dell'utente che ha postato la risposta
#			- 'PostCreationDate' data di creazione del post in formato '2014-01-30 21:30'
#	output_file: nome del file csv su cui scrivere i risultati, contiene i campi:
#			- 'PostId'
#			- 'AnswerDownVotes' numero dei down vote delle 
#			   risposte dell'utente prima della data in 'PostCreationDate'
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
#		- 'PostId'
#		- 'AnswerUpVotes' numero degli up vote delle risposte postate dall'utente 
#			prima della data di creazione della risposta
#		- 'AnswerDownVotes'	numero dei down vote delle risposte postate dall'utente 
#			prima della data di creazione della risposta
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


#Script che ricava le informazioni sulla reputazione sia dell'autore della risposta che di quello della domanda
#INPUT: -file_name : file csv che contiene l'id della risposta, l'id della domanda, lo score di reputazione dell'autore della risposta e lo score di 
#                    reputazione dell'autore della domanda
#OUTPUT: -output_file: file csv che contiene id della risposta, nome e numero della categoria di reputazione dell'autore della risposta e nome e numero
#	               di categoria di reputazione dell'autore della domanda


def reputation_csv(file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';') # DELIMITER
	
	head = dict_reader.fieldnames
	f = ['PostId', 'ReputationCategoryNameAnsw','ReputationCategoryNumberAnsw','ReputationCategoryNameQuest','ReputationCategoryNumberQuest']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)  # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		repScoreAnswStr = row['ReputationAnsw']
		repScoreAnsw = int(repScoreAnswStr)
		if (repScoreAnsw<10):
			categoryname='Inactive'
			categorynumber=int(0)
		if (repScoreAnsw>9 and repScoreAnsw<1000):
			categoryname='Low'
			categorynumber=int(1)
		if (repScoreAnsw>999 and repScoreAnsw<20000):
			categoryname='Medium'
			categorynumber=int(2)
		if (repScoreAnsw>19999):
			categoryname='High'
			categorynumber=int(3)

		r['ReputationCategoryNameAnsw']=categoryname
		r['ReputationCategoryNumberAnsw']=categorynumber

		repScoreQuestStr = row['ReputationQuest']
		repScoreQuest = int(repScoreQuestStr)

		if (repScoreQuest<10):
			categoryname='Inactive'
			categorynumber=int(0)
		if (repScoreQuest>9 and repScoreQuest<1000):
			categoryname='Low'
			categorynumber=int(1)
		if (repScoreQuest>999 and repScoreQuest<20000):
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


#Script che calcola il tempo intercorso tra il post della domanda ed il post della risposta
#INPUT: - file_name: file csv che contiene l'id della risposta, la data di creazione della risposta e la data di creazione della domanda a cui
#	             fa riferimento
#OUTPUT:- output_file: file csv che contiene il tempo intercorso tra il post della domanda ed il post della risposta corrente.Tale differenza 
#	               è espressa in diversi modi: in modo compatto (tutta in ore, tutta in minuti, tutta in secondi) o nella forma gg/hh/mm/ss.

def timeResponse_csv(file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';') # DELIMITER
	
	head = dict_reader.fieldnames
	f = ['PostId','RespTimeInHoursDays','RespTimeInMinsDays','RespTimeInSecsDays', 'RespDays','RespTimeHours','RespTimeMins','RespTimeSecs']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)  # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		date_answer = datetime.datetime.strptime(row['PostCreationDate'],"%Y-%m-%d %H:%M:%S")
		date_question = datetime.datetime.strptime(row['QuestionCreationDate'],"%Y-%m-%d %H:%M:%S")
		diff = date_answer - date_question
		hours = diff.seconds / 3600
		min = diff.seconds / 60
		min2 = (diff.seconds % 3600) / 60
		sec2 = (diff.seconds % 3600) % 60
	
		
		r['RespTimeInHoursDays'] = hours + (diff.days*24)
		r['RespTimeInMinsDays'] = min + (diff.days*(60 *24))
		r['RespTimeInSecsDays'] = diff.seconds + (diff.days*(60*60*24))
		r['RespDays'] = diff.days	
		r['RespTimeHours'] = hours
		r['RespTimeMins'] = min2
		r['RespTimeSecs'] = sec2

		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed for timeresponse.csv : ', count
	return 'Done'


# Query/test che verfiica se una risposta è accettata o no 
def testAccepted(post):
	return "SELECT postid AS pid FROM acceptedanswer_mv WHERE postid = " + post + ""


#Script che verifica, per ogni risposta, se essa è una risposta accettata o meno
#INPUT: -file_name: file csv che contiene gli id delle risposte
#OUTPUT: -output_file: file csv che per ogni idrisposta, memorizza se si tratta di una risposta accettata o no


def accepted(file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';')  # DELIMITER
	
	head = dict_reader.fieldnames
	f = ['PostId', 'Successful', 'NotAccepted']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)  # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		postid= row['PostId']
		accepted = 'no'
		notaccepted = 'yes'
		

		result_set5 = execute_param_query('stackoverflowSep', testAccepted(postid))
		tot_tuple = long(result_set5.rowcount)

		if tot_tuple > 0:
			accepted = 'yes'
			notaccepted = 'no'
		
		r['Successful'] = accepted
		r['NotAccepted'] = notaccepted
		
		dict_writer.writerow(r)
		count += 1

	print 'Post processed for accepted: ', count
	return 'Done'



#Script che stabilisce se una risposta è la prima risposta che è stata postata all'interno della discussione.
#INPUT: - db: nome del db
#	- input_file: file csv che contiene l'id delle risposte e quelli della rispettiva domanda
#OUTPUT:- output:file: file csv che contiene, per ogni risposta, se questa è la prima risposta postata 

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
		idquestion = row['QuestionId']

		result_set2 = execute_param_query(db,"SELECT a_PostId AS PostFirst, MIN(a_postdate) AS DateFirst FROM answers_mv WHERE a_QuestionId = " + idquestion + ";")
 			
		idfirstanswer=0
		for tup in result_set2:
			idfirstanswer = tup[0]
	
		isfirst = 'no'  
		if (str(postid)==str(idfirstanswer)):
			isfirst = 'yes'
			
		r['IsFirstAnswer'] = isfirst
		
		writer.writerow(r)
		count += 1

	print 'Post processed for isfirst: ', count
	return 'Done'



#Script che memorizza l'ordine di arrivo delle risposte di una discussione.
#INPUT: -db : nome del db
#	-input_file: file csv che contiene gli id delle risposte da esaminare e gli id delle rispettive domande
#OUTPUT:-output_file: file csv che contiene gli id delle risposte e per ognuna l'ordine di arrivo. Man mano
#	che vengono lette le risposte, si prende l'id della domanda a cui fa riferimento e vengono recuperate tutte le risposte di quella domanda 
#	in ordine crescente. Si effettua una scansione delle risposte ed in questo modo è possibile recuperare l'informazione sul ranking per
#       quella risposta.  

def rankinganswers(db, input_file, output_file):

        dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';')
        head = dict_reader.fieldnames

        f = ['PostId','Ranking']
        writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f) # DELIMITER
        writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
        count = 0


        for row in dict_reader:
                r = {}
                r['PostId'] = row['PostId']
                postid= row['PostId']
                idquestion = row['QuestionId']


                result_set2 = execute_param_query(db,"Select a.a_postid AS AnsId, a.a_postdate, a.a_QuestionId from  answers_mv a where a.a_QuestionId=" + idquestion +";")

                idpost=0
                rank=1
                for tup in result_set2:

                        idanswer = tup[0]
                        isfirst = 'no'
                        if (str(postid)==str(idanswer)):
                                r['Ranking'] = rank
                        else:
                                rank+=1

                writer.writerow(r)
                count += 1

        print 'Post processed for ranking answers: ', count
        return 'Done'


#Script che memorizza l'allineamento tra le categorie di reputazione e tra gli score di reputazione degli autori domanda-risposta
#INPUT: - file_name: file csv che contiene id della risposta, score di reputazione dell'autore della domanda e della risposte, 
#		     numero di categoria di reputazione dell'autore della domanda e della risposta
#OUTPUT:- output_file: file csv che contiene le informazioni sull'allineamento tra le reputazioni. NB:il confronto è fatto sempre
#		       lato answer-question


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



#Script che calcola la differenza ed il ratio tra gli score di reputazione dell'autore della risposta ed autore della domanda
#INPUT: -file_name:file csv che contiene gli id delle risposte ed gli score di reputazione dell'autore della risposta e dell'autore
#	della domanda
#OUTPUT: - output_file: file csv che contiene gli id delle risposte, la differenza tra gli score di reputazione degli autori risposta-domanda
#	   e il ratio tra gli score di reputazione degli autori risposta domanda. NB: Il calcolo viene sempre effettuato lato risposta-domanda


def score_reputation_difference(file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';')
	head = dict_reader.fieldnames
	f= ['PostId', 'ScoreRepDifferenceA-Q','RatioRepScoreAQ']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f))
	count=0
	difference=0
	for row in dict_reader:
		r={}
		r['PostId'] = row['PostId']
		repscoreA = row['ReputationAnsw']
		repscoreQ = row['ReputationQuest']

		difference = int(repscoreA)-int(repscoreQ)
		ratioAQ = float(repscoreA)/float(repscoreQ)
		r['ScoreRepDifferenceA-Q']=difference
		r['RatioRepScoreAQ']=ratioAQ

		dict_writer.writerow(r)
		count+=1

	print 'Post processed for difference score', count
	return 'Done'



#Script che consente di calcolare la media della metrica di readability FRE. Si sommano le risposte che hanno un valore FRE e la somma la si divide per
#il numero di risposte che effettivamente ha un valore FRE.
#INPUT: - input_file:file csv che contiene le risposte da cui calcolare la media FRE
#OUTPUT:- valore di ritorno della media FRE ricavata dal file fornito in input.

def media_fre(input_file):
	
	dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';') # DELIMITER
	c=0
	acc_fre=0
	media_fre=0
	fre_p=0
	for row in dict_reader:
		print row['PostId']
		if(str(row['FleschReadingEase'])!= 'NONE'):
			print 'Calcolo media non none'
			fre_p = decimal.Decimal(row['FleschReadingEase'])
             	       	fre_p= fre_p*1

			c+=1
			acc_fre= acc_fre+fre_p
	
	print 'fine accumulatore'	
	media_fre= acc_fre/c
	m= decimal.Decimal(media_fre)
        decimal.getcontext().prec = 2
        decimal.getcontext().rounding = getattr(decimal,'ROUND_HALF_EVEN')

        m= m*1
	print 'num', acc_fre
	print 'den', c
	print 'media', media_fre            
	return m


#Script di utility che provvede ad avvalorare con la media FRE i campi sprovvisti che la avevano a 'None'. Viene prima calcolato il fre medio e viene 
#associato a quelle risposte che lo avevano settato a 'None'
#INPUT: - input_file: file csv che contiene le risposte con i FRE da aggiornare e le metriche visibili nello script
#OUTPUT: - output_file: file csv che contiene le risposte con i valore FRE portati alla media per i casi dove di default era settato a 'None' 
#NB: Se si vuole procedere all'arrotondamento scommetare le istruzioni commentate

def conv_metrics(input_file, output_file):

        dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';')
        head = dict_reader.fieldnames

	f = ['PostId','Body', 'Accepted','ReputationScore','ReputationCategory','Align_on_category','Align_on_score','RatioRepScoreAQ','Weekday','GMTHour','RespTimeInSecs','IsFirstAnswer','Ranking','CodeSnippet','URL','BodyLength','NumberOfEdits','AnswerScore_pre_accept_date','QuestionScore','AnswerScore','UsersAnswersAccepted','UsersQuestionsAccepted','NumberOfBadges','Topic','IsSameTopic','SentimentPositiveScore','SentimentNegativeScore','NumberOfUsersComments','CommentSentimentPositiveScore','CommentSentimentNegativeScore','ARI','FKGL','CLI','FRE','NSentences','NChars','NSyllables','NComplexWords','AVGWordsPSentence','AVGUpperCharsPPost']

        writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f) # DELIMITER
        writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header

        count = 0
        total = 0
#	ari=0
#	fkgl=0
#	cli=0
#	fre=0
#	avgw=0
#	avgu=0
        fre_medio =0
        fre_medio = decimal.Decimal(media_fre(input_file))
	decimal.getcontext().prec = 2
        decimal.getcontext().rounding = getattr(decimal,'ROUND_HALF_EVEN')

        fre_medio= fre_medio*1


	print 'fremedio restiutito', fre_medio 
	for row in dict_reader:
        	r = {}
                r['PostId'] = row['PostId']
                r['Body']=row['Body']
                r['Accepted'] = row['Accepted']
                r['ReputationScore']=row['ReputationScore']
                r['ReputationCategory'] = row['ReputationCategory']
                r['Align_on_category']= row['Align_on_category']
                r['Align_on_score']=row['Align_on_score']
                r['RatioRepScoreAQ']=row['RatioRepScoreAQ']
                r['Weekday'] = row['Weekday']
                r['GMTHour'] = row['GMTHour']
                r['RespTimeInSecs'] = row['RespTimeInSecs']
                r['IsFirstAnswer'] = row['IsFirstAnswer']
                r['Ranking'] = row['Ranking']
                r['CodeSnippet']=row['CodeSnippet']
                r['URL']=row['URL']
                r['BodyLength'] = row['BodyLength']
                r['NumberOfEdits']=row['NumberOfEdits']
                r['AnswerScore_pre_accept_date']=row['AnswerScore_pre_accept_date']
                r['QuestionScore']=row['QuestionScore']
                r['AnswerScore']=row['AnswerScore']
                r['UsersAnswersAccepted']=row['UsersAnswersAccepted']
                r['UsersQuestionsAccepted']=row['UsersQuestionsAccepted']
                r['NumberOfBadges']= row['NumberOfBadges']
                r['Topic']=row['Topic']
                r['IsSameTopic']=row['IsSameTopic']
                r['SentimentPositiveScore']=row['SentimentPositiveScore']
                r['SentimentNegativeScore']=row['SentimentNegativeScore']
                r['NumberOfUsersComments']=row['NumberOfUsersComments']
                r['CommentSentimentPositiveScore']=row['CommentSentimentPositiveScore']
                r['CommentSentimentNegativeScore']=row['CommentSentimentNegativeScore']
		if(row['FRE']=='NONE'):
			#print 'Caso None'
                	r['ARI']= str(1)
                	r['FKGL'] = str(-3.4)
		     	r['CLI']= str(0)
                        r['FRE']=fre_medio
		else:
#			ari = decimal.Decimal(row['ARI'])
#			decimal.getcontext().prec = 2
#        		decimal.getcontext().rounding = getattr(decimal,'ROUND_HALF_EVEN')
#	                ari= ari*1
#			r['ARI']=ari
			r['ARI']=row['ARI']			

#			fkgl = decimal.Decimal(row['FKGL'])
#                       decimal.getcontext().prec = 2
#                       decimal.getcontext().rounding = getattr(decimal,'ROUND_HALF_EVEN')
#                       fkgl= fkgl*1
#			r['FKGL']=fkgl
			r['FKGL']=row['FKGL']

#                        cli = decimal.Decimal(row['CLI'])
#                        decimal.getcontext().prec = 2
#                        decimal.getcontext().rounding = getattr(decimal,'ROUND_HALF_EVEN')
#                        cli= cli*1
#                	r['CLI']=cli
			r['CLI']=row['CLI']			
			
#			fre = decimal.Decimal(row['FRE'])
#                        decimal.getcontext().prec = 2
#                        decimal.getcontext().rounding = getattr(decimal,'ROUND_HALF_EVEN')
#                        fre= fre*1
#                        r['FRE']=fre
			r['FRE']=row['FRE']			

                r['NSentences']=row['NSentences']
                r['NChars']=row['NChars']
                r['NSyllables']=row['NSyllables']
                r['NComplexWords']=row['NComplexWords']

#                avgw = decimal.Decimal(row['AVGWordsPSentences'])
#                decimal.getcontext().prec = 4
#                decimal.getcontext().rounding = getattr(decimal,'ROUND_HALF_EVEN')
#                avgw= avgw*1
#                r['AVGWordsPSentence']=avgw
                r['AVGWordsPSentence']=row['AVGWordsPSentence']
                
#		avgu = decimal.Decimal(row['AVGUpperCharsPPost'])
#                decimal.getcontext().prec = 2
#                decimal.getcontext().rounding = getattr(decimal,'ROUND_HALF_EVEN')
#                avgu = avgu*1
#                r['AVGUpperCharsPPost']=avgu

	        r['AVGUpperCharsPPost']=row['AVGUpperCharsPPost']
		                         
		writer.writerow(r)
                count += 1
        total+=1

        #print 'Post processed: ', total
        print 'Post last_30days: ', count
        return 'Done'


#Script che effettua l'elaborazione delle categorie della politeness. In particolare stabilita la soglia per gli score, viene attribuita la categoria
#di politeness per una data risposta.
#INPUT: input_file: file csv che contiene l'id della risposta, gli score di polite ed impolite.
#OUTPUT: output_file: file csv che contiene l'id della risposta e la categoria di politeness associata alla risposta considerando la soglia stabilita
#NB:Se nel file di output si vogliono anche conservare gli score di polite ed impolite scommentare le istruzioni commentate 
 
def elab_politeness (input_file, output_file):
	dict_reader = csv.DictReader(open(input_file, 'r'),delimiter=';')
	head = dict_reader.fieldnames
	#f = ['PostId','Pol','Impol', 'Politeness']
	f = ['PostId', 'Politeness']
	writer = csv.DictWriter(open(output_file, 'w'), delimiter=';',fieldnames=f)
	writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	c=0
	pol=0
	impol=0
	count=0
	for row in dict_reader:
		
		r = {}
		r['PostId'] = row['PostId']
		pol = decimal.Decimal(row['Polite'])
		impol = decimal.Decimal(row['Impolite'])
		print pol
		print impol
	
		decimal.getcontext().prec = 2
		decimal.getcontext().rounding = getattr(decimal,'ROUND_HALF_EVEN')		
			
		pol= pol*1
		impol = impol*1

		#r['Pol']=pol
		#r['Impol']=impol

		if( pol > 0.78):
			r['Politeness']='Polite'
		else:
			if ( impol > 0.78):
				r['Politeness']='Impolite'
			else:
				r['Politeness']= 'Neutral'

		writer.writerow(r)
		count += 1
	print 'Post processed for politeness_csv: ', count
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

	answers_body= "SELECT al2_postID AS PostId, al2_body AS Body FROM answers_last_30days2_mv order by PostId asc"
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


#Query che estrae tutti i commenti 
all_comments_query = "SELECT c.postID AS PostId, c.score AS Score, c.text AS Body, c.userid AS UserId, c.CreationDate AS CreationDate, u.Reputation FROM Comments c inner join Users u on c.userid=u.id where c.creationDate  > date('2014-08-14') order by c.PostId asc"

#Query che estrae tutte le risposte
all_answers_query = "SELECT a_postID AS PostId, a_title AS Title, a_body AS Body, a_tags AS Tags, a_postDate AS PostCreationDate, a_score AS Score, a_ownerID AS UserId, a_ownerReputation AS ReputationAnsw, a_QuestionId AS QuestionId, a_user_quest_id AS UserQuest, a_user_quest_reputation AS ReputationQuest, a_DateQuestion AS QuestionCreationDate FROM answers_mv order by PostId asc"

#Query che estrae tutte le risposte dell'ultimo mese
all_30days_answers_query = "SELECT al2_postID AS PostId, al2_title AS Title, al2_body AS Body, al2_tags AS Tags, al2_postDate AS PostCreationDate, al2_score AS Score, al2_ownerID AS UserId, al2_ownerReputation AS ReputationAnsw, al2_QuestionId AS QuestionId, al2_user_quest_id AS UserQuest, al2_user_quest_reputation AS ReputationQuest, al2_DateQuestion AS QuestionCreationDate FROM answers_last_30days2_mv order by PostId asc"



#Script di utility che conta quante risposte ci sono per ogni topic
#INPUT: - input_file: file csv che contiene gli id delle risposte ed i topic delle risposte
#OUTPUT:- out: creazione in automatico del file che contiene il dizionario cohe conserva il 
#	       conteggio richiesto
 
def n_post_topic(input_file,out= 'conta_topic_all.txt'):
        dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';') # DELIMITER
        head = dict_reader.fieldnames
	out_file = open(out, 'w')
	d={}
	c=0
	for c in range (0,15):
		d[str(c)]=0
		c+=1 
	print d

	for row in dict_reader:
		d[row['Topic']]= d[row['Topic']]+1

	print d
	
        out_file.write(str(d)+"\n")
	
        out_file.close()
        print 'Create!'
        return 'Done'


#Script di utility che consente di effetture l'append tra due file csv aventi la medesima struttura
#INPUT: -file_name_input: primo file csv F1
#	-file_name_metric: secondo file csv F2
#OUTPUT:-output_file: file csv F3= F2 in append ad F1

def append(file_name_input, file_name_metric, output_file):
	dict_reader_1 = csv.DictReader(open(file_name_input, 'r'), delimiter=';') # DELIMITER
	dict_reader_2 = csv.DictReader(open(file_name_metric, 'r'), delimiter=';') # DELIMITER
	
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
	print 'post processed'
	print tot
	print 'Done'

	return 'Done'

#Script di utility che dato un file csv isola alcuni campi, in questo caso il body
#INPUT: - input_file: file csv completo
#OUTPUT: - output_file: file csv che contiene solo alcuni campi del file di input (in questo caso postid e body)

def isola_body( input_file, output_file):

	dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';')
	head = dict_reader.fieldnames

	f = ['PostId','Body']
	writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f) # DELIMITER
	writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header

	total = 0 
	for row in dict_reader:
		
		r = {}
		r['PostId'] = row['PostId']
		r['Body'] = row['Body']
		writer.writerow(r)
		total+=1

	print 'Post processed: ', total
	return 'Done'


#Script di utility che dato un file csv conta quante sono le risposte accettate
#INPUT: - input_file: file csv che deve contenere almeno la metrica successful o accepted
#OUTPUT: stampa a video delle risposte accettate

def conta_risposte(input_file):

        dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';') # DELIMITER
        totale_risposte=0
	totale_risposte_accettate=0
        for row in dict_reader:
             totale_risposte+=1
	     #if(str(row['Accepted'])== 'yes'):
             if(str(row['Successful'])== 'yes'):
  
	   	totale_risposte_accettate+=1
                        
        print 'Risposte totali', totale_risposte
        print 'Risposte accettate', totale_risposte_accettate
        return 'Done'




# Estrae il numero di closevotes, prima di una certa data (@Date), ottenuti dai post postati da un certo utente (@User) */
def getCloseVotes(user, date):
	return "SELECT c_ownerID as UserID, count(c_voteID) as CloseVotes FROM closevotes_mv WHERE c_ownerID = " + user + " AND cts_voteDate < date(\'" + date + "\')"


# Estrae il numero di deletionvotes, prima di una certa data (@Date), ottenuti dai post postati da un certo utente (@User) */
def getDeletionVotes(user, date):
	return "SELECT del_ownerID as UserID, count(del_voteID) as DeletionVotes FROM deletionvotes_mv WHERE del_ownerID = " + user + " AND delts_voteDate < date(\'" + date + "\')"


# Estrae il numero di favoritevotes, prima di una certa data (@Date), ottenuti dai post postati da un certo utente (@User) */
def getFavoriteVotes(user, date):
	return "SELECT f_ownerID as UserID, count(f_voteID) as FavoriteVotes FROM favoritevotes_mv WHERE f_ownerID = " + user + " AND fts_voteDate < date(\'" + date + "\')"


# Estrae il numero di modreviewvotes, prima di una certa data (@Date), ottenuti dai post postati da un certo utente (@User) */
def getModReviewVotes(user, date):
	return "SELECT m_ownerID as UserID, count(m_voteID) as ModReviewVotes FROM modreviewvotes_mv WHERE m_ownerID = " + user + " AND mts_voteDate < date(\'" + date + "\')"


# Estrae il numero di reopenvotes, prima di una certa data (@Date), ottenuti dai post postati da un certo utente (@User) */
def getReOpenVotes(user, date):
	return "SELECT ro_ownerID as UserID, count(ro_voteID) as ReOpenVotes FROM reopenvotes_mv WHERE ro_ownerID = " + user + " AND rots_voteDate < date(\'" + date + "\')"


# Estrae il numero di spamvotes, prima di una certa data (@Date), ottenuti dai post postati da un certo utente (@User) */
def getSpamVotes(user, date):
	return "SELECT sp_ownerID as UserID, count(sp_voteID) as SpamVotes FROM spamvotes_mv WHERE sp_ownerID = " + user + " AND spts_voteDate < date(\'" + date + "\')"


# Estrae il numero di undeletionvotes, prima di una certa data (@Date), ottenuti dai post postati da un certo utente (@User) */
def getUndeletionVotes(user, date):
	return "SELECT udel_ownerID as UserID, count(udel_voteID) as UndeletionVotes FROM undeletionvotes_mv WHERE udel_ownerID = " + user + " AND udelts_voteDate < date(\'" + date + "\')"



# Script che recupera il totale di close votes ottenuti dai post postati dall'autore della risposta prima della data di creazione della risposta corrente
#INPUT: - db : nome del db
#	- file_name: file csv che contiene gli id delle risposte da analizzare
#OUTPUT:-output_file: file csv che contiene, per ogni id di risposte, il numero di close votes presi dall'autore della risposta prima della
#		      data di pubblicazione della risposta considerata

def closevotes(db, file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';')
	
	head = dict_reader.fieldnames
	f = ['PostId', 'CloseVotes']
		
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		user = row['UserId']
		date = row['PostCreationDate']
		
		result_set_c = execute_param_query(db, getCloseVotes(user, date))
		
		for tup in result_set_c:
			cl_v = tup[1]
		
		r['CloseVotes'] = cl_v

		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed: ', count
	return 'Done'



# Script che recupera il totale di deletion votes ottenuti dai post postati dall'autore della risposta prima della data di creazione della risposta corrente
#INPUT: - db : nome del db
#       - file_name: file csv che contiene gli id delle risposte da analizzare
#OUTPUT:-output_file: file csv che contiene, per ogni id di risposte, il numero di deletion votes presi dall'autore della risposta prima della
#                     data di pubblicazione della risposta considerata

def deletionvotes(db, file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';')
	
	head = dict_reader.fieldnames
	f = ['PostId', 'DeletionVotes']
		
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		user = row['UserId']
		date = row['PostCreationDate']
		
		result_set_d = execute_param_query(db, getDeletionVotes(user, date))
		
		for tup in result_set_d:
			del_v = tup[1]
		
		r['DeletionVotes'] = del_v

		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed: ', count
	return 'Done'


# Script che recupera il totale di favorite votes ottenuti dai post postati dall'autore della risposta prima della data di creazione della risposta corrente
#INPUT: - db : nome del db
#       - file_name: file csv che contiene gli id delle risposte da analizzare
#OUTPUT:-output_file: file csv che contiene, per ogni id di risposte, il numero di favorite votes presi dall'autore della risposta prima della
#                     data di pubblicazione della risposta considerata

def favoritevotes(db, file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';')
	
	head = dict_reader.fieldnames
	f = ['PostId', 'FavoriteVotes']
		
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		user = row['UserId']
		date = row['PostCreationDate']
		
		result_set_f = execute_param_query(db, getFavoriteVotes(user, date))
		
		for tup in result_set_f:
			fav_v = tup[1]
		
		r['FavoriteVotes'] = fav_v

		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed: ', count
	return 'Done'


# Script che recupera il totale di moderator review votes ottenuti dai post postati dall'autore della risposta prima della data di creazione della risposta corrente
#INPUT: - db : nome del db
#       - file_name: file csv che contiene gli id delle risposte da analizzare
#OUTPUT:-output_file: file csv che contiene, per ogni id di risposte, il numero di moderator review votes presi dall'autore della risposta prima della
#                     data di pubblicazione della risposta considerata


def modreviewvotes(db, file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';')
	
	head = dict_reader.fieldnames
	f = ['PostId', 'ModeratorReviewVotes']
		
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		user = row['UserId']
		date = row['PostCreationDate']
		
		result_set_mr = execute_param_query(db, getModReviewVotes(user, date))
		
		for tup in result_set_mr:
			modr_v = tup[1]
		
		r['ModeratorReviewVotes'] = modr_v

		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed: ', count
	return 'Done'


# Script che recupera il totale di reopen votes ottenuti dai post postati dall'autore della risposta prima della data di creazione della risposta corrente
#INPUT: - db : nome del db
#       - file_name: file csv che contiene gli id delle risposte da analizzare
#OUTPUT:-output_file: file csv che contiene, per ogni id di risposte, il numero di reopen votes presi dall'autore della risposta prima della
#                     data di pubblicazione della risposta considerata

def reopenvotes(db, file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';')
	
	head = dict_reader.fieldnames
	f = ['PostId', 'ReopenVotes']
		
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		user = row['UserId']
		date = row['PostCreationDate']
		
		result_set_rov = execute_param_query(db, getReOpenVotes(user, date))
		
		for tup in result_set_rov:
			reop_v = tup[1]
		
		r['ReopenVotes'] = reop_v

		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed: ', count
	return 'Done'




# Script che recupera il totale di spam votes ottenuti dai post postati dall'autore della risposta prima della data di creazione della risposta corrente
#INPUT: - db : nome del db
#       - file_name: file csv che contiene gli id delle risposte da analizzare
#OUTPUT:-output_file: file csv che contiene, per ogni id di risposte, il numero di spam votes presi dall'autore della risposta prima della
#                     data di pubblicazione della risposta considerata


def spamvotes(db, file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';')
	
	head = dict_reader.fieldnames
	f = ['PostId', 'SpamVotes']
		
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		user = row['UserId']
		date = row['PostCreationDate']
		
		result_set_spa = execute_param_query(db, getSpamVotes(user, date))
		
		for tup in result_set_spa:
			spa_v = tup[1]
		
		r['SpamVotes'] = spa_v

		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed: ', count
	return 'Done'



# Script che recupera il totale di undeletion votes ottenuti dai post postati dall'autore della risposta prima della data di creazione della risposta corrente
#INPUT: - db : nome del db
#       - file_name: file csv che contiene gli id delle risposte da analizzare
#OUTPUT:-output_file: file csv che contiene, per ogni id di risposte, il numero di undeletion votes presi dall'autore della risposta prima della
#                     data di pubblicazione della risposta considerata


def undeletionvotes(db, file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';')
	
	head = dict_reader.fieldnames
	f = ['PostId', 'UndeletionVotes']
		
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		user = row['UserId']
		date = row['PostCreationDate']
		
		result_set_undel = execute_param_query(db, getUndeletionVotes(user, date))
		
		for tup in result_set_undel:
			undel_v = tup[1]
		
		r['UndeletionVotes'] = undel_v

		dict_writer.writerow(r)
		count += 1
	
	print 'Post processed: ', count
	return 'Done'


# Script che recupera il totale di up votes ottenuti dai post postati dall'autore della risposta prima della data di creazione della risposta corrente
#INPUT: - db : nome del db
#       - file_name: file csv che contiene gli id delle risposte da analizzare, il numero di upvotes presi su domande scritte dall'autore della risposte
#		     e numero totale di upvotes presi su altre risposte scritte dall'autore della risposta		
#OUTPUT:-output_file: file csv che contiene, per ogni id di risposte, il numero di up votes presi dall'autore della risposta prima della
#                     data di pubblicazione della risposta considerata


def calculate_tot_upvotes(file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';')
	
	head = dict_reader.fieldnames
	f = ['PostId', 'UpVotes']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		q_up = row['QuestionUpVotes']
		a_up = row['AnswerUpVotes']
		
		tot_up = int(q_up) + int(a_up)
			
		r['UpVotes'] = tot_up

		dict_writer.writerow(r)
	
	return 'Done'

# Script che recupera il totale di down votes ottenuti dai post postati dall'autore della risposta prima della data di creazione della risposta corrente
#INPUT: - db : nome del db
#       - file_name: file csv che contiene gli id delle risposte da analizzare, il numero di down votes presi su domande scritte dall'autore della risposte
#                    e numero totale di down votes presi su altre risposte scritte dall'autore della risposta
#OUTPUT:-output_file: file csv che contiene, per ogni id di risposte, il numero di down votes presi dall'autore della risposta prima della
#                     data di pubblicazione della risposta considerata

def calculate_tot_downvotes(file_name, output_file):
	dict_reader = csv.DictReader(open(file_name, 'r'), delimiter=';')
	
	head = dict_reader.fieldnames
	f = ['PostId', 'DownVotes']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f)
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		q_down = row['QuestionDownVotes']
		a_down = row['AnswerDownVotes']
		
		tot_down = int(q_down) + int(a_down)
			
		r['DownVotes'] = tot_down

		dict_writer.writerow(r)
	
	return 'Done'






#Script che effettua l'allineamento del sentiment sui post e sui commenti dell'autore. Il sentiment positivo e negativo viene ricondotto
#ad una scala 0-4.
#INPUT: -input_file: file csv che contiene i valori di sentiment da allineare
#OUTPUT:-output_file: file csv che contiene i nuovi valori di sentiment allineati


def conv_sentiment(input_file, output_file):
        dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';') # DELIMITER

        dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=dict_reader.fieldnames) # DELIMITER
        dict_writer.writerow(dict((fn,fn) for fn in dict_reader.fieldnames)) #Scrive gli header


        for row in dict_reader:


                if int(row['CommentAutSentimentNegativeScore']) >= -1:
                        row['CommentAutSentimentNegativeScore'] = str(0)
                if int(row['CommentAutSentimentPositiveScore']) <= 1:
                        row['CommentAutSentimentPositiveScore'] = str(0)

                if row['CommentAutSentimentPositiveScore'] != str(0):
                        row['CommentAutSentimentPositiveScore'] = str(int(row['CommentAutSentimentPositiveScore']) - 1)

                if row['CommentAutSentimentNegativeScore'] != str(0):
                        row['CommentAutSentimentNegativeScore'] = str((int(row['CommentAutSentimentNegativeScore']) + 1) * -1)

                if int(row['SentimentNegativeScore']) >= -1:
                        row['SentimentNegativeScore'] = str(0)
                if int(row['SentimentPositiveScore']) <= 1:
                        row['SentimentPositiveScore'] = str(0)

                if row['SentimentPositiveScore'] != str(0):
                        row['SentimentPositiveScore'] = str(int(row['SentimentPositiveScore']) - 1)

                if row['SentimentNegativeScore'] != str(0):
                        row['SentimentNegativeScore'] = str((int(row['SentimentNegativeScore']) + 1) * -1)

                dict_writer.writerow(row)

        return "Done"



#script di utility che setta i valori di default delle metriche di readability
#INPUT: -input_file: file csv che contiene le risposte
#OUTPUT:-output_file: file csv che aggiorna i valori di default delle metriche di readability nelle osservazioni del
#        file csv di input


def conv_metrics_readability(input_file, output_file):
	dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';') # DELIMITER
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=dict_reader.fieldnames) # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in dict_reader.fieldnames)) #Scrive gli header
	
	
        fre_medio =0
        fre_medio = decimal.Decimal(media_fre(input_file))
	decimal.getcontext().prec = 2
        decimal.getcontext().rounding = getattr(decimal,'ROUND_HALF_EVEN')

        fre_medio= fre_medio*1

	print 'fremedio restiutito', fre_medio 
	
	#count = 0
	for row in dict_reader:
		
		if(row['FleschReadingEase']=='NONE'):
                	row['AutomatedReadingIndex']= str(1)
                	row['FleschKincaidGradeLevel'] = str(-3.4)
		     	row['ColemanLiauIndex']= str(0)
                        row['FleschReadingEase']=fre_medio

		dict_writer.writerow(row)

	return "Done"





#Script che consente di filtrare le risposte dell'ultimo test, verificandone la presenza dell'id nel gruppo presente nella base di dati (dove sono isolati gli id
#delle risposte dell'ultimo mese).
#INPUT: - db: nome del db da interrogare
#	- inpit_file: file csv che contiene gli id delle risposte con le metriche calcolate.
#OUTPUT:- output_file: file csv con le risposte dell'ultimo mese e le metriche calcolate NB:Per velocizzare i calcoli è stato calcolato l'id della risposta più
#                     piccolo.

def onlymyanswersfiltro1(db, input_file, output_file):

	dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';') # DELIMITER
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=dict_reader.fieldnames) # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in dict_reader.fieldnames)) #Scrive gli header
	

	count = 0
	total = 0
	for row in dict_reader:
		postidi = int(row['PostId'])
		if( postidi > 22851224):

			postid= row['PostId']

			result_set5 = execute_param_query('stackoverflowSep', "SELECT a.al_postID AS PostId FROM answers_last_30days_mv a WHERE a.al_postID = " + postid + "")
			tot_tuple = long(result_set5.rowcount)

			if tot_tuple > 0:
				dict_writer.writerow(row)
				count += 1
		total+=1

	print 'Post processed: ', total
	print 'Post last_30days: ', count
	return 'Done'





#Script che permette di tagliare le risposte che non sono associate a domande chiuse o cancellate attraverso una query sulla base di dati che contiene
#gli id delle domande chiuse o cancellate.
#INPUT: - db: nome del db da interrogare
#       - input_file: file csv che contiene gli id delle risposte da filtrare
#OUTPUT:- output_file: file csv che contiene gli id delle risposte non associati a domande chiuse o cancellate.


def onlymyanswersfiltro2(db, input_file, output_file):

	dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';') # DELIMITER
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=dict_reader.fieldnames) # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in dict_reader.fieldnames)) #Scrive gli header
	

	tenute =0
	tagliate =0
	total = 0
	for row in dict_reader:
		postid= row['PostId']
 			
		result_set5 = execute_param_query('stackoverflowSep', "SELECT a.al2_postID AS PostId FROM answers_last_30days2_mv a WHERE a.al2_postID = " + postid + " and a.al2_QuestionId not in (Select c.qc_questID from questions_closed_mv c);")
		tot_tuple = long(result_set5.rowcount)

		if tot_tuple > 0:
				
			dict_writer.writerow(row)
			tenute += 1
		else:
			tagliate+=1
		total+=1

	print 'Post processed: ', total
	print 'Risposte valide:', tenute
	print 'Risposte tagliate:', tagliate
	return 'Done'



#script che elimina le risposte wiki. Gli id da eliminare sono compresi in un'apposita vista nel db.
#INPUT: -db : nome del db 
#	-input_file: file csv che contiene le risposte
#OUTPUT:-output_file: file csv che contiene le sole risposte non wiki
 
def wiki_answers_remove(db, input_file, output_file):


        dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';') # DELIMITER
        dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=dict_reader.fieldnames) # DELIMITER
        dict_writer.writerow(dict((fn,fn) for fn in dict_reader.fieldnames)) #Scrive gli header


        tenute =0
        tagliate =0
        total = 0
        for row in dict_reader:
                postid= row['PostId']

                result_set5 = execute_param_query('stackoverflowSep', "SELECT w.nwa_postID AS PostId FROM answers_last_30days_nowiki_mv w WHERE w.nwa_postID = " + postid + ";")

                tot_tuple = long(result_set5.rowcount)

                if tot_tuple > 0:
                     dict_writer.writerow(row)
                     tenute += 1
                else:
                     tagliate+=1
                total+=1

        print 'Post processed: ', total
        print 'Risposte valide:', tenute
        print 'Risposte tagliate:', tagliate
        return 'Done'


#script che elimina le risposte wiki. Gli id da eliminare sono compresi in un'apposita vista nel db.
#INPUT: -db : nome del db
#       -input_file: file csv che contiene le risposte
#OUTPUT:-output_file: file csv che contiene le sole risposte non wiki

def edit_remove( input_file, output_file):

        dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';') # DELIMITER
        dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=dict_reader.fieldnames) # DELIMITER
        dict_writer.writerow(dict((fn,fn) for fn in dict_reader.fieldnames)) #Scrive gli header


        tenute =0
        tagliate =0
        total = 0
        for row in dict_reader:
                if(str(row['NumberOfEdits'])==str('0')):
                     dict_writer.writerow(row)
                     tenute += 1
                else:
                     tagliate+=1
                total+=1

        print 'Post processed: ', total
        print 'Risposte valide:', tenute
        print 'Risposte tagliate:', tagliate
        return 'Done'


#script di utility che isola le metriche rilevanti per il nostro studio 
#INPUT: -input_file: file csv che contiene le risposte con tutte le metriche
#OUTPUT:-output_file: file csv che contiene le sole metriche di interesse

def filtravariabiliIndip( input_file, output_file):

	dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';')
	head = dict_reader.fieldnames

	f = ['PostId','Body', 'Accepted','ReputationScore','ReputationCategory','Align_on_category','Align_on_score','RatioRepScoreAQ','Weekday','GMTHour','RespTimeInSecs','IsFirstAnswer','Ranking','CodeSnippet','URL','BodyLength','NumberOfEdits','AnswerScore_pre_accept_date','QuestionScore','AnswerScore','UsersAnswersAccepted','UsersQuestionsAccepted','NumberOfBadges','Topic','IsSameTopic','SentimentPositiveScore','SentimentNegativeScore','NumberOfUsersComments','CommentSentimentPositiveScore','CommentSentimentNegativeScore','ARI','FKGL','GFI','SMOGIndex','CLI','FRE','NSentences','NChars','NSyllables','NComplexWords','AVGWordsPSentence','AVGUpperCharsPPost']
	writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f) # DELIMITER
	writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header

	count = 0
	total = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		r['Body']=row['Body']
		r['Accepted'] = row['Accepted']
		r['ReputationScore']=row['ReputationAnsw']			
		r['ReputationCategory'] = row['ReputationCategoryNumberAnsw']
                r['Align_on_category']= row['Align_on_category']
        	r['Align_on_score']=row['Align_on_score']
	        r['RatioRepScoreAQ']=row['RatioRepScoreAQ']
        	r['Weekday'] = row['Weekday']
                r['GMTHour'] = row['GMTHour']
		r['RespTimeInSecs'] = row['RespTimeInSecsDays']
                r['IsFirstAnswer'] = row['IsFirstAnswer']
                r['Ranking'] = row['Ranking']
		r['CodeSnippet']=row['CodeSnippet']
		r['URL']=row['URL']
		r['BodyLength'] = row['BodyLength']
		r['NumberOfEdits']=row['NumberOfEdits']
		r['AnswerScore_pre_accept_date']=row['AnswerScore']
		r['QuestionScore']=row['QuestionScore']
		r['AnswerScore']=row['AnswerScoreR']
		r['UsersAnswersAccepted']=row['UsersAnswersAccepted']
		r['UsersQuestionsAccepted']=row['UsersQuestionsAccepted']
		r['NumberOfBadges']= row['NumberOfBadges']
		r['Topic']=row['Topic']
		r['IsSameTopic']=row['IsSameTopic']
		r['SentimentPositiveScore']=row['SentimentPositiveScore']
		r['SentimentNegativeScore']=row['SentimentNegativeScore']
		r['NumberOfUsersComments']=row['NumberOfUsersComments']
		r['CommentSentimentPositiveScore']=row['CommentSentimentPositiveScore']
		r['CommentSentimentNegativeScore']=row['CommentSentimentNegativeScore']
		r['ARI']=row['AutomatedReadingIndex']
		r['FKGL']= row['FleschKincaidGradeLevel']
		r['GFI']=row['GunningFogIndex']
		r['SMOGIndex']=row['SMOGIndex']
		r['CLI']= row['ColemanLiauIndex']
		r['FRE']=row['FleschReadingEase']  
		r['NSentences']=row['NSentences']
		r['NChars']=row['NChars']
		r['NSyllables']=row['NSyllables']
		r['NComplexWords']=row['NComplexWords']
		r['AVGWordsPSentence']=row['AvgWordsPSentence']
		r['AVGUpperCharsPPost']=row['AvgUpperCharsPPost']
		writer.writerow(r)
		count += 1
	total+=1

	print 'Post processed: ', total
	print 'Post last_30days: ', count
	return 'Done'


#script che identifica le domande chiuse/cancellate dalla base di dati
#INPUT: -db : nome del db
#       
#OUTPUT:-output_file: file csv che contiene gli id delle domande chiuse o cancellate
#NB: id da cambiare nella query 10,11,12,13

def closed_questions10(database, output_file):
        fieldnames = ['PostId']
        dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=fieldnames) # DELIMITER
        dict_writer.writerow(dict((fn,fn) for fn in fieldnames)) #Scrive gli header
        query_delQ="SELECT postId, creationDate,PostHistoryTypeId FROM questionsHistory_mv WHERE questionsHistory_mv.creationDate = (select MAX(creationDate) from questionsHistory_mv a where questionsHistory_mv.postID = a.postId Group by a.postId Order by a.creationDate desc LIMIT 1) AND PostHistoryTypeId ='13'"
        delQ = execute_param_query(database, query_delQ)
        c = 0
        for row in delQ:
                w_row = {}
                w_row['PostId'] = row[0]
                dict_writer.writerow(w_row)
                c += 1
        print "post con id 13: "
        print c


#script che conta tutti gli edits effettuati su una risposta
#INPUT: -db : nome del db
#       -input_file: file csv che contiene le risposte
#OUTPUT:-output_file: file csv che contiene le sole risposte ed il numero totale di edit effettuati sulla risposta

def n_edits_tot(database, inputfile, output_file):

        dict_reader = csv.DictReader(open(inputfile, 'r'), delimiter=';')
        head = dict_reader.fieldnames
        # Inizializza il csv da scrivere
        fieldnames = ['PostId' , 'NumberOfEditsTotal']
        count=0
        dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=fieldnames) # DELIMITER
        dict_writer.writerow(dict((fn,fn) for fn in fieldnames)) #Scrive gli header

        for row in dict_reader:
                w_row = {}
                w_row['PostId'] = row['PostId']
                bodyedits  = execute_param_query(database, getBodyEdits(str(row['PostId'])))


                w_row['NumberOfEditsTotal'] = str(bodyedits.rowcount)
                dict_writer.writerow(w_row)
                count+=1

        print 'Processed',count
        return 'Done'


#script che conta tutti gli edits effettuati dall'autore della risposta
#INPUT: -db : nome del db
#       -input_file: file csv che contiene le risposte
#OUTPUT:-output_file: file csv che contiene le sole risposte ed il numero totale di edit effettuati dall'autore
#        della risposta, sulla sua risposta

def n_edits_author(database, inputfile, output_file):

        dict_reader = csv.DictReader(open(inputfile, 'r'), delimiter=';')
        head = dict_reader.fieldnames
        # Inizializza il csv da scrivere
        fieldnames = ['PostId' , 'NumberOfEditsTotalAuthor']
        count=0
        dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=fieldnames) # DELIMITER
        dict_writer.writerow(dict((fn,fn) for fn in fieldnames)) #Scrive gli header


        for row in dict_reader:
          
                w_row = {}
                w_row['PostId'] = row['PostId']

                bodyedits  = execute_param_query(database, getBodyAuthEdits(str(row['PostId']),str(row['UserId'])))


                w_row['NumberOfEditsTotalAuthor'] = str(bodyedits.rowcount)
                dict_writer.writerow(w_row)
                count+=1

        print 'Processed',count
        return 'Done'


#Script che crea il file .sql per riempire la vista che contiene le coppie id_domanda - topic 
#soluzione utilizzata per accelerare i tempi di esecuzione
#INPUT: - input_file: file csv contenente le informazioni circa l'id della domanda ed il topic della domanda
#OUTPUT:- output_file: file .sql che eseguito in mysql riempie la tabella topic_questions_mv 



def ins_topicQdb( input_file, output_sql_file):

	dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';')
	head = dict_reader.fieldnames

	out_file = open(output_sql_file, 'w')
	c=0
	for row in dict_reader:
		postQ = str(row['PostId'])
		topicQ = str(row['Topic'])
		query="INSERT INTO topic_questions_mv (t_postID, t_topic) VALUES ("+ postQ +"," + topicQ + ");"
		out_file.write(query+"\n")
		c+=1
	out_file.close()
	print 'Create!'
	return 'Done'


# Crea il file csv da dare in input alle funzioni che calcolano lo score di
# sentiment e le frequenze delle classi LIWC.
#
# parametri:
#	input_file: nome del file csv da cui leggere, deve contenere almeno i campi:
#			- 'PostId'
#			- 'Body' corpo del post
#	output_file: nome del file csv su cui scrivere, conterra' i campi:
#			- 'PostId'
#			- 'Corpus' che ha la concatenazione del campo 'Title' con il campo 'Body'
def dataset_liwc_senti(input_file, output_file):
	dict_reader = csv.DictReader(open(input_file, 'r'), delimiter=';') # DELIMITER
	
	head = dict_reader.fieldnames
	f = ['PostId', 'Corpus']
	
	dict_writer = csv.DictWriter(open(output_file, 'w'), delimiter=';', fieldnames=f) # DELIMITER
	dict_writer.writerow(dict((fn,fn) for fn in f)) #Scrive gli header
	
	count = 0
	for row in dict_reader:
		r = {}
		r['PostId'] = row['PostId']
		corpus = row['Body']
		
		try:
			#corpus = title + " " + body
			
			try:
				r['Corpus'] = corpus.decode('unicode_escape').encode('ascii','ignore')
			except UnicodeDecodeError:
				print r['PostId']
				try:
					r['Corpus'] = unicode(corpus).encode('ascii', 'ignore')
				except Exception:
					r['Corpus'] = unicode(corpus, errors='ignore')

			
		except Exception:
			dict_writer.writerow(r)
			continue
		dict_writer.writerow(r)
	print 'Post processed: ', count
	return 'Done'




