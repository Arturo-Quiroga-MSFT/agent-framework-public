"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import { useCopilotAction, useDefaultTool } from "@copilotkit/react-core";
import "@copilotkit/react-ui/styles.css";
import { WeatherCard, CompareWeatherCard } from "@/components/weather-card";

function AgentContent() {
  // Default tool renderer for debugging - shows all tool calls
  useDefaultTool({
    render: ({ name, args, status, result }) => {
      console.log('Tool call:', { name, args, status, result });
      return <></>; // Return empty fragment to let specific renderers handle display
    },
  });

  // Render get_weather tool with custom UI
  useCopilotAction({
    name: "get_weather",
    available: "disabled", // Backend handles execution, frontend only renders
    parameters: [
      { name: "location", type: "string", required: true },
    ],
    render: ({ args, status, result }) => {
      console.log('get_weather render:', { args, status, result });
      
      // Show loading state while executing
      if (status === "executing" || status === "inProgress") {
        return (
          <div className="rounded-xl shadow-lg bg-gradient-to-br from-blue-50 to-indigo-100 p-6 max-w-md w-full animate-pulse">
            <div className="flex items-center space-x-3 mb-4">
              <div className="h-8 w-8 bg-blue-300 rounded-full"></div>
              <div className="h-6 bg-blue-300 rounded w-32"></div>
            </div>
            <div className="space-y-3">
              <div className="h-4 bg-blue-200 rounded w-full"></div>
              <div className="h-4 bg-blue-200 rounded w-3/4"></div>
              <div className="h-4 bg-blue-200 rounded w-5/6"></div>
            </div>
          </div>
        );
      }
      
      // Parse and render weather data when complete
      if (status === "complete" && result) {
        try {
          // Result might be a string or already parsed object
          const weatherData = typeof result === 'string' ? JSON.parse(result) : result;
          return <WeatherCard weather={weatherData} />;
        } catch (e) {
          console.error('Failed to parse weather data:', e, result);
          return (
            <div className="text-sm text-red-500 bg-red-50 p-3 rounded">
              Error parsing weather data: {String(e)}
            </div>
          );
        }
      }
      
      return (
        <div className="text-sm text-blue-600 italic">
          Getting weather for {args.location}...
        </div>
      );
    },
  });

  // Render compare_weather tool with custom UI
  useCopilotAction({
    name: "compare_weather",
    available: "disabled",
    parameters: [
      { name: "cities", type: "object", required: true },
    ],
    render: ({ args, status, result }) => {
      console.log('compare_weather render:', { args, status, result });
      
      // Show loading state
      if (status === "executing" || status === "inProgress") {
        return (
          <div className="rounded-xl shadow-lg bg-gradient-to-br from-blue-50 to-indigo-100 p-6 max-w-4xl w-full animate-pulse">
            <div className="h-8 bg-blue-300 rounded w-48 mb-4"></div>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="h-48 bg-blue-200 rounded"></div>
              <div className="h-48 bg-blue-200 rounded"></div>
            </div>
          </div>
        );
      }
      
      // Parse and render comparison data when complete
      if (status === "complete" && result) {
        try {
          const citiesData = typeof result === 'string' ? JSON.parse(result) : result;
          return <CompareWeatherCard cities={citiesData} />;
        } catch (e) {
          console.error('Failed to parse comparison data:', e, result);
          return (
            <div className="text-sm text-red-500 bg-red-50 p-3 rounded">
              Error parsing comparison data: {String(e)}
            </div>
          );
        }
      }
      
      return (
        <div className="text-sm text-blue-600 italic">
          Comparing weather across cities...
        </div>
      );
    },
  });

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-br from-blue-50 to-indigo-100">
          <div className="max-w-4xl w-full space-y-8">
            {/* Header */}
            <div className="text-center space-y-4">
              <h1 className="text-5xl font-bold text-gray-900">
                Azure AI Weather Agent
              </h1>
              <p className="text-xl text-gray-600">
                Production-ready AI agent with CopilotKit + Agent Framework
              </p>
            </div>

            {/* Features Card */}
            <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                ✨ Features
              </h2>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <h3 className="font-semibold text-lg text-gray-700">🌤️ Real Weather Data</h3>
                  <p className="text-gray-600">
                    Live weather information from OpenWeatherMap API
                  </p>
                </div>

                <div className="space-y-2">
                  <h3 className="font-semibold text-lg text-gray-700">🤖 Azure AI Powered</h3>
                  <p className="text-gray-600">
                    Built with Microsoft Agent Framework and Azure AI
                  </p>
                </div>

                <div className="space-y-2">
                  <h3 className="font-semibold text-lg text-gray-700">⚡ AG-UI Protocol</h3>
                  <p className="text-gray-600">
                    Open standard for agent-to-UI communication
                  </p>
                </div>

                <div className="space-y-2">
                  <h3 className="font-semibold text-lg text-gray-700">🎨 Production Ready</h3>
                  <p className="text-gray-600">
                    Custom branded UI with React and Next.js
                  </p>
                </div>
              </div>
            </div>

            {/* Example Queries */}
            <div className="bg-white rounded-2xl shadow-xl p-8">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                💬 Try These Queries
              </h2>
              <ul className="space-y-3 text-gray-700">
                <li className="flex items-start">
                  <span className="mr-2">▸</span>
                  <span>What&apos;s the weather in Toronto?</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">▸</span>
                  <span>How&apos;s the weather in Mexico City?</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">▸</span>
                  <span>Compare weather in Guadalajara and Monterrey</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">▸</span>
                  <span>Tell me about the weather in Puebla</span>
                </li>
              </ul>
            </div>

            {/* Tech Stack */}
            <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl shadow-xl p-8 text-white">
              <h2 className="text-2xl font-semibold mb-4">
                🛠️ Technology Stack
              </h2>
              <div className="grid md:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="font-semibold mb-1">Backend</p>
                  <ul className="space-y-1 opacity-90">
                    <li>• Agent Framework</li>
                    <li>• FastAPI</li>
                    <li>• Azure AI</li>
                  </ul>
                </div>
                <div>
                  <p className="font-semibold mb-1">Frontend</p>
                  <ul className="space-y-1 opacity-90">
                    <li>• Next.js 15</li>
                    <li>• React 19</li>
                    <li>• CopilotKit</li>
                  </ul>
                </div>
                <div>
                  <p className="font-semibold mb-1">Protocol</p>
                  <ul className="space-y-1 opacity-90">
                    <li>• AG-UI (Open)</li>
                    <li>• Server-Sent Events</li>
                    <li>• REST API</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Instructions */}
            <div className="text-center text-gray-600 space-y-2">
              <p className="text-sm">
                👉 <strong>Open the sidebar</strong> on the right to chat with the agent
              </p>
              <p className="text-xs opacity-75">
                This is the same weather agent from DevUI, now in a production-ready UI
              </p>
            </div>
          </div>
        </main>
  );
}

export default function Home() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="weather_agent">
      <CopilotSidebar
        defaultOpen={true}
        labels={{
          title: "Azure AI Weather Agent",
          initial: "Hi! 👋 I'm your Azure AI weather assistant. Ask me about the weather in any city!",
        }}
      >
        <AgentContent />
      </CopilotSidebar>
    </CopilotKit>
  );
}
