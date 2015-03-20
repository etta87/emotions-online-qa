import csv
from builddataset_answers import readability_metrics

#readability_metrics('../build-stackoverflow/output3/so_all_answers.csv','../build-stackoverflow/output3/read_metricsOK.csv')
readability_metrics('../build-stackoverflow/output_p2/so_answersp2.csv','../build-stackoverflow/output_p2/read_metrics.csv')

#readability_metrics('../build-stackoverflow/output3/cutanswersfine.csv','../build-stackoverflow/output3/rmetrV3.csv')
#readability_metrics('../build-stackoverflow/output3/problema_codifica.csv','../build-stackoverflow/output3/pro_cod_unicode.csv')
#verificaprint('../build-stackoverflow/output3/problema_codifica.csv')
