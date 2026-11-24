import radio
import tela
import time
import random

PONTOS_PARA_VENCER = 10
APAGADO = 255

pontos = [0, 0]
led_atual = APAGADO
ultimo_envio = -1
ultimo_clique = [0, 0]
acertou = 0
esmagou = 0
apertou = False


def atualizar_display(mensagem="ESMAGA!"):
    tela.atualizar_display(mensagem, pontos, led_atual, led_atual, esmagou)


def publicar_estado():
    global ultimo_envio
    if ultimo_envio != led_atual:
        ultimo_envio = led_atual
        radio.enviar_estado(led_atual)


def apagar_leds():
    global led_atual
    led_atual = APAGADO
    publicar_estado()


def clique(jogador, index):
    global acertou, esmagou, apertou

    agora = time.ticks_ms()
    if time.ticks_diff(agora, ultimo_clique[jogador]) < 200:
        return
    ultimo_clique[jogador] = agora
    apertou = True

    if index == led_atual:
        pontos[jogador] += 1
        apagar_leds()
        acertou = jogador + 1
        esmagou = jogador + 1


def processar_eventos():
    evento = radio.receber()
    while evento is not None:
        jogador, index = evento
        clique(jogador - 1, index)
        evento = radio.receber()


def esperar(ms):
    global acertou

    fim = time.ticks_add(time.ticks_ms(), ms)
    while time.ticks_diff(fim, time.ticks_ms()) > 0:
        processar_eventos()
        if acertou:
            atualizar_display("J{} ACERTOU!".format(acertou))
            acertou = 0
        time.sleep_ms(10)


def jogar():
    global led_atual, acertou, esmagou, apertou, ultimo_envio

    pontos[0] = 0
    pontos[1] = 0
    acertou = 0
    esmagou = 0
    apertou = False
    ultimo_envio = -1
    apagar_leds()

    for numero in ("3", "2", "1"):
        tela.mostrar_numero("PREPARAR...", numero)
        esperar(1000)

    while max(pontos) < PONTOS_PARA_VENCER:
        anterior = led_atual
        while led_atual == anterior:
            led_atual = random.randint(0, 2)

        esmagou = 0
        publicar_estado()
        atualizar_display("APERTE!")
        esperar(max(800, 1500 - max(pontos) * 80))

        apagar_leds()
        atualizar_display("J{} ACERTOU!".format(esmagou) if esmagou else "ESMAGA!")
        esperar(max(500, 800 - max(pontos) * 30))

    vencedor = 1 if pontos[0] > pontos[1] else 2
    esmagou = 0
    atualizar_display("J{} VENCEU!".format(vencedor))


radio.conectar()
tela.desenhar_titulo("CONECTANDO...")

while True:
    jogar()
    esperar(3000)
    apertou = False
    while not apertou:
        esperar(50)
