from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.system import SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory  # Correct import here
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from prompt import prompt
import uuid


load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
SESSION_STORE = {}
FEEDBACK_STORE = {}  # Store feedback per user_id: {user_id: [feedback1, feedback2, ...]}

def get_user_history(user_id: str) -> ChatMessageHistory:
    if user_id not in SESSION_STORE:
        user_id = str(uuid.uuid4())
        SESSION_STORE[user_id] = ChatMessageHistory()
    return SESSION_STORE[user_id], user_id

def add_feedback(query: str, code, feedback):
    """Store feedback (thumbs_up, thumbs_down, or None) for the last query/result pair."""
    if query not in FEEDBACK_STORE:
        FEEDBACK_STORE[query] = []
    
    FEEDBACK_STORE[query]= [code, feedback]
    print("Storing feedback:", FEEDBACK_STORE)

class code_gen:
    def __init__(self, user_id: str):
        self.model = "gpt-4o-mini"
        self.llm = llm
        self.history, self.user_id = get_user_history(user_id)

        if not any(isinstance(m, SystemMessage) for m in self.history.messages):
            system_prompt = prompt
            self.history.add_message(SystemMessage(content=system_prompt))

    async def generate_code(self, query, df):
        info = {
            "shape": df.shape,  
            "columns": list(df.columns),
            "dtypes": df.dtypes.astype(str).to_dict(),
        }
        user_content = f"User query: {query} DataFrame info: {info}"
        
        self.history.add_user_message(user_content)
        
        # Get full messages from history and invoke
        messages = self.history.messages
        response = await self.llm.ainvoke(messages)
        generated_code = response.content.strip()

        # Clean code (remove markdown formatting)
        if "```python" in generated_code:
            generated_code = generated_code.split("```python")[1].split("```")[0].strip()
        elif "```" in generated_code:
            generated_code = generated_code.split("```")[1].split("```")[0].strip()

        self.history.add_ai_message(generated_code)

        return generated_code, self.user_id