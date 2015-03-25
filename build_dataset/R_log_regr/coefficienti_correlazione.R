st_ov_dataset <- read.csv('../../../../build-stackoverflow/output3/may+sep/rebuild2/04c.Expert_first_answers.csv',sep=';')

cor_pears <- cor.test(st_ov_dataset$ReputationScore, st_ov_dataset$CommentAutSentimentPositiveScore, method = "pearson")
capture.output(summary(cor_pears), file="07a.corpears_repscore_sentposcom_prob.txt")


#cor_spearman <- cor.test(st_ov_dataset$ReputationScore, st_ov_dataset$CommentAutSentimentPositiveScore, method = "spearman")
#capture.output(summary(cor_spearman), file="07b.corspe_repscore_sentposcom_prob.txt")


cor_pears2 <- cor.test(st_ov_dataset$ReputationScore, st_ov_dataset$CommentAutSentimentNegativeScore, method = "pearson")
capture.output(summary(cor_pears2), file="08a.corpears_repscore_sentnegcom_prob.txt")

#cor_spearman2 <- cor.test(st_ov_dataset$ReputationScore, st_ov_dataset$CommentAutSentimentNegativeScore, method = "spearman")
#capture.output(summary(cor_spearman2), file="08b.corpears_repscore_sentnegcom_prob.txt")


cor_pears22 <- cor.test(st_ov_dataset$CommentAutSentimentPositiveScore,st_ov_dataset$ReputationScore, method = "pearson")
capture.output(summary(cor_pears22), file="09a.corpears_repscore_sentposcom_prob.txt")


#cor_spearman22 <- cor.test(st_ov_dataset$CommentAutSentimentPositiveScore,st_ov_dataset$ReputationScore, method = "spearman")
#capture.output(summary(cor_spearman22), file="09b.corspe_repscore_sentposcom_prob.txt")


cor_pears22 <- cor.test(st_ov_dataset$CommentAutSentimentNegativeScore,st_ov_dataset$ReputationScore, method = "pearson")
capture.output(summary(cor_pears22), file="10a.corpears_repscore_sentnegcom_prob.txt")

#cor_spearman22 <- cor.test(st_ov_dataset$CommentAutSentimentNegativeScore,st_ov_dataset$ReputationScore, method = "spearman")
#capture.output(summary(cor_spearman22), file="10b.corpears_repscore_sentnegcom_prob.txt")


