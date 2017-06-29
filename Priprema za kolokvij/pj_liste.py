from pj import *

class LST(enum.Enum):
    IME='ime'
    BROJ=123
    MINUSBROJ=-123
    LISTA='LISTA'
    PRAZNA='PRAZNA'
    UBACI='UBACI'
    IZBACI='IZBACI'
    DOHVATI='DOHVATI'
    KOLIKO='KOLIKO'
    ID='L1'

def lista_lex(string):
    lex= Tokenizer(string)
    znak=lex.čitaj()
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak == 'L':
            id = lex.čitaj()
            if id.isdigit() and id!='0': yield lex.token(LST.ID)
            else: lex.greška('očekivana znamenka veća od nule')
        elif znak.isalpha():
            lex.zvijezda(str.isalpha)
            yield lex.token(ključna_riječ(LST, lex.sadržaj, False) or E.GREŠKA)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(LST.BROJ)
        elif znak =='-':
            idući=lex.čitaj()
            if idući.isdigit():
                lex.zvijezda(str.isdigit)
                yield lex.token(LST.MINUSBROJ)
            else: lex.greška("očekivana znamenka nakon -")
        else: lex.greška()

## Beskontekstna gramatika
# start -> naredba start | ε
# naredba -> deklaracija | provjera | ubaci | izbaci | dohvati | duljina
# deklaracija -> LISTA ID
# provjera -> PRAZNA ID
# ubaci -> UBACI ID ( BROJ | MINUSBROJ ) BROJ
# izbaci -> IZBACI ID BROJ
# dohvati -> DOHVATI ID BROJ
# duljina -> KOLIKO ID


class Program(AST('naredbe')):
    def izvrši(self):
        memorija={}
        izlazi=[]
        for naredba in self.naredbe: izlazi.append(naredba.izvrši(memorija))
        return izlazi

class Deklaracija(AST('lista')):
    def izvrši(self,mem):
        mem[self.lista.sadržaj]=[]
        print(mem)

class Provjera(AST('lista')):
    def izvrši(self,mem):
        if not len(mem[self.lista.sadržaj]):
            print ('Lista', self.lista.sadržaj, 'je prazna')

class Ubaci(AST('lista element pozicija')):
    def izvrši(self,mem):
        mem[self.lista.sadržaj].append(self.element.sadržaj)
        print(mem)

class Izbaci(AST('lista pozicija')):
    def izvrši(self,mem):
        pozicija=int(self.pozicija.sadržaj)
        del mem[self.lista.sadržaj][pozicija]

class Dohvati(AST('lista broj')):
    def izvrši(self, mem):
        pozicija = int(self.broj.sadržaj)
        print(mem[self.lista.sadržaj][pozicija])

class Duljina(AST('Lista')):
    def izvrši(self, mem):
        return len(mem[self.lista.sadržaj])


class LSTParser(Parser):
    def start(self):
        naredbe=[]
        while not self>>E.KRAJ: naredbe.append(self.naredba())
        return Program(naredbe)

    def naredba(self):
        if self>>LST.LISTA: return Deklaracija(self.pročitaj(LST.ID))
        elif self>>LST.PRAZNA: return Provjera(self.pročitaj(LST.ID))
        elif self>>LST.UBACI: return Ubaci(self.pročitaj(LST.ID), self.pročitaj(LST.BROJ, LST.MINUSBROJ), self.pročitaj(LST.BROJ))
        elif self>>LST.IZBACI: return Izbaci(self.pročitaj(LST.ID), self.pročitaj(LST.BROJ))
        elif self>>LST.DOHVATI: return Dohvati(self.pročitaj(LST.ID), self.pročitaj(LST.BROJ))
        elif self>>LST.KOLIKO: return Duljina(self.pročitaj(LST.ID))
        else: self.greška()

if __name__=='__main__':
    print(*lista_lex('lista L1 prazna ubaci -2345 izbaci L9 dohvati 3 koliko tr'))
    program = LSTParser.parsiraj(lista_lex('''lista L1  lista L3 ubaci L3 45 0  dohvati L3 0'''))
    program.izvrši()