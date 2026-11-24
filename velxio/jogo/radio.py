import network
import time

SIMULADOR = False
SALA = b"whac-a-mole-7f3k9q"
TODOS = bytes([255] * 6)

conexao = None
recebidas = []


def chegou(origem, mensagem):
    recebidas.append(bytes(mensagem))


def conectar():
    global conexao

    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    if SIMULADOR:
        from umqtt.simple import MQTTClient

        wifi.connect("Velxio-GUEST", "")
        while not wifi.isconnected():
            time.sleep_ms(200)

        conexao = MQTTClient(SALA + b"-jogo", "broker.hivemq.com")
        conexao.set_callback(chegou)
        conexao.connect()
        conexao.sock.setsockopt(6, 1, 1)
        conexao.subscribe(SALA + b"/jogador1/botao")
        conexao.subscribe(SALA + b"/jogador2/botao")
    else:
        import espnow

        conexao = espnow.ESPNow()
        conexao.active(True)
        conexao.add_peer(TODOS)


def enviar_estado(index):
    pacote = bytes([0x20, index])
    try:
        if SIMULADOR:
            conexao.publish(SALA + b"/estado", pacote)
        else:
            conexao.send(TODOS, pacote, False)
    except OSError:
        pass


def receber():
    try:
        if SIMULADOR:
            conexao.check_msg()
        else:
            origem, mensagem = conexao.recv(0)
            if mensagem:
                recebidas.append(bytes(mensagem))
    except OSError:
        pass

    if recebidas:
        mensagem = recebidas.pop(0)
        if len(mensagem) >= 3 and mensagem[0] == 0x10:
            return mensagem[1], mensagem[2]
    return None
