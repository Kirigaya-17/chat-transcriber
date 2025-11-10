# Projeto: ChatGPT + Vosk (Transcrição e Formatação de Áudio)

Este projeto implementa um sistema completo de **transcrição e formatação de áudio**.  
O usuário grava um áudio (`.wav`) no frontend React, o backend processa o arquivo com **Vosk** para extrair o texto e utiliza a **LLM** para gerar uma versão **formatada e legível** da fala.

---

## Estrutura do Geral

📁 chat-transcriber/
 ┣ 📂 frontend/   ← React (captura e exibição)
 ┗ 📂 backend/    ← Python + Flask ou FastAPI (Vosk + OpenAI)


## Estrutura do projeto





---

## 1. Instalação do Backend (FastAPI + Vosk)

### Pré-requisitos
- Python 3.10+  
- `pip` atualizado  
- Modelo Vosk em português:  
  [📥 Baixar aqui](https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip)

Descompacte o modelo dentro da pasta `backend/` e renomeie para `vosk-model-small-pt-0.3`.

ou

```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip
unzip vosk-model-small-pt-0.3.zip
```

### Instalação

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### Rodar servidor 

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 2. Instalação do Frontend (React)

### Instalação

```bash
cd frontend
npm install

npm run dev
```

