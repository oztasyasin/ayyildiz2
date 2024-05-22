import numpy as np
import heapq

class Problem:
    def __init__(self, h, hedef_testi, konum):
        self.ilk_konum = konum
        self.hedef_konum = None
        self.eylemler = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        self.h = h
        self.g = 1
        self.hedef_testi = hedef_testi

class Node:
    def __init__(self, parent=None, durum=None):
        self.parent = parent
        self.durum = durum
        self.g = self.h = self.f = 0

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return self.f == other.f

class Ajan:
    counter = 0
    
    def __init__(self, cevre):
        self.cevre = cevre
        self.problem = Problem(self.h, self.hedef_testi, cevre[1])
        dunya = cevre[0]
        self.m = len(dunya)
        self.n = len(dunya[0])
        self.algi = self.algila()
        x, y = konum = self.algi[0]
        
        dunyam = np.zeros((self.m, self.n), dtype='int')
        dunyam[x][y] = 1
        
        self.durum = [dunyam, konum]
        self.id = Ajan.counter + 1
        Ajan.counter += 1
    
    def h(self, durum):
        x, y = durum[1]
        for i in range(self.m):
            for j in range(self.n):
                if self.cevre[0][i][j] == 'k':
                    return abs(x - i) + abs(y - j)
        return float('inf')
    
    def hedef_testi(self, durum):
        return self.cevre[0][durum[1][0]][durum[1][1]] == 'k'
    
    def guncelle_durum(self, konum):
        self.durum[1] = konum
        self.durum[0][konum[0]][konum[1]] += 1
    
    def algila(self):
        x, y = 0, 0 
        engeller = []
        kapi = None
        for i in range(self.m):
            for j in range(self.n):
                if self.cevre[0][i][j] == 'd':
                    engeller.append((i, j))
                elif self.cevre[0][i][j] == 'k':
                    kapi = (i, j)
        return [(x, y), engeller, kapi]
    
    def karar_al(self, algi, derinlik=None):
        hedef = algi[2]
        return self.arama_yap(self.durum, derinlik)
    
    def icra_et(self, eylemler, n=None):
        if n is None:
            n = len(eylemler)
        for eylem in eylemler[:n]:
            self.guncelle_durum(eylem)
    
    def genislet(self, nod, kuyruk, incelendi):
        for eylem in self.problem.eylemler:
            yeni_konum = (nod.durum[1][0] + eylem[0], nod.durum[1][1] + eylem[1])
            if 0 <= yeni_konum[0] < self.m and 0 <= yeni_konum[1] < self.n:
                if self.cevre[0][yeni_konum[0]][yeni_konum[1]] != 'd' and yeni_konum not in incelendi:
                    yeni_node = Node(nod, [nod.durum[0], yeni_konum])
                    yeni_node.g = nod.g + 1
                    yeni_node.h = self.h(yeni_node.durum)
                    yeni_node.f = yeni_node.g + yeni_node.h
                    heapq.heappush(kuyruk, (yeni_node.f, yeni_node))
    
    def cozum(self, nod):
        yol = []
        while nod:
            yol.append(nod.durum[1])
            nod = nod.parent
        return yol[::-1]
    
    def arama_yap(self, durum, derinlik=None):
        baslangic_node = Node(None, durum)
        baslangic_node.g = baslangic_node.h = baslangic_node.f = 0
        kuyruk = []
        heapq.heappush(kuyruk, (baslangic_node.f, baslangic_node))
        incelendi = set()
        
        while kuyruk:
            _, mevcut_node = heapq.heappop(kuyruk)
            mevcut_konum = mevcut_node.durum[1]
            
            if self.cevre[0][mevcut_konum[0]][mevcut_konum[1]] == 'k':
                return self.cozum(mevcut_node)
            
            incelendi.add(mevcut_konum)
            self.genislet(mevcut_node, kuyruk, incelendi)
        
        return None

def main():
    labirent = [[0,  0,  0,  0, 'd',  0,  0,   0,   0,  'k'],
                [0,  0,  0,  0, 'd',  0,  0,   0,   0,  0],
                [0,  0,  0,  0, 'd',  0,  0,   0,   0,  0],
                [0,  0,  0,  0, 'd',  0,  0,   0,   0,  0],
                [0,  0,  0,  0, 'd',  0,  0,   0,   0,  0],
                [0,  0,  0,  0, 'd',  0,  0,   0,   0,  0],
                [0,  0,  0,  0,  0,  'd', 0,   0,   0,  0],
                [0,  0,  0,  0, 'd',  0, 'd',  0,   0,  'd'],
                [0,  0,  0,  0,  0,   0, 'd', 'd', 'd', 0],
                [0,  0,  0,  0, 'd', 'd',  0, 'd',  0,  0]]

    # Ajanı başlatma ve çözümü bulma
    ajan = Ajan([labirent, (0, 0)])
    cozum_yolu = ajan.karar_al(ajan.algi)
    print("Çözüm Yolu:", cozum_yolu)

main()
