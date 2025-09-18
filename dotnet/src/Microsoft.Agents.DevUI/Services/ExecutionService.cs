using Microsoft.Agents.DevUI.Models;
using Microsoft.Extensions.AI.Agents;
using Microsoft.Extensions.AI;
using Microsoft.Agents.Workflows;

namespace Microsoft.Agents.DevUI.Services;

/// <summary>
/// Unified execution service that handles both agents and workflows
/// with real execution and proper OpenAI format mapping
/// </summary>
public class ExecutionService
{
    private readonly EntityDiscoveryService _discoveryService;
    private readonly ILogger<ExecutionService> _logger;

    public ExecutionService(EntityDiscoveryService discoveryService, ILogger<ExecutionService> logger)
    {
        _discoveryService = discoveryService;
        _logger = logger;
    }

    /// <summary>
    /// Execute entity and return simple response (non-streaming)
    /// </summary>
    public async Task<object> ExecuteEntityAsync(string entityId, DevUIExecutionRequest request)
    {
        var entityInfo = _discoveryService.GetEntityInfo(entityId);
        if (entityInfo == null)
        {
            throw new InvalidOperationException($"Entity '{entityId}' not found");
        }

        _logger.LogInformation("Executing entity {EntityId}", entityId);

        if (entityInfo.Type == "agent")
        {
            return await ExecuteAgentAsync(entityId, request);
        }
        else
        {
            return await ExecuteWorkflowAsync(entityId, request);
        }
    }

    /// <summary>
    /// Execute real agent
    /// </summary>
    private async Task<object> ExecuteAgentAsync(string entityId, DevUIExecutionRequest request)
    {
        // Get the actual agent instance
        var agent = _discoveryService.GetEntityObject(entityId) as AIAgent;
        if (agent == null)
        {
            throw new InvalidOperationException($"Agent '{entityId}' not found or not accessible");
        }

        try
        {
            // Convert request to framework messages
            var messages = ConvertRequestToMessages(request);

            _logger.LogInformation("Executing agent {AgentId} with {MessageCount} messages", entityId, messages.Length);

            // Execute the agent
            var response = await agent.RunAsync(messages);

            // Extract text from response
            var responseText = response.Text ?? "No response text";

            // Convert to OpenAI format
            return CreateSimpleResponse(request, responseText);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing agent {AgentId}", entityId);
            return CreateErrorResponse(request, $"Agent execution failed: {ex.Message}");
        }
    }

    /// <summary>
    /// Execute real workflow
    /// </summary>
    private async Task<object> ExecuteWorkflowAsync(string entityId, DevUIExecutionRequest request)
    {
        // Get the actual workflow instance
        var workflow = _discoveryService.GetEntityObject(entityId);
        if (workflow == null)
        {
            throw new InvalidOperationException($"Workflow '{entityId}' not found or not accessible");
        }

        try
        {
            // Get the input type and create appropriate input
            var workflowType = workflow.GetType();
            var inputContent = request.GetLastMessageContent();

            _logger.LogInformation("Executing workflow {WorkflowId} with input: {Input}", entityId, inputContent);

            // For workflows that accept string input
            if (workflow is Workflow<string> stringWorkflow)
            {
                var run = await InProcessExecution.RunAsync(stringWorkflow, inputContent);
                return await ConvertWorkflowRunToOpenAI(request, run, entityId);
            }
            // For workflows that accept ChatMessage[] input
            else if (workflow is Workflow<ChatMessage[]> messageWorkflow)
            {
                var messages = ConvertRequestToMessages(request);
                var run = await InProcessExecution.RunAsync(messageWorkflow, messages);
                return await ConvertWorkflowRunToOpenAI(request, run, entityId);
            }
            else
            {
                // Fallback for other workflow types
                _logger.LogWarning("Unsupported workflow input type for {WorkflowId}: {Type}", entityId, workflowType);
                return CreateSimpleResponse(request,
                    $"⚙️ Workflow '{entityId}' executed. Unsupported input type: {workflowType}. Please implement specific input handling.");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing workflow {WorkflowId}", entityId);
            return CreateErrorResponse(request, $"Workflow execution failed: {ex.Message}");
        }
    }

    /// <summary>
    /// Convert workflow run events to OpenAI format
    /// </summary>
    private async Task<object> ConvertWorkflowRunToOpenAI(DevUIExecutionRequest request, Run run, string workflowId)
    {
        var responseBuilder = new List<string>();

        // Process all workflow events
        foreach (var evt in run.OutgoingEvents)
        {
            var eventText = ConvertWorkflowEventToText(evt);
            if (!string.IsNullOrEmpty(eventText))
            {
                responseBuilder.Add(eventText);
            }
        }

        // If no meaningful events, create a basic response
        if (responseBuilder.Count == 0)
        {
            responseBuilder.Add($"🔄 Workflow '{workflowId}' completed with status: {run.Status}");
        }

        var finalResponse = string.Join("\n", responseBuilder);
        return CreateSimpleResponse(request, finalResponse);
    }

    /// <summary>
    /// Convert individual workflow event to text representation
    /// </summary>
    private string ConvertWorkflowEventToText(WorkflowEvent evt)
    {
        return evt switch
        {
            AgentRunResponseEvent responseEvent =>
                $"🤖 Agent Response: {responseEvent.Response.Text ?? "No content"}",

            AgentRunUpdateEvent updateEvent =>
                $"📝 Agent Update: {updateEvent.Update.Text ?? "Update"}",

            WorkflowCompletedEvent =>
                "✅ Workflow completed successfully",

            WorkflowStartedEvent startedEvent =>
                $"🚀 Workflow started: {startedEvent.Data?.ToString() ?? "Processing input"}",

            WorkflowErrorEvent errorEvent =>
                $"❌ Workflow error: {(errorEvent.Data as Exception)?.Message ?? "Unknown error"}",

            WorkflowWarningEvent warningEvent =>
                $"⚠️ Workflow warning: {warningEvent.Data?.ToString() ?? "Warning occurred"}",

            ExecutorCompletedEvent executorEvent =>
                $"⚙️ Executor '{executorEvent.ExecutorId}' completed",

            ExecutorFailureEvent failureEvent =>
                $"❌ Executor '{failureEvent.ExecutorId}' failed: {failureEvent.Data}",

            ExecutorInvokedEvent invokedEvent =>
                $"🔧 Executor '{invokedEvent.ExecutorId}' invoked: {invokedEvent.Data?.ToString() ?? "Processing"}",

            SuperStepStartedEvent stepStartedEvent =>
                $"📊 Step {stepStartedEvent.StepNumber} started",

            SuperStepCompletedEvent stepCompletedEvent =>
                $"📈 Step {stepCompletedEvent.StepNumber} completed",

            RequestInfoEvent requestEvent =>
                $"📨 External request: {requestEvent.Data?.ToString() ?? "User input required"}",

            _ =>
                $"📋 {evt.GetType().Name}: {evt.Data?.ToString() ?? "No data"}"
        };
    }

    /// <summary>
    /// Convert DevUI request to framework ChatMessage array
    /// </summary>
    private ChatMessage[] ConvertRequestToMessages(DevUIExecutionRequest request)
    {
        if (request.Messages == null || request.Messages.Count == 0)
        {
            // Fallback: create from last message content
            return [new ChatMessage(ChatRole.User, request.GetLastMessageContent())];
        }

        return request.Messages.Select(m => new ChatMessage(
            role: m.Role.ToLowerInvariant() switch
            {
                "user" => ChatRole.User,
                "assistant" => ChatRole.Assistant,
                "system" => ChatRole.System,
                _ => ChatRole.User
            },
            content: m.Content
        )).ToArray();
    }

    /// <summary>
    /// Create simple OpenAI-compatible response
    /// </summary>
    private object CreateSimpleResponse(DevUIExecutionRequest request, string content)
    {
        return new
        {
            id = Guid.NewGuid().ToString(),
            @object = "chat.completion",
            created = DateTimeOffset.UtcNow.ToUnixTimeSeconds(),
            model = request.Model,
            choices = new[]
            {
                new
                {
                    index = 0,
                    message = new
                    {
                        role = "assistant",
                        content = content
                    },
                    finish_reason = "stop"
                }
            },
            usage = new
            {
                prompt_tokens = EstimateTokens(request.GetLastMessageContent()),
                completion_tokens = EstimateTokens(content),
                total_tokens = EstimateTokens(request.GetLastMessageContent()) + EstimateTokens(content)
            }
        };
    }

    /// <summary>
    /// Create error response
    /// </summary>
    private object CreateErrorResponse(DevUIExecutionRequest request, string message)
    {
        return new
        {
            id = Guid.NewGuid().ToString(),
            @object = "error",
            created = DateTimeOffset.UtcNow.ToUnixTimeSeconds(),
            model = request.Model,
            error = new
            {
                message = message,
                type = "execution_error",
                code = "agent_execution_failed"
            }
        };
    }

    /// <summary>
    /// Estimate token count (rough approximation)
    /// </summary>
    private int EstimateTokens(string text)
    {
        return (text?.Length ?? 0) / 4; // Rough estimate: 4 chars per token
    }
}