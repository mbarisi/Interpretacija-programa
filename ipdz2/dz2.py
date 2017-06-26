from pj import *

class XHTML(enum.Enum):
    OTV = '<'
    ZAT = '>'
    KOSA = '/'
    HTML = 'html'
    HEAD = 'head'
    BODY = 'body'
    OL = 'ol'
    UL = 'ul'
    LI = 'li'
    TEXT = 'NekiText'


def xhtml_lex(kod):
    lex = Tokenizer(kod)
    for znak in iter(lex.čitaj, ''):
        if znak.isspace(): lex.token(E.PRAZNO)
        elif znak == '<':
            yield lex.token(operator(XHTML, znak))
            if lex.pogledaj() == '/':
                lex.pročitaj('/')
                yield lex.token(operator(XHTML, lex.sadržaj))
            lex.zvijezda('>'.__ne__)
            yield lex.token(ključna_riječ(XHTML, lex.sadržaj, False))
            lex.pročitaj('>')
            yield lex.token(operator(XHTML, lex.sadržaj))
        else:
            lex.zvijezda('<'.__ne__)
            yield lex.token(XHTML.TEXT)


### Beskontekstna gramatika
#unutar( tag, sadrzaj) -> OTV tag ZAT sadrzaj OTV KOSA tag ZATV
#start -> unutar(HTML, blok)
#blok -> head body
#head -> unutar(HEAD, tekst)
#body -> unutar(BODY, tBody)
#tBody -> '' | tekst tbody | oLista tbody | uLista tbody
#oLista -> unutar(OL, lista)
#uLista -> unutar(UL, lista)
#lista ->'' | unutar(LI, tekst) lista | unutra(LI, oLista) lista | unutra(LI, uLista) lista
#tekst -> TEXT | '';

class XHTMLParser(Parser):
    def lista(self):
        if self >> XHTML.TEXT:
            tekst = self.zadnji
            self.pročitaj(XHTML.OTV)
            return li(tekst)
        elif self >> XHTML.OTV:
            if self >> XHTML.OL:
                self.pročitaj(XHTML.ZAT)
                oList = self.oLista()
                self.pročitaj(XHTML.KOSA)
                self.pročitaj(XHTML.OL)
                self.pročitaj(XHTML.ZAT)
                self.pročitaj(XHTML.OTV)
                return li(oList)
            elif self >> XHTML.UL:
                self.pročitaj(XHTML.ZAT)
                uList = self.uLista()
                self.pročitaj(XHTML.KOSA)
                self.pročitaj(XHTML.UL)
                self.pročitaj(XHTML.ZAT)
                self.pročitaj(XHTML.OTV)
                return li(uList)
            else:
                return li(self.tekst())
        else:
            print(ovdje)
            self.greška()

    def oLista(self):
        oList = []
        self.pročitaj(XHTML.OTV)
        self.pročitaj(XHTML.LI)
        self.pročitaj(XHTML.ZAT)
        oList.append(self.lista())
        self.pročitaj(XHTML.KOSA)
        self.pročitaj(XHTML.LI)
        self.pročitaj(XHTML.ZAT)
        while True:
            self.pročitaj(XHTML.OTV)
            if self >> XHTML.LI:
                self.pročitaj(XHTML.ZAT)
                oList.append(self.lista())
                self.pročitaj(XHTML.KOSA)
                self.pročitaj(XHTML.LI)
                self.pročitaj(XHTML.ZAT)
            else:
                return ol(oList)

    def uLista(self):
        uList = []
        self.pročitaj(XHTML.OTV)
        self.pročitaj(XHTML.LI)
        self.pročitaj(XHTML.ZAT)
        uList.append(self.lista())
        self.pročitaj(XHTML.KOSA)
        self.pročitaj(XHTML.LI)
        self.pročitaj(XHTML.ZAT)
        while True:
            self.pročitaj(XHTML.OTV)
            if self >> XHTML.LI:
                self.pročitaj(XHTML.ZAT)
                uList.append(self.lista())
                self.pročitaj(XHTML.KOSA)
                self.pročitaj(XHTML.LI)
                self.pročitaj(XHTML.ZAT)
            else:
                return ul(uList)

    def tBody(self):
        body = []
        while True:
            if self >> XHTML.TEXT:
                body.append(self.zadnji)
            elif self >> XHTML.OTV:
                if self >> XHTML.OL:
                    self.pročitaj(XHTML.ZAT)
                    body.append(self.oLista())
                    self.pročitaj(XHTML.KOSA)
                    self.pročitaj(XHTML.OL)
                    self.pročitaj(XHTML.ZAT)
                elif self >> XHTML.UL:
                    self.pročitaj(XHTML.ZAT)
                    body.append(self.uLista())
                    self.pročitaj(XHTML.KOSA)
                    self.pročitaj(XHTML.UL)
                    self.pročitaj(XHTML.ZAT)
                else:
                    return body
            else:
                self.greška()

    def head(self):
        self.pročitaj(XHTML.OTV)
        self.pročitaj(XHTML.HEAD)
        self.pročitaj(XHTML.ZAT)
        tekst = self.tekst()
        self.pročitaj(XHTML.OTV)
        self.pročitaj(XHTML.KOSA)
        self.pročitaj(XHTML.HEAD)
        self.pročitaj(XHTML.ZAT)
        return head(tekst)

    def body(self):
        self.pročitaj(XHTML.OTV)
        self.pročitaj(XHTML.BODY)
        self.pročitaj(XHTML.ZAT)
        tBody = self.tBody()
        self.pročitaj(XHTML.KOSA)
        self.pročitaj(XHTML.BODY)
        self.pročitaj(XHTML.ZAT)
        return body(tBody)

    def tekst(self):
        tekst = ''
        if self >> XHTML.TEXT:
            tekst = self.zadnji
        return tekst

    def blok(self):
        head = self.head()
        body = self.body()
        return html([head, body])

    def start(self):
        self.pročitaj(XHTML.OTV)
        self.pročitaj(XHTML.HTML)
        self.pročitaj(XHTML.ZAT)
        blok = self.blok()
        self.pročitaj(XHTML.OTV)
        self.pročitaj(XHTML.KOSA)
        self.pročitaj(XHTML.HTML)
        self.pročitaj(XHTML.ZAT)
        return blok


if __name__ == '__main__':
    ulaz = '''
        <html>
            <head> </head>
            <body>
                <ol>
                    <li>tekst</li>
                    <li>
                        <ol>
                            <li>tekst</li>
                            <li></li>
                        </ol>
                    </li>
                    <li>Jos elementa</li>
                </ol>
            </body>
        </html>
    '''
    tokeni = list(xhtml_lex(ulaz))
    print(*tokeni)
    print(XHTMLParser.parsiraj(tokeni))
