from machine import Pin
import radio
import tela
import time
import random

leds = [Pin(12, Pin.OUT), Pin(27, Pin.OUT), Pin(25, Pin.OUT)]
buttons = [Pin(13, Pin.IN, Pin.PULL_UP), Pin(14, Pin.IN, Pin.PULL_UP), Pin(26, Pin.IN, Pin.PULL_UP)]

# pontuação máxima
PONTOS_PARA_VENCER = 10
# número que avisa o controle 2 que nenhum LED está aceso
APAGADO = 255

pontos = [0, 0]
led_atual = -1
led_aceso = APAGADO
led_enviado = -1
ultimo_envio = 0
ultimo_clique = [0, 0]
acertou = 0
esmagou = 0
apertou = False

def atualizar_display(mensagem="ESMAGA!"):
    tela.atualizar_display(mensagem, pontos, led_aceso, led_atual, esmagou)

def acender_leds(index):
    global led_aceso

    leds[index].value(1)
    led_aceso = index

def apagar_leds():
    global led_aceso

    for led in leds:
        led.value(0)
    led_aceso = APAGADO

def enviar_led():
    global led_enviado, ultimo_envio

    # avisa o controle 2 quando o LED muda e repete a cada 300 ms
    if led_enviado != led_aceso or time.ticks_diff(time.ticks_ms(), ultimo_envio) >= 300:
        led_enviado = led_aceso
        ultimo_envio = time.ticks_ms()
        radio.enviar(led_aceso)

def clique(jogador, index):
    global acertou, esmagou, apertou

    # ignora o mesmo botão apertado duas vezes em menos de 200 ms
    agora = time.ticks_ms()
    if time.ticks_diff(agora, ultimo_clique[jogador]) < 200:
        return
    ultimo_clique[jogador] = agora
    apertou = True

    if index == led_aceso:
        pontos[jogador] += 1
        apagar_leds()
        acertou = jogador + 1
        esmagou = jogador + 1

def trata_botao(pin):
    for index, btn in enumerate(buttons):
        if btn == pin:
            clique(0, index)
            return

def esperar(ms):
    global acertou

    fim = time.ticks_add(time.ticks_ms(), ms)
    while time.ticks_diff(fim, time.ticks_ms()) > 0:
        # botão que o jogador 2 apertou
        index = radio.receber()
        if index is not None:
            clique(1, index)
        enviar_led()

        if acertou:
            atualizar_display("J{} ACERTOU!".format(acertou))
            acertou = 0
        time.sleep_ms(10)

def jogar():
    global led_atual, acertou, esmagou

    pontos[0] = 0
    pontos[1] = 0
    acertou = 0
    esmagou = 0

    for numero in ("3", "2", "1"):
        tela.mostrar_numero("PREPARAR...", numero)
        esperar(1000)

    while max(pontos) < PONTOS_PARA_VENCER:
        # a toupeira nunca sai no mesmo buraco duas vezes seguidas
        led_anterior = led_atual
        while led_atual == led_anterior:
            led_atual = random.randint(0, 2)
        print("Acendendo LED no pino:", led_atual)

        esmagou = 0
        acender_leds(led_atual)
        atualizar_display("APERTE!")

        # o tempo da toupeira diminui a cada ponto
        esperar(max(800, 1500 - max(pontos) * 80))

        apagar_leds()
        atualizar_display("J{} ACERTOU!".format(esmagou) if esmagou else "ESMAGA!")

        esperar(max(500, 800 - max(pontos) * 30))

    vencedor = 1 if pontos[0] > pontos[1] else 2
    esmagou = 0
    atualizar_display("J{} VENCEU!".format(vencedor))

for btn in buttons:
    btn.irq(trigger=Pin.IRQ_FALLING, handler=trata_botao)

apagar_leds()
tela.desenhar_titulo("CONECTANDO...")
radio.conectar(b"led", b"botao")

while True:
    jogar()
    esperar(3000)

    apertou = False
    while not apertou:
        esperar(50)
