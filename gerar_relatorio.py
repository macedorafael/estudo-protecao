"""
Script simples para gerar o estudo FRIGOSUL.
Envia os parâmetros diretamente para a API e salva o PDF.

Uso:
  python gerar_frigosul.py
"""

import json
import sys
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:
    print("Instalando 'requests'...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "--quiet"])
    import requests

# ─────────────────────────────────────────────────────────────────────────────
# PARÂMETROS DO ESTUDO — FRIGOSUL
# (baseados no ESTUDO DE PROTEÇÃO E SELETIVIDADE FRIGOSUL.pdf
#  e no documento CC_ FRIGOSUL_2784224.pdf da ENERGISA)
# ─────────────────────────────────────────────────────────────────────────────

estudo = {

    # ── Engenheiro responsável ───────────────────────────────────────────────
    "engenheiro": {
        "nome": "FLAVIO DE JESUS SALETTI",
        "crea": "5062320435D / VISTO MS: 25168"
    },

    # ── Dados da concessionária (documento CC_ FRIGOSUL_2784224.pdf) ─────────
    "concessionaria": {
        "tensao_kv":            34.5,
        "icc_3f_a":             1049.0,   # ICC trifásico simétrico
        "angulo_3f_grau":       -70.0,
        "icc_ft_a":             850.9,    # ICC fase-terra simétrico
        "angulo_ft_grau":       -73.0,
        "r1_pu":                0.5543,   # Impedância sequência positiva
        "x1_pu":                1.4959,
        "r0_pu":                0.6319,   # Impedância sequência zero
        "x0_pu":                2.6459,
        "potencia_base_mva":    100.0,
        "subestacao":           "APARECIDA DO TABOADO",
        "circuito":             "ATA51",

        # Ajustes do religador da ENERGISA (retaguarda)
        "religador_upstream": {
            "modelo":           "COOPER F6 (595-06)",
            "pickup_fase_a":    150.0,    # 51F pickup
            "dial_fase":        0.20,     # 51F dial
            "curva_fase":       "IEC VI",
            "inst_fase_a":      690.0,    # 50F instantânea
            "pickup_neutro_a":  35.0,     # 51N pickup
            "dial_neutro":      0.86,     # 51N dial
            "curva_neutro":     "IEC VI",
            "inst_neutro_a":    690.0     # 50N instantânea
        }
    },

    # ── Dados do cliente ─────────────────────────────────────────────────────
    "cliente": {
        "razao_social":  "FRIGOSUL - FRIGORIFICO SUL LTDA",
        "cnpj":          "",
        "endereco":      "Aparecida do Taboado - MS",
        "uc":            "1628723",
        # Demanda em kVA: 1840 kW ÷ 0,92 fp = 2000 kVA
        # (In = 2000 / (√3 × 34,5) = 33,47 A  ✓ confirma o estudo)
        "demanda_kva":       2000.0,
        "fator_potencia":    0.92
    },

    # ── Transformadores (5 unidades, dados da plaqueta) ───────────────────────
    "transformadores": [
        {
            "potencia_kva":    45,
            "impedancia_pct":  4.05,
            "tipo":            "Óleo",
            "fator_inrush":    10,
            "tempo_inrush_s":  0.1,
            "tempo_ansi_s":    3,
            "fusivel":         "1H"
        },
        {
            "potencia_kva":    500,
            "impedancia_pct":  5.27,
            "tipo":            "Óleo",
            "fator_inrush":    10,
            "tempo_inrush_s":  0.1,
            "tempo_ansi_s":    4,
            "fusivel":         "10K"
        },
        {
            "potencia_kva":    750,
            "impedancia_pct":  5.35,
            "tipo":            "Óleo",
            "fator_inrush":    10,
            "tempo_inrush_s":  0.1,
            "tempo_ansi_s":    4,
            "fusivel":         "12K"
        },
        {
            "potencia_kva":    1000,
            "impedancia_pct":  5.34,
            "tipo":            "Óleo",
            "fator_inrush":    10,
            "tempo_inrush_s":  0.1,
            "tempo_ansi_s":    4,
            "fusivel":         "15K"
        },
        {
            "potencia_kva":    1000,
            "impedancia_pct":  5.34,
            "tipo":            "Óleo",
            "fator_inrush":    10,
            "tempo_inrush_s":  0.1,
            "tempo_ansi_s":    4,
            "fusivel":         "15K"
        }
    ],

    # ── Equipamentos de proteção ──────────────────────────────────────────────
    "equipamentos": {
        # TC integrado ao religador NOJA Power OSM38-12-800
        "tc_primario_a":              2500,
        "tc_secundario_a":            1,
        "ztc_ohm":                    0.10,
        "cabo_comprimento_m":         20.0,
        "cabo_secao_mm2":             4.0,
        "rele_fabricante":            "NOJA Power",
        "rele_modelo":                "OSM38-12-800",
        "rele_corrente_nominal_a":    1,
        "rele_impedancia_ohm":        0.028,
        "possui_geracao_distribuida": False,   # "Não haverá GD na unidade"
        "possui_nobreak":             True     # TP auxiliar instalado (p.9)
    },

    # ── Funções ANSI ──────────────────────────────────────────────────────────
    "funcoes_ansi": {
        "f51_fase":    True,
        "f50_fase":    True,
        "f51n_neutro": True,
        "f50n_neutro": True,
        "f51gs":       False,
        "f27":         False,
        "f47":         False,
        "f59":         False,
        "f79v":        False,   # "função 79 será Desabilitada"
        "f81u":        False,
        "f81o":        False,
        "f86":         False,
        "curva_rele":              "IEC VI",   # "Muito Inversa" conforme ENERGISA
        "pickup_neutro_pct_fase":  19          # 19% conforme NDU-002 / estudo p.8
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# ENVIO PARA A API
# ─────────────────────────────────────────────────────────────────────────────

API_URL = "http://localhost:8000/api/gerar-estudo"

print("=" * 60)
print("  Gerador de Estudo — FRIGOSUL")
print("=" * 60)
print(f"  Cliente : {estudo['cliente']['razao_social']}")
print(f"  UC      : {estudo['cliente']['uc']}")
print(f"  Circuito: {estudo['concessionaria']['circuito']}")
print(f"  Data    : {date.today().strftime('%d/%m/%Y')}")
print("=" * 60)
print()
print("Enviando parâmetros para a API...", end=" ", flush=True)

try:
    resp = requests.post(API_URL, json=estudo, timeout=30)
except requests.ConnectionError:
    print("\n")
    print("ERRO: Não foi possível conectar à API.")
    print("      Certifique-se de que o start.bat está rodando.")
    print("      API esperada em: http://localhost:8000")
    input("\nPressione Enter para sair...")
    sys.exit(1)

if resp.status_code != 200:
    print(f"\nERRO {resp.status_code}:")
    try:
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(resp.text[:500])
    input("\nPressione Enter para sair...")
    sys.exit(1)

print("OK")

# Salva o PDF na pasta do projeto
nome_arquivo = f"Estudo_FRIGOSUL_{date.today().strftime('%Y%m%d')}.pdf"
caminho_pdf = Path(__file__).parent / nome_arquivo

with open(caminho_pdf, "wb") as f:
    f.write(resp.content)

tamanho_kb = len(resp.content) // 1024
print(f"PDF gerado com sucesso: {nome_arquivo} ({tamanho_kb} KB)")
print(f"Caminho: {caminho_pdf}")
print()

# Abre o PDF automaticamente
import subprocess, os
try:
    os.startfile(str(caminho_pdf))
    print("Abrindo PDF...")
except Exception:
    print("Abra manualmente o arquivo acima.")

input("\nPressione Enter para sair...")
