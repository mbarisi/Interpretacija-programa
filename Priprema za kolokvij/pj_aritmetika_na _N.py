from pj import *
"""nesto ne radi"""
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
class Zbroj(AST('pribrojnici')):pass
class Umnožak(AST('faktori')):pass
class Potencija(AST('baza eksponent')):pass
class ANParser(Parser):
    def izraz(self):
        član = self.član()
        if self >> AN.PLUS: return Zbroj([član, self.izraz()])
        else:
            return član

    def član(self):
        faktor= self.faktor()
        if self >> AN.PUTA: return Umnožak([faktor, self.član()])
        else:
            return faktor

    def faktor(self):
        baza = self.baza()
        if self >> AN.NA: return Potencija(baza, self.faktor())
        else:
            return baza

    def baza(self):
        if self >> AN.BROJ: return self.zadnji
        elif self >> AN.OTVORENA:
            uzagradi=self.izraz()
            self.pročitaj(AN.ZATVORENA)
            return uzagradi
        else: self.greška()

    start=izraz




if __name__ == '__main__':
    lexer=an_lex('2+3')

    for token in iter(lexer):
        print(token)
    print(ANParser.parsiraj(lexer))
