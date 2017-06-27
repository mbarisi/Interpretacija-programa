from pj import *
import pprint

class SQL(enum.Enum):
    SELECT= 'SELECT'
    CREATE= 'CREATE'
    TABLE= 'TABLE'
    FROM= 'FROM'
    OTVORENA= '('
    ZATVORENA=')'
    BROJ=123
    TOČKAZAREZ= ';'
    KOMENTAR='--'
    IME='ime'
    ZVJEZDICA='*'
    ZAREZ=','

def sql_lex(kod):
    lex=Tokenizer(kod)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak.isdigit():
            lex.zvijezda(str.isdigit)
            yield lex.token(SQL.BROJ)
        elif znak == '-':
            lex.pročitaj('-')
            lex.zvijezda('\n'.__ne__)
            lex.pročitaj('\n')
            lex.token(SQL.KOMENTAR)
        elif znak.isalpha():
            lex.zvijezda(str.isalnum)
            yield lex.token(ključna_riječ(SQL, lex.sadržaj, False) or SQL.IME)
        else: yield lex.token(operator(SQL, znak) or lex.greška())

### Beskontekstna gramatika:
# start -> naredba | naredba start
# naredba -> ( select | create ) TOČKAZAREZ
# select -> SELECT ( ZVJEZDICA | stupci ) FROM IME
# stupci -> IME ZAREZ stupci | IME
# create -> CREATE TABLE IME OTVORENA spec_stupci ZATVORENA
# spec_stupci -> spec_stupac ZAREZ spec_stupci | spec_stupac
# spec_stupac -> IME IME | IME IME OTVORENA BROJ ZATVORENA

### Apstraktna sintaksna stabla:
# Skripta: naredbe - niz SQL naredbi, svaka završava znakom ';'
# Create: tablica, specifikacije - CREATE TABLE naredba
# Select: tablica, sve, stupci - SELECT naredba
# Stupac: ime, tip, veličina - specifikacija stupca u tablici (za Create)

class SQLParser(Parser):
    def start(self):
        naredbe=[self.naredba()]
        while not self>>E.KRAJ: naredbe.append(self.naredba())
        return Skripta(naredbe)

    def naredba(self):
        if self >> SQL.SELECT: rezultat= self.select()
        elif self >> SQL.CREATE: rezultat= self.create()
        self.pročitaj(SQL.TOČKAZAREZ)
        return rezultat

    def select(self):
        if self >> SQL.ZVJEZDICA:
            sve=True
            stupci=nenavedeno
            self.pročitaj(SQL.FROM)
        elif self >> SQL.IME:
            sve=False
            stupci=[self.zadnji]
            while not self >> SQL.FROM:
                self.pročitaj(SQL.ZAREZ)
                stupci.append(self.pročitaj(SQL.IME))
        else: self.greška()
        return Select(self.pročitaj(SQL.IME), sve, stupci)

    def create(self):
        self.pročitaj(SQL.TABLE)
        tablica= self.pročitaj(SQL.IME)
        self.pročitaj(SQL.OTVORENA)
        stupci= [self.spec_stupac()]
        while not self >> SQL.ZATVORENA:
            self.pročitaj(SQL.ZAREZ)
            stupci.append(self.spec_stupac())
        return Create(tablica, stupci)

    def spec_stupac(self):
        ime = self.pročitaj(SQL.IME)
        tip = self.pročitaj(SQL.IME)
        if self >> SQL.OTVORENA:
            veličina = self.pročitaj(SQL.BROJ)
            self.pročitaj(SQL.ZATVORENA)
        else: veličina = nenavedeno
        return Stupac(ime, tip, veličina)

class Skripta(AST('naredbe')):
    def razriješi(self):
        imena = {}
        for naredba in self.naredbe: naredba.razriješi(imena)
        return imena

class Create(AST('tablica specifikacije')):
    """CREATE TABLE naredba."""
    def razriješi(self, imena):
        tb = imena[self.tablica.sadržaj] = {}
        for stupac in self.specifikacije:
            tb[stupac.ime.sadržaj] = StupacLog(stupac)

class Select(AST('tablica sve stupci')):
    """SELECT naredba."""
    def razriješi(self, imena):
        tn = self.tablica.sadržaj
        if tn not in imena: self.tablica.nedeklaracija('nema tablice')
        tb = imena[tn]
        if self.sve:
            for log in tb.values(): log.pristup += 1
        else:
            for st in self.stupci:
                sn = st.sadržaj
                if sn not in tb:
                    st.nedeklaracija('u tablici {} nema stupca'.format(tn))
                tb[sn].pristup += 1

class Stupac(AST('ime tip veličina')): """Specifikacija stupca u tablici."""

class StupacLog(types.SimpleNamespace):
    def __init__(self, specifikacija):
        self.tip = specifikacija.tip.sadržaj
        vel = specifikacija.veličina
        if vel: self.veličina = int(vel.sadržaj)
        self.pristup = 0


if __name__ == '__main__':
    lexer=sql_lex('''
            CREATE TABLE Persons
            (
                PersonID int,
                Name varchar(255),
                Birthday date,
                Married bool,
                City varchar(9)
            );  -- Sada krenimo nešto selektirati
            SELECT Name, City FROM Persons;
            SELECT * FROM Persons;
            CREATE TABLE Trivial (ID void(0));  -- još jedna tablica
            SELECT * FROM Trivial;
            SELECT Name, Married FROM Persons;
            SELECT Name from Persons;
    ''')
    print(SQLParser.parsiraj(lexer))
