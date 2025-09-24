# 🩺 Healthcare Graph-RAG Chatbot  

An AI-powered **healthcare assistant** that uses a **Knowledge Graph (Neo4j)** + **RAG (Retrieval-Augmented Generation)** + **LLMs (LLaMA via Ollama + LangChain)** to answer medical queries.  

⚠️ **Disclaimer**: This chatbot is **not a replacement for professional medical advice**. Always consult a qualified healthcare professional for medical concerns.  

---

## 🚀 Features
- **Conversational Chatbot**: Ask how you’re feeling, and the bot analyzes your symptoms.  
- **Knowledge Graph Powered**: Symptoms, diseases, cures, medicines, and precautions are stored in Neo4j.  
- **RAG Pipeline**: Queries fetch relevant knowledge graph data and inject it into the LLM context.  
- **Agent Support**: Uses LangGraph agents + tools for flexible reasoning and multi-step actions.  
- **Custom Instructions**: Behavior is guided by an external `instructions.txt` file.  

---

## 🛠️ Tech Stack & Skills Demonstrated

| Area | Technologies & Skills |
|------|------------------------|
| **LLMs** | [Ollama](https://ollama.ai) with **LLaMA 3** |
| **RAG (Retrieval-Augmented Generation)** | [LangChain](https://www.langchain.com), context building |
| **Graph Database** | [Neo4j](https://neo4j.com) |
| **ETL & Data Engineering** | Custom pipelines to ingest raw data → JSON → Neo4j |
| **Agents** | [LangGraph](https://langchain-ai.github.io/langgraph/) with ReAct agents & tools |
| **Python Development** | Pydantic, structured JSON schemas, OOP |
| **Prompt Engineering** | Instruction-based system prompts |
| **Software Engineering Skills** | Modular code, configs, logging, testing-ready design |

---

## 📂 Project Structure

```bash
healthcare-graph-rag/
│
├── app/
│   ├── graph_connector.py      # Handles Neo4j queries & builds RAG context
│   ├── llm_agent.py            # LLM + Agent setup with Ollama + LangGraph
│   ├── instructions.txt        # Customizable system prompt for LLM
│   └── ...
│
├── data/
│   ├── diseases.json           # Example data with cures, medicines, precautions
│   ├── symptoms.json
│   └── ...
│
├── README.md                   # This file
└── requirements.txt            # Python dependencies
```

---

## ⚙️ Setup & Installation

### 1. Clone Repository
```bash
git clone https://github.com/SameerSingh2901/AI-Healthcare-Chatbot.git
cd AI-Healthcare-Chatbot
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scriptsctivate      # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

Key dependencies include:
- `neo4j`
- `langchain`
- `langchain-ollama`
- `langgraph`
- `pydantic`

### 4. Setup Neo4j
- Install [Neo4j Desktop](https://neo4j.com/download/) or run via Docker.  
- Create a database and note down:
  - `NEO4J_URI`
  - `NEO4J_USER`
  - `NEO4J_PASSWORD`
- Update these in your config or environment variables.

### 5. Install & Run Ollama
- Install [Ollama](https://ollama.ai/download)  
- Pull the LLaMA model:
```bash
ollama pull llama3.1:latest
```

---

## ▶️ Usage

### Run Graph Connector
```bash
python app/graph_connector.py
```
- Tests queries against your Neo4j database.
- Example: get diseases by symptoms, retrieve details.

### Run LLM Agent
```bash
python app/llm_agent.py
```
- Starts demo mode with two flows:
  1. **Direct RAG Query**: Injects graph context into LLM.  
  2. **Agent Query**: Lets the agent call tools (graph query, dummy agent).  

---

## 🧠 How It Works

### 🔹 Pipeline
1. **User Input**: “I have fever and cough.”  
2. **Symptom Extraction**: Symptoms mapped to graph nodes.  
3. **Neo4j Query**: Finds diseases linked to those symptoms.  
4. **Context Builder**: Formats disease info (description, cures, medicines, precautions).  
5. **RAG**: Injects context into the LLM prompt.  
6. **LLM Reasoning**: LLaMA answers user queries using only graph context.  
7. **Agent Mode**: Tools can be called dynamically for more info.  

### 🔹 Example Conversation
```text
User: I have fever and cough.
Assistant:
Possible Diseases:
- Flu
- Pneumonia

Next Steps:
- Stay hydrated, rest
- Consider paracetamol for fever
- Consult a doctor if symptoms persist

Disclaimer: I am not a doctor. Please consult a healthcare professional.
```

---

## 🖼️ Architecture Diagram (Mermaid)

```mermaid
flowchart TD
    User([User Query]) -->|Symptoms| Extract[Symptom Extraction]
    Extract -->|Input| Neo4j[(Neo4j Graph DB)]
    Neo4j --> Context[Context Builder]
    Context --> RAG[RAG Pipeline]
    RAG --> LLM[LLaMA via Ollama]
    LLM --> Response[Final Answer]
    Response --> User
```

---

## 🔧 Skills Showcased for Resume/Portfolio
- ✅ Retrieval-Augmented Generation (RAG) with LangChain  
- ✅ Neo4j Knowledge Graph integration  
- ✅ LLaMA model deployment via Ollama  
- ✅ AI Agents with LangGraph (ReAct paradigm)  
- ✅ Python best practices (modular code, OOP, configs)  
- ✅ Prompt engineering with instruction-tuning  

---

## 📌 Next Steps / Future Improvements
- Add **NER-based Symptom Extraction** (spaCy, transformers).  
- Expand dataset with real medical ontologies (e.g., SNOMED CT).  
- Enhance **agent with external APIs** (drug info, hospitals).  
- Build a **frontend (React/Streamlit)** for patient-like interaction.  
- Add **evaluation metrics** for chatbot responses.  

---

## ⚠️ Disclaimer
This project is for **educational purposes only**.  
It is **not a substitute for professional medical advice, diagnosis, or treatment**.  
Always seek advice from a licensed healthcare provider.  
