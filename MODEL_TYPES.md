# Типы моделей и их конфигурация

В приложении ChatList поддерживаются следующие типы моделей нейросетей:

## Поддерживаемые типы моделей

### 1. OpenAI
**Тип:** `openai`  
**API URL:** `https://api.openai.com/v1/chat/completions`  
**API Key:** `OPENAI_API_KEY`  
**Примеры моделей:** `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`

**Пример конфигурации:**
- Название: `GPT-4`
- API URL: `https://api.openai.com/v1/chat/completions`
- API Key (env var): `OPENAI_API_KEY`
- Тип модели: `openai`

---

### 2. OpenRouter
**Тип:** `openrouter`  
**API URL:** `https://openrouter.ai/api/v1/chat/completions`  
**API Key:** `OPENROUTER_API_KEY`  
**Примеры моделей:** `openai/gpt-4`, `meta-llama/llama-3.3-70b-instruct:free`, `xiaomi/mimo-v2-flash:free`

**Пример конфигурации:**
- Название: `meta-llama/llama-3.3-70b-instruct:free`
- API URL: `https://openrouter.ai/api/v1/chat/completions`
- API Key (env var): `OPENROUTER_API_KEY`
- Тип модели: `openrouter`

---

### 3. DeepSeek
**Тип:** `deepseek`  
**API URL:** `https://api.deepseek.com/v1/chat/completions`  
**API Key:** `DEEPSEEK_API_KEY`  
**Примеры моделей:** `deepseek-chat`, `deepseek-coder`

**Пример конфигурации:**
- Название: `deepseek-chat`
- API URL: `https://api.deepseek.com/v1/chat/completions`
- API Key (env var): `DEEPSEEK_API_KEY`
- Тип модели: `deepseek`

---

### 4. Groq
**Тип:** `groq`  
**API URL:** `https://api.groq.com/openai/v1/chat/completions`  
**API Key:** `GROQ_API_KEY`  
**Примеры моделей:** `llama-3.1-70b-versatile`, `mixtral-8x7b-32768`

**Пример конфигурации:**
- Название: `llama-3.1-70b-versatile`
- API URL: `https://api.groq.com/openai/v1/chat/completions`
- API Key (env var): `GROQ_API_KEY`
- Тип модели: `groq`

---

### 5. Anthropic (Claude)
**Тип:** `anthropic`  
**API URL:** Зависит от провайдера (обычно через прокси с OpenAI-совместимым API)  
**API Key:** `ANTHROPIC_API_KEY` или через провайдера  
**Примеры моделей:** `claude-3-5-sonnet`, `claude-3-opus`

**Пример конфигурации (через OpenRouter):**
- Название: `anthropic/claude-3-5-sonnet`
- API URL: `https://openrouter.ai/api/v1/chat/completions`
- API Key (env var): `OPENROUTER_API_KEY`
- Тип модели: `openrouter`

---

### 6. Google (Gemini)
**Тип:** `google`  
**API URL:** Зависит от провайдера (через OpenAI-совместимый API)  
**API Key:** `GOOGLE_API_KEY` или через провайдера  
**Примеры моделей:** `gemini-pro`, `gemini-1.5-pro`

**Пример конфигурации (через OpenRouter):**
- Название: `google/gemini-pro`
- API URL: `https://openrouter.ai/api/v1/chat/completions`
- API Key (env var): `OPENROUTER_API_KEY`
- Тип модели: `openrouter`

---

### 7. Mistral AI
**Тип:** `mistral`  
**API URL:** `https://api.mistral.ai/v1/chat/completions` (или через провайдера)  
**API Key:** `MISTRAL_API_KEY`  
**Примеры моделей:** `mistral-large`, `mistral-medium`

**Пример конфигурации:**
- Название: `mistral-large`
- API URL: `https://api.mistral.ai/v1/chat/completions`
- API Key (env var): `MISTRAL_API_KEY`
- Тип модели: `mistral`

---

### 8. Cohere
**Тип:** `cohere`  
**API URL:** Зависит от провайдера (через OpenAI-совместимый API)  
**API Key:** `COHERE_API_KEY`  
**Примеры моделей:** `command`, `command-light`

**Пример конфигурации:**
- Название: `command`
- API URL: `https://api.cohere.ai/v1/chat/completions` (если поддерживается)
- API Key (env var): `COHERE_API_KEY`
- Тип модели: `cohere`

---

### 9. Perplexity
**Тип:** `perplexity`  
**API URL:** `https://api.perplexity.ai/chat/completions`  
**API Key:** `PERPLEXITY_API_KEY`  
**Примеры моделей:** `llama-3.1-sonar-large-128k-online`, `sonar-pro`

**Пример конфигурации:**
- Название: `llama-3.1-sonar-large-128k-online`
- API URL: `https://api.perplexity.ai/chat/completions`
- API Key (env var): `PERPLEXITY_API_KEY`
- Тип модели: `perplexity`

---

### 10. Together AI
**Тип:** `together`  
**API URL:** `https://api.together.xyz/v1/chat/completions`  
**API Key:** `TOGETHER_API_KEY`  
**Примеры моделей:** `meta-llama/Llama-3-70b-chat-hf`, `mistralai/Mixtral-8x7B-Instruct-v0.1`

**Пример конфигурации:**
- Название: `meta-llama/Llama-3-70b-chat-hf`
- API URL: `https://api.together.xyz/v1/chat/completions`
- API Key (env var): `TOGETHER_API_KEY`
- Тип модели: `together`

---

### 11. Replicate
**Тип:** `replicate`  
**API URL:** Зависит от модели (через OpenAI-совместимый API)  
**API Key:** `REPLICATE_API_KEY`  
**Примеры моделей:** Зависит от доступных моделей на платформе

**Пример конфигурации:**
- Название: `meta/llama-2-70b-chat`
- API URL: `https://api.replicate.com/v1/chat/completions` (если поддерживается)
- API Key (env var): `REPLICATE_API_KEY`
- Тип модели: `replicate`

---

### 12. Hugging Face
**Тип:** `huggingface`  
**API URL:** `https://api-inference.huggingface.co/v1/chat/completions`  
**API Key:** `HUGGINGFACE_API_KEY`  
**Примеры моделей:** `meta-llama/Llama-2-70b-chat-hf`, `mistralai/Mistral-7B-Instruct-v0.1`

**Пример конфигурации:**
- Название: `meta-llama/Llama-2-70b-chat-hf`
- API URL: `https://api-inference.huggingface.co/v1/chat/completions`
- API Key (env var): `HUGGINGFACE_API_KEY`
- Тип модели: `huggingface`

---

### 13. Azure OpenAI
**Тип:** `azure-openai`  
**API URL:** `https://YOUR_RESOURCE.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT/chat/completions?api-version=2024-02-15-preview`  
**API Key:** `AZURE_OPENAI_API_KEY`  
**Примеры моделей:** `gpt-4`, `gpt-35-turbo`

**Пример конфигурации:**
- Название: `gpt-4`
- API URL: `https://YOUR_RESOURCE.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT/chat/completions?api-version=2024-02-15-preview`
- API Key (env var): `AZURE_OPENAI_API_KEY`
- Тип модели: `azure-openai`

---

### 14. Ollama (локальные модели)
**Тип:** `ollama`  
**API URL:** `http://localhost:11434/v1/chat/completions` (или ваш сервер)  
**API Key:** Не требуется (или `OLLAMA_API_KEY` если настроено)  
**Примеры моделей:** `llama2`, `mistral`, `codellama`

**Пример конфигурации:**
- Название: `llama2`
- API URL: `http://localhost:11434/v1/chat/completions`
- API Key (env var): `OLLAMA_API_KEY` (или оставить пустым)
- Тип модели: `ollama`

---

### 15. LocalAI
**Тип:** `localai`  
**API URL:** `http://localhost:8080/v1/chat/completions` (или ваш сервер)  
**API Key:** Не требуется  
**Примеры моделей:** Зависит от установленных моделей

**Пример конфигурации:**
- Название: `gpt-4`
- API URL: `http://localhost:8080/v1/chat/completions`
- API Key (env var): `LOCALAI_API_KEY` (или оставить пустым)
- Тип модели: `localai`

---

### 16. Other (Другие)
**Тип:** `other`  
**API URL:** Любой OpenAI-совместимый API  
**API Key:** Зависит от провайдера  

Используется для любых других провайдеров, которые поддерживают OpenAI-совместимый формат API.

**Пример конфигурации:**
- Название: `custom-model`
- API URL: `https://api.example.com/v1/chat/completions`
- API Key (env var): `CUSTOM_API_KEY`
- Тип модели: `other`

---

## Примечания

1. **OpenAI-совместимый формат:** Большинство провайдеров используют формат API, совместимый с OpenAI, поэтому они будут работать через универсальный запрос (`send_generic_request`).

2. **OpenRouter как универсальный провайдер:** OpenRouter предоставляет доступ ко многим моделям через единый API, что упрощает использование различных моделей.

3. **Локальные модели:** Для Ollama и LocalAI убедитесь, что сервер запущен и доступен по указанному URL.

4. **API ключи:** Все API ключи должны быть указаны в файле `.env` с соответствующими именами переменных.

5. **Проверка доступности:** Перед добавлением модели рекомендуется проверить её доступность через тестовый запрос.

