########################## ÜNİVERSİTELERİN ETKİNLİĞİ ####################################################
# Bu kod, python ile indirilip temizlenen veriyi kullanarak, universiteler için performans indeksini yaratacaktır.
# Kod yaratilan performans endekslerini excel dosyasina yazdiracaktir.
# rm(list=ls(all=TRUE))
args <- commandArgs(trailingOnly=TRUE)
options(warn=-1)
library(readxl) # Excel dosyasını yüklemek için
library(sfaR) # SFA modelini çalıştırmak için
library(openxlsx)
library(xlsx)
# Get the directory where this R script is located
script.dir <- getwd()
setwd(script.dir)
save_eff=args[1]
# save_eff <- readline(prompt="Save Efficiencies? Yes=1, No=0")
## Distribution) specification for the onesided error term. 10 different distributions are available:
#1) 'hnormal', for the half normal distribution (Aigner et al. 1977, Meeusen and Vandenbroeck 1977)
#2) 'exponential', for the exponential distribution
#3) 'tnormal' for the truncated normal distribution (Stevenson 1980)
#4) 'rayleigh', for the Rayleigh distribution (Hajargasht 2015)
#5) 'uniform', for the uniform distribution (Li 1996, Nguyen 2010)
#6) 'gamma', for the Gamma distribution (Greene 2003)
#7) 'lognormal', for the log normal distribution (Migon and Medici 2001, Wang and Ye 2020)
#8) 'weibull', for the Weibull distribution (Tsionas 2007)
#9) 'genexponential', for the generalized exponential distribution (Papadopoulos 2020)
#10) 'tslaplace', for the truncated skewed Laplace distribution (Wang 2012).
wb = createWorkbook()
jj=0
year.names=seq(2015,2022,1) # Yil isimleri
dist.names=c('hnormal','exponential','tnormal','rayleigh','lognormal',
             'weibull','genexponential','tslaplace')
w=c(3,7,7,7,6,6,6,6,6,6,6,4,5)/100
w=w/sum(w)
weighted.avg<-function(data,w){
  w[which(is.na(data))]=NA
  w[which(!is.na(data))]=w[which(!is.na(data))]/sum(w[which(!is.na(data))])
  data0=data[which(!is.na(data))]
  avg=sum(data0*w,na.rm=T)
  if (all(is.na(data))){
    avg=NA
  }
  avg
}

weighted.median<-function(data,w){
  data0=data[which(!is.na(data))]
  ind=order(data0)
  w0=w[which(!is.na(data))]/sum(w[which(!is.na(data))])
  if (!is.null(w0)){
    w0=w0[ind]
    data0=data0[ind]
    ind0=min(which(cumsum(w0)>=0.5))
    if (length(data0) %% 2 == 0){
      wmed=as.numeric((data0[ind0]+data[ind0+1])/2)
    }else wmed=as.numeric(data0[ind0])
  }else wmed=NA
  wmed
}
for (dist.name in dist.names[1]){ # simdilik hnormal dagilim kullanalim.
  
  print(dist.name)
  jj=0
  for (year.name in year.names){
    data0 <- read_excel("../data/Hamveri 26102024.xlsx", sheet=paste0(year.name)) # Not: İlgili yılın verisi yıl.xlsx formatında kaydedilmemli
    output.names=grep("^[y]", names(data0), value=TRUE)
    input.names=grep("^[x]", names(data0), value=TRUE)
    input.reg.str=paste0("log(",input.names[1],")")
    for (str.name in input.names[2:length(input.names)]){
      input.reg.str=(paste0(input.reg.str,"+log(",str.name,")"))
    }
    
    n=nrow(data0) # Universite sayısı
    EFF=data0[,1:1]
    
    ######## Cobb Douglas (production function) half normal distribution (BC92 Model) ###########
    
    for (depvar in output.names){
      eval(parse(text=paste0("try({res <- sfacross(formula = log(",depvar,") ~",input.reg.str,
                             ", udist = dist.name, data = data0, S = 1, method = 'bfgs')},silent=T)"))) # SFA tahmini
      
      # Create output directory if it doesn't exist
      output_dir <- "SFA Regression Tables with 13 vars"
      if (!dir.exists(output_dir)) {
        dir.create(output_dir, recursive = TRUE)
      }
      
      err0=try({
        sink(file=paste0(output_dir,'/SFA_',year.name,'_',depvar,'_',dist.name,'.txt'))
        print(summary(res))
        sink()
      },silent=T)
      
      eff0 <- efficiencies(res) # Verimlilik Hesabi
      eff=eff0$teJLMS
      if (is.null(eff)) eff=eff0$teJLMS1
      uni.ind=as.numeric(rownames(model.frame(res$dataTable))) # Verimlilik hesaplanan gözlemler
      mat0=as.matrix(rep(NA,n),ncol=1)
      mat0[uni.ind]=eff
      colnames(mat0)<-depvar
      EFF=cbind(EFF,mat0)
    }
    mat=EFF
    data1=as.matrix(EFF[,2:dim(EFF)[2]])
    colnames(mat)=c(colnames(EFF)[1],paste(colnames(data1),"-Skor",sep=""))
    mat.med0=as.matrix(sapply(1:n,function(x) weighted.median(data1[x,],w)),ncol=1)
    colnames(mat.med0)<-"Medyan-Skor"
    mat.mean0=as.matrix(sapply(1:n,function(x) weighted.avg(data1[x,],w)),ncol=1)
    colnames(mat.mean0)<-"Ortalama-Skor"
    mat.EFF.rank=sapply(2:dim(EFF)[2],function(x) rank(-EFF[,x],na.last="keep"))
    colnames(mat.EFF.rank)<-paste(colnames(EFF[,2:dim(EFF)[2]]),'-Sıralama',sep="")
    mat0=cbind(rank(-mat.mean0,na.last="keep"),rank(-mat.med0,na.last="keep"))
    colnames(mat0)<-c("Ortalama-Sıralama","Medyan-Sıralama")
    mat=cbind(mat,mat.mean0,mat.med0,mat.EFF.rank,mat0)
    eval(parse(text=paste0("s",jj+1,"=createSheet(wb,","\'",year.name,"\'",")")))
    eval(parse(text=paste0("addDataFrame(mat, sheet=s",jj+1,", startColumn=1,startRow=1,row.names=F,col.names = T)")))
    jj=jj+1
  }
}
xlsx.file.name='SFA Skorlar 26102024.xlsx'
if (file.exists(xlsx.file.name)) file.remove(xlsx.file.name)
saveWorkbook(wb, xlsx.file.name)