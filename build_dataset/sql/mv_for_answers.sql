use stackoverflowSep;

#vista materializzata all Answers con informazione sulla reputazione dell'autore della risposta
DROP TABLE answers1_mv;
CREATE TABLE answers1_mv (
    a1_postID INTEGER  NOT NULL PRIMARY KEY
  , a1_title TEXT
  , a1_body TEXT
  , a1_tags TEXT
  , a1_postDate   DATETIME           NOT NULL
  , a1_score INTEGER
  , a1_ownerID INTEGER   , a1_ownerReputation INTEGER, a1_QuestionId    INTEGER
  , a1_DateQuestion DATETIME, UNIQUE INDEX pID (a1_postID)
  , INDEX pDate (a1_postDate)
  , INDEX pOwner (a1_ownerID)
  , INDEX pQuest (a1_QuestionId)
);


INSERT INTO answers1_mv
SELECT p.Id, p.Title, p.Body, p.Tags, p.CreationDate, p.score, p.OwnerUserId, u.reputation, p.ParentId, q.q_postDate 
FROM Posts p inner join questions_mv q on p.parentid=q.q_postId inner join Users u on p.owneruserid=u.id where p.posttypeid = 2 and p.owneruserid <> 0;


DROP TABLE answers_mv;

#vista materializzata all Answers che contiene anche lo score di reputazione dell'autore della domanda
CREATE TABLE answers_mv (
    a_postID INTEGER  NOT NULL PRIMARY KEY
  , a_title TEXT
  , a_body TEXT
  , a_tags TEXT
  , a_postDate   DATETIME           NOT NULL
  , a_score INTEGER
  , a_ownerID INTEGER   
  , a_ownerReputation INTEGER
  , a_QuestionId    INTEGER
  , a_user_quest_id INTEGER
  , a_user_quest_reputation INTEGER
  , a_DateQuestion DATETIME, UNIQUE INDEX pID (a_postID)
  , INDEX pDate (a_postDate)
  , INDEX pOwner (a_ownerID)
  , INDEX pQuest (a_QuestionId)
);



INSERT INTO answers_mv
SELECT a.a1_postID, a.a1_title, a.a1_body, a.a1_tags, a.a1_postDate, a.a1_score, a.a1_ownerID, a.a1_ownerReputation, a.a1_QuestionId, q.q_ownerid, u.Reputation, a.a1_DateQuestion FROM answers1_mv a inner join questions_mv q on a.a1_QuestionId = q.q_postID inner join Users u on q.q_ownerID=u.id;

DROP TABLE answers1_mv;


#vista materializzata che contiene le informazione delle risposte relative a domande pubblicate nell'ultimo mese
DROP TABLE answers_last_30days2_mv;
CREATE TABLE answers_last_30days2_mv (
    al2_postID INTEGER  NOT NULL PRIMARY KEY
  , al2_title TEXT
  , al2_body TEXT
  , al2_tags TEXT
  , al2_postDate   DATETIME           NOT NULL
  , al2_score INTEGER
  , al2_ownerID INTEGER
  , al2_ownerReputation INTEGER
  , al2_QuestionId    INTEGER
  , al2_user_quest_id INTEGER
  , al2_user_quest_reputation INTEGER
  , al2_DateQuestion DATETIME, UNIQUE INDEX pID (al2_postID)
  , INDEX pDate (al2_postDate)
  , INDEX pOwner (al2_ownerID)
  , INDEX pQuest (al2_QuestionId)
);



INSERT INTO answers_last_30days2_mv
SELECT a.a_postID, a.a_title, a.a_body, a.a_tags, a.a_postDate, a.a_score, a.a_ownerID, a.a_ownerReputation, a.a_QuestionId, a.a_user_quest_id, a.a_user_quest_reputation, a.a_DateQuestion FROM answers_mv a WHERE a.a_DateQuestion > date('2014-08-14');



#creazione della tabella questions_closed_mv, riempita con il .sql prodotto dallo script python ins_questions_closeddb
CREATE TABLE questions_closed_mv (
    qc_questID INTEGER  NOT NULL PRIMARY KEY,
    UNIQUE INDEX qID (qc_questID)
);




#query per vista risposte non wiki

CREATE TABLE answers_last_30days_nowiki_mv (
    nwa_postID INTEGER  NOT NULL PRIMARY KEY,
    UNIQUE INDEX qID (nwa_postID)
);


INSERT INTO answers_last_30days_nowiki_mv
select a.al2_postID as nwa_postID from answers_last_30days2_mv a inner join Posts p on a.al2_postID=p.id where p.communityowneddate is null;



# userscommentanswers_mv
# Vista materializzata: Contiene tutti i commenti che un utente di una risposta ha scritto alla sua risposta
# la data di creazione di può creare anche di tipo date

DROP TABLE userscommentsanswers_mv;
CREATE TABLE  userscommentsanswers_mv (
	ca_Id INTEGER NOT NULL PRIMARY KEY
  ,	qa_Id INTEGER NOT NULL
  ,	userId INTEGER NOT NULL
  ,	c_text TEXT
  ,	ca_ts_creationDate DATE NOT NULL   
  ,	INDEX idx_c_Id (ca_Id)
  ,	INDEX idx_q_Id (qa_Id)
  ,	INDEX idx_userId (userId)
  ,	INDEX idx_c_ts_creationDate (ca_ts_creationDate)
  ,	INDEX idx_quest_dataVoto(qa_Id, ca_ts_creationDate)
);

INSERT INTO userscommentsanswers_mv
SELECT Comments.Id as ca_Id, answers_mv.a_postID as a_Id, answers_mv.a_ownerID as userId, Comments.Text as c_text, date(Comments.CreationDate) as ca_ts_creationDate
FROM answers_mv INNER JOIN Comments ON answers_mv.a_postId = Comments.PostId AND answers_mv.a_ownerId = Comments.UserId;
