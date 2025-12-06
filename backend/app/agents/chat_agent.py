from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from backend.app.services.memory_service import memory_service
import os

# Define tools
@tool
def search_memory(query: str, session_id: str):
    """Searches the long-term memory for relevant past conversation context based on the query."""
    # Note: In a real agent, session_id might need to be injected or retrieved from state.
    # The agent might pass it explicitly if instructed.
    # For now, we will handle session_id injection outside or rely on the agent to pass it.
    # To make it easier for the agent, we might wrap this tool to auto-inject session_id if we have a stateful object.

    # Since we are using a stateless tool function here, we rely on the agent to provide session_id
    # OR we use a global/context var.
    # But `create_react_agent` is stateless.

    # Let's trust the agent to pass it if we give it the session_id in the system prompt.
    try:
        results = memory_service.search_memory(session_id, query)
        return str(results)
    except Exception as e:
        return f"Error searching memory: {e}"

class ChatAgent:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.mock_mode = False
        if not api_key or api_key == "sk-dummy-key":
             self.mock_mode = True
             print("Warning: ChatAgent in MOCK MODE")

        self.llm = None
        self.agent_executor = None

        if not self.mock_mode:
            try:
                self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
                tools = [search_memory]
                # We create the graph
                self.agent_executor = create_react_agent(self.llm, tools)
            except Exception as e:
                print(f"Failed to init ChatAgent: {e}")
                self.mock_mode = True

        self.system_prompt = """You are a modern voice chatbot.
        You are helpful, concise (since you are a voice bot), and intelligent.
        You have access to long-term memory via the 'search_memory' tool.
        ALWAYS check the memory if the user asks a follow-up question or refers to past context.
        The current session_id is: {session_id}
        """

    async def get_response(self, session_id: str, user_input: str) -> str:
        if self.mock_mode:
            return f"Mock response to: {user_input}"

        try:
            # We inject the session_id into the system prompt for this run
            formatted_system_prompt = self.system_prompt.format(session_id=session_id)

            inputs = {
                "messages": [
                    ("system", formatted_system_prompt),
                    ("human", user_input),
                ]
            }

            # Use invoke for sync or ainvoke for async
            # LangGraph graphs are async compatible
            response = await self.agent_executor.ainvoke(inputs)

            # The response from create_react_agent is the state, which contains "messages"
            # The last message should be the AIMessage
            messages = response["messages"]
            ai_message = messages[-1]
            content = ai_message.content

            # Save to memory (we do this manually here to ensure everything is captured)
            # The agent might have searched memory, but we also want to Append the new interaction
            memory_service.add_memory(session_id, "user", user_input)
            memory_service.add_memory(session_id, "assistant", content)

            return content

        except Exception as e:
            print(f"Error in agent execution: {e}")
            return "I'm sorry, I encountered an error."

chat_agent = ChatAgent()
