# 🏷️ WatermarkTool

**Aplicador de marca d'água para imagens — leve, open source, sem dependências de nuvem.**

Faça upload de uma ou várias imagens, carregue sua logo (por arquivo ou URL), ajuste posição, escala e opacidade — e baixe em PNG (1 imagem) ou ZIP (várias). Tudo processado localmente no seu servidor, sem envio de dados para terceiros.

---

## ✨ Funcionalidades

| Recurso | Detalhe |
|---|---|
| **Upload de logo** | Arraste ou clique — PNG, JPG, WEBP |
| **Logo por URL** | Cole a URL de qualquer logo hospedada |
| **Pré-visualização local** | Canvas ao vivo — sem enviar nada ao servidor |
| **7 posições** | 4 cantos, 3 centros (horizontal e absoluto) |
| **Escala** | 3% a 40% relativo à menor dimensão |
| **Opacidade** | 20% a 100% |
| **Margem** | 0% a 12% |
| **Lote** | Múltiplas imagens → ZIP automático |
| **Sem banco de dados** | Logos temporárias ficam em memória do OS |
| **Open source** | MIT License |

---

## 🚀 Instalação e uso

### Pré-requisitos

- Python 3.9 ou superior
- pip

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/watermark-tool.git
cd watermark-tool

# 2. (Opcional) Crie um ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Inicie o servidor
python app.py
```

Acesse em: **http://localhost:5000**

### Windows (sem terminal)

Use os atalhos incluídos:

- `instalar.bat` → instala as dependências (rode uma vez)
- `iniciar.bat` → inicia o servidor (use sempre que quiser abrir a ferramenta)

---

## 📁 Estrutura do projeto

```
watermark-tool/
├── app.py                  # Backend Flask — rotas e processamento
├── config.json             # Configurações padrão e empresas (se aplicável)
├── requirements.txt        # Dependências Python
├── instalar.bat            # Instalador Windows
├── iniciar.bat             # Iniciador Windows
│
├── static/
│   └── img/
│       └── guebly.png      # Logo exibida no header (substitua pela sua)
│
└── templates/
    ├── index.html          # Interface pública
    └── guebly.html         # Painel interno (rota /g) — opcional
```

---

## ⚙️ Configuração (`config.json`)

```json
{
  "default_position":    "bottom-right",
  "default_scale_pct":   15,
  "default_margin_pct":  3,
  "default_opacity_pct": 90
}
```

| Campo | Descrição | Valores |
|---|---|---|
| `default_position` | Posição padrão da logo | `top-left`, `top-center`, `top-right`, `center`, `bottom-left`, `bottom-center`, `bottom-right` |
| `default_scale_pct` | Escala padrão (% da menor dimensão) | `3` a `40` |
| `default_margin_pct` | Margem padrão | `0` a `12` |
| `default_opacity_pct` | Opacidade padrão | `20` a `100` |

---

## 🔒 Painel interno de empresas (`/g`)

> Esta seção é opcional e destina-se ao uso com empresas pré-configuradas.

O WatermarkTool inclui uma rota interna em `/g` que permite selecionar uma empresa e usar a logo pré-configurada, sem precisar fazer upload toda vez.

### Como configurar

Adicione as empresas no `config.json`:

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

| Campo | Descrição |
|---|---|
| `id` | Identificador único (slug, sem espaços) |
| `name` | Nome exibido na interface |
| `logo_url` | URL pública da logo (PNG com transparência recomendado) |
| `color` | Cor de destaque no painel (hex) |

### Usando o painel interno

1. Acesse `http://localhost:5000/g`
2. Selecione a empresa
3. (Opcional) Sobrescreva a logo com upload ou outra URL
4. Selecione as imagens, ajuste posição/escala e baixe

---

## 🌐 Deploy em produção

### Com Gunicorn (Linux)

```bash
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:5000 --workers 4
```

### Com variável de ambiente para porta

```bash
PORT=8080 python app.py
```

### Configurações recomendadas

- Coloque um **proxy reverso** (Nginx, Caddy) na frente
- Se usar a rota `/g`, proteja-a com autenticação HTTP básica no proxy
- Defina `debug=False` em produção (o `app.py` já lida com isso via `PORT`)

---

## 🖼️ Formatos suportados

**Entrada (imagens):** PNG, JPG, JPEG, WEBP, BMP, TIFF  
**Logo:** PNG (recomendado — suporte a transparência), JPG, WEBP  
**Saída:** PNG (sempre, com melhor qualidade)

---

## 📦 Dependências

```
flask>=3.0
pillow>=10.0
```

---

## 🤝 Contribuindo

1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/minha-feature`
3. Commit: `git commit -m 'feat: minha feature'`
4. Push: `git push origin feature/minha-feature`
5. Abra um Pull Request

---

## 📄 Licença

MIT License — use livremente, inclusive comercialmente.

---

*Desenvolvido por Guebly Holding LTDA · [guebly.com.br](https://guebly.com.br)*
