"""

Napišite leksički analizator za „programski jezik“ koji radi sa skupovima u 
kojima se nalaze cijeli brojevi (niz znamenki). Jezik treba omogućiti

deklariranje skupa (npr. SKUP S), gdje se ime skupa sastoji od jednog 
velikog slova iz engleske abecede (npr. 'S'). Operacije za rad sa 
skupom su uobičajene: provjera je li skup prazan (PRAZAN S),

ubacivanje elementa u skup (UBACI S 2345 32 41), izbacivanje 
elementa iz skupa (IZBACI S 2345 13), provjera da li je element 
u skupu (ELEMENT S 2345), vraćanje broja elemenata u skupu

(VELIČINA S), te ispis skupa (ISPIŠI S). Napišite sintaksni 
analizator za taj programski jezik (svaka vrsta naredbe odgovara 
jednom tipu apstraktnog sintaksnog stabla).

Omogućite da operacije
UBACI i IZBACI mogu primiti više brojeva. Napišite i odgovarajući 
semantički analizator (interpreter).

"""

from pj import *

"""
Skup sa cijelim brojevima
"""


class SK(enum.Enum):
    BROJ = 123
    MINUSBROJ = -123
    UBACI = "UBACI"
    IZBACI = "IZBACI"
    ELEMENT = "ELEMENT"
    VELIČINA = "VELIČINA"
    ISPIŠI = "ISPIŠI"
    PRAZAN = "PRAZAN"
    SKUP = "SKUP"  # deklaracija
    IME = "ime skupa"


"""
Pretpostavljamo kako je savaka ključna riječ odvojena razmakom od druge.
Od broja ne mora biti, ali su brojevi međusobno odn+vojeni razmakom.
"""


def pročitaj_prazno(lex):
    lex.zvijezda(lambda znak: znak != '' or znak.isspace())
    lex.token(E.PRAZNO)


def skup_lex(string):
    lex = Tokenizer(string)

    for znak in iter(lex.čitaj, ''):
        if znak != '' and znak.isspace():
            lex.token(E.PRAZNO)
            continue

        if znak.isalpha():
            lex.zvijezda(lambda znak:
                         znak != '' and znak.isalpha()
                         and not str.isspace(znak))
            if len(lex.sadržaj) == 1:
                yield lex.token(SK.IME)
            else:
                yield lex.token(ključna_riječ(SK, lex.sadržaj) or E.GREŠKA)
        elif znak.isnumeric():
            lex.zvijezda(lambda znak:
                         znak != '' and znak.isnumeric()
                         and not str.isspace(znak))
            yield lex.token(SK.BROJ)
        else:
            yield lex.token(E.GREŠKA)


class Skup_par(Parser):
    def start(self):

        naredbe = []
        while not self >> E.KRAJ:
            naredbe.append(self.naredba())
        return PROGRAM(naredbe)

    def naredba(self):
        if self >> SK.SKUP:
            return SKUP(self.pročitaj(SK.IME))

        elif self >> SK.PRAZAN:
            return PRAZAN(self.pročitaj(SK.IME))

        elif self >> SK.VELIČINA:
            return VELIČINA(self.pročitaj(SK.IME))

        elif self >> SK.ISPIŠI:
            return ISPIŠI(self.pročitaj(SK.IME))

        elif self >> SK.UBACI:
            ime = self.pročitaj(SK.IME)
            brojevi = []
            while True:
                broj = self.čitaj()

                if broj ** SK.BROJ:
                    brojevi.append(broj)
                else:
                    self.vrati()
                    break
            return UBACI(ime, brojevi)

        elif self >> SK.IZBACI:
            ime = self.pročitaj(SK.IME)
            brojevi = []
            while True:
                broj = self.čitaj()

                if broj ** SK.BROJ:
                    brojevi.append(broj)
                else:
                    self.vrati()
                    break
            return IZBACI(ime, brojevi)

        elif self >> SK.ELEMENT:
            return ELEMENT(self.pročitaj(SK.IME), self.pročitaj(SK.BROJ))
        else:
            self.greška()


def skup_definiran(ime, okolina):
    pass


class PROGRAM(AST("naredbe")):
    def izvrši(self):
        print('----------------------')
        print('Naredba: ', self)
        print('----------------------')
        okolina = {}
        out = []
        for naredba in self.naredbe:
            o = naredba.izvrši(okolina)
            out.append(o)
            if (type(o) == list and E.GREŠKA in o):
                raise Exception('greška(interpreter): ' + str(o[1]))

            print(okolina)

        if E.GREŠKA in out:
            raise Exception('Pogreška!')

        for o in out:
            print(o)


class SKUP(AST("ime")):
    def izvrši(self, okolina):
        out = 'Naredba: ' + str(self) + '\n'
        okolina[self.ime.sadržaj] = set()
        return out


class PRAZAN(AST("ime")):
    def izvrši(self, okolina):
        out = 'Naredba: ' + str(self) + '\n'
        je = ''
        ime = self.ime.sadržaj
        if ime not in okolina:
            return [E.GREŠKA, 'Skup {0} nije definiran.'.format(ime)]

        if len(okolina[ime]):
            je = 'ni'

        return out + 'out: Skup {0} {1}je prazan'.format(ime, je) + '\n'


class UBACI(AST("ime brojevi")):
    def izvrši(self, okolina):
        out = 'Naredba: ' + str(self) + '\n'

        ime = self.ime.sadržaj
        if ime not in okolina:
            return [E.GREŠKA, 'Skup {0} nije definiran.'.format(ime)]
        for broj in self.brojevi:
            okolina[ime].add(broj.sadržaj)

        return out


class IZBACI(AST("ime brojevi")):
    def izvrši(self, okolina):
        out = 'Naredba: ' + str(self) + '\n'

        ime = self.ime.sadržaj
        if ime not in okolina:
            return [E.GREŠKA, 'Skup {0} nije definiran.'.format(ime)]

        for broj in self.brojevi:
            print()
            try:
                okolina[ime].remove(broj.sadržaj)
            except (Exception):
                pass

        return out


class ELEMENT(AST("ime broj")):
    def izvrši(self, okolina):
        print('Naredba: ', self)
        ime = self.ime.sadržaj
        if ime not in okolina:
            return [E.GREŠKA, 'Skup {0} nije definiran.'.format(ime)]

        odg = 'NE'
        if self.broj.sadržaj in okolina[ime]:
            odg = 'DA'

        return out + 'out: Je li skup {0} sadrži {1}? {2}.'.format(ime, self.broj.sadržaj, odg)


class VELIČINA(AST("ime")):
    def izvrši(self, okolina):
        out = 'Naredba: ' + str(self) + '\n'

        ime = self.ime.sadržaj
        if ime not in okolina:
            return [E.GREŠKA, 'Skup {0} nije definiran.'.format(ime)]

        return out + 'out: Skup {0} sadrži {1} elemenata'.format(ime, len(okolina[ime]))


class ISPIŠI(AST("ime")):
    def izvrši(self, okolina):
        out = 'Naredba: ' + str(self) + '\n'

        ime = self.ime.sadržaj
        if ime not in okolina:
            return [E.GREŠKA, 'Skup {0} nije definiran.'.format(ime)]
        for broj in okolina[ime]:
            out = out + 'out: ' + str(broj.sadržaj)
        return out


tests = [5]
if __name__ == '__main__':
    if 1 in tests:
        print('lexer: ')
        print(*skup_lex('''\
    SKUP S UBACI 89 IZBACI 89 UBACI 7 8 9 PRAZAN S
    '''))
        # print("First, thou shalt count to {2}".format(1,2,3))
        string = '''\
                SKUP S UBACI S 89 IZBACI S 89 UBACI S 7 8 9 PRAZAN S
                '''
        print('parser: ')
        print(*Skup_par.parsiraj(skup_lex(string)))
        par = Skup_par.parsiraj(skup_lex(string))
        print('interpreter: ')
        par.izvrši()

    if 2 in tests:  # GREŠKU BACA LEXER
        string = '''\
                SKkakUP UBACI S 89 IZBACI S 89 UBACI S 7 8 9 PRAZAN S
                '''
        par = Skup_par.parsiraj(skup_lex(string))
        print('interpreter2: ')
        par.izvrši()

    if 3 in tests:  # GREŠKU BACA PARSER
        string = '''\
                SKUP UBACI S 89 IZBACI S 89 UBACI S 7 8 9 PRAZAN S      '''
        print('parser: ')
        print(*skup_lex(string))
        par = Skup_par.parsiraj(skup_lex(string))

        print('interpreter2: ')
        par.izvrši()

    if 4 in tests:  # GREŠKU BACA interpreter
        string = '''\
                SKUP K UBACI S 89 IZBACI S 89 UBACI S 7 8 9 PRAZAN S      '''

        print('parser: ')
        print(*skup_lex(string))
        par = Skup_par.parsiraj(skup_lex(string))

        print('interpreter2: ')
        par.izvrši()

    if 5 in tests:
        string = '''\
                SKUP S SKUP K UBACI S 89 IZBACI K 8 9 UBACI S 7 8 9 PRAZAN S      '''
        print('parser: ')
        print(*skup_lex(string))
        par = Skup_par.parsiraj(skup_lex(string))

        print('interpreter3: ')
        par.izvrši()







