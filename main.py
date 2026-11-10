import os
import json

from openai import OpenAI
from dotenv import load_dotenv

from Utils.util import log, log_error
from tools import tools, TOOLS

# 1. Load environment variables
load_dotenv()

base_api = os.getenv("BASE_API")
api_key = os.getenv("API_KEY")
model = os.getenv("MODEL")

# 2. Initialize OpenAI client
client = OpenAI(
    base_url=base_api,
    api_key=api_key
)

# 3. Conversation history
messages = [
    {
        "role": "system",
        "content": (
            "You are a reliable and helpful AI assistant. "
            "Use the entire conversation history for context. "
            f"Available tools: {', '.join(TOOLS.keys())}. "
            "Use relevant tools whenever external or real-time "
            "information is required. "
            "Never fabricate information or tool results. "
            "If information is unavailable, say so clearly. "
            "Provide accurate, clear, and concise answers. "
            "Explain in detail when requested."
        )
    }
]

# 4. Execute a requested Python tool
def execute_tool(tool_call):
    function_name = tool_call["function"]["name"]
    try:
        if function_name not in TOOLS:
            raise ValueError(f"Unknown tool: {function_name}")
        arguments = json.loads(
            tool_call["function"]["arguments"]
        )
        function = TOOLS[function_name]
        result = function(**arguments)
        return str(result)
    except Exception as e:
        return f"Tool execution error: {str(e)}"

# 5. Streaming agent with tool calling
def run_agent(user_input):
    messages.append({
        "role": "user",
        "content": user_input
    })
    max_tool_rounds = 10
    for _ in range(max_tool_rounds):
        log(f"-> {model}")
        log("   thinking...")
        # Request streaming response
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            stream=True
        )
        assistant_content = ""
        # Collect streamed tool calls
        tool_calls = {}
        print("\nLLM: ", end="", flush=True)
        # Receive streaming chunks
        for chunk in stream:
            delta = chunk.choices[0].delta
            # 1. Stream normal text
            if delta.content:
                assistant_content += delta.content
                print(
                    delta.content,
                    end="",
                    flush=True
                )
            # 2. Collect tool-call information
            if delta.tool_calls:
                for tool_call in delta.tool_calls:
                    index = tool_call.index
                    if index not in tool_calls:
                        tool_calls[index] = {
                            "id": "",
                            "type": "function",
                            "function": {
                                "name": "",
                                "arguments": ""
                            }
                        }
                    current_call = tool_calls[index]
                    # Collect tool call ID
                    if tool_call.id:
                        current_call["id"] = tool_call.id
                    # Collect function name and arguments
                    if tool_call.function:
                        if tool_call.function.name:
                            current_call["function"]["name"] += (
                                tool_call.function.name
                            )
                        if tool_call.function.arguments:
                            current_call["function"]["arguments"] += (
                                tool_call.function.arguments
                            )
        print("\n")
        # Sort tool calls by their original index
        collected_tool_calls = [
            tool_calls[index]
            for index in sorted(tool_calls)
        ]
        # 3. No tool calls: final assistant response
        if not collected_tool_calls:
            messages.append({
                "role": "assistant",
                "content": assistant_content
            })
            log("   completed")
            return assistant_content
        # 4. Save complete assistant message with tool calls
        messages.append({
            "role": "assistant",
            "content": assistant_content or None,
            "tool_calls": collected_tool_calls
        })
        # 5. Execute requested tools
        for tool_call in collected_tool_calls:
            function_name = tool_call["function"]["name"]
            log(f"   tool requested: {function_name}")
            result = execute_tool(tool_call)
            log(f"   tool result: {result}")
            # 6. Send tool result back to conversation
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result
            })
        # Continue loop:
        # LLM receives tool results and generates its next response.
    raise RuntimeError(
        f"Maximum tool execution rounds ({max_tool_rounds}) exceeded."
    )

# 6. Interactive terminal chat
if __name__ == "__main__":
    print("AI Agent Started! Type 'exit' to quit.\n")
    while True:
        try:
            user_input = input("User: ").strip()
            if not user_input:
                continue
            if user_input.lower() in [
                "exit", "bye", "goodbye", "quit"
            ]:
                print("Agent: Goodbye!")
                break
            run_agent(user_input)
            print()
        except KeyboardInterrupt:
            log_error("\nYou Stoped!")
        except Exception as e:
            log_error(f"\n Error: {e}")
