# Projeto-Whac-a-Mhole
Jogo de Whack a Mole (bater na toupeira), onde ao acender uma luz no sensor, deve ser clicado o botão correspondente antes da luz apagar para contabilizar pontos.

## Arquitetura no Velxio

O projeto usa três ESP32:

- **Controle 1 (`velxio/controle1`)**: botões e LEDs do jogador 1.
- **Controle 2 (`velxio/controle2`)**: botões e LEDs do jogador 2.
- **Jogo (`velxio/jogo`)**: lógica da partida, pontuação dos dois jogadores e display ILI9341.

Os controles não calculam pontuação e não dependem um do outro. O ESP32 do jogo sorteia a toupeira, recebe as jogadas dos dois jogadores, valida os acertos, atualiza o placar e transmite o LED ativo para os dois controles. Assim, nenhum jogador fica responsável por executar parte da lógica do adversário.

## Comunicação

O protocolo usa mensagens curtas e identificadas:

- `0x10, jogador, botão`: botão pressionado por um jogador.
- `0x20, LED`: estado da toupeira/LED atual; `255` significa que todos os LEDs devem apagar.

No Velxio, essas mensagens são transportadas por MQTT nos tópicos separados de cada jogador e do estado do jogo. Em placas físicas, o mesmo protocolo é enviado por ESP-NOW em broadcast. A identificação do jogador é necessária porque os três ESP32 compartilham o meio de comunicação.

## Organização dos arquivos

Cada diretório de controlador contém o `main.py`, `radio.py` e o `diagram.json` correspondente. O diretório `jogo` também contém `tela.py` e `ili9341.py`, pois somente o controlador central usa o display.

O arquivo `velxio/whac-a-mole.vlx` reúne os três ESP32 e seus arquivos para execução no emulador Velxio.

## Execução

Abra `velxio/whac-a-mole.vlx` no Velxio e execute os três ESP32. Para usar placas físicas, altere `SIMULADOR` em cada `radio.py` para `False`; nesse modo a comunicação utiliza ESP-NOW.
