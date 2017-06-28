from pj import *

class JS(enum.Enum):
    FUNCTION= 'function'
    IME= 'ime_funkcije_ili_argumenta'
    OTV= '('
    ZATV= ')'
    VOTV= '{'
    VZATV='}'
    VAR= 'var'
    ZAREZ= ','
    KOMENTAR= '//'
    KOSACRTA= '/'
    TOČKAZAREZ=';'
    NAREDBA='naredba'

def js_lex(kod):
    lex= Tokenizer(kod)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak == '(': yield lex.token(JS.OTV)
        elif znak == ')': yield lex.token(JS.ZATV)
        elif znak == '{': yield lex.token(JS.VOTV)
        elif znak == '}': yield lex.token(JS.VZATV)
        elif znak == ';': yield lex.token(JS.TOČKAZAREZ)
        elif znak == ',': yield lex.token(JS.ZAREZ)
        elif znak== '/':
            if lex.čitaj()=='/':
                lex.zvijezda(lambda znak: znak != '\n')
                lex.pročitaj('\n')
                yield lex.token(JS.KOMENTAR)
            else:
                lex.vrati()
                yield lex.token(JS.KOSACRTA)
        elif znak.isalpha():
            lex.zvijezda(identifikator)
            yield lex.token(ključna_riječ(JS, lex.sadržaj) or JS.IME)
        else: lex.greška()

### Beskontekstna gramatika
# funkcija -> FUNCTION IME O_OTV argumenti O_ZATV V_OTV tijelo V_ZATV
# argumenti -> VAR IME ZAREZ argumenti | VAR IME | ε
# tijelo -> komentari naredbe | naredbe
# komentari -> KOMENTAR komentari | KOMENTAR
# naredbe -> naredba separator naredbe | naredba | ε
# separator -> TOČKAZAREZ | komentari

class Funkcija(AST('ime argumenti tijelo')):pass
class Program(AST('funkcije')):pass
class JSParser(Parser):
    def funkcija(self):
        self.pročitaj(JS.FUNCTION)
        ime= self.pročitaj(JS.IME)
        self.pročitaj(JS.OTV)
        if self >> JS.ZATV: argumenti=[]
        else:
            argumenti=[self.argument()]
            while not self >> JS.ZATV:
                self.pročitaj(JS.ZAREZ)
                argumenti.append(self.argument())
        return Funkcija(ime, argumenti, self.tijelo())

    def argument(self):
        self.pročitaj(JS.VAR)
        return self.pročitaj(JS.IME)

    def tijelo(self):
        self.pročitaj(JS.VOTV)
        while self>>JS.KOMENTAR:pass
        naredbe=[]
        while not self >> JS.VZATV:
            naredbe.append(self.naredba())
            if self>> JS.TOČKAZAREZ: pass
            elif self>> JS.KOMENTAR:
                while self>> JS.KOMENTAR: pass
            else: self.greška()
        return naredbe

    def start(self):
        funkcije=[self.funkcija()]
        while not self >> E.KRAJ: funkcije.append(self.funkcija())
        return Program(funkcije)

    def naredba(self):
        return self.pročitaj(JS.NAREDBA)



if __name__=='__main__':
    print(JSParser.parsiraj(js_lex('''\
           function ime (var x, var y, var z) {
                naredba;
           }
       ''')))
