# Carica il file csv che contiene il dataset.
# Converte i campi CodeSnippet,Successful, Is Same Topic,  da 'yes', 'no' a TRUE, FALSE.
# Avvia la regressione logistica.

library(biglm)
#source('orcip_etta.R')

stackoverflow_dataset_1msr25pv <- read.csv('../../../../build-stackoverflow/output3/rebuildprof/dataset_prime_n_x_R_1802.csv',sep=';')
#stackoverflow_dataset_1msr25pv <- read.csv('../../../../build-stackoverflow/output3/rebuildprof/dataset_prime_n_x_R_1802_verifica.csv',sep=';')
#stackoverflow_dataset_1msr25p <- read.csv('../../../../build-stackoverflow/output3/rebuildprof/dataset368correz_sentiment2.csv',sep=';')



stackoverflow_dataset_1msr25pv$CodeSnippet <- sapply(as.character(stackoverflow_dataset_1msr25pv$CodeSnippet),switch,'yes'=as.logical(TRUE),'no'=as.logical(FALSE))
stackoverflow_dataset_1msr25pv$Successful <- sapply(as.character(stackoverflow_dataset_1msr25pv$Successful),switch,'yes'=as.logical(TRUE),'no'=as.logical(FALSE))

stackoverflow_dataset_1msr25pv$IsSameTopic <- sapply(as.character(stackoverflow_dataset_1msr25pv$IsSameTopic),switch,'yes'=as.logical(TRUE),'no'=as.logical(FALSE))



#bigglm
stackoverflow_logit_ans_msr225pv <- bigglm(formula=Successful ~ NChars + URL + AVGUpperCharsPPost + I(IsSameTopic=='FALSE') + CodeSnippet +
                                ReputationScore + ReputationScoreQuest + NumberOfBadges + SentimentPositiveScore +
                                SentimentNegativeScore + CommentAutSentimentPositiveScore + CommentAutSentimentNegativeScore,
                                data=stackoverflow_dataset_1msr25pv, family=binomial())

capture.output(summary(stackoverflow_logit_ans_msr225pv), file="01.Regr_log.txt")
#orcipwald.bigglm(stackoverflow_logit_ans_msr225p)





