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
esmagados = [None, None]
acertos_rodada = [False, False]
acertos_pendentes = []
apertou = False


def atualizar_display(mensagem="ESMAGA!"):
    tela.atualizar_display(mensagem, pontos, led_atual, esmagados)


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
    global apertou

    agora = time.ticks_ms()
    if time.ticks_diff(agora, ultimo_clique[jogador]) < 200:
        return
    ultimo_clique[jogador] = agora
    apertou = True

    # Cada jogador pode pontuar uma vez na toupeira atual. O LED
    # continua aceso para dar ao outro jogador a mesma oportunidade.
    if index == led_atual and not acertos_rodada[jogador]:
        pontos[jogador] += 1
        acertos_rodada[jogador] = True
        esmagados[jogador] = index
        acertos_pendentes.append(jogador + 1)


def processar_eventos():
    evento = radio.receber()
    while evento is not None:
        jogador, index = evento
        clique(jogador - 1, index)
        evento = radio.receber()


def esperar(ms):
    fim = time.ticks_add(time.ticks_ms(), ms)
    while time.ticks_diff(fim, time.ticks_ms()) > 0:
        processar_eventos()
        while acertos_pendentes:
            jogador = acertos_pendentes.pop(0)
            atualizar_display("J{} ACERTOU!".format(jogador))
        time.sleep_ms(10)


def esperar_toupeira(ms):
    fim = time.ticks_add(time.ticks_ms(), ms)
    while time.ticks_diff(fim, time.ticks_ms()) > 0:
        processar_eventos()
        while acertos_pendentes:
            jogador = acertos_pendentes.pop(0)
            atualizar_display("J{} ACERTOU!".format(jogador))

        if acertos_rodada[0] and acertos_rodada[1]:
            break
        time.sleep_ms(10)


def jogar():
    global led_atual, esmagados, acertos_rodada, apertou, ultimo_envio

    pontos[0] = 0
    pontos[1] = 0
    apertou = False
    ultimo_envio = -1
    esmagados = [None, None]
    acertos_rodada = [False, False]
    apagar_leds()

    for numero in ("3", "2", "1"):
        tela.mostrar_numero("PREPARAR...", numero)
        esperar(1000)

    while max(pontos) < PONTOS_PARA_VENCER:
        anterior = led_atual
        while led_atual == anterior:
            led_atual = random.randint(0, 2)

        esmagados = [None, None]
        acertos_rodada = [False, False]
        publicar_estado()
        atualizar_display("APERTE!")
        esperar_toupeira(max(800, 1500 - max(pontos) * 80))

        apagar_leds()
        if not acertos_rodada[0] and not acertos_rodada[1]:
            atualizar_display("ESMAGA!")
        esperar(max(500, 800 - max(pontos) * 30))

    vencedor = 1 if pontos[0] > pontos[1] else 2
    atualizar_display("J{} VENCEU!".format(vencedor))


radio.conectar()
tela.desenhar_titulo("CONECTANDO...")

while True:
    jogar()
    esperar(3000)
    apertou = False
    while not apertou:
        esperar(50)
