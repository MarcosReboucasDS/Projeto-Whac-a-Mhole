import struct
import time


class ILI9341:
    def __init__(self, spi, cs, dc, rst, rotacao=0x28, largura=320, altura=240):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.rotacao = rotacao
        self.largura = largura
        self.altura = altura
        self.cs.value(1)
        self.iniciar()

    def comando(self, codigo, dados=None):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytes([codigo]))
        if dados:
            self.dc.value(1)
            self.spi.write(dados)
        self.cs.value(1)

    def iniciar(self):
        self.rst.value(0)
        time.sleep_ms(50)
        self.rst.value(1)
        time.sleep_ms(150)
        self.comando(0x01)
        time.sleep_ms(150)
        self.comando(0x11)
        time.sleep_ms(150)
        self.comando(0x3A, bytes([0x55]))
        self.comando(0x36, bytes([self.rotacao]))
        self.comando(0x29)

    def janela(self, x, y, largura, altura):
        self.comando(0x2A, struct.pack(">HH", x, x + largura - 1))
        self.comando(0x2B, struct.pack(">HH", y, y + altura - 1))

    def desenhar(self, x, y, largura, altura, pixels):
        self.janela(x, y, largura, altura)
        self.comando(0x2C, pixels)

    def preencher(self, x, y, largura, altura, cor):
        self.janela(x, y, largura, altura)
        total = largura * altura
        bloco = struct.pack("<H", cor) * min(total, 256)
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytes([0x2C]))
        self.dc.value(1)
        while total > 0:
            parte = min(total, 256)
            self.spi.write(bloco if parte == 256 else bloco[: parte * 2])
            total -= parte
        self.cs.value(1)
