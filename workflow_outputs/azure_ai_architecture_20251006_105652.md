# ☁️ Azure AI Architecture Advisor - Comprehensive Guidance

---

## 🤖 AZURE AI SERVICES
Absolutely! Here's a practical architectural approach to building a customer service agent with the **Microsoft Agent Framework** and **Azure OpenAI Service**:

---

## 1. **Overview: Architecture & Key Components**

- **Microsoft Agent Framework** (now part of Azure AI Foundry) is designed to orchestrate conversations, behaviors, and multi-modal workflows.
- **Azure OpenAI Service** provides large language models (like GPT-4) for dialogue generation, intent extraction, and customer interaction.
- Optional integrations: Azure Cognitive Services (Vision, Speech, Language), Azure AI Document Intelligence.

---

## 2. **High-Level Architecture Diagram**

```
[Customer] <---> [Web App/Channel] <---> [Azure Agent Framework] <---> [Azure OpenAI Service]
                                                                        |
                                              [Azure Cognitive Services, Document Intelligence]
```

---

## 3. **Implementation Steps**

### **Step 1: Provision Services**
- Deploy **Azure OpenAI Resource** in the Azure portal.
- Deploy **Azure Agent Framework** via Azure AI Foundry (preview).
- Set up integration endpoints for web or Teams Bot channels.

### **Step 2: Build the Agent with Microsoft Agent Framework**

#### **Sample Code: Python Agent Using OpenAI Service**
```python
from agent_framework import Agent, Conversation, Action
from azure.openai import OpenAIClient

# Setup OpenAI Client
client = OpenAIClient(api_key="YOUR_AZURE_OPENAI_KEY", endpoint="YOUR_OPENAI_ENDPOINT")

class CustomerServiceAgent(Agent):
    def on_message(self, conversation: Conversation, message: str):
        # Use the Azure OpenAI Service
        response = client.chat_completion(
            deployment_id="YOUR_DEPLOYMENT_NAME",
            messages=[{"role": "user", "content": message}]
        )
        return conversation.reply(response['choices'][0]['message']['content'])

    def actions(self):
        # Define more actions here (search, escalate, query docs)
        return [
            Action("lookup_account", self.lookup_account),
            Action("escalate", self.escalate_ticket)
        ]

    def lookup_account(self, conversation, account_id):
        # Integrate with internal database/API
        ...
        return "Here's your account info."

    def escalate_ticket(self, conversation, issue):
        # Integrate with ticketing system (e.g., ServiceNow)
        ...
        return "Your issue has been escalated."

agent = CustomerServiceAgent()

# Bind agent to conversation channel (web, Teams, etc.)
```

> **Note:** This is an illustrative skeleton. Concrete implementations depend on your agent configuration, orchestration, conversation state, and channel adapters.

### **Step 3: Integrate Cognitive Services & Document Intelligence (Optional)**
- Add capabilities like:
  - Speech-to-text (Azure Speech)
  - Document extraction (Azure AI Document Intelligence)
  - Image analysis (Azure Computer Vision)
- Example: Extract customer info from uploaded PDF using Document Intelligence

```python
from azure.ai.formrecognizer import DocumentAnalysisClient

doc_client = DocumentAnalysisClient(endpoint, credential)
poller = doc_client.begin_analyze_document("prebuilt-document", pdf_bytes)
result = poller.result()
for field, value in result.fields.items():
    print(f"{field}: {value.value}")
```

---

## 4. **Configuration: Azure OpenAI Integration in Agent Framework**

```yaml
# agent_config.yaml (Example)
openai:
  endpoint: "https://YOUR_RESOURCE_NAME.openai.azure.com"
  api_key: "YOUR API KEY"
  deployment: "YOUR_MODEL_DEPLOYMENT_NAME"
agent:
  name: "CustomerSupportAgent"
  actions:
    - lookup_account
    - escalate
```
Register the config with your agent orchestration pipeline.

---

## 5. **Deployment Options**

- **Azure Web App** or **Bot Service** (for Teams, Webchat, etc.)
- Use **Azure Functions** for lightweight agent hosting.
- Monitoring and logging via **Azure Application Insights**.

---

## 6. **Best Practices & Next Steps**

- Manage OpenAI quotas and pricing [Azure OpenAI pricing docs](https://aka.ms/azureopenai/pricing).
- Use **Foundry’s** orchestration for multi-step and tool-augmented workflows.
- Add enterprise connectors for escalation, knowledge base search, ticketing.
- Secure endpoints & API keys with Azure Key Vault.

---

### **References**

- [Azure AI Agent Framework Documentation](https://learn.microsoft.com/en-us/azure/ai-services/agent-framework/)
- [Azure OpenAI Service Quickstart](https://learn.microsoft.com/en-us/azure/ai-services/openai/quickstart)
- [Azure AI Foundry for Agents](https://learn.microsoft.com/en-us/azure/ai-services/ai-foundry/overview)

---

**Let me know which integration patterns or channel adapters you'd like detailed code for: webchat, Teams, telephony, etc.**

---

## 🔄 AGENT FRAMEWORK
Certainly! Building a customer service agent with the **Microsoft Agent Framework** and **Azure OpenAI** combines agentic AI patterns, LLM integration, and robust orchestration. Below, I outline an architecture and provide actionable steps and example code snippets.

---

## 1. Architecture Overview

**Components:**
- **Agent Host/Application:** Manages the agent lifecycle (using Agent Framework).
- **Customer Service Agent:** Implements logic for handling user queries.
- **Azure OpenAI:** Used for natural language understanding and response generation.
- **State & Context Management:** Manage conversational context and maintain state.

---

## 2. High-Level Workflow

**Sequential Pattern:**
1. Receive user query.
2. Forward to Azure OpenAI for understanding/response.
3. (Optionally) Call supporting tools/APIs (e.g., CRM, order lookup).
4. Aggregate/design final response.
5. Send back to user.

**Diagram:**

```
User → Agent Host → CustomerServiceAgent → Azure OpenAI → [optional: API/tools] → Agent Host → User
```

---

## 3. Sample Implementation

### Prerequisites

- .NET 8+ or Python 3.10+
- Microsoft.Agent Framework NuGet/pkg (C#) or PyPI package (Python)
- Azure OpenAI resource & API key

---

### Example 1: C#/.NET Implementation

**1. Install Packages**
```shell
dotnet add package Microsoft.Agent.Abstractions
dotnet add package Microsoft.Agent.AzureOpenAI
```

**2. Configure Azure OpenAI**

```csharp
var openAiOptions = new OpenAIOptions
{
    Endpoint = "<YOUR_ENDPOINT>",
    ApiKey = "<YOUR_KEY>",
    Deployment = "<YOUR_DEPLOYMENT>"
};
```

**3. Create Customer Service Agent**

```csharp
public class CustomerServiceAgent : AgentBase
{
    private readonly OpenAIClient _client;
    public CustomerServiceAgent(OpenAIClient client)
    {
        _client = client;
    }

    public override async Task<AgentResponse> OnMessageAsync(AgentMessage message, AgentContext context)
    {
        var prompt = $"You are a helpful customer service agent. User input: {message.Content}";
        var completion = await _client.Completions.CreateCompletionAsync(prompt);

        // Optional: parse intent, route, or call APIs as needed

        return new AgentResponse
        {
            Content = completion.Choices[0].Text
        };
    }
}
```

**4. Host the Agent**

```csharp
var builder = AgentHost.CreateDefaultBuilder()
    .WithAgent<CustomerServiceAgent>()
    .Build();

await builder.RunAsync();
```

---

### Example 2: Python Implementation

```python
from msagent.agent import AgentBase
from msagent.azure_openai import AzureOpenAIClient

class CustomerServiceAgent(AgentBase):
    def __init__(self, openai_client):
        self.openai_client = openai_client

    async def on_message(self, message, context):
        prompt = f"You are a helpful customer service agent. User input: {message.content}"
        response = await self.openai_client.complete(prompt=prompt)
        return response.choices[0].text

# Initialization
openai_client = AzureOpenAIClient(
    endpoint="<YOUR_ENDPOINT>",
    api_key="<YOUR_API_KEY>",
    deployment_name="<YOUR_DEPLOYMENT>"
)

agent = CustomerServiceAgent(openai_client)
# Integrate agent with your messaging or web framework
```

---

## 4. Best Practices and Orchestration

- **Context Handling:** Use AgentContext to share session information (e.g., customer ID, previous queries).
- **Error Handling:** Implement try/except (Python) or try/catch (C#) around external calls.
- **Tool Integration:** Extend agent to call REST APIs for order status, ticket lookups, etc. Use function calling patterns supported in Agent Framework.
- **State Management:** Use storage providers (e.g., Azure Table, Blob, in-memory) for user state.

---

## 5. References

- [Microsoft Agent Framework documentation](https://learn.microsoft.com/en-us/azure/ai-services/agent-framework/)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

---

## 6. Next Steps

- **Expand Workflow:** Add dispatch logic for multi-turn conversations, escalation to human agents, etc.
- **Orchestrate Multiple Agents:** Use a parallel/hierarchical pattern if integrating FAQ, order status, and feedback agents.

---

**Let me know if you need a complete working sample or more advanced orchestration patterns (multi-agent, parallel, etc.)!**

---

## 🏗️ ARCHITECTURE PATTERNS
To design and deploy a **customer service agent** using the **Microsoft Agent Framework** with **Azure OpenAI**, you should follow proven Azure architecture patterns. Here's a step-by-step guide incorporating reference architecture, design patterns, scalability, and infrastructure as code.

---

## 1. Reference Architecture Overview

A robust architecture for a customer service agent on Azure commonly uses:

- **Azure Bot Service** for conversational logic
- **Azure OpenAI Service** for generative AI (GPT models)
- **Microsoft Agent Framework** for dialog orchestration
- **Azure Functions or Logic Apps** for event-driven integration
- **Azure Cognitive Search** for Retrieval Augmented Generation (RAG)
- **Data sources**: Azure Cosmos DB or Azure SQL for knowledge base/Q&A pairs
- **APIs/Connectors** for external CRM or ticketing systems

### High-level architecture diagram

```
User -> Bot Service -> Azure Functions (Bot Logic) -> Azure OpenAI (GPT) <-> Cognitive Search (Documents/FAQs)
                                 |
                                 v
                          Databases (Cosmos DB/SQL)
```

---

## 2. Design Patterns

- **Microservices/Event-Driven:** Use Azure Functions for modular business logic and integration with downstream systems.
- **Serverless:** Bot logic and RAG components can run as Functions or Logic Apps for scalability and operation cost-efficiency.
- **Retrieval Augmented Generation (RAG):** Leverage Cognitive Search to enhance GPT responses with relevant, up-to-date information from your enterprise dataset.

---

## 3. Azure Well-Architected Framework Pillars

- **Reliability:** Use Azure Functions with retries, implement Bot Service scale-out, and ensure Cosmos DB replication.
- **Security:** Secure endpoints with managed identities, use Azure Key Vault for secrets, and enable logging/monitoring.
- **Cost Optimization:** Serverless design minimizes idle cost. Use consumption plans for Bot Service and Functions.
- **Operational Excellence:** Implement monitoring via Azure Monitor and Application Insights for conversation analytics.
- **Performance Efficiency:** Use caching and indexing in Cognitive Search to speed up semantic queries for RAG.

---

## 4. Implementation Example: Microsoft Agent Framework

Referencing [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/example-scenario/ai/bot-framework-cognitive-services):

**Sample Code Snippet**

```python
# Azure Functions endpoint for Bot dialog
import logging
import openai
import azure.functions as func

def main(req: func.HttpRequest) -> func.HttpResponse:
    user_question = req.params.get('question')
    
    # Retrieve relevant documents
    results = search_documents(user_question)  # integrate with Cognitive Search
    
    # Compose RAG prompt
    prompt = f"FAQ/Docs:\n{results}\n\nUser: {user_question}\nAgent:"
    
    # Azure OpenAI completion
    response = openai.Completion.create(
        engine="gpt-35-turbo",
        prompt=prompt,
        max_tokens=250
    )
    answer = response.choices[0].text.strip()
    return func.HttpResponse(answer)
```

**Infrastructure as Code: Bicep Example**

```bicep
resource botService 'Microsoft.BotService/botServices@2021-05-01-preview' = {
  name: 'custservice-agent-bot'
  location: resourceGroup().location
  sku: { name: 'S1' }
  properties: {
    displayName: 'Customer Service Agent'
    endpoint: 'https://<function-app-url>/api/messages'
    enabledChannels: [ 'WebChat', 'Teams' ]
  }
}

resource openAI 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: 'ai-gpt-service'
  location: resourceGroup().location
  sku: { name: 'S0' }
  kind: 'OpenAI'
  properties: {
    apiProperties: {
      azureOpenAIResourceId: '<resource-id>'
    }
  }
}
```

---

## 5. Retrieval Augmented Generation (RAG) Pattern

**How RAG Works:**

1. Receive user query.
2. Search knowledge base/documents for relevant information using Cognitive Search.
3. Feed retrieved content into GPT prompt as context.
4. Generate a context-aware answer.
5. Return response with citations or references (for explainability).

**Reference:** [RAG with Azure Cognitive Search and OpenAI](https://learn.microsoft.com/en-us/azure/architecture/example-scenario/ai/rag-with-azure-openai)

---

## 6. Scalability, High Availability and Resilience

- Use **Azure Functions** with autoscale enabled.
- Host data in **Cosmos DB** with geo-replication for high availability.
- Deploy OpenAI in regions with failover.
- Configure Bot Service with multiple channels and regional endpoints.
- Enable disaster recovery by backing up configuration and using Azure Traffic Manager.

---

## 7. Best Practices

- Decouple UI (WebChat, Teams) from bot backend logic.
- Use staging slots and blue-green deployment for Bot Service/Functions.
- Monitor and log user interactions for continual improvement.
- Apply role-based access control (RBAC) and managed identities.
- Regularly update and retrain knowledge base.

---

### Additional Resources

- [Build a chatbot with Azure Bot Service and Azure OpenAI](https://learn.microsoft.com/en-us/azure/architecture/example-scenario/ai/openai-chatbot)
- [Azure Well-Architected Review for AI](https://learn.microsoft.com/en-us/azure/architecture/framework/ai/overview)
- [RAG Architecture Example](https://learn.microsoft.com/en-us/azure/architecture/example-scenario/ai/rag-with-azure-openai)

---

**Would you like a full deployment template or a more detailed code sample for a specific component (Bot Framework, RAG, etc.)?**

---

## 🔒 SECURITY COMPLIANCE
Certainly! Building a **secure customer service agent** using the **Microsoft Agent Framework (MAF)** with **Azure OpenAI** involves several architecture and compliance components. Below is a high-level overview, with a focus on robust **security**, **data protection**, **responsible AI**, and **regulatory compliance**.

---

### 1. **Solution Architecture Overview**

**Components:**
- **Azure Bot Service** (hosting the agent logic)
- **Microsoft Agent Framework (MAF)** (conversational flow orchestration)
- **Azure OpenAI Service** (for advanced language understanding)
- **Azure Key Vault** (secrets management)
- **Azure Cosmos DB** or **SQL Database** (customer data, chat logs)
- **Identity Management:** Azure Active Directory Managed Identities
- **Private Endpoints & VNet Integration** (network security)

---

### 2. **Identity & Access Management**

- **Managed Identity:**  
  Assign a system-assigned managed identity to your Bot Service. This lets it securely access Azure OpenAI, Key Vault, and Cosmos DB **without credentials in code**.
- **Role-Based Access Control (RBAC):**  
  Use Azure RBAC to **grant only required permissions** to services, e.g., Bot Service can access OpenAI but not administrative functions.

**Example (Assigning RBAC role):**  
```azurecli
az role assignment create --assignee <objectId-of-managed-identity> \
  --role "Cognitive Services OpenAI User" \
  --scope /subscriptions/<subId>/resourceGroups/<rg>/providers/Microsoft.CognitiveServices/accounts/<openai-account>
```

---

### 3. **Network Security**

- **Private Endpoints:**  
  Deploy OpenAI, Key Vault, and data storage behind private endpoints so traffic **never leaves Azure backbone**.
- **Virtual Network Service Endpoints** link all services for **east-west protection**.
- **Azure Firewall/NSG Rules** for additional segmentation as needed.

---

### 4. **Data Protection & Encryption**

- **At Rest:**  
  All data in Cosmos DB, SQL, and Key Vault is encrypted at rest with customer-managed keys as an option.
- **In Transit:**  
  Enforce HTTPS/TLS for all communication between components.
- **Key Management:**  
  Store secrets, keys, and credentials only in Azure Key Vault. Enable **logging of key access** for compliance reporting.

---

### 5. **Compliance**

- **Data Residency:**  
  Ensure OpenAI and customer data are **deployed to regions compliant with your data residency requirements** (e.g., EU for GDPR, US for HIPAA).
- **Certifications:**  
  Azure OpenAI is **GDPR-compliant**, ISO 27001, SOC 2, HIPAA (review current Azure compliance docs).
- **Audit & Policy:**  
  Use **Azure Policy** to enforce security baselines, log changes, and utilize **Microsoft Defender for Cloud** for threat protection.

---

### 6. **Responsible AI Guidelines**

- **Content Filtering:**  
  Use Azure OpenAI's built-in content filtering; configure it to **block harmful or inappropriate outputs**.
- **Transparency:**  
  Clearly inform users that they’re interacting with an AI agent.
- **Bias Detection & Fairness:**  
  Regularly audit agent output logs for bias; leverage Azure’s Responsible AI Dashboard for bias and quality monitoring.
- **Human Escalation:**  
  Add logic in MAF to escalate to human agent for sensitive cases.
- **Explainability:**  
  Use Azure’s responsible AI tooling to provide explanations for complex decisions if required by regulation.

---

### 7. **Sample Configuration (MAF + OpenAI Integration)**

```python
# Pseudocode - Microsoft Agent Framework integration with Azure OpenAI
from ms_agent_framework import Agent
from azure.identity import DefaultAzureCredential
from azure.ai.openai import OpenAIClient

credential = DefaultAzureCredential()
openai_client = OpenAIClient(endpoint="https://<your-openai-endpoint>.openai.azure.com/", credential=credential)

class CustomerServiceAgent(Agent):
    async def handle_user_message(self, message):
        # Content filtering
        if self.is_harmful_content(message):
            return "Sorry, I can't process that request."

        # Query OpenAI
        response = openai_client.chat_completion(model="gpt-4", messages=[{"role": "user", "content": message}])
        return response["choices"][0]["message"]["content"]

agent = CustomerServiceAgent()
agent.run()

# Note:
# - OpenAI endpoint must be behind a private endpoint
# - No secrets are embedded, all identities are managed
```

---

### 8. **Continuous Governance & Monitoring**

- Enable **Defender for Cloud** for threat detection and recommendations.
- Log activity in **Azure Monitor & Sentinel** for auditing.
- Periodic review using **Responsible AI tools**.

---

## **References & Next Steps**
- [Azure OpenAI Security Best Practices](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/security)
- [Responsible AI Standards](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/responsible-ai)
- [Azure Bot Service & MAF Docs](https://learn.microsoft.com/en-us/azure/bot-service/)
- [Compliance Offerings](https://learn.microsoft.com/en-us/azure/compliance/offerings/)

**Would you like a detailed deployment template or more code samples for specific components (Bot Service, OpenAI, Agent Framework)?**

---

## 💰 COST OPTIMIZATION
Certainly! Here’s a cost-optimized approach for building a **Customer Service Agent** using Microsoft Agent Framework and Azure OpenAI, with a focus on efficient architecture, pricing models, and best practices for cost-control.

---

## **Solution Architecture Overview**

1. **Service**: Azure Bot Service using Microsoft Bot Framework (Agent Framework)
2. **AI Model**: Azure OpenAI Service (GPT models for natural language understanding/generation)
3. **Backend**: Azure Functions or App Service (cost-efficient compute options)
4. **Data Storage**: Azure Table Storage or Cosmos DB (for user logs, history)
5. **Optimization**: Caching (Azure Redis), batch processing, token quotas

---

## **Cost-Efficient Implementation Patterns**

### **Key Implementation Steps**

#### 1. **Bot Framework SDK**  
Use the [Bot Framework SDK](https://learn.microsoft.com/en-us/azure/bot-service/?view=azure-bot-service-4.0) to quickly create the conversational agent logic.

#### 2. **Calling Azure OpenAI**  
In your bot's dialog flow, use Azure OpenAI’s APIs to generate intelligent responses.

**Sample pattern (C#):**
```csharp
using Azure.AI.OpenAI;

var client = new OpenAIClient(new Uri(endpoint), new AzureKeyCredential(apiKey));

var response = await client.GetChatCompletionsAsync(
    "deploymentName", 
    new ChatCompletionsOptions
    {
        Messages = { new ChatMessage(ChatRole.User, userInput) },
        MaxTokens = 400 // Limit token usage to control cost
    });
```
**Optimization:**
- Use `MaxTokens` parameter to control token counts per request.
- Implement simple caching for frequent user queries (e.g., retrieve FAQ from Redis before calling OpenAI).

#### 3. **Batching & Caching**  
- Cache frequent answers (using Azure Redis) to reduce repeated OpenAI calls.
- Batch related requests or summarize exchanges to minimize completion requests.

#### 4. **Model Selection**
- Use the **cheapest model** that meets your needs (e.g., GPT-3.5 over GPT-4 for basic scenarios).
- Deploy only the models you’ll use—don’t deploy all tiers.

#### 5. **Quota Management**
- Configure API usage quotas and alerts in Azure Cost Management.
- Set budgets with automatic alerts.

---

## **Azure OpenAI Pricing Insights**

### **Pricing Model Options**

- **Pay-As-You-Go (PAYG)**: Charges per 1,000 tokens processed. No upfront commitment.  
- **Provisioned Throughput Units (PTU)**: Commit to reserved capacity (e.g., tokens/sec). Lower unit costs, requires commitment.

**Token Pricing Example (2024):**
- **GPT-4 8k**: ~$0.03 / 1,000 prompt tokens, ~$0.06 / 1,000 completion tokens (PAYG)
- **GPT-3.5 Turbo**: ~$0.0015 / 1,000 tokens
- [Current Pricing Calculator](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/)  
*(Always confirm with latest calculator as rates change)*

**Cost Estimate Example:**  
For a FAQ bot using GPT-3.5 Turbo, handling 10,000 requests/month, each averaging 400 tokens (prompt+completion):  
- 10,000 * 400 = 4,000,000 tokens  
- 4,000,000 / 1,000 = 4,000 * $0.0015 = **$6 / month**

---

## **Cost Optimization Strategies**

- **Cache frequent queries:** Use Redis/Cosmos DB; avoid redundant completions.
- **Restrict max tokens:** Lower `MaxTokens` to reduce cost per response.
- **Use lower-tier models:** Unless quality demands GPT-4, use GPT-3.5 Turbo.
- **Monitor and control:** Use Azure Cost Management, set automated budget alerts.
- **Batch processing:** Summarize longer user exchanges before sending to OpenAI.
- **Review usage logs:** Analyze which interactions consume the most tokens.

---

## **Azure Cost Management Tools**

- **Budgets & Alerts:** Set monthly limits on your OpenAI resource.
- **Usage Reports:** Monitor token consumption and cost drivers.
- **Advisor Recommendations:** Get optimization tips directly in Azure Portal.

---

## **Sample Solution Repository**

- [Microsoft Bot Framework Customer Service Sample](https://github.com/microsoft/BotBuilder-Samples/tree/main/samples/csharp_dotnetcore/13.core-bot)
- [Azure OpenAI Integration Code Sample](https://github.com/Azure/azure-openai-samples)

---

## **Summary Table: Cost-Effective Choices**

| Component        | Cost Efficiency Tactic                                               |
|------------------|---------------------------------------------------------------------|
| Bot Service      | Choose consumption plan; auto-scale                                 |
| OpenAI           | Choose lowest feasible model; restrict tokens; cache responses      |
| DB/Cache         | Use Table Storage/Redis for low-cost storage/access                 |
| Monitoring       | Set up cost alerts, usage dashboards                                |

---

## **TCO Analysis Considerations**

- Estimate monthly token usage (prompt+completion).
- Model selection: GPT-3.5 is 20x cheaper than GPT-4 for most cases.
- Caching can reduce OpenAI usage by up to 60% for FAQ-style bots.
- Always pilot with usage logging enabled; tune before scaling.

---

**Need further code samples or detailed pricing breakdown for your expected usage? Let me know your scenario details, and I’ll tailor a cost estimate!**

---

## ⏱️ Execution Time

- **Start Time:** 2025-10-06 10:56:24
- **End Time:** 2025-10-06 10:56:52
- **Duration:** 28.57 seconds (0m 28s)

---

## ✅ Analysis Complete
