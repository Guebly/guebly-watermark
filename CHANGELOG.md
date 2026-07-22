# Changelog

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
