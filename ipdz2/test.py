from pj import *

class XHTML(enum.Enum):
	OTVHTML = '<html>'
	OTVHEAD = '<head>'
	OTVBODY = '<body>'
	ZATVHTML = '</html>'
	ZATVHEAD = '</head>'
	ZATVBODY = '</body>'
	OTVOL = '<ol>'
	OTVUL = '<ul>'
	OTVLI = '<li>'
	ZATVOL = '</ol>'
	ZATVUL = '</ul>'
	ZATVLI = '</li>'
	PRAZAN = '\n\t '
	TEKST = 'nekitekst'


def zadaca_lex(kod):
	lex = Tokenizer(kod)
	for znak in iter(lex.čitaj, ''):
		if znak == '<':
			lex.vrati()
			lex.pročitaj('<')
			prvo = lex.čitaj()
			if prvo == '/':
				drugo = lex.čitaj()
				for izraz in iter(zatvoren(drugo, lex)):
					yield izraz
			else:
				for izraz in iter(otvoren(prvo, lex)):
					yield izraz
		else:
			lex.zvijezda(lambda znak: znak not in ['<' , '>' , ''])
			if (lex.sadržaj) and (not lex.sadržaj.strip()):
				yield lex.token(XHTML.PRAZAN)

			else:
				yield lex.token(XHTML.TEKST)

def zatvoren(drugo, lex):
	if drugo == 'h':
		treće = lex.čitaj()
		if treće == 't':
			lex.pročitaj('m')
			lex.pročitaj('l')
			lex.zvijezda(str.isspace or '')
			lex.pročitaj('>')
			yield lex.token(XHTML.ZATVHTML)
		elif treće == 'e':
			lex.pročitaj('a')
			lex.pročitaj('d')
			lex.zvijezda(str.isspace or '')
			lex.pročitaj('>')
			yield lex.token(XHTML.ZATVHEAD)
	elif drugo == 'b':
		lex.pročitaj('o')
		lex.pročitaj('d')
		lex.pročitaj('y')
		lex.zvijezda(str.isspace or '')
		lex.pročitaj('>')
		yield lex.token(XHTML.ZATVBODY)
	elif drugo == 'u':
		lex.pročitaj('l')
		lex.zvijezda(str.isspace or '')
		lex.pročitaj('>')
		yield lex.token(XHTML.ZATVUL)
	elif drugo == 'o':
		lex.pročitaj('l')
		lex.zvijezda(str.isspace or '')
		lex.pročitaj('>')
		yield lex.token(XHTML.ZATVOL)
	elif drugo == 'l':
		lex.pročitaj('i')
		lex.zvijezda(str.isspace or '')
		lex.pročitaj('>')
		yield lex.token(XHTML.ZATVLI)
	else:
		yield lex.token(lex.greška())

def otvoren(drugo, lex):
	if drugo == 'h':
		treće = lex.čitaj()
		if treće == 't':
			lex.pročitaj('m')
			lex.pročitaj('l')
			lex.zvijezda(str.isspace or '')
			lex.pročitaj('>')
			yield lex.token(XHTML.OTVHTML)
		elif treće == 'e':
			lex.pročitaj('a')
			lex.pročitaj('d')
			lex.zvijezda(str.isspace or '')
			lex.pročitaj('>')
			yield lex.token(XHTML.OTVHEAD)
	elif drugo == 'b':
		lex.pročitaj('o')
		lex.pročitaj('d')
		lex.pročitaj('y')
		lex.zvijezda(str.isspace or '')
		lex.pročitaj('>')
		yield lex.token(XHTML.OTVBODY)
	elif drugo == 'u':
		lex.pročitaj('l')
		lex.zvijezda(str.isspace or '')
		lex.pročitaj('>')
		yield lex.token(XHTML.OTVUL)
	elif drugo == 'o':
		lex.pročitaj('l')
		lex.zvijezda(str.isspace or '')
		lex.pročitaj('>')
		yield lex.token(XHTML.OTVOL)
	elif drugo == 'l':
		lex.pročitaj('i')
		lex.zvijezda(str.isspace or '')
		lex.pročitaj('>')
		yield lex.token(XHTML.OTVLI)
	else:
		yield lex.token(lex.greška())



"""
dokument -> OTV HTML ZATV u_html OTV KOSACRTA HTML ZATV

u_html -> ((OTV HEAD ZATV) TEKST (OTV KOSACRTA HEAD ZATV)) ((OTV BODY ZATV) u_body (OTV KOSACRTA BODY ZATV)) 

u_body  -> TEKST u_body  | LISTA u_body | EPS

LISTA -> (OTV OL ZATV) u_listi (OTV KOSACRTA OL ZATV) | (OTV UL ZATV) u_listi (OTV KOSACRTA UL ZATV)

u_listi -> (OTV LI ZATV) u_li (OTV KOSACRTA LI ZATV) u_listi | epsilon

u_li -> TEKST | viselisti

viselisti -> LISTA viselisti | EPS 
"""

class zadaca_parser(Parser):
	def start(self):
		while self >> XHTML.PRAZAN: pass
		self.pročitaj(XHTML.OTVHTML)
		uhtml=self.uhtml()
		self.pročitaj(XHTML.ZATVHTML)
		while self >> XHTML.PRAZAN: pass
		if not self >> E.KRAJ: self.greška()
		return Program(uhtml)

	def uhtml(self):
		head = self.head()
		body = self.body()
		return Html(head, body)

	def head(self):
		while self >> XHTML.PRAZAN: pass
		self.pročitaj(XHTML.OTVHEAD)
		tekst = self.tekst()
		self.pročitaj(XHTML.ZATVHEAD)
		return Head(tekst)


	def body(self):
		elementi = []
		while self >> XHTML.PRAZAN: pass
		self.pročitaj(XHTML.OTVBODY)
		while self >> XHTML.PRAZAN: pass
		while not self>>XHTML.ZATVBODY:
			elementi.append(self.element())
			while self >> XHTML.PRAZAN: pass

		while self >> XHTML.PRAZAN: pass
		return Body(elementi)


	def tekst(self):
		tekst = ''
		if self >> XHTML.TEKST:
			tekst = self.zadnji
		return tekst

	def element(self):
		sadržaj = []
		if self >> XHTML.TEKST:
			return Tekst(self.zadnji)
		elif self >> XHTML.OTVOL:
			while self >> XHTML.PRAZAN: pass
			while not self >> XHTML.ZATVOL:
				sadržaj.append(self.li())
				while self >> XHTML.PRAZAN: pass

			return Lista(sadržaj)

		elif self >> XHTML.OTVUL:
			while not self >> XHTML.ZATVOL:
				sadržaj.append(self.li())
				while self >> XHTML.PRAZANTXT: pass
			return Lista(sadržaj)

		else:
			self.greška()

	def li(self):
		sadrzi = []
		if self >> XHTML.OTVLI:
			while self >> XHTML.PRAZAN: pass
			if self >> XHTML.TEKST:
				self.vrati()
				sadrzi.append(self.element())
				self.pročitaj(XHTML.ZATVLI)
			else:
				while not self >> XHTML.ZATVLI:
					self.pročitaj(XHTML.OTVOL, XHTML.OTVUL)
					self.vrati()
					sadrzi.append(self.element())
					while self >> XHTML.PRAZAN: pass
			return Li(sadrzi)
		else:
			self.greška()


class Program(AST('html')):
	def izvrši(self):
		self.html.izvrši()


class Html(AST('head body')):
	def izvrši(self):
		self.head.izvrši()
		self.body.izvrši()

class Head(AST('tekst')):
	def izvrši(self):
		pass

class Body(AST('tijelo')):
	def izvrši(self):
		for el in self.tijelo:
			el.izvrši()

class Element(AST('element')):
	def izvrši(self, gdje=''):
		self.element.izvrši(gdje)

class Tekst(AST('string')):
	def izvrši(self, gdje=''):
		print(gdje, self.string.sadržaj)

class Lista(AST('članovi_liste')):
	def izvrši(self, gdje=''):
		print(len(self.članovi_liste))
		kraj = ''
		for član in self.članovi_liste:
			print(kraj)
			član.izvrši(str(gdje) + '\t')
			kraj = '\n'

class Li(AST('lielementi')):
	def izvrši(self, gdje=''):

		gdje = str(gdje) + '*'
		print(gdje)
		for el in (self.lielementi):
			el.izvrši(str(gdje))
		if not self.lielementi:
			print(gdje)

if __name__ == '__main__':
	ulaz = '''
          <html>
              <head></head>
              <body>
                  <ol>
                      <li>Računarstvo</li>
                      <li>
                          <ol>
                              <li>Interpretacija programa</li>
                              <li></li>
                          </ol>
                      </li>
                      <li>Matematika</li>
                  </ol>
              </body>
          </html>
      '''
	tokeni = list(zadaca_lex(ulaz))
	print(*tokeni)
	print(zadaca_parser.parsiraj(tokeni))
	zadaca_parser.parsiraj(tokeni).izvrši()