import network
import time

# True no Velxio (WiFi + MQTT), False nas placas de verdade (ESP-NOW)
SIMULADOR = False

# nome que separa o nosso jogo dos outros no servidor MQTT
SALA = b"whac-a-mole-7f3k9q"
# endereço do ESP-NOW que fala com qualquer placa por perto
TODOS = bytes([255] * 6)

conexao = None
topico = None
recebidas = []

# o MQTT chama esta função quando chega uma mensagem
def chegou(origem, mensagem):
    recebidas.append(bytes(mensagem))

# envia e recebe são os assuntos de cada controle: led ou botao
def conectar(envia, recebe):
    global conexao, topico

    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)

    if SIMULADOR:
        from umqtt.simple import MQTTClient

        wifi.connect("Velxio-GUEST", "")
        while not wifi.isconnected():
            time.sleep_ms(200)

        topico = SALA + b"/" + envia
        conexao = MQTTClient(SALA + b"-" + envia, "broker.hivemq.com")
        conexao.set_callback(chegou)
        conexao.connect()
        conexao.sock.setsockopt(6, 1, 1)
        conexao.subscribe(SALA + b"/" + recebe)
    else:
        import espnow

        conexao = espnow.ESPNow()
        conexao.active(True)
        conexao.add_peer(TODOS)

# manda um número só: o LED aceso ou o botão apertado
def enviar(numero):
    try:
        if SIMULADOR:
            conexao.publish(topico, bytes([numero]))
        else:
            conexao.send(TODOS, bytes([numero]), False)
    except OSError:
        pass

# devolve o número que chegou, ou None se não chegou nada
def receber():
    try:
        if SIMULADOR:
            conexao.check_msg()
        else:
            origem, mensagem = conexao.recv(0)
            if mensagem:
                recebidas.append(mensagem)
    except OSError:
        pass

    if recebidas:
        return recebidas.pop(0)[0]
    return None
