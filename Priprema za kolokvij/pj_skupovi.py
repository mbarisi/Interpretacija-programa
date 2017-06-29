from pj import *

class S(enum.Enum):
    SKUP='SKUP'
    UBACI='UBACI'
    IZBACI='IZBACI'
    VELIČINA='VELIČINA'
    ELEMENT='ELEMENT'
    PRAZAN='PRAZAN'
    ISPIŠI='ISPIŠI'
    BROJ=123
    MINUSBROJ=-123
    ID='S'

def skup_lex(string):
    lex = Tokenizer(string)
    znak = lex.čitaj()
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak.isalpha():
            lex.zvijezda(lambda znak:znak != '' and znak.isalpha() and not str.isspace(znak))
            if len(lex.sadržaj) == 1:
                yield lex.token(S.ID)
            else:
                lex.zvijezda(str.isalpha)
                yield lex.token(ključna_riječ(S, lex.sadržaj, False) or E.GREŠKA)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(S.BROJ)
        elif znak =='-':
            idući=lex.čitaj()
            if idući.isdigit():
                lex.zvijezda(str.isdigit)
                yield lex.token(S.MINUSBROJ)
            else:
                lex.greška("očekivana znamenka nakon -")
        else:
            lex.greška()


## Beskontekstna gramatika
# start -> naredba start | ε
# naredba -> deklaracija | provjera | ubaci | izbaci | veličina | ispiši
# deklaracija -> SKUP ID
# provjera -> PRAZAN ID
# ubaci -> UBACI ID brojevi
# izbaci -> IZBACI ID brojevi
# veličina -> VELIČINA ID
# ispiši -> ISPIŠI ID

class SParser(Parser):
    def start(self):
        naredbe = []
        while not self >> E.KRAJ: naredbe.append(self.naredba())
        return Program(naredbe)

    def naredba(self):
        if self >>S.SKUP: return Deklaracija(self.pročitaj(S.ID))
        elif self>>S.PRAZAN: return Provjera(self.pročitaj(S.ID))
        elif self>>S.VELIČINA: return Veličina(self.pročitaj(S.ID))
        elif self>>S.ISPIŠI: return Ispiši(self.pročitaj(S.ID))
        elif self>> S.ELEMENT: return Element(self.pročitaj(S.ID), self.pročitaj(S.BROJ, S.MINUSBROJ))
        elif self>>S.UBACI:
            ime=self.pročitaj(S.ID)
            brojevi=[]
            while True:
                broj=self.čitaj()

                if broj ** S.BROJ:
                    brojevi.append(broj)
                else:
                    self.vrati()
                    break
            return Ubaci(ime,brojevi)

        elif self>>S.IZBACI:
            ime = self.pročitaj(S.ID)
            brojevi=[]
            while True:
                broj=self.čitaj()

                if broj ** S.BROJ:
                    brojevi.append(broj)
                else:
                    self.vrati()
                    break
            return Izbaci(ime,brojevi)

class Program(AST('naredbe')):
    def izvrši(self):
        memorija = {}
        izlazi = []
        for naredba in self.naredbe: izlazi.append(naredba.izvrši(memorija))
        return izlazi

class Deklaracija(AST('skup')):
    def izvrši(self,mem):
        def izvrši(self, mem):
            mem[self.skup.sadržaj] = []
            print(mem)

class Provjera(AST('skup')):
    def izvrši(self, mem):
        if not len(mem[self.skup.sadržaj]):
            print('Skup', self.skup.sadržaj, 'je prazan')

class Veličina(AST('skup')):
    def izvrši(self, mem):
        print('Skup sadrži {0} elemenata', len(mem[self.skup.sadržaj]))

class Ispiši(AST('skup')):
    def izvrši(self,mem):
        print(self.skup.sadržaj)
        try:
            for broj in mem[self.skup.sadržaj]:
                print(broj.sadržaj, ' ')
        except (Exception):
            pass

class Ubaci(AST('skup elementi')):
    def izvrši(self, mem):
        ime=self.skup.sadržaj
        try:
            for broj in self.elementi:
                mem[ime].add(broj.sadržaj)
        except (Exception):
            pass

class Izbaci(AST('skup elementi')):
    def izvrši(self, mem):
        try:
            for broj in self.elementi:
                mem[self.skup.sadržaj].remove(broj.sadržaj)
        except (Exception): pass

class Element(AST('skup element')):
    def izvrši(self, mem):
        if self.element.sadržaj in mem[self.skup.sadržaj]:
            print('Element skupa je')
        else:
            print('Nije element skupa')

if __name__=='__main__':
    string = '''\
                    SKUP S UBACI S 3 ISPIŠI S   '''
    print('parser: ')
    print(*skup_lex(string))
    par = SParser.parsiraj(skup_lex(string))

    print('interpreter3: ')
    par.izvrši()