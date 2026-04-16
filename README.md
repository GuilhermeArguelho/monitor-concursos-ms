# Monitor de Concursos Públicos de TI - Campo Grande/MS

Script que processa a resposta JSON do Gemini Deep Research e insere novas oportunidades em uma planilha do Google Sheets.

## Como usar em outro computador

1. **Clone o repositório**

```bash
git clone https://github.com/GuilhermeArguelho/monitor-concursos-ms.git
```

2. **Instale as dependências**

```bash
pip install gspread google-auth
```

3. **Configure o Google Sheets**

```bash
- Crie uma conta de serviço e baixe o arquivo credenciais.json (veja instruções no [link para seu guia]).

- Coloque o credenciais.json na pasta raiz.

- Compartilhe sua planilha com o e-mail da conta de serviço como Editor.
```

4. **Edite o ID da planilha no arquivo processar_concursos.py.**

5. **Execute**

```bash
python processar_concursos.py
```
