from machine import Pin, I2C
import ssd1306
import framebuf
import time
import random

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
displayLED = ssd1306.SSD1306_I2C(128, 64, i2c)
tela = displayLED.framebuf

leds = [
    [Pin(12, Pin.OUT), Pin(27, Pin.OUT), Pin(25, Pin.OUT), Pin(32, Pin.OUT)],
    [Pin(19, Pin.OUT), Pin(17, Pin.OUT), Pin(16, Pin.OUT), Pin(2, Pin.OUT)]
]
buttons = [
    [Pin(13, Pin.IN, Pin.PULL_UP), Pin(14, Pin.IN, Pin.PULL_UP), Pin(26, Pin.IN, Pin.PULL_UP), Pin(33, Pin.IN, Pin.PULL_UP)],
    [Pin(18, Pin.IN, Pin.PULL_UP), Pin(5, Pin.IN, Pin.PULL_UP), Pin(4, Pin.IN, Pin.PULL_UP), Pin(15, Pin.IN, Pin.PULL_UP)]
]

PONTOS_PARA_VENCER = 20

pontos = [0, 0]
led_atual = -1
ultimo_clique = [0, 0]
acertou = 0
apertou = False

def texto_centro(texto, y):
    displayLED.text(texto, (128 - len(texto) * 8) // 2, y, 1)

def texto_grande(texto, centro_x, y, escala):
    largura = len(texto) * 8
    letras = framebuf.FrameBuffer(bytearray(largura), largura, 8, framebuf.MONO_VLSB)
    letras.text(texto, 0, 0, 1)
    x = centro_x - largura * escala // 2
    for coluna in range(largura):
        for linha in range(8):
            if letras.pixel(coluna, linha):
                tela.fill_rect(x + coluna * escala, y + linha * escala, escala, escala, 1)

def atualizar_display(mensagem="ESMAGA RATA!"):
    displayLED.fill(0)
    texto_centro(mensagem, 0)
    tela.hline(0, 11, 128, 1)
    tela.vline(63, 11, 53, 1)
    texto_centro("J1      J2", 16)
    texto_grande(str(pontos[0]), 32, 30, 3)
    texto_grande(str(pontos[1]), 96, 30, 3)
    displayLED.show()

def mostrar_numero(mensagem, numero):
    displayLED.fill(0)
    texto_centro(mensagem, 0)
    tela.hline(0, 11, 128, 1)
    texto_grande(numero, 64, 20, 5)
    displayLED.show()

def apagar_leds():
    for jogador in range(2):
        for led in leds[jogador]:
            led.value(0)

def trata_botao(pin):
    global acertou, apertou

    for jogador in range(2):
        for index, btn in enumerate(buttons[jogador]):
            if btn == pin:
                agora = time.ticks_ms()
                if time.ticks_diff(agora, ultimo_clique[jogador]) < 200:
                    return
                ultimo_clique[jogador] = agora
                apertou = True

                if leds[jogador][index].value() == 1:
                    pontos[jogador] += 1
                    apagar_leds()
                    acertou = jogador + 1
                return

def esperar(ms):
    global acertou

    fim = time.ticks_add(time.ticks_ms(), ms)
    while time.ticks_diff(fim, time.ticks_ms()) > 0:
        if acertou:
            atualizar_display("J{} ACERTOU!".format(acertou))
            acertou = 0
        time.sleep_ms(10)

def jogar():
    global led_atual, acertou

    pontos[0] = 0
    pontos[1] = 0
    acertou = 0

    for numero in ("3", "2", "1"):
        mostrar_numero("PREPARAR...", numero)
        time.sleep(1)

    while max(pontos) < PONTOS_PARA_VENCER:
        led_atual = random.randint(0, 3)
        print("Acendendo LED no pino:", led_atual)

        leds[0][led_atual].value(1)
        leds[1][led_atual].value(1)
        atualizar_display("APERTE!")

        esperar(max(300, 800 - max(pontos) * 50))

        apagar_leds()

        esperar(max(400, 1000 - max(pontos) * 50))

    vencedor = 1 if pontos[0] > pontos[1] else 2
    atualizar_display("J{} VENCEU!".format(vencedor))

for jogador in range(2):
    for btn in buttons[jogador]:
        btn.irq(trigger=Pin.IRQ_FALLING, handler=trata_botao)

apagar_leds()

while True:
    jogar()
    time.sleep(3)

    apertou = False
    while not apertou:
        time.sleep_ms(50)
