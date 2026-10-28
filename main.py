# from machine import Pin, I2C
# import ssd1306
# #include <Wire.h> //Inclusão da biblioteca wire
# #include <Adafruit_SSD1306.h> //Inclusão da biblioteca Adafruit_SSD1306.h


# # ESP32 Pin assignment
 
# # CÓDIGO QUE VEIO JUNTO, ONDE MOSTRA JOGO ESMAGA RATA
# #i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# # oled_width = 128
# # oled_height = 64
# # oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# # oled.text('Jogo esmaga ratai!', 10, 10)      
# # oled.show()

from machine import Pin, I2C, PWM
import ssd1306
import time
from time import sleep

# Pinos do ESP32 conectados aos canais do LED RGB
# Ajuste conforme as conexões da sua protoboard
vermelho = PWM(Pin(19), freq=1000, duty=0)
verde = PWM(Pin(18), freq=1000, duty=0)
azul = PWM(Pin(17), freq=1000, duty=0)

# Configuração do I2C no ESP32
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

# Configuração botões


# Inicialização do display OLED 128x64
displayLED = ssd1306.SSD1306_I2C(128, 64, i2c)

#definição da cor
def definir_cor(r, g, b):
    # Valores de 0 a 255 convertidos para 0 a 1023
    led_r.duty(r * 1023 // 255)
    led_g.duty(g * 1023 // 255)
    led_b.duty(b * 1023 // 255)



while True:
    vermelho.duty(1023)
    verde.duty(0)
    azul.duty(0)
    sleep(1)

    vermelho.duty(0)
    verde.duty(1023)
    azul.duty(0)
    sleep(1)

    vermelho.duty(0)
    verde.duty(0)
    azul.duty(1023)
    sleep(1)
    
    # Primeira mensagem
    displayLED.fill(0)
    displayLED.text("Markinhos", 10, 12, 1)
    displayLED.show()

    time.sleep(1.5)

    # Segunda mensagem
    displayLED.fill(0)
    displayLED.text("Daneu", 10, 12, 1)
    displayLED.show()

    time.sleep(1.5)

    # Terceira mensagem
    displayLED.fill(0)
    displayLED.text("Soph", 10, 12, 1)
    displayLED.show()

    time.sleep(1.5)

    # Quarta mensagem
    displayLED.fill(0)
    displayLED.text("ErikAH", 10, 12, 1)
    displayLED.show()

    time.sleep(1.5)

    # Quinta mensagem
    displayLED.fill(0)
    displayLED.text("Gigi", 10, 12, 1)
    displayLED.show()

    time.sleep(1.5)

    # Limpa o display
    displayLED.fill(0)
    displayLED.show()
