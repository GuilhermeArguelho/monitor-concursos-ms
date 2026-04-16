import json
import os
import glob
import hashlib
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ===== CONFIGURAÇÕES =====
PASTA_HISTORICO = "historico"
ARQUIVO_CREDENCIAIS = "credenciais.json"   # o arquivo baixado do Google Cloud
ID_PLANILHA = "1ToO3v8byFsprg2s9B8xYW_DciNIxnq-vy9syi0_mtoM" # o ID da sua planilha
# =========================

def conectar_planilha():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(ARQUIVO_CREDENCIAIS, scope)
    client = gspread.authorize(creds)
    return client.open_by_key(ID_PLANILHA).sheet1

def carregar_relatorio_anterior():
    arquivos = glob.glob(os.path.join(PASTA_HISTORICO, "*.json"))
    if not arquivos:
        return None
    arquivos.sort()
    with open(arquivos[-1], "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_relatorio_atual(dados):
    os.makedirs(PASTA_HISTORICO, exist_ok=True)
    caminho = os.path.join(PASTA_HISTORICO, f"{dados['data_execucao']}.json")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON salvo em {caminho}")

def gerar_chave_unica(oportunidade):
    chave = f"{oportunidade.get('orgao','')}|{oportunidade.get('cargo','')}|{oportunidade.get('edital_numero','')}|{oportunidade.get('data_publicacao','')}"
    return hashlib.md5(chave.encode()).hexdigest()

def filtrar_novidades(atual, anterior):
    if not anterior:
        return atual.get("novas_oportunidades", [])
    chaves_anteriores = set()
    for item in anterior.get("novas_oportunidades", []):
        chaves_anteriores.add(gerar_chave_unica(item))
    return [item for item in atual.get("novas_oportunidades", []) if gerar_chave_unica(item) not in chaves_anteriores]

def linha_ja_existe_na_planilha(sheet, oportunidade):
    """Verifica se a vaga já está na planilha (pelo link ou pelo título do edital)"""
    try:
        celulas = sheet.findall(oportunidade['link_direto'])
        if celulas:
            return True
        if oportunidade.get('edital_numero'):
            celulas = sheet.findall(oportunidade['edital_numero'])
            if celulas:
                return True
    except:
        pass
    return False

def adicionar_linha_planilha(sheet, data_execucao, oportunidade):
    """Adiciona uma linha à planilha se ainda não existir"""
    if linha_ja_existe_na_planilha(sheet, oportunidade):
        print(f"⏩ Vaga já existe na planilha: {oportunidade['orgao']} - {oportunidade['cargo']}")
        return False
    
    linha = [
        data_execucao,
        oportunidade['orgao'],
        oportunidade['cargo'],
        oportunidade.get('edital_numero', ''),
        oportunidade['link_direto'],
        oportunidade['data_publicacao'],
        oportunidade['resumo']
    ]
    sheet.append_row(linha)
    print(f"➕ Adicionada à planilha: {oportunidade['orgao']} - {oportunidade['cargo']}")
    return True

def main():
    print(f"🕒 Processando relatório de {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Carregar JSON atual (resposta do Gemini)
    try:
        with open("relatorio_hoje.json", "r", encoding="utf-8") as f:
            relatorio_atual = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo 'relatorio_hoje.json' não encontrado. Coloque a resposta do Gemini nesse arquivo.")
        return
    
    # 2. Carregar histórico local anterior
    relatorio_anterior = carregar_relatorio_anterior()
    
    # 3. Salvar JSON de hoje no histórico local
    salvar_relatorio_atual(relatorio_atual)
    
    # 4. Identificar novidades (evitar repetição do dia anterior)
    novidades = filtrar_novidades(relatorio_atual, relatorio_anterior)
    
    if not novidades:
        print("✅ Nenhuma novidade em relação ao dia anterior.")
        return
    
    # 5. Conectar à planilha e adicionar as novidades
    try:
        sheet = conectar_planilha()
        print(f"📊 Conectado à planilha. Adicionando {len(novidades)} oportunidade(s)...")
        for oport in novidades:
            adicionar_linha_planilha(sheet, relatorio_atual['data_execucao'], oport)
        print("🎉 Processamento concluído! Consulte sua planilha no Google Sheets.")
    except Exception as e:
        print(f"❌ Erro ao conectar ou escrever na planilha: {e}")
        print("Verifique se o arquivo credenciais.json está no lugar certo e o ID da planilha está correto.")

if __name__ == "__main__":
    main()