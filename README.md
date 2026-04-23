# Gerador de Estudos de Proteção e Seletividade de Média Tensão

Aplicação web local para geração automática de **estudos de coordenação de proteção e seletividade** de instalações de média tensão, conforme:

- **ABNT NBR 14039:2005** — Instalações elétricas de média tensão de 1,0 kV a 36,2 kV
- **NDU 002 ENERGISA** — Norma de distribuição para conexão de consumidores MT

Desenvolvido para o **Eng. Flávio de Jesus Saletti** (CREA 5062320435D).

---

## Funcionalidades

- Formulário web completo com todos os parâmetros do estudo
- Campos da concessionária com badge **ENERGISA** e tooltips explicativos
- Cálculos automáticos conforme metodologia de João Mamede Filho (8ª ed.)
- Geração de relatório em **PDF** com:
  - Capa com dados do cliente e engenheiro responsável
  - Tabela de correntes (demanda, inrush real, ponto ANSI por transformador)
  - Dimensionamento do TC e verificação de saturação
  - Tabela de ajustes de proteção (51F, 50F, 51N, 50N)
  - Verificação de coordenação com o religador upstream
  - **Dois coordenogramas** (FASE e NEUTRO) em páginas paisagem A4
- Script de geração rápida para clientes recorrentes (ex: `gerar_relatorio.py`)

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS |
| Backend | Python 3.11 + FastAPI |
| Cálculos | NumPy |
| Coordenograma | Matplotlib |
| PDF | ReportLab |
| Comunicação | REST JSON → PDF binário |

---

## Requisitos

- **Python 3.11+** — [python.org](https://www.python.org/downloads/)
- **Node.js 18+** — [nodejs.org](https://nodejs.org/)

---

## Instalação

Execute apenas uma vez após clonar o repositório:

```bat
instalar.bat
```

Isso irá:
1. Criar o ambiente virtual Python em `backend/.venv`
2. Instalar as dependências Python (`FastAPI`, `ReportLab`, `Matplotlib`, etc.)
3. Instalar as dependências Node.js (`React`, `Vite`, `Tailwind CSS`)

---

## Como usar

### 1. Iniciar a aplicação

```bat
start.bat
```

Abre automaticamente:
- **Frontend** → http://localhost:5173
- **API** → http://localhost:8000/docs

### 2. Preencher o formulário

Preencha os campos agrupados em 5 seções:

| Seção | Descrição |
|-------|-----------|
| **Engenheiro** | Nome e CREA do responsável pelo estudo |
| **Concessionária** | Dados do documento ATA/NCC (marcados com badge ENERGISA) |
| **Cliente** | Razão social, UC, demanda e fator de potência |
| **Transformadores** | Lista dinâmica — adicione quantos forem necessários |
| **Equipamentos** | Dados do TC, cabo e relé de proteção |
| **Funções ANSI** | Habilitação de cada função e curva do relé |

### 3. Gerar o estudo

Clique em **"Gerar Estudo PDF"** — o arquivo é baixado automaticamente.

---

## Geração rápida (script)

Para clientes com parâmetros fixos, edite `gerar_relatorio.py` com os dados do cliente e execute:

```bat
GERAR_RELATORIO.bat
```

O PDF é gerado e aberto automaticamente. O backend precisa estar rodando via `start.bat`.

---

## Estrutura do projeto

```
estudo-protecao/
├── backend/
│   ├── app/
│   │   ├── main.py           # Rotas FastAPI
│   │   ├── models.py         # Schemas Pydantic (parâmetros de entrada)
│   │   ├── calculations.py   # Fórmulas do estudo (IEC, inrush, ANSI, TC)
│   │   ├── curves.py         # Coordenogramas Matplotlib (FASE e NEUTRO)
│   │   └── report.py         # Geração do PDF ReportLab
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.tsx
│       ├── types.ts
│       └── components/
│           └── sections/     # Um componente por grupo de parâmetros
├── gerar_relatorio.py        # Script de geração rápida (ex: FRIGOSUL)
├── GERAR_RELATORIO.bat       # Atalho Windows para o script
├── instalar.bat              # Instalação das dependências
└── start.bat                 # Inicialização do app
```

---

## API

```
POST /api/gerar-estudo
Content-Type: application/json
Body: { StudyParameters }
Response: application/pdf
```

```
GET /api/health
Response: { "status": "ok" }
```

Documentação interativa disponível em http://localhost:8000/docs após iniciar o backend.

---

## Cálculos implementados

| Cálculo | Fórmula |
|---------|---------|
| Corrente de demanda | `In = S / (√3 × V)` |
| Inrush parcial | `10 × In_maior + Σ In_demais` |
| Inrush real (corrigido) | `I_real = Vfn / (Zs + Zitm)` |
| Ponto ANSI fase | `I_ANSI = In_trafo / (Z% / 100)` |
| Ponto ANSI neutro | `I_ANSI_N ≈ 0,578 × I_ANSI_fase` |
| Pickup 51F | `Ip = 1,25 × In_demanda` |
| Pickup 51N | `Ip_N = x% × Ip_fase` (configurável, padrão 19%) |
| Instantânea 50F | `I_inst = 1,1 × I_inrush_real` |
| Time Dial (IEC) | `TD = t_max × (M − 1) / K` |
| Saturação do TC | `I_sat = RTC × 20 > ICC_3Ø` |

Curvas IEC suportadas: **VI** (Very Inverse), **EI** (Extremely Inverse), **MI** (Moderately Inverse), **LI** (Long-Time Inverse).

---

## Licença

Uso privado — desenvolvido para uso interno do escritório do Eng. Flávio Saletti.
