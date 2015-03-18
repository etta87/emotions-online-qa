use stackoverflowSep;


#vista che isola i close votes (validi solo su domande)
DROP TABLE closevotes_mv;    
CREATE TABLE closevotes_mv (
    c_postID INTEGER  NOT NULL 
  , c_ownerID INTEGER NOT NULL
  , c_postDate   DATETIME           NOT NULL
  , c_voteDate    DATETIME         NOT NULL
  , cts_voteDate DATE NOT NULL  
  , c_voteID INTEGER NOT NULL PRIMARY KEY
  , INDEX pID (c_postID)
  , INDEX oID (c_ownerID)
  , INDEX pDate (c_postDate)
  , INDEX vDate (c_voteDate)
  , INDEX v_ts_Date (cts_voteDate)
  , UNIQUE INDEX vID (c_voteID)
 , INDEX user_datavoto (c_ownerID, cts_voteDate)
);


INSERT INTO closevotes_mv
SELECT Posts.Id, Posts.OwnerUserId, Posts.CreationDate, Votes.CreationDate, date(Votes.CreationDate), Votes.Id 
FROM Posts INNER JOIN Votes ON Posts.Id = Votes.PostId 
WHERE Votes.VoteTypeId = 6
;


#vista che isola i deletion votes
DROP TABLE deletionvotes_mv;
CREATE TABLE deletionvotes_mv (
    del_postID INTEGER  NOT NULL 
  , del_ownerID INTEGER NOT NULL
  , del_postDate   DATETIME           NOT NULL
  , del_voteDate    DATETIME         NOT NULL
  , delts_voteDate DATE NOT NULL  
  , del_voteID INTEGER NOT NULL PRIMARY KEY
  , INDEX pID (del_postID) 
  , INDEX oID (del_ownerID)
  , INDEX pDate (del_postDate)
  , INDEX vDate (del_voteDate)
  , INDEX v_ts_Date (delts_voteDate)
  , UNIQUE INDEX vID (del_voteID)
 , INDEX user_datavoto (del_ownerID, delts_voteDate)
);


INSERT INTO deletionvotes_mv
SELECT Posts.Id, Posts.OwnerUserId, Posts.CreationDate, Votes.CreationDate, date(Votes.CreationDate), Votes.Id 
FROM Posts INNER JOIN Votes ON Posts.Id = Votes.PostId 
WHERE Votes.VoteTypeId = 10
;



#vista che isola i favorite votes
DROP TABLE favoritevotes_mv;
CREATE TABLE favoritevotes_mv (
    f_postID INTEGER  NOT NULL 
  , f_ownerID INTEGER NOT NULL
  , f_postDate   DATETIME           NOT NULL
  , f_voteDate    DATETIME         NOT NULL
  , fts_voteDate DATE NOT NULL  
  , f_voteID INTEGER NOT NULL PRIMARY KEY
  , INDEX pID (f_postID)
  , INDEX oID (f_ownerID)
  , INDEX pDate (f_postDate)
  , INDEX vDate (f_voteDate)
  , INDEX v_ts_Date (fts_voteDate)
  , UNIQUE INDEX vID (f_voteID)
 , INDEX user_datavoto (f_ownerID, fts_voteDate)
);


INSERT INTO favoritevotes_mv
SELECT Posts.Id, Posts.OwnerUserId, Posts.CreationDate, Votes.CreationDate, date(Votes.CreationDate), Votes.Id 
FROM Posts INNER JOIN Votes ON Posts.Id = Votes.PostId 
WHERE Votes.VoteTypeId = 5
;



#vista che isola i moderator review votes
DROP TABLE modreviewvotes_mv;
CREATE TABLE modreviewvotes_mv (
    m_postID INTEGER  NOT NULL 
  , m_ownerID INTEGER NOT NULL
  , m_postDate   DATETIME           NOT NULL
  , m_voteDate    DATETIME         NOT NULL
  , mts_voteDate DATE NOT NULL  
  , m_voteID INTEGER NOT NULL PRIMARY KEY
  , INDEX pID (m_postID)
  , INDEX oID (m_ownerID)
  , INDEX pDate (m_postDate)
  , INDEX vDate (m_voteDate)
  , INDEX v_ts_Date (mts_voteDate)
  , UNIQUE INDEX vID (m_voteID)
 , INDEX user_datavoto (m_ownerID, mts_voteDate)
);


INSERT INTO modreviewvotes_mv
SELECT Posts.Id, Posts.OwnerUserId, Posts.CreationDate, Votes.CreationDate, date(Votes.CreationDate), Votes.Id 
FROM Posts INNER JOIN Votes ON Posts.Id = Votes.PostId 
WHERE Votes.VoteTypeId = 15
;



#vista che isola i reopen votes
DROP TABLE reopenvotes_mv;
CREATE TABLE reopenvotes_mv (
    ro_postID INTEGER  NOT NULL 
  , ro_ownerID INTEGER NOT NULL
  , ro_postDate   DATETIME  NOT NULL
  , ro_voteDate    DATETIME  NOT NULL
  , rots_voteDate DATE NOT NULL  
  , ro_voteID INTEGER NOT NULL PRIMARY KEY
  , INDEX pID (ro_postID)
  , INDEX oID (ro_ownerID)
  , INDEX pDate (ro_postDate)
  , INDEX vDate (ro_voteDate)
  , INDEX v_ts_Date (rots_voteDate)
  , UNIQUE INDEX vID (ro_voteID)
 , INDEX user_datavoto (ro_ownerID, rots_voteDate)
);


INSERT INTO reopenvotes_mv
SELECT Posts.Id, Posts.OwnerUserId, Posts.CreationDate, Votes.CreationDate, date(Votes.CreationDate), Votes.Id 
FROM Posts INNER JOIN Votes ON Posts.Id = Votes.PostId 
WHERE Votes.VoteTypeId = 7
;


#vista che isola gli undeletion votes
DROP TABLE undeletionvotes_mv;
CREATE TABLE undeletionvotes_mv (
    udel_postID INTEGER  NOT NULL 
  , udel_ownerID INTEGER NOT NULL
  , udel_postDate   DATETIME           NOT NULL
  , udel_voteDate    DATETIME         NOT NULL
  , udelts_voteDate DATE NOT NULL  
  , udel_voteID INTEGER NOT NULL PRIMARY KEY
  , INDEX pID (udel_postID)
  , INDEX oID (udel_ownerID)
  , INDEX pDate (udel_postDate)
  , INDEX vDate (udel_voteDate)
  , INDEX v_ts_Date (udelts_voteDate)
  , UNIQUE INDEX vID (udel_voteID)
 , INDEX user_datavoto (udel_ownerID, udelts_voteDate)
);


INSERT INTO undeletionvotes_mv
SELECT Posts.Id, Posts.OwnerUserId, Posts.CreationDate, Votes.CreationDate, date(Votes.CreationDate), Votes.Id 
FROM Posts INNER JOIN Votes ON Posts.Id = Votes.PostId 
WHERE Votes.VoteTypeId = 11
;




