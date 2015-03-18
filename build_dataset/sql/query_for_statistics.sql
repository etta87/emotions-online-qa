#contaggio utenti totali
select count(*) from Users u;

#conteggio utenti per categorie
select count(distinct u.id) from Users u where (u.reputation<10);
select count(distinct u.id) from Users u where (u.reputation>9 and u.reputation<1000);
select count(distinct u.id) from Users u where (u.reputation>999 and u.reputation<20000);
select count(distinct u.id) from Users u where (u.reputation>19999);



#conteggio risposte scritte su stack overflow per categorie di utenti
select count(distinct a.Id)  From Posts a inner join Users u on u.id=a.owneruserid Where u.reputation<10 and a.posttypeid=2;
select count(distinct a.Id)  From Posts a inner join Users u on u.id=a.owneruserid Where u.reputation>9 and u.reputation<1000 and a.posttypeid=2;
select count(distinct a.Id)  From Posts a inner join Users u on u.id=a.owneruserid Where u.reputation>999 and u.reputation<20000 and a.posttypeid=2;	
Select count(distinct a.Id)  From Posts a inner join Users u on u.id=a.owneruserid Where u.reputation>19999 and a.posttypeid=2;


#conteggio risposte scritte considerate per lo studio per categorie di utenti
select count(distinct a.a_postId)  From answers_mv a Where a.a_ownerreputation<10;
select count(distinct a.a_postId)  From answers_mv a Where a.a_ownerreputation>9 and a.a_ownerreputation<1000;
select count(distinct a.a_postId)  From answers_mv a  Where a.a_ownerreputation>999 and a.a_ownerreputation<20000;
Select count(distinct a.a_postId)  From answers_mv a Where a.a_ownerreputation>19999;


#conteggio risposte scritte conseiderate per lo studio, variante 2 
#select count(distinct a.a_postId)  From answers_mv a inner join Users u on a.a_ownerid=u.id Where u.reputation<10;
#select count(distinct a.a_postId)  From answers_mv a inner join Users u on a.a_ownerid=u.id Where u.reputation>9 and u.reputation<1000;
#select count(distinct a.a_postId)  From answers_mv a inner join Users u on a.a_ownerid=u.id Where u.reputation>999 and u.reputation<20000;
#Select count(distinct a.a_postId)  From answers_mv a inner join Users u on a.a_ownerid=u.id Where u.reputation>19999;

#conteggio risposte accettate scritte per categorie di utenti
Select count(distinct a.postID)   From acceptedanswer_mv a inner join Users u on u.id=a.ownerid Where u.reputation<10;
Select count(distinct a.postID)   From acceptedanswer_mv a inner join Users u on u.id=a.ownerid Where u.reputation>9 and u.reputation<1000;
Select count(distinct a.postID)   From acceptedanswer_mv a inner join Users u on u.id=a.ownerid Where u.reputation>999 and u.reputation<20000;
Select count(distinct a.postID)   From acceptedanswer_mv a inner join Users u on u.id=a.ownerid Where u.reputation>19999;
