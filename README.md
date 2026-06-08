<div align="center">

<img src="https://www.guebly.com.br/guebly.png" alt="Guebly" width="48" height="48" style="border-radius: 12px" />

# Guebly Watermark

**Ferramenta visual para aplicar marcas d'agua em imagens e videos — open-source, sem nuvem, 100% local**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-direto-007808?style=flat-square&logo=ffmpeg&logoColor=white)](https://ffmpeg.org)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](./LICENSE)
[![Feito pela Guebly](https://img.shields.io/badge/feito%20por-Guebly-9854F1?style=flat-square)](https://www.guebly.com.br)

[Como instalar](#-instalacao) · [Como usar](#-como-usar) · [Configuracao](#-configuracao) · [Contribuir](#-contribuindo)

</div>

---

## Sobre

O **Guebly Watermark** e uma ferramenta web local desenvolvida pela [Guebly](https://www.guebly.com.br) para aplicar marcas d'agua em imagens e videos de forma rapida e profissional. Todo o processamento acontece na sua maquina — nenhum arquivo e enviado para servidores externos.

A interface roda no navegador via Flask, com preview ao vivo, animacoes de marca d'agua e processamento em lote com download automatico em ZIP.

> **Fluxo:** arraste suas midias, escolha o logo/texto, ajuste posicao e escala, processe tudo de uma vez.

---

## Funcionalidades

| Recurso | Descricao |
|---------|-----------|
| **Imagens** | Suporte a PNG, JPG, WEBP, BMP, TIFF — saida em PNG |
| **Videos** | Suporte a MP4, MOV, AVI, MKV, WEBM, FLV, WMV — saida em MP4 |
| **Logo por arquivo** | Upload de PNG, JPG ou WEBP como marca d'agua |
| **Logo por URL** | Cole qualquer URL publica de imagem |
| **Texto como marca d'agua** | Cor, fundo e opacidade configuraveis |
| **Inserir video** | Insere um video no inicio, meio ou final de outro video |
| **Tela final (endscreen)** | Imagem estatica exibida ao final do video (0-15s) |
| **Pre-visualizacao local** | Canvas ao vivo para imagens, frame para videos |
| **11 animacoes** | Estatico, ticker, pendulo, bounce, diagonal e mais |
| **7 posicoes** | 4 cantos + 3 centros |
| **Escala / Opacidade / Margem** | Sliders em tempo real |
| **Processamento em lote** | Multiplas midias processadas de uma vez com ZIP automatico |
| **Painel interno** | Rota `/guebly` com logos pre-configuradas por empresa |
| **Progresso em tempo real** | SSE (Server-Sent Events) durante processamento de videos |
| **100% local** | Nenhum dado sai da sua maquina |

---

## Stack tecnica

| Tecnologia | Funcao |
|------------|--------|
| [Python 3.9+](https://python.org) | Linguagem principal do backend |
| [Flask 3.0](https://flask.palletsprojects.com) | Servidor web e rotas da API |
| [Pillow 10+](https://python-pillow.org) | Processamento de imagens e geracoes de texto |
| [FFmpeg](https://ffmpeg.org) | Processamento de videos (via subprocess direto, sem MoviePy) |
| [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) | Binario FFmpeg embutido como fallback |
| [NumPy](https://numpy.org) | Manipulacao de arrays de pixels |
| HTML5 Canvas | Preview ao vivo no navegador |
| SSE (Server-Sent Events) | Progresso em tempo real do processamento |

> O FFmpeg e chamado via `subprocess` diretamente — isso e **10-50x mais rapido** que abordagens com MoviePy.

---

## Instalacao

### Requisitos

- **Python 3.9** ou superior
- **FFmpeg** (necessario para processar videos)

### Windows (rapido)

1. Instale o [Python 3.9+](https://python.org/downloads/) (marque "Add to PATH")
2. Instale o [FFmpeg](https://ffmpeg.org/download.html) ou deixe o `imageio-ffmpeg` resolver automaticamente
3. Clique duas vezes em **`iniciar.bat`**
4. Na primeira execucao, as dependencias sao instaladas automaticamente
5. Acesse **http://localhost:5000** no navegador

> O `iniciar.bat` unifica instalacao + inicializacao em um unico arquivo.

### Linux / macOS (manual)

```bash
# 1. Instale o FFmpeg
sudo apt install ffmpeg          # Debian / Ubuntu
brew install ffmpeg              # macOS

# 2. Clone o repositorio
git clone https://github.com/Guebly/watermark.git
cd watermark

# 3. Instale as dependencias Python
pip install -r requirements.txt

# 4. Inicie o servidor
python app.py
```

Acesse [http://localhost:5000](http://localhost:5000) no navegador.

---

## Como usar

### Marca d'agua com logo

1. Acesse `http://localhost:5000`
2. Arraste ou selecione as imagens/videos que deseja marcar
3. Na aba **Logo**, faca upload de um arquivo PNG/JPG/WEBP ou cole uma URL
4. Ajuste **posicao**, **escala**, **opacidade** e **margem** com os sliders
5. Para videos, escolha uma das **11 animacoes** disponiveis
6. Clique em **Processar** — o download e automatico (ZIP para lotes)

### Marca d'agua com texto

1. Na aba **Texto**, digite o conteudo (ex: `Confidencial`, `© Guebly 2026`)
2. Escolha a cor do texto e a cor/opacidade do fundo
3. O tamanho e controlado pelo slider de **Escala**
4. Funciona em imagens e videos

### Inserir video dentro de outro

1. Selecione um video como arquivo base
2. Na secao **Inserir Video**, arraste o video que deseja inserir (ate 200 MB)
3. Escolha a posicao: **Inicio**, **Meio** ou **Final**
4. Se escolher **Meio**, use o slider para definir o ponto exato (% da duracao)
5. O video inserido e re-encodado para a mesma resolucao do video principal
6. Funciona combinado com watermark e tela final, ou sozinho

### Tela final (endscreen)

1. Faca upload de uma imagem na secao **Tela Final**
2. Defina a duracao (0 a 15 segundos)
3. A imagem e exibida como frame estatico ao final do video

---

## Configuracao

O arquivo `config.json` na raiz do projeto controla os valores padrao e o painel interno.

### Valores padrao

```json
{
  "default_position":    "bottom-right",
  "default_scale_pct":   15,
  "default_margin_pct":  3,
  "default_opacity_pct": 90
}
```

| Parametro | Descricao | Valores |
|-----------|-----------|---------|
| `default_position` | Posicao inicial da marca d'agua | `top-left`, `top-center`, `top-right`, `center-left`, `center`, `center-right`, `bottom-left`, `bottom-center`, `bottom-right` |
| `default_scale_pct` | Escala padrao (% da largura) | `1` a `100` |
| `default_margin_pct` | Margem padrao (% da dimensao) | `0` a `50` |
| `default_opacity_pct` | Opacidade padrao | `0` a `100` |

### Painel interno (`/guebly`)

O painel interno permite selecionar logos pre-configuradas por empresa. Adicione empresas no array `guebly_companies`:

```json
{
  "guebly_companies": [
    {
      "id":       "minha-empresa",
      "name":     "Minha Empresa",
      "logo_url": "https://meusite.com/logo.png",
      "color":    "#9854F1"
    }
  ]
}
```

| Campo | Descricao |
|-------|-----------|
| `id` | Identificador unico (slug) |
| `name` | Nome exibido no painel |
| `logo_url` | URL publica do logo PNG |
| `color` | Cor do card no painel (hex) |

---

## Estrutura do projeto

```
watermark/
├── app.py                 # Backend Flask — rotas, processamento de imagens e videos
├── config.json            # Configuracoes padrao e empresas do painel interno
├── requirements.txt       # Dependencias Python
├── iniciar.bat            # Script Windows: instala dependencias + inicia servidor
├── CHANGELOG.md           # Historico de versoes
├── static/
│   └── img/
│       └── guebly.png     # Logo do header da interface
└── templates/
    ├── index.html         # Interface publica principal
    └── guebly.html        # Painel interno com logos pre-configuradas
```

---

## Deploy em producao

Para servir em producao com videos longos, use **Gunicorn** com timeout estendido:

```bash
pip install gunicorn

gunicorn app:app --bind 0.0.0.0:5000 --workers 2 --timeout 300
```

| Parametro | Recomendacao |
|-----------|--------------|
| `--workers` | 2-4 (cada worker processa um video por vez) |
| `--timeout` | 300+ segundos para videos longos em alta resolucao |
| `--bind` | `0.0.0.0:5000` para acesso na rede local |

> Videos curtos (< 30s em 1080p) levam cerca de 10-30 segundos. Videos mais longos ou em 4K podem levar varios minutos.

---

## Contribuindo

1. Faca um fork do repositorio
2. Crie uma branch para sua feature (`git checkout -b feature/minha-feature`)
3. Commit suas alteracoes (`git commit -m "Adicionada minha feature"`)
4. Push para a branch (`git push origin feature/minha-feature`)
5. Abra um Pull Request

### Diretrizes

- Commits em portugues, descritivos e concisos
- Teste com imagens e videos antes de submeter
- Mantenha compatibilidade com Python 3.9+

---

## Changelog

Veja o arquivo [CHANGELOG.md](./CHANGELOG.md) para o historico completo de versoes.

### Ultima versao: v3.3 (2026-05-31)

- Insercao de video dentro de outro video (inicio, meio ou final)
- Upload de video de insercao ate 200 MB
- Slider de posicao para insercao no meio
- Validacao atualizada para combinacoes de watermark + tela final + video inserido

---

## Licenca

MIT License — [Guebly Holding LTDA](https://www.guebly.com.br) · guebly.com.br
