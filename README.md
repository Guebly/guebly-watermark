<div align="center">

<img src="static/img/guebly.png" alt="Guebly LTDA" width="72" height="72" />

# Guebly Watermark

**Marca d'água em imagens e vídeos — aplicativo de desktop, 100% local, sem nuvem**

[![Windows](https://img.shields.io/badge/Windows-.exe-0078D4?style=flat-square&logo=windows&logoColor=white)](../../releases/latest)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-embutido-007808?style=flat-square&logo=ffmpeg&logoColor=white)](https://ffmpeg.org)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](./LICENSE)

**[⬇️ Baixar a última versão (.exe)](../../releases/latest)**

</div>

---

## O que é

Ferramenta da **Guebly LTDA** para aplicar marcas d'água em imagens e vídeos.
Roda como **aplicativo de desktop** (janela própria, não é aba de navegador) e
processa **tudo na sua máquina** — nenhum arquivo sai do computador.

O app tem **duas ferramentas separadas**, escolhidas no seletor do topo:

| Ferramenta | Para quê |
|---|---|
| 🎨 **Ferramenta livre** | Marca d'água com **a sua logo** (upload) ou **texto**. Uso geral. |
| 🏢 **Marcas Guebly** | Escolhe a **empresa do grupo** e aplica a logo dela, já configurada. Uso interno. |

---

## Instalação

### Opção 1 — Aplicativo (recomendado)

1. Baixe o **`GueblyWatermark.exe`** na [página de releases](../../releases/latest).
2. Dê dois cliques. Pronto.

Não precisa instalar Python nem FFmpeg: **já vem tudo dentro do .exe** (~66 MB).
O app avisa sozinho quando sai uma versão nova.

> **Windows SmartScreen:** como o executável não é assinado digitalmente, o Windows
> pode mostrar "Windows protegeu o computador". Clique em **Mais informações →
> Executar assim mesmo**. É esperado para apps sem certificado de assinatura (que é pago).

### Opção 2 — Rodando pelo código (dev)

```bash
git clone https://github.com/Guebly/guebly-watermark.git
cd guebly-watermark
pip install -r requirements.txt

python desktop.py     # abre em janela própria (como o app)
# ou
python app.py         # abre em http://127.0.0.1:5000 no navegador
```

---

## Como usar

### 🎨 Ferramenta livre

1. **Escolha os arquivos** — imagens e/ou vídeos, vários de uma vez. A lista
   **acumula**: pode ir juntando de pastas diferentes sem perder o que já
   escolheu. Cada arquivo tem um **×** para tirar só ele, e clicar num arquivo
   troca o **preview** para aquela imagem — útil para conferir o resultado numa
   foto específica antes de processar tudo.
2. **Defina a marca d'água** — envie uma logo (PNG com transparência fica melhor)
   ou escreva um texto (com fonte, cor e fundo configuráveis).
3. **Ajuste** posição, tamanho, margem e opacidade — o preview atualiza na hora.
4. **Processe.** Vários arquivos saem num `.zip`.

### 🏢 Marcas Guebly

1. **Selecione a empresa** (Guebly LTDA, Studio, Games, Pay, Contábil, Lirya…).
2. **Solte as imagens.**
3. **Processe** — a logo daquela empresa é aplicada com os padrões configurados.

### Tema claro e escuro

Botão **☾ / ☀** no topo. Na primeira vez segue o tema do Windows; depois lembra
a sua escolha.

---

## Formatos suportados

| Tipo | Entrada | Saída |
|---|---|---|
| **Imagens** | PNG, JPG, WEBP, BMP, TIFF | PNG |
| **Vídeos** | MP4, MOV, AVI, MKV, WEBM, FLV, WMV | MP4 |
| **Marca d'água** | PNG, JPG, WEBP (ou texto) | — |

Outros recursos: marca d'água **animada** (movimento no vídeo), **lote** com
download em ZIP, **progresso em tempo real** e preview ao vivo.

---

## Empresas configuradas

Editáveis em [`config.json`](./config.json):

| Empresa | Logo |
|---|---|
| Guebly Holding | remota |
| **Guebly LTDA** | local (`guebly.png`) |
| **Guebly Studio** | local (`guebly-studio.png`) — logo completa |
| **Guebly Studio (símbolo)** | local (`guebly-studio-simbolo.png`) — só o símbolo, ideal para marca pequena |
| Guebly Games · Pay · Contábil | remotas |
| **Lirya LTDA · Lirya+ · Lirya Academy** | ⏳ aguardando as artes |
| Sentrion | remota |

### Adicionar ou trocar uma logo

**Logo local (recomendado — funciona sem internet):**

1. Coloque o arquivo em `static/img/` (PNG com fundo transparente).
2. Em `config.json`, aponte `logo_file` para o nome do arquivo:

```json
{
  "id": "lirya-ltda",
  "name": "Lirya LTDA",
  "logo_file": "lirya.png",
  "color": "#ec4899"
}
```

**Logo remota:** use `logo_url` com o endereço da imagem. O app tenta o
`logo_file` primeiro e só cai para a URL se não houver arquivo local.

> **Por que preferir local:** o app se propõe a rodar 100% offline. Com `logo_url`
> ele baixa a imagem do site toda vez — sem internet, ou com o site fora do ar,
> a marca d'água não sai.

### As logos da Lirya

As três entradas da Lirya já existem em `config.json` com o `logo_url` vazio.
Quando as artes ficarem prontas, salve em `static/img/` como `lirya.png`,
`lirya-plus.png` e `lirya-academy.png` e troque `logo_url` por `logo_file` em
cada uma. **Nenhuma mudança de código é necessária.**

---

## Configuração

Padrões em [`config.json`](./config.json):

| Campo | O que faz | Padrão |
|---|---|---|
| `default_position` | Canto da marca d'água | `bottom-right` |
| `default_scale_pct` | Tamanho, em % da imagem | `15` |
| `default_margin_pct` | Distância da borda, em % | `3` |
| `default_opacity_pct` | Opacidade | `90` |

Posições (grade 3×3): `top-left`, `top-center`, `top-right`, `middle-left`,
`center`, `middle-right`, `bottom-left`, `bottom-center`, `bottom-right`.

---

## Atualizações

O app consulta os **Releases do GitHub** ao abrir. Havendo versão nova, aparece
uma faixa no topo com o link do download. Sem internet, ele ignora em silêncio —
nunca trava o uso.

### Publicando uma versão nova (mantenedor)

```bash
echo "3.4.0" > VERSION
git commit -am "release 3.4.0" && git push
git tag v3.4.0 && git push --tags
```

A [GitHub Action](.github/workflows/release.yml) compila o `.exe` no Windows e
publica o Release sozinha. Quem abrir o app recebe o aviso.

---

## Compilando o .exe manualmente

```bash
pip install -r requirements.txt pywebview pyinstaller
pyinstaller GueblyWatermark.spec --noconfirm --clean
# resultado: dist/GueblyWatermark.exe
```

---

## Como funciona por dentro

```
desktop.py     → sobe o Flask numa porta livre e abre a janela nativa (pywebview)
app.py         → servidor: rotas, imagem (Pillow) e vídeo (FFmpeg)
templates/
  index.html   → tela da Ferramenta livre
  guebly.html  → tela das Marcas Guebly
static/img/    → logos empacotadas + ícone do app
config.json    → empresas e padrões
VERSION        → versão exibida e usada na checagem de atualização
```

**Imagens** são compostas com Pillow (respeitando transparência).
**Vídeos** vão direto para o FFmpeg com filtro de overlay — sem recodificar o
áudio, e com suporte a marca d'água animada.

### Endpoints

| Rota | Método | Para quê |
|---|---|---|
| `/` | GET | Ferramenta livre |
| `/guebly` | GET | Marcas Guebly |
| `/api/process` | POST | Processa os arquivos (assíncrono, devolve um job) |
| `/api/progress/<id>` | GET | Progresso do job |
| `/api/download/<id>` | GET | Baixa o resultado |
| `/api/version` | GET | Versão instalada |
| `/api/update-check` | GET | Compara com o último Release do GitHub |

### Por que aplicativo em vez de site

Os arquivos nunca saem da máquina. Não há upload, servidor, fila nem custo por
uso — e funciona offline.

### Por que pywebview e não Electron

O app é Python. Com Electron seria preciso empacotar **três runtimes** (Node +
Python + FFmpeg), passando de 300 MB. O pywebview usa o **WebView2**, que já vem
no Windows 10/11 — o executável fica em ~66 MB com o FFmpeg incluso.

---

## Requisitos

- **Windows 10/11** para o `.exe` (usa o WebView2, nativo do sistema)
- **Python 3.9+** para rodar pelo código
- FFmpeg **não** precisa ser instalado — vem via `imageio-ffmpeg`

---

## Privacidade

Nenhum arquivo é enviado para lugar nenhum. O único acesso à internet é a
checagem de versão no GitHub (e o download de `logo_url`, se você usar logos
remotas em vez de locais).

---

## Licença

MIT — veja [LICENSE](./LICENSE).

<div align="center">
<sub>Feito pela <a href="https://www.guebly.com.br">Guebly LTDA</a></sub>
</div>
