all_affect_new <- matrix(c(72696,765,602,30522),nrow=2, dimnames= list("all"= c("classifallOK","classifallKO"),"all-aff" = c("ClassifOK","classifKO")))
all_affect_new
all_clearness_new <- matrix(c(72844,617,622,30502),nrow=2, dimnames= list("all"= c("classifallOK","classifallKO"),"all-cles" = c("ClassifOK","classifKO")))
all_clearness_new
all_social_new <- matrix(c(72074,1387,1221,29903),nrow=2, dimnames= list("all"= c("classifallOK","classifallKO"),"all-soc" = c("ClassifOK","classifKO")))
all_social_new
all_time_new <- matrix(c(72369,1092,893,30231),nrow=2, dimnames= list("all"= c("classifallOK","classifallKO"),"all-cles" = c("ClassifOK","classifKO")))
all_time_new
all_affansw_new <- matrix(c(73284,177,162,30962),nrow=2, dimnames= list("all"= c("classifallOK","classifallKO"),"all-soc" = c("ClassifOK","classifKO")))
all_affansw_new
all_affcomments_new <- matrix(c(72710,751,606,30518),nrow=2, dimnames= list("all"= c("classifallOK","classifallKO"),"all-soc" = c("ClassifOK","classifKO")))
all_affcomments_new

allVSallnoAffect_new <- mcnemar.test(all_affect_new)
allVSallnoClearness_new <- mcnemar.test(all_clearness_new)
allVSallnoSocial_new <- mcnemar.test(all_social_new)
allVSallnoTime_new <- mcnemar.test(all_time_new)
allVSallnoAffansw_new <- mcnemar.test(all_affansw_new)
allVSallnoAffcomm_new <- mcnemar.test(all_affcomments_new)

capture.output(allVSallnoAffect_new, file="mc_nemar_all_allnoAffect_new.txt")
capture.output(allVSallnoClearness_new, file="mc_nemar_all_allnoClearness_new.txt")
capture.output(allVSallnoSocial_new, file="mc_nemar_all_allnoSocial_new.txt")
capture.output(allVSallnoTime_new, file="mc_nemar_all_allnoTime_new.txt")
capture.output(allVSallnoAffansw_new, file="mc_nemar_all_allnoAffectAnswer_new.txt")
capture.output(allVSallnoAffcomm_new, file="mc_nemar_all_allnoAffectComments_new.txt")
