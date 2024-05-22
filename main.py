#Bu kod A* algoritmanın bir çevre programı içinde kullanımını gösteriyor.
#Ajan bir matrix dünyasında labirent içinden çıkış kapısını arıyor..
#Ajan labirent haritasını bilmiyor(duvarları gezdikçe keşfediyor). 
#Ajanın donanımları:
#i-  gps sensörü (hücre konumunu algılayabilir)
#ii- engel sensörü(komşu hücredeki duvarları ve sınırları algılar),
#iii-kapı sensörü (aynı hücredeki çıkış kapısını algılar)

#Bu kod ayrıca python da nesneye yonelik programla yeteneginizde geliştirecektir.

#Code Author, Zeki Yetgin, April 2024.
import copy as cp
import numpy as np

class Problem():
    def __init__(self, h, hedef_testi,konum): #formule edilmis problem
        self.ilk_konum = konum
        self.hedef_konum = (9,9)
        self.eylemler=[(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.h=h
        self.g=1
        self.hedef_testi=hedef_testi
        
class Ajan():
    counter=0 # static(class) degiskeni; ajana ID vermek icin kullanilacak 
    def __init__(self, cevre):
        self.cevre=cevre #dis dunyaya bir referans (tum ajanlar icin ortak)

        self.problem=Problem(self.h, self.hedef_testi,cevre[1]) 

        # çevre değişkenleri alınıyor, gps, engel ve kapi sensörlerinden gelen bilgiler
        dunya=cevre[0]
        self.m=len(dunya)  #labirent büyüklüğü (m x n) biliniyor 
        self.n=len(dunya[0])
        self.algi=self.algila()
        x,y=konum=self.algi[0]  #mevcut konum alındı

        dunyam = np.zeros((self.m,self.n),dtype='int') #ajan başlangıçta hiçbirşey bilmiyor
        dunyam[x][y] = 1               #ziyaret sayıları takip edilecek

        self.durum = [dunyam, konum]  #durum ile cevre benzer formata sahip, çünkü durum dış dünyanın bir yansımasıdır
        self.id =Ajan.counter+1 # her ajana tekil bir ID verelim
        Ajan.counter +=1
        
    # hedefe olan tahmini uzaklık h = mevcut konumun, hedef konuma olan oklid uzakligi    
    def h(self,durum):
        x1,y1=durum[1] #mevcut konum
        x2,y2=self.problem.hedef_konum #hedef konum
        return(x1 - x2) ** 2 + (y1 - y2) ** 2    

    def hedef_testi(self,durum): #mevcut konum hedef konum mu 
        #return self.algi[2] #ödev-2 nin 2.uygulaması için bu satır kullanılabilir
        return durum[1]==self.problem.hedef_konum
    
    def guncelle_durum(self, algi=None,eylem=None): #Durum ya eylem yada algi neticesinde degisir 
        if eylem:
            x,y = eylem
            self.durum[1]=(x,y) #konum guncelle
            self.durum[0][x][y] += 1  #ziyaret sayisini bir arttir
        if algi:  #algi[0]:konum, algi[1]:komşu duvar konumları
            dunyam= self.durum[0]  
            self.durum[1]=algi[0]  #konum guncelle
            for (x,y) in algi[1]: dunyam[x][y]=-1 #komsu karelerde duvar olduğunu iç duruma yansıt 

    def algila(self):   #cevre ile sensorler yoluyla etkilesim var. gps(algi[0]), engel(algi[1]) ve kapı (algi[2]) algılama
           dunya= self.cevre[0]
           x0,y0 =konum= self.cevre[1] #Ajanın konumunu al.
    
           duvarliste=[]
           for eylem in self.problem.eylemler:# komsu karelerde duvar algıla              
              sonraki_pos = (x0 + eylem[0], y0 + eylem[1])
              x, y = sonraki_pos
              # sinirlari aşma durumunu algıla(engel sensörü)
              if x > (self.m - 1) or x < 0 or y > (self.n -1) or y < 0: continue
              # engel durumunu algıla(engel sensörü)
              if dunya[x][y] == 'd':  duvarliste.append(sonraki_pos) # duvar konumunu listeye ekle
           kapiVarmi=dunya[x0][y0] == 'k'
           algi=[konum,duvarliste,kapiVarmi]
           self.algi=algi #son sensör bilgilerini sakla 
           return algi 
    
    def karar_al(self, algi,derinlik=None): # bu algi ustune karar al: hedefe goturecek eylem dizisi planla
        self.guncelle_durum(algi=algi)       
        plan = self.arama_yap(self.durum,derinlik) # mevcut durumdan hedefe eylem dizisi planla
        return plan

    def icra_et(self, eylemler, n=None): # n: planin ilk n eylemini uygula, cevre ile etkilesim var
       if (n is None): n=len(eylemler)-1 # n verilmemisse tum planı uygula demektir
       for i in range(n) :
            x,y=eylemler[i+1]
            if (x,y) in self.algi[1]:
                print((x,y),"konumunda duvar var.Plan yarıda bırakıldı")
                return False #yol üzerinde duvar varsa dur
            self.cevre[1]=(x,y)              # eylemimi cevreye yansit=ilerle
            algi=self.algila()               # yeni konumda algilama yap
            self.guncelle_durum(algi, eylem=[x,y])  # eylemimim ve algim neticesini ic durumuma yansit
            print(self.id,":",eylemler[i],"-->",eylemler[i+1]," : uygulandi")
            if self.hedef_testi(self.durum):
                print("Zaten hedefteyiz..")
                return False          #eylemi durdur eger hedefe ulasilmissa
       return True

    def genislet(self, nod, kuyruk,incelendi):
        dunyam=nod.durum[0] # nodun temsil ettigi dunya
        # child nodlari kuyruga ekle
        for eylem in self.problem.eylemler:# komsu kareler              
            # child nod pozisyonunu al
            x0, y0 = nod.durum[1]
            sonraki_pos = (x0 + eylem[0], y0 + eylem[1])
            x, y = sonraki_pos
        
            # dunyanin sinirlarini asma, sonraki durum her zaman uygun olmali
            if x > (self.m - 1) or x < 0 or y > (self.n -1) or y < 0: continue

            if dunyam[x][y] < 0:  continue # nod pozisyonunda bir duvar var mi..                             

            # tekrardan kacin!
            if sonraki_pos in incelendi: continue
            
            #sonraki dunyayının ziyaret durumunu guncelle 
            sonrakiDunya=cp.deepcopy(dunyam) #kuyruktaki her nodun, bağımsız bir durumu olmalı
            sonrakiDunya[x][y] += 1
            child = Node(nod, durum=[sonrakiDunya, sonraki_pos]) #yeni pozisyona karsilik gelen child yarat 

            # f, g, ve h degerlerini hesapla  
            child.g = nod.g + self.problem.g
            child.h = self.problem.h(child.durum)
            #child.f = max(nod.f,child.g + child.h) #monoton olmayan heuristic icin yorumu aç
            child.f = child.g + child.h
            # childi kuyruga (agaca) ekle
            kuyruk.append(child)   

    def cozum(self, nod):
        path = []
        current = nod
        while current is not None:
           path.append(current.durum[1])
           current = current.parent
        return path[::-1] # Return reversed path

    def arama_yap(self,durum, derinlik):    # maliyet sinirli A* algoritma, ders notlarindaki algoritma
        """A* Algorithm: returns a list of tuples as a path from the current to the end"""
        ilk_nod = Node(None, durum) # mevcut dugumu yarat
        kuyruk=[]
        incelendi=[]
        kuyruk.append(ilk_nod) # mevcut nodu kuyruga ekle

        while len(kuyruk) > 0:  # hedefe ulasana kadar agaci genislet
            mevcut_nod = kuyruk.pop(0) # ilk elemanini uzaklastir
            mevcut_konum = mevcut_nod.durum[1]
            if self.problem.hedef_testi(mevcut_nod.durum) or (mevcut_nod.g == derinlik):
                return self.cozum(mevcut_nod)
            incelendi.append(mevcut_konum) # gözden geçirilen durumu, incelendi listesine at
            self.genislet(mevcut_nod, kuyruk, incelendi) # nodu genislet ve kuyrugu f ye gore sirala
            kuyruk.sort(key=lambda x: x.f)
  
class Node():
    def __init__(self, parent=None, durum=None):
        self.parent = parent
        self.durum = durum
        self.g = self.h = self.f = 0
    
#cevre programi
def main():
    labirent = [[0,  0,  0,  0, 'd',  0,  0,   0,   0,  0],
                [0,  0,  0,  0, 'd',  0,  0,   0,   0,  0],
                [0,  0,  0,  0, 'd',  0,  0,   0,   0,  0],
                [0,  0,  0,  0, 'd',  0,  0,   0,   0,  0],
                [0,  0,  0,  0, 'd',  0,  0,   0,   0,  0],
                [0,  0,  0,  0, 'd',  0,  0,   0,   0,  0],
                [0,  0,  0,  0,  0,  'd', 0,   0,   0,  0],
                [0,  0,  0,  0, 'd',  0, 'd',  0,   0,  'd'],
                [0,  0,  0,  0,  0,   0, 'd', 'd', 'd', 0],
                [0,  0,  0,  0, 'd', 'd',  0, 'd',  0,  'k']]
    
    cevre = [labirent, (0, 0)]
    ajan1 = Ajan(cevre)
    while not ajan1.hedef_testi(ajan1.durum):
        algi = ajan1.algila()
        plan = ajan1.karar_al(algi)
        print("Plan: ", plan)
        ajan1.icra_et(plan)

main()
