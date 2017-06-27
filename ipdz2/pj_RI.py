from pj import *
import RI


class Ri(enum.Enum):
    OTV, ZATV, ILI, ZVIJEZDA, PLUS, UPITNIK = '()|*+?'
    PRAZAN, EPSILON, ZNAK, ESCAPE = '/0', '/1', 'a', '/'

#AKO IZA / DOLAZI BILO ŠTA OSIM /,0,1 SMATRAJ TO ZNAKOM !
def ri_lex(ri):
    lex = Tokenizer(ri)
    for znak in iter(lex.čitaj, ''):
        if znak == '/':
            lex.token(Ri.ESCAPE)
            sljedeći = lex.čitaj()
            if sljedeći == '0': yield lex.token(Ri.PRAZAN)
            elif sljedeći == '1': yield lex.token(Ri.EPSILON)
            elif not sljedeći: lex.greška('"escape"an kraj stringa')
            elif sljedeći=='(': yield lex.token(Ri.ZNAK)
            elif sljedeći==')': yield lex.token(Ri.ZNAK)
            elif sljedeći=='|': yield lex.token(Ri.ZNAK)
            elif sljedeći=='*': yield lex.token(Ri.ZNAK)
            elif sljedeći=='+': yield lex.token(Ri.ZNAK)
            elif sljedeći=='?': yield lex.token(Ri.ZNAK)
            else: lex.greška('nepostojeći "escape" znak')
        elif znak=='(': yield lex.token(Ri.OTV)
        elif znak==')': yield lex.token(Ri.ZATV)
        elif znak=='|': yield lex.token(Ri.ILI)
        elif znak=='*': yield lex.token(Ri.ZVIJEZDA)
        elif znak=='+': yield lex.token(Ri.PLUS)
        elif znak=='?': yield lex.token(Ri.UPITNIK)
        else: yield lex.token(Ri.ZNAK)


### Beskontekstna gramatika
# izraz -> disjunkt ILI izraz | disjunkt
# disjunkt -> faktor disjunkt | faktor
# faktor -> element | faktor ZVIJEZDA | faktor PLUS | faktor UPITNIK
# element -> PRAZAN | EPSILON | ZNAK | OTV izraz ZATV

class RIParser(Parser):
    def izraz(self):
        disjunkt=self.disjunkt()
        if self >> Ri.ILI: return RI.Unija(disjunkt, self.izraz())
        else: return disjunkt

    def disjunkt(self):
        faktor=self.faktor()
        if self>>{Ri.PRAZAN, Ri.EPSILON, Ri.ZNAK, Ri.OTV}:
            self.vrati()
            return RI.Konkatenacija(faktor, self.disjunkt())
        else: return faktor

    def faktor(self):   #mora ići while inače error!!
        element=self.element()
        while True:
            if self >> Ri.ZVIJEZDA: element = RI.Zvijezda(element)
            elif self >> Ri.PLUS: element = RI.Plus(element)
            elif self >> Ri.UPITNIK: element = RI.Upitnik(element)
            else: return element

    def element(self):
        if self >> Ri.PRAZAN: return RI.prazan
        elif self >> Ri.EPSILON: return RI.epsilon
        elif self >> Ri.ZNAK: return RI.Elementaran(self.zadnji.sadržaj)
        elif self >> Ri.OTV:
            uzagradi = self.izraz()
            self.pročitaj(Ri.ZATV)
            return uzagradi
        else: self.greška()


    start = izraz

if __name__ == '__main__':
    print(*ri_lex('? )a/1|/('), sep=',')
    print(RIParser.parsiraj(ri_lex('/1|a(/(c?)*')).početak())
