from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, Tool
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import spacy
nlp = spacy.load("en_core_web_sm")
import fitz
import re
import json

with open("glossary.json", "r", encoding="utf-8") as f:
    glossary = json.load(f)

client = MongoClient("mongodb+srv://vinaycheripally1:vinay123@cluster0.kq7rnjc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["translations"]
collection = db["memory"]

model = SentenceTransformer("intfloat/e5-small")

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

def critique_translation(input: dict) -> str:
    original = input["original"]
    translation = input["translation"]
    critique_prompt = f"""
You are a legal translation quality reviewer.

Please critique the following Telugu translation of a legal sentence in English.

- Comment on tone, clarity, and formality.
- Note if the translation deviates from the meaning.
- Suggest improvements if necessary.
- Comment on whether the output is adding more to what it actually should translate.

English: {original}
Telugu: {translation}
"""
    return llm.invoke([HumanMessage(content=critique_prompt)]).content

critique_tool = Tool.from_function(
    name="critique_translation",
    description=(
        "Provides a quality critique of the Telugu translation, including tone, clarity, and legal accuracy."
        "Input should be a dict with 'original' (English sentence) and 'translation' (Telugu translation). "
        "Returns comments on how good the translation is and suggests how to make it better."
    ),
    func=critique_translation,
)



def validate_translation_with_glossary_tool(input: dict) -> str:
    original = input["original"]
    translation = input["translation"]
    issues = []
    for eng_term, telugu_term in glossary.items():
        if eng_term.lower() in original.lower():
            if telugu_term not in translation:
                issues.append(
                    f"Term '{eng_term}' found in English but Telugu equivalent '{telugu_term}' not found in translation."
                )
    if not issues:
        return "No glossary compliance issues found."
    return "\n".join(issues)


glossary_validator_tool = Tool.from_function(
    name="validate_translation_with_glossary",
    description=(
        "Checks if the Telugu translation correctly uses terms from a legal glossary. "
        "Input should be a dict with 'original' (English sentence) and 'translation' (Telugu translation). "
        "Returns a string of issues if any glossary terms are missing in the translation."
    ),
    func=validate_translation_with_glossary_tool,
)

def get_examples(english: str, k: int = 5) -> list:
    """This is the code to get list of examples from mongodb using vector database"""
    embedding = model.encode(english).tolist()
    results = collection.aggregate([
        {
            "$vectorSearch": {
                "queryVector": embedding,
                "path": "embedding",
                "numCandidates": 100,
                "limit": k,
                "index": "vector_index"
            }
        }
    ])
    ans = []
    for i in list(results):
        ans.append({i["english_text"]:i["telugu_text"]})
    return ans

tool = Tool.from_function(
    name="get_examples",
    description="Useful to retrieve top-k similar legal sentence pairs (English-Telugu).",
    func=lambda input: get_examples(input),
)

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="""You are a legal translation assistant. Your job is to translate English legal sentences into formal Telugu using example translations.

**Important:** You will only translate the English text provided in the user's current input.Do not include any English explanatory text, prefixes, or suffixes like "Here is the translation:" or "The Telugu translation is:". Return only the pure Telugu text."""),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

def chunk_text(text):
    doc = nlp(text)
    return [sent.text for sent in doc.sents]

from langchain_core.runnables import RunnableLambda

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_function_messages(x.get("intermediate_steps", [])),
    }
    | prompt
    | llm
    | OpenAIFunctionsAgentOutputParser()
)

agent_executor = AgentExecutor(agent=agent, tools=[tool,glossary_validator_tool,critique_tool], verbose=True)

pdf_path= "second.pdf"
text= ""
doc  = fitz.open(pdf_path)
for page in doc:
    text+=page.get_text()

chunks = chunk_text(text)
translated_chunks = []
for chunk in chunks:
    chunk = re.sub(r'\s+', ' ', chunk).strip()
    if len(chunk)<10:
        continue
    result = agent_executor.invoke({
        "input":"English" + chunk,
    })
    translated_chunks.append(result["output"])

# Join final output
final_translation = "\n\n".join(translated_chunks)
with open("prowithcritique.txt","w",encoding="UTF-8") as file:
    file.write(final_translation)

