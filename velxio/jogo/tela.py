from machine import Pin, SPI
import ili9341
import framebuf
import gc

spi = SPI(2, baudrate=40000000, sck=Pin(18), mosi=Pin(23), miso=Pin(19))
display = ili9341.ILI9341(spi, cs=Pin(5, Pin.OUT), dc=Pin(2, Pin.OUT), rst=Pin(4, Pin.OUT))

VAZIO = 0
TOUPEIRA = 1
ESMAGADA = 2

# converte a cor para o formato que a tela entende
def cor(r, g, b):
    c = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return ((c & 0xFF) << 8) | (c >> 8)

PRETO = cor(0, 0, 0)
BRANCO = cor(255, 255, 255)
AMARELO = cor(255, 214, 0)
FUNDO_TITULO = cor(30, 30, 46)
GRAMA = cor(76, 160, 60)
GRAMA_ESCURA = cor(52, 120, 44)
TERRA = cor(50, 30, 18)
PELO = cor(140, 92, 50)
PELO_ESCURO = cor(104, 66, 34)
FOCINHO = cor(240, 150, 160)
CORES_BOTOES = [cor(230, 40, 40), cor(40, 190, 70), cor(250, 210, 30)]

# desenho de um buraco de 64 x 64, reaproveitado em todos
pixels_buraco = bytearray(64 * 64 * 2)
buraco = framebuf.FrameBuffer(pixels_buraco, 64, 64, framebuf.RGB565)

# guarda o que já está na tela para não desenhar de novo
campo_desenhado = False
titulo_desenhado = None
pontos_desenhados = [None, None]
buracos_desenhados = [[None] * 3, [None] * 3]

# escreve o texto ampliado, com o centro em centro_x
def texto_grande(texto, centro_x, y, escala, cor_texto, cor_fundo):
    largura = len(texto) * 8
    letras = framebuf.FrameBuffer(bytearray(largura), largura, 8, framebuf.MONO_VLSB)
    letras.text(texto, 0, 0, 1)
    pixels = bytearray(largura * escala * 8 * escala * 2)
    quadro = framebuf.FrameBuffer(pixels, largura * escala, 8 * escala, framebuf.RGB565)
    quadro.fill(cor_fundo)
    for coluna in range(largura):
        for linha in range(8):
            if letras.pixel(coluna, linha):
                quadro.fill_rect(coluna * escala, linha * escala, escala, escala, cor_texto)
    display.desenhar(centro_x - largura * escala // 2, y, largura * escala, 8 * escala, pixels)
    gc.collect()

def elipse(centro_x, centro_y, raio_x, raio_y, cor_forma):
    for linha in range(-raio_y, raio_y + 1):
        metade = int(raio_x * (1 - (linha * linha) / (raio_y * raio_y)) ** 0.5)
        buraco.hline(centro_x - metade, centro_y + linha, 2 * metade + 1, cor_forma)

# orelhas, corpo, olhos, focinho e dentes
def desenhar_toupeira():
    elipse(17, 16, 5, 5, PELO_ESCURO)
    elipse(47, 16, 5, 5, PELO_ESCURO)
    elipse(32, 30, 17, 18, PELO)
    buraco.fill_rect(15, 30, 35, 21, PELO)
    elipse(25, 26, 4, 4, BRANCO)
    elipse(39, 26, 4, 4, BRANCO)
    elipse(26, 27, 2, 2, PRETO)
    elipse(38, 27, 2, 2, PRETO)
    elipse(32, 35, 5, 3, FOCINHO)
    buraco.fill_rect(29, 39, 3, 5, BRANCO)
    buraco.fill_rect(33, 39, 3, 5, BRANCO)

# toupeira achatada com olhos em X e estrelas
def desenhar_esmagada():
    elipse(32, 46, 22, 8, PELO)
    for x in (22, 36):
        buraco.line(x, 42, x + 6, 48, PRETO)
        buraco.line(x + 6, 42, x, 48, PRETO)
    for x, y in ((12, 22), (32, 12), (52, 22)):
        buraco.hline(x - 5, y, 11, AMARELO)
        buraco.vline(x, y - 5, 11, AMARELO)
        buraco.line(x - 3, y - 3, x + 3, y + 3, AMARELO)
        buraco.line(x - 3, y + 3, x + 3, y - 3, AMARELO)

def desenhar_buraco(jogador, index, tipo):
    # só redesenha o buraco que mudou
    if buracos_desenhados[jogador][index] == tipo:
        return
    buracos_desenhados[jogador][index] = tipo

    buraco.fill(GRAMA)
    elipse(32, 50, 27, 11, GRAMA_ESCURA)
    elipse(32, 50, 24, 9, TERRA)
    if tipo == TOUPEIRA:
        desenhar_toupeira()
    elif tipo == ESMAGADA:
        desenhar_esmagada()
    display.desenhar(80 + index * 80, 56 + jogador * 106, 64, 64, pixels_buraco)

def desenhar_titulo(mensagem):
    global titulo_desenhado

    if titulo_desenhado == mensagem:
        return
    titulo_desenhado = mensagem
    display.preencher(0, 0, 320, 28, FUNDO_TITULO)
    texto_grande(mensagem, 160, 6, 2, BRANCO, FUNDO_TITULO)

# grama, placar dos dois jogadores e faixas com a cor de cada botão
def desenhar_campo():
    global campo_desenhado

    campo_desenhado = True
    display.preencher(0, 28, 320, 212, GRAMA)
    for jogador in range(2):
        y = 30 + jogador * 106
        display.preencher(0, y, 64, 100, GRAMA_ESCURA)
        texto_grande("J{}".format(jogador + 1), 32, y + 16, 2, AMARELO, GRAMA_ESCURA)
        pontos_desenhados[jogador] = None
        for index in range(3):
            display.preencher(88 + index * 80, y + 8, 48, 10, CORES_BOTOES[index])
            buracos_desenhados[jogador][index] = None

def atualizar_display(mensagem, pontos, toupeira, esmagados):
    if not campo_desenhado:
        desenhar_campo()
    desenhar_titulo(mensagem)

    for jogador in range(2):
        if pontos_desenhados[jogador] != pontos[jogador]:
            pontos_desenhados[jogador] = pontos[jogador]
            display.preencher(0, 74 + jogador * 106, 64, 24, GRAMA_ESCURA)
            texto_grande(str(pontos[jogador]), 32, 74 + jogador * 106, 3, BRANCO, GRAMA_ESCURA)

        for index in range(3):
            tipo = VAZIO
            if index == esmagados[jogador]:
                tipo = ESMAGADA
            elif index == toupeira:
                tipo = TOUPEIRA
            desenhar_buraco(jogador, index, tipo)

# contagem antes do jogo começar
def mostrar_numero(mensagem, numero):
    global campo_desenhado

    campo_desenhado = False
    desenhar_titulo(mensagem)
    display.preencher(0, 28, 320, 212, GRAMA)
    texto_grande(numero, 160, 94, 10, BRANCO, GRAMA)
