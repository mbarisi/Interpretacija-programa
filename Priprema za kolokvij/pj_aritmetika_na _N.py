from pj import *
"""nesto ne radi, a nije mi jasno štoooo"""
class AN(enum.Enum):
  BROJ=1
  PLUS='+'
  PUTA='*'
  NA='^'
  OTVORENA='('
  ZATVORENA=')'
def an_lex(kod):
    lex=Tokenizer(kod)
    for znak in iter(lex.čitaj, ''):
        if znak.isdigit():
            if znak !='0': lex.zvijezda(str.isdigit)
            yield lex.token(AN.BROJ)
        elif znak=='+':
            yield lex.token(AN.PLUS)
        elif znak == '*':
            yield lex.token(AN.PUTA)
        elif znak == '^':
            yield lex.token(AN.NA)
        elif znak == '(':
            yield lex.token(AN.OTVORENA)
        elif znak== ')':
            yield lex.token(AN.ZATVORENA)
        else:
            yield lex.greška()

### Beskontekstna gramatika: (desno asocirani operatori)
# izraz -> član PLUS izraz | član
# član -> faktor PUTA član | faktor
# faktor -> baza NA faktor | baza
# baza -> BROJ | OTVORENA izraz ZATVORENA
class Zbroj(AST('pribrojnici')): pass
class Umnožak(AST('faktori')): pass
class Potencija(AST('baza eksponent')): pass

class ANParser(Parser):
    def izraz(self):
        član = self.član()
        if self >> AN.PLUS: return Zbroj([član, self.izraz()])
        else: return član

    def član(self):
        faktor = self.faktor()
        if self >> AN.PUTA: return Umnožak([faktor, self.član()])
        else: return faktor

    def faktor(self):
        baza = self.baza()
        if self >> AN.NA: return Potencija(baza, self.faktor())
        else: return baza

    def baza(self):
        if self >> AN.BROJ: return self.zadnji
        elif self >> AN.OTVORENA:
            u_zagradi = self.izraz()
            self.pročitaj(AN.ZATVORENA)
            return u_zagradi
        else: self.greška()

    start = izraz

def an_interpret(izraz):
    if izraz ** AN.BROJ: return int(izraz.sadržaj)
    elif izraz ** Zbroj: return sum(map(an_interpret, izraz.pribrojnici))
    elif izraz ** Umnožak:
        f1, f2= izraz.faktori
        return an_interpret(f1)*an_interpret(f2)
    elif izraz ** Potencija:
        return an_interpret(izraz.baza)**an_interpret(izraz.eksponent)


<<<<<<< HEAD
if __name__ == '__main__': ###SMETALA MU JE FOR PETLJA!!!!
    lexer=an_lex('2+3')
    print(ANParser.parsiraj(lexer))
=======
if __name__ == '__main__':
    lexer=an_lex('(2+3)')

    for token in iter(lexer):
        print(token)
    mi= an_interpret(ANParser.parsiraj(lexer))
    print(mi)
>>>>>>> 1f6bc6ead729ba1a20c3cc881ab14c2178bc7ac8
