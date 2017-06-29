from pj import *

class AN(enum.Enum):
  BROJ=1
  MINUS='-'
  PUTA='*'
  NA='^'
  OTVORENA='('
  ZATVORENA=')'
<<<<<<< HEAD
  PLUS='+'

=======
>>>>>>> d43c9ea0b06269096f406fb2190b2353c7f89885

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
        elif znak == '-':
            yield lex.token(AN.MINUS)
        elif znak == '^':
            yield lex.token(AN.NA)
        elif znak == '(':
            yield lex.token(AN.OTVORENA)
        elif znak== ')':
            yield lex.token(AN.ZATVORENA)
        else:
            yield lex.greška()

### Beskontekstna gramatika: (desno asocirani operatori)
# izraz -> član (PLUS|MINUS) izraz | član
# član -> faktor PUTA član | faktor
# faktor -> baza NA faktor | baza
# baza -> BROJ | OTVORENA izraz ZATVORENA
class Umnožak(AST('faktori')): pass
class Potencija(AST('baza eksponent')): pass
class Razlika(AST('brojevi')):pass
class Zbroj(AST('pribrojnici')):pass

class ANParser(Parser):
    def izraz(self):
        član = self.član()
        if self >> AN.MINUS: return Razlika([član, self.izraz()])
        elif self >> AN.PLUS:
            return Zbroj([član, self.izraz()])
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
    elif izraz ** Razlika:
        f1, f2= izraz.brojevi
        if an_interpret(f1) >= an_interpret(f2):
            return an_interpret(f1)-an_interpret(f2)
        else:
            print('Nemoguće oduzeti')

    elif izraz ** Umnožak:
        f1, f2= izraz.faktori
        return an_interpret(f1)*an_interpret(f2)
    elif izraz ** Potencija:
        return an_interpret(izraz.baza)**an_interpret(izraz.eksponent)

def an_optim(izraz):
    nula, jedan=Token(AN.BROJ, '0'), Token(AN.BROJ, '1')
    if izraz ** AN.BROJ: return izraz
<<<<<<< HEAD
    elif izraz ** Razlika:
        o1, o2 = map(an_optim, izraz.brojevi)
        if o1 == nula: return E.GREŠKA
        elif o2 == nula:
            return o1
        else: return Razlika([o1, o2])
    elif izraz ** Zbroj:
        o1, o2 = map(an_optim, izraz.pribrojnici)
        if o1 == nula: return o2
        elif o2 == nula:
            return o1
        else: return Zbroj([o1, o2])

=======
    elif izraz ** Zbroj:
        o1, o2=map(an_optim, izraz.pribrojnici)
        if o1 == nula: return o2
        elif o2 == nula: return o1
        else: return Zbroj([o1, o2])
>>>>>>> d43c9ea0b06269096f406fb2190b2353c7f89885
    elif izraz ** Umnožak:
        o1, o2=map(an_optim, izraz.faktori)
        if o1 == jedan: return o2
        elif o2 == jedan: return o1
        elif nula in {o1, o2}: return nula
        else: return Umnožak([o1, o2])
    elif izraz ** Potencija:
        o_baza=an_optim(izraz.baza)
        o_eksponent= an_optim(izraz.eksponent)
        if o_eksponent == nula: return jedan
        elif o_baza== nula: return nula
        elif jedan in {o_baza, o_eksponent}: return o_baza
        else: return Potencija(o_baza, o_eksponent)
<<<<<<< HEAD




if __name__ == '__main__':
    lexer=an_lex('2*3-1*2')
    x=ANParser.parsiraj(lexer)
=======




if __name__ == '__main__': ###SMETALA MU JE FOR PETLJA!!!!
    lexer=an_lex('2+3*5')
    l2=an_lex('2*0+6*3')
    x=ANParser.parsiraj(l2)
>>>>>>> d43c9ea0b06269096f406fb2190b2353c7f89885
    x=an_optim(x)
    print(x)
    print(an_interpret(x))
