from machine import Pin, I2C
import ssd1306
import time
import random

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
displayLED = ssd1306.SSD1306_I2C(128, 64, i2c)

leds = [
    Pin(33, Pin.OUT),
    Pin(25, Pin.OUT),
    Pin(26, Pin.OUT),
    Pin(27, Pin.OUT)
]
buttons = [
    Pin(5, Pin.IN, Pin.PULL_DOWN),
    Pin(4, Pin.IN, Pin.PULL_DOWN),
    Pin(2, Pin.IN, Pin.PULL_DOWN),
    Pin(12, Pin.IN, Pin.PULL_DOWN)
]

pontos = 0
led_atual = -1
ultimo_clique = 0

def atualizar_display(mensagem="ESMAGA RATA!"):
    displayLED.fill(0)
    displayLED.text(mensagem, 10, 15, 1)
    displayLED.text("Pontos: {}".format(pontos), 10, 40, 1)
    displayLED.show()

def trata_botao(pin):
    global pontos, led_atual, ultimo_clique
    
    agora = time.ticks_ms()
    if time.ticks_diff(agora, ultimo_clique) < 200:
        return
    ultimo_clique = agora

    for index, btn in enumerate(buttons):
        if btn == pin:
            if leds[index].value() == 1:
                pontos += 1
                leds[index].value(0)
                atualizar_display("ACERTOU!")
            break

for btn in buttons:
    btn.irq(trigger=Pin.IRQ_RISING, handler=trata_botao)

for led in leds:
    led.value(0)

atualizar_display("Iniciando...")
time.sleep(2)

while True:
    led_atual = random.randint(0, 3)
    print("Acendendo LED no pino:", led_atual)
    
    leds[led_atual].value(1)
    atualizar_display("APERTE!")
    
    time.sleep(0.8)
    
    leds[led_atual].value(0)
    
    time.sleep(1.0)
