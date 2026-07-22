# Changelog

## [3.5.1] — 2026-07-22

- **Removida a Guebly Holding** da lista de marcas (11 empresas agora). Logo órfã
  `guebly-holding.png` apagada.
- **Tiradas as informações societárias** das descrições: nada de participação
  (%), sócios ou repasse. Cada empresa mostra só a identidade/uso (ex.: "Marca
  principal", "Grupo Guebly", "Só o símbolo · ideal para marca pequena").

## [3.5.0] — 2026-07-22

### Redesign completo + tema claro de verdade

**Tema claro agora é o padrão.** O app abre no claro; o escuro entra pela chavinha
☾/☀ (e é lembrado). Antes ele piscava escuro antes do JS decidir.

**O tema claro estava "meio falhado" — e a causa era estrutural.** Havia cerca de
90 cores fixas fora do sistema de temas: fundos pretos translúcidos, brancos,
sombras. Elas não mudavam ao trocar de tema, então no claro sobravam manchas
escuras e textos sem contraste. Agora **toda** superfície, borda, sombra e brilho
vem de variáveis — o claro e o escuro são só dois conjuntos de valores.

**Uma folha de estilo única.** As duas telas carregavam CSS embutido, com ~50
classes idênticas duplicadas. Qualquer ajuste tinha que ser feito duas vezes e na
prática escapava. Extraí tudo para `static/css/app.css`, compartilhado pelas duas.

**Redesign das telas:**
- Superfícies com hierarquia real (cartão → campo rebaixado → trilho), sombras
  suaves no claro e profundas no escuro.
- Prévia com fundo quadriculado — fica claro o que é transparência da imagem.
- Coluna da prévia acompanha a rolagem; botões, chips e campos com estados de
  foco/hover acessíveis; contraste do texto secundário corrigido nos dois temas.
- Barra de rolagem, seleção de texto e foco combinando com o tema.
- Responsivo até o celular; respeita "reduzir movimento" do sistema.

### Corrigido
- **Layout da tela Marcas quebrado:** um `</div>` do seletor de empresas tinha
  sido removido por engano na 3.4.3, e o painel de prévia caía dentro da lista
  rolante. Os dois painéis voltam a ficar lado a lado.
- **Aba ativa do seletor sem cor de fundo:** apontava para uma variável que não
  existia (`--c`).
- **Acentuação:** dezenas de textos estavam sem acento (Água, vídeo, posição,
  configuração, pré-visualização…).

## [3.4.3] — 2026-07-22

### "Logo não configurada" em quem tinha logo
A tela Marcas Guebly decidia se a empresa tinha logo olhando **só o `logo_url`**.
Quem tem a logo empacotada no app (`logo_file`) aparecia como não configurada —
mesmo funcionando no processamento. Atingia Guebly LTDA, Studio e as variações
de símbolo.

- O backend passou a resolver um endereço único (`logo_src`): usa o arquivo local
  se ele existir, senão a URL. A tela usa só isso.
- A bolinha de status agora explica ao passar o mouse se a logo está **empacotada
  no app** ou vem do **site** (e portanto precisa de internet).

### Empresas que nunca apareciam no seletor
Os grupos eram **três blocos de HTML com os ids escritos à mão**. Empresa nova no
`config.json` simplesmente não aparecia:

- **Lirya LTDA, Lirya+ e Lirya Academy** estavam invisíveis desde que foram
  cadastradas.
- **Guebly LTDA (símbolo)** e **Guebly Studio (símbolo)** também.
- Ainda havia referências a **Trocaí, Vendaí e Ayon**, que já tinham sido removidos.

Agora é um bloco só: grupo e descrição vêm do `config.json`, e as 12 empresas
aparecem. Cadastrar uma nova não exige mais mexer no HTML.

## [3.4.2] — 2026-07-22

### Ícone do app estava invisível
O ícone tinha sido gerado a partir do símbolo **branco**, então sumia em qualquer
fundo claro — barra de tarefas, Explorer, aba do navegador. Agora usa o
**hexágono roxo**, que aparece tanto no claro quanto no escuro.

- Ícone do `.exe` regerado em 7 tamanhos (16 a 256px).
- Favicon das duas telas trocado para o símbolo roxo.
- A janela do app não recebia ícone: o pywebview no Windows não repassa o
  parâmetro `icon` para o WebView2. Resolvido aplicando o ícone via `WM_SETICON`
  depois que a janela abre.
- Definido um `AppUserModelID` próprio — sem ele o Windows agrupa o app com o
  interpretador Python e mostra o ícone do Python na barra de tarefas.

## [3.4.1] — 2026-07-22

### Logo errada no app inteiro
O app usava o `logo-email.png` — a logo da **Guebly Holding** — salva com o nome
`guebly.png`, o que escondia a troca. A logo correta é a da **Guebly LTDA**,
que estava em `Guebly/Guebly/src/assets/images/icons/`.

- Cabeçalho das duas telas, favicon e ícone do `.exe` agora usam a **Guebly LTDA**.
- Como a logo traz a palavra "Guebly" escrita, o app troca entre a **versão branca
  (tema escuro)** e a **escura (tema claro)** — antes o texto sumia no fundo.
- Ícone do `.exe` regerado a partir do símbolo oficial.
- Em Marcas Guebly: "Guebly LTDA" passou a apontar para a logo certa (apontava
  para a da Holding), ganhou a variação **só símbolo**, e a Holding foi mantida
  em entrada própria.
- Todas as logos agora são **locais**: o favicon vinha de `guebly.com.br`, então
  não aparecia sem internet.

## [3.4.0] — 2026-07-22

### Fila de arquivos (era o maior incômodo)
- **Os arquivos agora se acumulam.** Antes, escolher novos arquivos **apagava** os
  anteriores — não dava para ir juntando de pastas diferentes.
- **Cada arquivo tem o seu "×"** para sair da lista, um por um.
- **Miniatura** de cada imagem, em vez de só o nome.
- **Clique num arquivo para pré-visualizá-lo** (marcado com "PREVIEW"). Dá para
  ajustar a marca d'água olhando exatamente a foto que você quer conferir.
- **"Limpar tudo"** e contador com o tamanho somado.
- Arquivo repetido é detectado e ignorado, avisando.

### Posicionamento
- **A grade de posição estava quebrada**: eram 7 opções numa grade de 3 colunas,
  então o "centro" caía visualmente no lugar do meio-esquerda e as de baixo
  desalinhavam. Agora é uma **grade 3×3 de verdade**, com as 9 posições.
- **Meio-esquerda e meio-direita** passaram a existir (não eram suportadas nem no
  backend).
- Cada posição tem dica ao passar o mouse.

## [3.3.0] — 2026-07-22

### Aplicativo de desktop
- **Vira app de verdade**: janela nativa via pywebview, empacotado num
  `GueblyWatermark.exe` único (~66 MB) com PyInstaller. Não exige Python nem
  FFmpeg instalados. Escolhido no lugar do Electron, que precisaria embutir
  três runtimes (Node + Python + FFmpeg) e passaria de 300 MB.
- **Atualização automática**: o app consulta os Releases do GitHub e mostra uma
  faixa com o link do download quando há versão nova. Falha em silêncio offline.
- **Release automatizado**: GitHub Action compila o `.exe` e publica o Release
  ao criar uma tag `v*`.
- Ícone próprio (logo da Guebly LTDA) no executável e na janela.

### Interface
- **As duas ferramentas ficaram separadas e navegáveis**: seletor no topo entre
  🎨 *Ferramenta livre* (sua logo/texto) e 🏢 *Marcas Guebly* (empresas do grupo).
  Antes as telas existiam mas não havia como ir de uma para a outra.
- **Tema claro e escuro**, com botão no topo. Segue o tema do sistema na primeira
  vez e lembra a escolha depois.
- Marca do app corrigida para **Guebly LTDA** (Guebly Holding segue como empresa
  na lista de marcas).

### Marcas
- **Guebly Studio com a identidade nova** (S em gradiente azul), em duas
  variações: completa (símbolo + texto) e só o símbolo — melhor para marca
  d'água pequena. Fundo branco removido: PNG com transparência real.
- **Ayon vira Lirya**: Lirya LTDA, Lirya+ e Lirya Academy. Ayon Studios removida.
- **Trocaí e Vendaí removidas.**
- Entradas da Lirya já preparadas — basta soltar as artes em `static/img/`.

### Correções
- **`logo_file`**: as logos das empresas agora podem vir de `static/img/`, em vez
  de serem baixadas do site. O app se dizia "100% local" mas dependia do
  guebly.com.br estar no ar para montar a marca d'água. Caminho sanitizado
  (bloqueia *path traversal*).

## 2026-05-31 — v3.3
- Adicionada funcionalidade de **inserir vídeo dentro de outro vídeo** (início, meio ou final)
- Upload de vídeo de inserção via endpoint dedicado (até 200 MB)
- Slider de posição para inserção no meio (porcentagem da duração)
- Validação atualizada: aceita watermark, tela final ou vídeo inserido (ou combinação)
- README atualizado com documentação da nova funcionalidade

## Anteriores — v3.2
- Cache de FFmpeg e fontes na inicialização
- Validações de segurança (path traversal, tokens)
- Cleanup em background de jobs antigos
- Tela final (endscreen) com imagem estática
- 11 animações de marca d'água em vídeo
- Preview ao vivo com canvas
- Processamento em lote com ZIP automático
