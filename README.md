# WatermarkTool v3.0

**Aplicador de marca d'água para imagens e vídeos — open source, sem dependências de nuvem.**

---

## Funcionalidades

| Recurso | Detalhe |
|---|---|
| **Imagens** | PNG, JPG, WEBP, BMP, TIFF — saída em PNG |
| **Vídeos** | MP4, MOV, AVI, MKV, WEBM, FLV, WMV — saída em MP4 |
| **Logo por arquivo** | Upload de PNG, JPG ou WEBP |
| **Logo por URL** | Cole qualquer URL pública |
| **Texto como marca d'água** | Cor, fundo e opacidade configuráveis |
| **Pré-visualização local** | Canvas ao vivo para imagens, frame para vídeos |
| **7 posições** | 4 cantos + 3 centros |
| **Escala / Opacidade / Margem** | Sliders em tempo real |
| **Lote** | Múltiplas mídias → ZIP automático |

---

## Instalação rápida no Windows

1. Instale o **FFmpeg** (necessário para vídeos): https://ffmpeg.org/download.html
2. Clique duas vezes em **`iniciar.bat`**
3. Na primeira execução as dependências Python são instaladas automaticamente
4. Acesse **http://localhost:5000**

> O `iniciar.bat` unifica instalação + inicialização em um arquivo só.

---

## Instalação manual (Linux/macOS)

```bash
# FFmpeg
sudo apt install ffmpeg          # Debian/Ubuntu
brew install ffmpeg              # macOS

# Dependências Python
pip install -r requirements.txt

# Iniciar
python app.py
```

---

## Marca d'água em texto

Na aba **Texto** da ferramenta:

- Digite qualquer texto (ex: `© Guebly 2025`, `Confidencial`)
- Escolha a cor do texto e a cor/opacidade do fundo
- O tamanho é controlado pelo slider **Escala**

Funciona em imagens e vídeos.

---

## Marca d'água em vídeos

O processamento usa **MoviePy + FFmpeg**. O tempo varia conforme duração e resolução.
Vídeos curtos (< 30s em 1080p) levam cerca de 30–60 segundos.

Para vídeos longos em produção, use Gunicorn com timeout estendido:

```bash
gunicorn app:app --bind 0.0.0.0:5000 --workers 2 --timeout 300
```

---

## Configuração (`config.json`)

```json
{
  "default_position":    "bottom-right",
  "default_scale_pct":   15,
  "default_margin_pct":  3,
  "default_opacity_pct": 90
}
```

---

## Painel interno (`/guebly`)

Rota não divulgada com logos pré-configuradas por empresa. Configure em `config.json`:

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

---

## Estrutura do projeto

```
watermark-tool/
├── app.py              # Backend Flask
├── config.json         # Configurações e empresas
├── requirements.txt    # Dependências Python
├── iniciar.bat         # Instala + inicia (Windows)
├── static/img/         # Logo do header
└── templates/
    ├── index.html      # Interface pública
    └── guebly.html     # Painel interno
```

---

## Dependências

```
flask>=3.0
pillow>=10.0
moviepy>=1.0.3
imageio-ffmpeg>=0.4.9
numpy>=1.24
```

---

MIT License — *Guebly Holding LTDA · guebly.com.br*
