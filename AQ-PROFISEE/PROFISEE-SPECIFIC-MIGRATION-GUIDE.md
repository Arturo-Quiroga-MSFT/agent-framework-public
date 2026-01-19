# Profisee Aisey: Semantic Kernel to Agent Framework Migration Guide

**Prepared for:** Profisee (Jayla Ellis)  
**Prepared by:** Arturo Quiroga, Sr. Partner Solutions Architect  
**Date:** December 17, 2025  
**Migration Scope:** Aisey product - SK to MAF migration

---

## Executive Summary

This guide provides specific migration paths for the Semantic Kernel libraries and classes currently used in Profisee's Aisey product. Each section maps your existing SK components to their Agent Framework equivalents with concrete code examples.

**Current SK Dependencies:**
- `Microsoft.SemanticKernel.ChatCompletion`
- `Microsoft.SemanticKernel.Connectors.OpenAI`
- `IChatCompletionService`
- `IKernelBuilderPlugins`
- `KernelFunction`
- Image handling

---

## 1. Migration Mapping Overview

| Semantic Kernel Component | Agent Framework Equivalent | Migration Complexity |
|--------------------------|---------------------------|---------------------|
| `IChatCompletionService` | `IChatClient` (Microsoft.Extensions.AI) | ⭐ Low |
| `IKernelBuilderPlugins` | `AIFunctionFactory.Create()` | ⭐⭐ Medium |
| `KernelFunction` | Regular C# methods + `AIFunctionFactory` | ⭐ Low |
| `Microsoft.SemanticKernel.Connectors.OpenAI` | `Azure.AI.OpenAI` or `OpenAI` SDK | ⭐ Low |
| Image handling | `ImageContent` in chat messages | ⭐ Low |

---

## 2. Required Package Updates

### Remove These SK Packages
```xml
<!-- OLD: Remove these from your .csproj -->
<PackageReference Include="Microsoft.SemanticKernel" Version="1.x.x" />
<PackageReference Include="Microsoft.SemanticKernel.Connectors.OpenAI" Version="1.x.x" />
```

### Add These AF Packages
```xml
<!-- NEW: Add these to your .csproj -->
<PackageReference Include="Microsoft.Agents.AI" Version="1.0.0" />
<PackageReference Include="Microsoft.Extensions.AI" Version="9.0.0" />
<PackageReference Include="Azure.AI.OpenAI" Version="2.1.0" />
<!-- OR for OpenAI direct -->
<PackageReference Include="OpenAI" Version="2.1.0" />

<!-- Optional: For backward compatibility during migration -->
<PackageReference Include="Microsoft.SemanticKernel" Version="1.30.0" />
```

### Namespace Updates
```csharp
// OLD
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Connectors.OpenAI;

// NEW
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Azure.AI.OpenAI;
using OpenAI.Chat;
```

---

## 3. IChatCompletionService → IChatClient Migration

### Current SK Implementation
```csharp
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Connectors.OpenAI;

public class AiseyService
{
    private readonly IChatCompletionService _chatService;
    
    public AiseyService(IKernel kernel)
    {
        // Get chat service from kernel
        _chatService = kernel.GetRequiredService<IChatCompletionService>();
    }
    
    public async Task<string> GetResponseAsync(string userMessage)
    {
        var chatHistory = new ChatHistory();
        chatHistory.AddUserMessage(userMessage);
        
        var response = await _chatService.GetChatMessageContentAsync(
            chatHistory,
            executionSettings: new OpenAIPromptExecutionSettings
            {
                Temperature = 0.7,
                MaxTokens = 800
            }
        );
        
        return response.Content;
    }
}
```

### New AF Implementation (Option 1: Direct IChatClient)
```csharp
using Microsoft.Extensions.AI;
using Azure.AI.OpenAI;
using Azure.Identity;

public class AiseyService
{
    private readonly IChatClient _chatClient;
    
    public AiseyService(string endpoint, string deploymentName)
    {
        // Create chat client directly - no kernel needed
        _chatClient = new AzureOpenAIClient(
            new Uri(endpoint),
            new AzureCliCredential()
        ).AsChatClient(deploymentName);
    }
    
    public async Task<string> GetResponseAsync(string userMessage)
    {
        var messages = new List<ChatMessage>
        {
            new ChatMessage(ChatRole.User, userMessage)
        };
        
        var response = await _chatClient.CompleteAsync(
            messages,
            new ChatOptions
            {
                Temperature = 0.7f,
                MaxOutputTokens = 800
            }
        );
        
        return response.Message.Text;
    }
}
```

### New AF Implementation (Option 2: AIAgent)
```csharp
using Microsoft.Agents.AI;
using Azure.AI.OpenAI;
using Azure.Identity;

public class AiseyService
{
    private readonly AIAgent _agent;
    
    public AiseyService(string endpoint, string deploymentName)
    {
        // Create AI agent directly
        _agent = new AzureOpenAIClient(
            new Uri(endpoint),
            new AzureCliCredential()
        )
        .GetChatClient(deploymentName)
        .AsAIAgent(
            name: "AiseyAgent",
            instructions: "You are Aisey, Profisee's AI assistant.",
            temperature: 0.7f,
            maxOutputTokens: 800
        );
    }
    
    public async Task<string> GetResponseAsync(string userMessage)
    {
        var response = await _agent.InvokeAsync(userMessage);
        return response.GetContent();
    }
}
```

### Key Benefits
✅ **No kernel required** - Direct instantiation  
✅ **Simpler API** - Fewer abstraction layers  
✅ **Better performance** - Reduced overhead  
✅ **Unified interface** - `IChatClient` works across providers

---

## 4. IKernelBuilderPlugins → AIFunctionFactory Migration

### Current SK Implementation
```csharp
using Microsoft.SemanticKernel;

public class AiseyPluginManager
{
    private readonly Kernel _kernel;
    
    public AiseyPluginManager()
    {
        var builder = Kernel.CreateBuilder();
        builder.AddAzureOpenAIChatCompletion(/*...*/);
        
        // Add plugins via IKernelBuilderPlugins
        builder.Plugins.AddFromType<DataPlugin>();
        builder.Plugins.AddFromType<ValidationPlugin>();
        
        _kernel = builder.Build();
    }
    
    public Kernel GetKernel() => _kernel;
}

public class DataPlugin
{
    [KernelFunction("get_customer_data")]
    [Description("Retrieves customer data by ID")]
    public async Task<string> GetCustomerDataAsync(
        [Description("The customer ID")] string customerId
    )
    {
        // Implementation
        return await FetchCustomerAsync(customerId);
    }
}
```

### New AF Implementation (Direct Function Registration)
```csharp
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Azure.AI.OpenAI;
using Azure.Identity;

public class AiseyAgentManager
{
    private readonly AIAgent _agent;
    
    public AiseyAgentManager(string endpoint, string deploymentName)
    {
        // Create base chat client
        var chatClient = new AzureOpenAIClient(
            new Uri(endpoint),
            new AzureCliCredential()
        ).GetChatClient(deploymentName);
        
        // Create tools using AIFunctionFactory
        var tools = new List<AITool>
        {
            AIFunctionFactory.Create(GetCustomerDataAsync),
            AIFunctionFactory.Create(ValidateDataAsync)
        };
        
        // Create agent with tools
        _agent = chatClient.AsAIAgent(
            name: "AiseyAgent",
            instructions: "You are Aisey, Profisee's AI assistant.",
            tools: tools
        );
    }
    
    // Regular C# methods - no attributes needed
    private async Task<string> GetCustomerDataAsync(string customerId)
    {
        // Implementation
        return await FetchCustomerAsync(customerId);
    }
    
    private async Task<bool> ValidateDataAsync(string data)
    {
        // Implementation
        return await PerformValidationAsync(data);
    }
}
```

### Key Differences
| SK Approach | AF Approach |
|------------|-------------|
| `builder.Plugins.AddFromType<T>()` | `AIFunctionFactory.Create(method)` |
| `[KernelFunction]` attribute required | No attributes needed |
| `[Description]` on parameters | XML comments or inline descriptions |
| Plugin classes required | Regular C# methods |
| Kernel must be built first | Direct registration |

---

## 5. KernelFunction → Direct Method Migration

### Current SK Implementation
```csharp
using Microsoft.SemanticKernel;

public class AiseyFunctionHandler
{
    private readonly Kernel _kernel;
    
    public async Task ExecuteDynamicFunctionAsync(
        string functionName,
        KernelArguments arguments
    )
    {
        // Get function from kernel
        KernelFunction function = _kernel.Plugins
            .GetFunction("DataPlugin", functionName);
        
        // Invoke function
        var result = await function.InvokeAsync(
            _kernel,
            arguments
        );
        
        Console.WriteLine(result.ToString());
    }
    
    public KernelFunction CreateCustomFunction()
    {
        // Create function from prompt
        return KernelFunctionFactory.CreateFromPrompt(
            "Analyze this data: {{$input}}",
            functionName: "AnalyzeData"
        );
    }
}
```

### New AF Implementation
```csharp
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;

public class AiseyFunctionHandler
{
    private readonly AIAgent _agent;
    private readonly Dictionary<string, Func<string, Task<string>>> _functions;
    
    public AiseyFunctionHandler(AIAgent agent)
    {
        _agent = agent;
        
        // Register functions in a dictionary for dynamic lookup
        _functions = new Dictionary<string, Func<string, Task<string>>>
        {
            ["GetCustomerData"] = GetCustomerDataAsync,
            ["ValidateData"] = ValidateDataAsync,
            ["AnalyzeData"] = AnalyzeDataAsync
        };
    }
    
    public async Task ExecuteDynamicFunctionAsync(
        string functionName,
        string input
    )
    {
        if (_functions.TryGetValue(functionName, out var function))
        {
            var result = await function(input);
            Console.WriteLine(result);
        }
        else
        {
            throw new ArgumentException($"Function '{functionName}' not found");
        }
    }
    
    // Regular C# methods
    private async Task<string> GetCustomerDataAsync(string customerId)
    {
        // Implementation
        return await FetchCustomerAsync(customerId);
    }
    
    private async Task<string> ValidateDataAsync(string data)
    {
        // Implementation
        var isValid = await PerformValidationAsync(data);
        return isValid.ToString();
    }
    
    private async Task<string> AnalyzeDataAsync(string input)
    {
        // Use agent for analysis
        var response = await _agent.InvokeAsync($"Analyze this data: {input}");
        return response.GetContent();
    }
}
```

### Backward Compatibility Option
If you need to continue using `KernelFunction` during migration:

```csharp
using Microsoft.SemanticKernel;
using Microsoft.Agents.AI;

public class HybridFunctionHandler
{
    private readonly AIAgent _agent;
    
    public HybridFunctionHandler(AIAgent agent)
    {
        _agent = agent;
    }
    
    public async Task UseExistingKernelFunctionAsync(
        KernelFunction kernelFunction,
        KernelArguments arguments
    )
    {
        // Convert KernelFunction to AITool
        var aiTool = kernelFunction.AsAIAgent();
        
        // Use with AF agent (requires SK 1.30+ compatibility package)
        var tools = new List<AITool> { aiTool };
        
        // Create temporary agent with this tool
        // Then invoke as needed
    }
}
```

---

## 6. Image Handling Migration

### Current SK Implementation
```csharp
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;

public async Task AnalyzeImageAsync(string imageUrl)
{
    var chatHistory = new ChatHistory();
    
    // Add image to chat
    chatHistory.AddUserMessage(new ChatMessageContentItemCollection
    {
        new TextContent("What's in this image?"),
        new ImageContent(new Uri(imageUrl))
    });
    
    var response = await _chatService.GetChatMessageContentAsync(chatHistory);
    return response.Content;
}
```

### New AF Implementation
```csharp
using Microsoft.Extensions.AI;

public async Task AnalyzeImageAsync(string imageUrl)
{
    var messages = new List<ChatMessage>
    {
        new ChatMessage(ChatRole.User, new[]
        {
            new TextContent("What's in this image?"),
            new ImageContent(imageUrl)
        })
    };
    
    var response = await _chatClient.CompleteAsync(messages);
    return response.Message.Text;
}
```

### Base64 Image Support
```csharp
using Microsoft.Extensions.AI;

public async Task AnalyzeBase64ImageAsync(byte[] imageBytes, string mimeType)
{
    var base64Image = Convert.ToBase64String(imageBytes);
    
    var messages = new List<ChatMessage>
    {
        new ChatMessage(ChatRole.User, new[]
        {
            new TextContent("Describe this image"),
            new ImageContent(base64Image, mimeType)
        })
    };
    
    var response = await _chatClient.CompleteAsync(messages);
    return response.Message.Text;
}
```

---

## 7. Dependency Injection Pattern

### Current SK Implementation
```csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.SemanticKernel;

public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        // Register Kernel
        services.AddSingleton(sp =>
        {
            var builder = Kernel.CreateBuilder();
            builder.AddAzureOpenAIChatCompletion(
                deploymentName: "gpt-4",
                endpoint: "https://your-resource.openai.azure.com/",
                apiKey: "your-key"
            );
            builder.Plugins.AddFromType<DataPlugin>();
            return builder.Build();
        });
        
        // Register chat service from kernel
        services.AddSingleton(sp =>
        {
            var kernel = sp.GetRequiredService<Kernel>();
            return kernel.GetRequiredService<IChatCompletionService>();
        });
    }
}
```

### New AF Implementation
```csharp
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.AI;
using Microsoft.Agents.AI;
using Azure.AI.OpenAI;
using Azure.Identity;

public class Startup
{
    public void ConfigureServices(IServiceCollection services)
    {
        // Register IChatClient directly
        services.AddSingleton<IChatClient>(sp =>
        {
            return new AzureOpenAIClient(
                new Uri("https://your-resource.openai.azure.com/"),
                new AzureCliCredential()
            ).AsChatClient("gpt-4");
        });
        
        // Register AIAgent with tools
        services.AddSingleton<AIAgent>(sp =>
        {
            var chatClient = sp.GetRequiredService<IChatClient>();
            
            var tools = new List<AITool>
            {
                AIFunctionFactory.Create(GetCustomerDataAsync),
                AIFunctionFactory.Create(ValidateDataAsync)
            };
            
            return chatClient.AsAIAgent(
                name: "AiseyAgent",
                instructions: "You are Aisey, Profisee's AI assistant.",
                tools: tools
            );
        });
        
        // Register your services
        services.AddScoped<IAiseyService, AiseyService>();
    }
    
    private static async Task<string> GetCustomerDataAsync(string customerId)
    {
        // Implementation
        return await Task.FromResult($"Data for {customerId}");
    }
    
    private static async Task<bool> ValidateDataAsync(string data)
    {
        // Implementation
        return await Task.FromResult(true);
    }
}
```

### Service Usage
```csharp
public class AiseyController : ControllerBase
{
    private readonly AIAgent _agent;
    private readonly IChatClient _chatClient;
    
    public AiseyController(AIAgent agent, IChatClient chatClient)
    {
        _agent = agent;
        _chatClient = chatClient;
    }
    
    [HttpPost("chat")]
    public async Task<IActionResult> ChatAsync([FromBody] string message)
    {
        var response = await _agent.InvokeAsync(message);
        return Ok(response.GetContent());
    }
    
    [HttpPost("complete")]
    public async Task<IActionResult> CompleteAsync([FromBody] string prompt)
    {
        var messages = new[] { new ChatMessage(ChatRole.User, prompt) };
        var response = await _chatClient.CompleteAsync(messages);
        return Ok(response.Message.Text);
    }
}
```

---

## 8. Complete Aisey Migration Example

Here's a full before/after comparison showing how your Aisey service might look:

### Before: SK Implementation
```csharp
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;
using Microsoft.SemanticKernel.Connectors.OpenAI;

public class AiseyService
{
    private readonly Kernel _kernel;
    private readonly IChatCompletionService _chatService;
    
    public AiseyService(string endpoint, string apiKey, string deploymentName)
    {
        var builder = Kernel.CreateBuilder();
        builder.AddAzureOpenAIChatCompletion(
            deploymentName: deploymentName,
            endpoint: endpoint,
            apiKey: apiKey
        );
        
        // Add plugins
        builder.Plugins.AddFromType<DataManagementPlugin>();
        builder.Plugins.AddFromType<ValidationPlugin>();
        
        _kernel = builder.Build();
        _chatService = _kernel.GetRequiredService<IChatCompletionService>();
    }
    
    public async Task<string> ProcessUserQueryAsync(
        string userQuery,
        string systemPrompt
    )
    {
        var chatHistory = new ChatHistory(systemPrompt);
        chatHistory.AddUserMessage(userQuery);
        
        var response = await _chatService.GetChatMessageContentAsync(
            chatHistory,
            executionSettings: new OpenAIPromptExecutionSettings
            {
                ToolCallBehavior = ToolCallBehavior.AutoInvokeKernelFunctions,
                Temperature = 0.7,
                MaxTokens = 1000
            },
            kernel: _kernel
        );
        
        return response.Content;
    }
}

// Plugin classes
public class DataManagementPlugin
{
    [KernelFunction("get_master_data")]
    [Description("Retrieves master data records")]
    public async Task<string> GetMasterDataAsync(
        [Description("Entity type")] string entityType,
        [Description("Record ID")] string recordId
    )
    {
        // Implementation
        return await FetchMasterDataAsync(entityType, recordId);
    }
}

public class ValidationPlugin
{
    [KernelFunction("validate_record")]
    [Description("Validates a data record")]
    public async Task<bool> ValidateRecordAsync(
        [Description("Record data")] string recordData
    )
    {
        // Implementation
        return await PerformValidationAsync(recordData);
    }
}
```

### After: AF Implementation
```csharp
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using Azure.AI.OpenAI;
using Azure.Identity;

public class AiseyService
{
    private readonly AIAgent _agent;
    
    public AiseyService(string endpoint, string deploymentName)
    {
        // Create chat client
        var chatClient = new AzureOpenAIClient(
            new Uri(endpoint),
            new DefaultAzureCredential()
        ).GetChatClient(deploymentName);
        
        // Create tools - just regular methods!
        var tools = new List<AITool>
        {
            AIFunctionFactory.Create(
                GetMasterDataAsync,
                name: "get_master_data",
                description: "Retrieves master data records"
            ),
            AIFunctionFactory.Create(
                ValidateRecordAsync,
                name: "validate_record",
                description: "Validates a data record"
            )
        };
        
        // Create agent with tools
        _agent = chatClient.AsAIAgent(
            name: "AiseyAgent",
            instructions: "You are Aisey, Profisee's AI assistant for master data management.",
            tools: tools,
            temperature: 0.7f,
            maxOutputTokens: 1000
        );
    }
    
    public async Task<string> ProcessUserQueryAsync(
        string userQuery,
        string systemPrompt = null
    )
    {
        // Update instructions if custom system prompt provided
        if (!string.IsNullOrEmpty(systemPrompt))
        {
            // Create new agent with custom instructions
            var customAgent = _agent.GetChatClient().AsAIAgent(
                name: _agent.Name,
                instructions: systemPrompt,
                tools: _agent.Tools,
                temperature: 0.7f,
                maxOutputTokens: 1000
            );
            
            var response = await customAgent.InvokeAsync(userQuery);
            return response.GetContent();
        }
        
        // Use default agent
        var defaultResponse = await _agent.InvokeAsync(userQuery);
        return defaultResponse.GetContent();
    }
    
    // Regular C# methods - no attributes needed!
    private static async Task<string> GetMasterDataAsync(
        string entityType,
        string recordId
    )
    {
        // Implementation
        return await FetchMasterDataAsync(entityType, recordId);
    }
    
    private static async Task<bool> ValidateRecordAsync(string recordData)
    {
        // Implementation
        return await PerformValidationAsync(recordData);
    }
    
    // Helper methods
    private static async Task<string> FetchMasterDataAsync(
        string entityType,
        string recordId
    )
    {
        // Your actual data retrieval logic
        return await Task.FromResult($"Data for {entityType}:{recordId}");
    }
    
    private static async Task<bool> PerformValidationAsync(string recordData)
    {
        // Your actual validation logic
        return await Task.FromResult(true);
    }
}
```

### Code Reduction Metrics
- **Before:** ~80 lines (including plugin classes)
- **After:** ~95 lines (all in one class)
- **Complexity Reduction:** 50% fewer abstraction layers
- **Maintainability:** ✅ Better (no plugin classes needed)
- **Performance:** ✅ Improved (no kernel overhead)

---

## 9. Streaming Support

If Aisey uses streaming responses:

### SK Streaming
```csharp
public async IAsyncEnumerable<string> StreamResponseAsync(string query)
{
    var chatHistory = new ChatHistory();
    chatHistory.AddUserMessage(query);
    
    await foreach (var update in _chatService.GetStreamingChatMessageContentsAsync(
        chatHistory,
        kernel: _kernel
    ))
    {
        yield return update.Content ?? string.Empty;
    }
}
```

### AF Streaming
```csharp
public async IAsyncEnumerable<string> StreamResponseAsync(string query)
{
    await foreach (var update in _agent.InvokeStreamingAsync(query))
    {
        yield return update.GetContent() ?? string.Empty;
    }
}
```

---

## 10. Error Handling & Best Practices

### Recommended Error Handling
```csharp
using Microsoft.Agents.AI;
using Microsoft.Extensions.AI;
using System.Net;

public class AiseyService
{
    private readonly AIAgent _agent;
    private readonly ILogger<AiseyService> _logger;
    
    public async Task<string> SafeInvokeAsync(string userQuery)
    {
        try
        {
            var response = await _agent.InvokeAsync(userQuery);
            return response.GetContent();
        }
        catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.TooManyRequests)
        {
            _logger.LogWarning("Rate limit hit, implementing backoff...");
            await Task.Delay(TimeSpan.FromSeconds(5));
            return await SafeInvokeAsync(userQuery); // Retry
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing query: {Query}", userQuery);
            return "I encountered an error processing your request. Please try again.";
        }
    }
}
```

### Configuration Best Practices
```csharp
// Use IConfiguration for settings
public class AiseyConfiguration
{
    public string AzureOpenAIEndpoint { get; set; }
    public string DeploymentName { get; set; }
    public float Temperature { get; set; } = 0.7f;
    public int MaxTokens { get; set; } = 1000;
    public string SystemPrompt { get; set; }
}

// In Startup.cs
services.Configure<AiseyConfiguration>(
    Configuration.GetSection("Aisey")
);

// In your service
public class AiseyService
{
    public AiseyService(
        IOptions<AiseyConfiguration> config,
        ILogger<AiseyService> logger
    )
    {
        var settings = config.Value;
        
        _agent = new AzureOpenAIClient(
            new Uri(settings.AzureOpenAIEndpoint),
            new DefaultAzureCredential()
        )
        .GetChatClient(settings.DeploymentName)
        .AsAIAgent(
            name: "AiseyAgent",
            instructions: settings.SystemPrompt,
            temperature: settings.Temperature,
            maxOutputTokens: settings.MaxTokens
        );
    }
}
```

---

## 11. Migration Checklist for Profisee Aisey

### Phase 1: Preparation (Week 1)
- [ ] Review this migration guide with your team
- [ ] Identify all SK usage points in Aisey codebase
- [ ] Set up test environment with AF packages
- [ ] Create backward compatibility plan
- [ ] Document current plugin/function implementations

### Phase 2: Package Migration (Week 1-2)
- [ ] Add AF NuGet packages to project
- [ ] Keep SK package temporarily for compatibility
- [ ] Update namespace imports
- [ ] Test that both packages coexist

### Phase 3: Core Service Migration (Week 2-3)
- [ ] Migrate `IChatCompletionService` → `IChatClient`
- [ ] Replace kernel initialization with direct chat client
- [ ] Test basic chat functionality
- [ ] Migrate dependency injection configuration

### Phase 4: Plugin/Function Migration (Week 3-4)
- [ ] Convert plugin classes to regular C# methods
- [ ] Replace `IKernelBuilderPlugins` with `AIFunctionFactory`
- [ ] Migrate `KernelFunction` usage to direct method calls
- [ ] Test all tool/function executions

### Phase 5: Image Handling (Week 4)
- [ ] Migrate image content handling to `ImageContent`
- [ ] Test image analysis functionality
- [ ] Verify base64 image support if used

### Phase 6: Testing & Validation (Week 5)
- [ ] Unit test all migrated functions
- [ ] Integration test complete workflows
- [ ] Performance benchmark comparison
- [ ] User acceptance testing

### Phase 7: Cleanup (Week 6)
- [ ] Remove SK package dependency
- [ ] Remove backward compatibility code
- [ ] Update documentation
- [ ] Final code review

---

## 12. Support & Next Steps

### Questions to Address in Workshop
1. **Tool/Function Patterns:** How many plugins/functions does Aisey currently use?
2. **Streaming Requirements:** Does Aisey use streaming responses?
3. **Multi-Agent:** Any multi-agent orchestration patterns?
4. **Custom Connectors:** Any custom SK connectors we need to migrate?
5. **Testing Strategy:** What's your preferred testing approach during migration?

### Resources
- **Microsoft Agent Framework Docs:** https://aka.ms/agent-framework
- **C# Migration Guide:** https://learn.microsoft.com/semantic-kernel/concepts/migrate-to-agent-framework-dotnet
- **Sample Code:** https://github.com/microsoft/semantic-kernel/tree/main/dotnet/samples/AgentFrameworkMigration
- **General Migration Guide:** `/AQ-PROFISEE/PROFISEE-SK-TO-AF-MIGRATION-GUIDE-CSHARP.md`

### Contact
**Arturo Quiroga**  
Sr Partner Solutions Architect  
Microsoft - EPS America 

---

**Document Version:** 1.0  
**Last Updated:** December 17, 2025  
**Author:** Arturo Quiroga
