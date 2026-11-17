from machine import Pin
import radio
import time

leds = [Pin(19, Pin.OUT), Pin(17, Pin.OUT), Pin(16, Pin.OUT)]
buttons = [Pin(18, Pin.IN, Pin.PULL_UP), Pin(5, Pin.IN, Pin.PULL_UP), Pin(4, Pin.IN, Pin.PULL_UP)]

botao_apertado = -1
ultimo_clique = 0

def acender_led(index):
    for posicao, led in enumerate(leds):
        led.value(1 if posicao == index else 0)

def trata_botao(pin):
    global botao_apertado, ultimo_clique

    for index, btn in enumerate(buttons):
        if btn == pin:
            agora = time.ticks_ms()
            if time.ticks_diff(agora, ultimo_clique) < 200:
                return
            ultimo_clique = agora
            botao_apertado = index
            return

for btn in buttons:
    btn.irq(trigger=Pin.IRQ_FALLING, handler=trata_botao)

acender_led(-1)
radio.conectar(b"botao", b"led")

# o controle 2 só manda o botão apertado e acende o LED que o controle 1 pedir
while True:
    if botao_apertado >= 0:
        radio.enviar(botao_apertado)
        botao_apertado = -1

    index = radio.receber()
    if index is not None:
        acender_led(index)
    time.sleep_ms(5)
