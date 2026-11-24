import network
import time

SIMULADOR = False
SALA = b"whac-a-mole-7f3k9q"
TODOS = bytes([255] * 6)

conexao = None
topico_estado = None
recebidas = []


def chegou(origem, mensagem):
    recebidas.append(bytes(mensagem))


def conectar(jogador):
    global conexao, topico_estado

    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    if SIMULADOR:
        from umqtt.simple import MQTTClient

        wifi.connect("Velxio-GUEST", "")
        while not wifi.isconnected():
            time.sleep_ms(200)

        prefixo = SALA + b"/"
        topico_estado = prefixo + b"estado"
        conexao = MQTTClient(SALA + b"-jogador" + bytes([48 + jogador]), "broker.hivemq.com")
        conexao.set_callback(chegou)
        conexao.connect()
        conexao.sock.setsockopt(6, 1, 1)
        conexao.subscribe(topico_estado)
    else:
        import espnow

        conexao = espnow.ESPNow()
        conexao.active(True)
        conexao.add_peer(TODOS)


def enviar_botao(jogador, index):
    pacote = bytes([0x10, jogador, index])
    try:
        if SIMULADOR:
            conexao.publish(SALA + b"/jogador" + bytes([48 + jogador]) + b"/botao", pacote)
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
        if len(mensagem) >= 2 and mensagem[0] == 0x20:
            return mensagem[1]
    return None
