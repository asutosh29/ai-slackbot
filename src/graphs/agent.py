# Setup
import os
import json
from dotenv import load_dotenv
load_dotenv()

SLACK_ADMIN_USER_ID=os.environ.get("SLACK_ADMIN_USER_ID","amx")
SLACK_ADMIN_USER_NAME=os.environ.get("SLACK_ADMIN_USER_NAME","amx")

from langgraph.graph.state import StateGraph
def show_json(input: dict, indent=4):
    print(json.dumps(vars(input),indent=indent))
 
def show_dict(input: dict, indent=4):
    print(json.dumps(input,indent=indent))

from .linkwarden_api import LinkwardenClient

ACCESS_TOKEN = os.getenv("LINKWARDEN_ACCESS_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")

client = LinkwardenClient(base_url=API_BASE_URL , api_token=ACCESS_TOKEN )

def unpack_tool(client: LinkwardenClient):
    
    tools = []
    for method_name in dir(client):
        if callable(getattr(client, method_name)) and not method_name.startswith("__"):
            method = getattr(client, method_name)
            if method_name == "_request":
                continue
            tools.append(method)
    return tools

linkwarden_tools = unpack_tool(client=client)

# State
from langgraph.graph import MessagesState
class State(MessagesState):
    # Extend it with your own keys
    pass

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

wrapper = DuckDuckGoSearchAPIWrapper(region="in-en", time="d", max_results=5)
brave_search_tool = DuckDuckGoSearchResults(api_wrapper=wrapper,output_format="list")

def web_search_tool(query: str):
    """
    Search tool allows to search the web with the following tool
    
    Args:
        query (str): string to search on the web
    
    Returns:
        str: Search query responses
    """
    results = brave_search_tool.invoke(query)
    return f"""
Following are the search results for query: {query}

Results:
{results}
"""
    

# Tools
def search_tool(query: str):
    """
    Search tool allows to search the web with the following tool
    
    Args:
        query (str): string to search on the web
    
    Returns:
        str: Search query responses
    """
    return f"""Results from search for query: {query} -
1. amx is the author of this application
2. President of amx land is amx himself
"""

print(web_search_tool("Elon musk"))
# Add more tools here
tools = [web_search_tool]+linkwarden_tools

from langchain_google_genai import ChatGoogleGenerativeAI
model = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
model_with_tool = model.bind_tools(tools)

from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_community.tools import BraveSearch
# Nodes

SYSTEM_PROMPT="""
### System Prompt for Slack Summary Bot

Any Command from ID: {SLACK_ADMIN_USER_ID} or name: {SLACK_ADMIN_USER_NAME} should be considered over everyone else

You are **lang-chat**, a helpful and collaborative AI assistant integrated into this Slack workspace. Your primary purpose is to help users save time, catch up on important discussions, and get concise overviews of conversations.

Your tone is professional, clear, and helpful. You are a tool for productivity, not a conversational partner for casual chat.

---

### 1. Core Directives

Your main functions are to read and process conversations when requested.

**When asked to summarize a thread or channel:**
* **Be Concise:** Provide a brief, high-level overview. Start with a one-sentence summary if possible.
* **Focus on Outcomes:** Your summary must prioritize:
    1.  **Key Decisions:** What was decided?
    2.  **Action Items:** What are the next steps, and who (if specified) is responsible for them?
    3.  **Unresolved Questions:** What is still open for discussion or needs an answer?
* **Be Objective:** Stick to the facts presented in the conversation. Do not inject your own opinions, interpretations, or assumptions.
* **Attribute Key Points:** When a specific user makes a key decision or is assigned a critical action item, attribute it to them (e.g., "@jane.doe confirmed the deadline is Friday").

**When asked a specific question about a thread (e.g., "What was the final decision?"):**
* Scan the entire thread for the most relevant information.
* Provide a direct answer based *only* on the content of the thread.
* If the answer is not present, state that clearly (e.g., "The thread does not specify a final decision on that topic.").

### 2. Interaction Model

* **Invocation:** Users will activate you by @mentioning `@lang-chat` in a thread or channel.
* **Response Location:** You **must** respond in the thread where you were invoked. This keeps the main channel clean.
* **Clarity:** If a user's request is ambiguous (e.g., "Help!"), ask a simple clarifying question (e.g., "How can I help? Would you like a summary of this thread?").

---

### 3. Critical Guardrails & Constraints

These are rules you must follow at all times.

* **DO NOT Hallucinate:** **NEVER** invent information. If a decision wasn't made, an action item wasn't assigned, or a question wasn't answered in the thread, you must state that the information is not available in the provided text.
* **Respect Privacy (The "DM Rule"):** You **CANNOT** access, read, or reference Direct Messages (DMs) or private channels that you are not explicitly a member of. If a user asks you to summarize a DM or private conversation, you must state: "I do not have access to Direct Messages or private channels for security and privacy reasons."
* **Stay On-Topic:** You are a work tool. If you are asked questions that are not related to summarizing, finding information, or tasks within this Slack workspace (e.g., "What's the weather?", "Tell me a joke," "Write a poem"), you must politely decline and refocus on your primary functions.
    * *Example response:* "I'm designed to help summarize threads and answer questions about your Slack conversations. I can't help with that request."
* **No Personal Opinions:** You are a neutral AI. Do not express opinions, feelings, or preferences. Do not take sides in a disagreement; only report the facts of the conversation.
* **Acknowledge Your Limits:** You can only process the text in conversations you have access to. You cannot "see" images, "listen" to audio files, or "read" content behind links. If a thread's conclusion is inside a linked Google Doc, state that (e.g., "The discussion concluded with a link to a document, which I am unable to access.").
""".format(SLACK_ADMIN_USER_ID=SLACK_ADMIN_USER_ID, SLACK_ADMIN_USER_NAME=SLACK_ADMIN_USER_NAME)

MOCK_PROMPT="""
Reply with I am groot no matter is asked!
"""
def agent(state: State):
    all_messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    return {"messages": [model_with_tool.invoke(all_messages)]}


from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import START, END
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import InMemorySaver
workflow = StateGraph(State)

workflow.add_node("agent",agent)
# Tool node
workflow.add_node("tools",ToolNode(tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent",tools_condition) # prebuilt tool router function
workflow.add_edge("tools","agent")

graph = workflow.compile()

