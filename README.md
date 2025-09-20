
# Obsidian LLM Assistant

**Offline-first LLM assistant for Obsidian with task queue, semantic linking, and analytics.**

---

## **Features**

**Phase 1: Core Functionality**

- Ask questions to local LLaMA/GPT4All models
    
- Hybrid LLM routing (fast LLaMA vs deeper GPT4All)
    
- Session memory for context
    
- Automatic note creation (`Assistant_${timestamp}.md`)
    
- Task queue with inline previews
    

**Phase 2: Medium-Term Enhancements**

- Batch processing of multiple notes
    
- Vault scanning and indexing (`.md`, PDF, web pages)
    
- Semantic linking of notes
    
- Note formatting via LLM
    

**Phase 3: Advanced Features**

- Analytics dashboard: semantic coverage & QA history
    
- Queue search & filter
    
- Voice input support
    
- Optional caching & encryption for answers
    
- Multi-vault support
    

---

## **Project Structure**

```
obsidian-llm-assistant/
├─ backend/                # FastAPI backend modules
├─ plugin/                 # Obsidian plugin
├─ models/                 # Offline LLaMA/GPT4All models
├─ vault/                  # Example vault for notes
├─ cache/                  # Cached answers
├─ venv/                   # Python virtual environment
├─ setup.sh                # Linux/macOS setup script
├─ setup.ps1               # Windows setup script
└─ README.md
```


![[diagram.png]]


---

## **Setup Instructions**

### **1. Run Setup Script**

**Linux/macOS:**

```bash
bash setup.sh
```

**Windows:**

```powershell
.\setup.ps1
```

This will:

1. Create a Python virtual environment
    
2. Install dependencies (`fastapi`, `torch`, `chromadb`, `llama-cpp-python`, `gpt4all`, etc.)
    
3. Detect GPU/CPU
    
4. Download default models (LLaMA 7B Q4, GPT4All Lora)
    
5. Build the Obsidian plugin automatically
    

---

### **2. Activate Backend**

**Linux/macOS:**

```bash
source venv/bin/activate
python backend/backend.py
```

**Windows:**

```powershell
& venv\Scripts\Activate.ps1
python backend\backend.py
```

The backend will start at `http://localhost:8000` by default.

---

### **3. Install Plugin in Obsidian**

1. Copy the `plugin/` folder to your vault’s `.obsidian/plugins/obsidian-llm-plugin/`
    
2. Open Obsidian → Settings → Community Plugins → Enable `Obsidian LLM Assistant`
    
3. Configure:
    
    - **Backend URL**: `http://localhost:8000`
        
    - **Vault Path**: path to your notes
        
    - **Prefer Fast LLM**: toggle for LLaMA vs GPT4All
        

---

### **4. Using the Plugin**

- **Ask Question:** Ribbon icon 🎲 → input question → task added to queue
    
- **Start Queue:** Ribbon icon ▶ → processes tasks in order/batches
    
- **Pause Queue:** Ribbon icon ⏹ → pause processing
    
- **Voice Input:** optional microphone icon → speak your query
    
- **Analytics Dashboard:** Ribbon icon 📊 → semantic coverage, QA history
    
- **Inline Note Formatting:** Task queue automatically formats notes via backend
    
- **Link Notes:** Task queue generates semantic links automatically
    

---

### **5. Recommended Workflow**

1. **Scan Vault:** `Scan Vault` endpoint or first run → index all `.md` and PDFs
    
2. **Ask Questions:** Add queries to queue, or speak via voice input
    
3. **Process Queue:** Format notes, link notes, cache answers
    
4. **Review Analytics:** Track coverage and recent questions
    
5. **Iterate:** Update notes, reindex vault, repeat
    

---

### **6. Optional Features**

- **Web/PDF fetching:** Backend `/fetch_url` → index external resources
    
- **Reindex Vault:** Backend `/reindex` → refresh all embeddings
    
- **Encryption:** Enable in `backend/security.py` → encrypt cached answers
    

---

### **7. Screenshots / Placeholders**

> _(Add screenshots here if desired)_
> 
> - Task Queue Pane
>     
> - Ribbon Buttons
>     
> - Analytics Dashboard
>     
> - Inline Note Formatting
>     

---

### **8. Dependencies**

- Python 3.10+
    
- Node.js 18+ (for plugin build)
    
- `fastapi`, `uvicorn`, `torch`, `sentence-transformers`, `chromadb`
    
- `llama-cpp-python`, `gpt4all`
    
- `beautifulsoup4`, `readability-lxml`, `PyPDF2`
    
- Obsidian 1.5+
    

---

### **9. License / Author**

- Author: **Your Name**
    
- License: MIT
    
- GitHub: _(optional link)_
    

---

This `README.md` provides **everything a user needs** to install, configure, and start using your offline-first Obsidian LLM assistant.



