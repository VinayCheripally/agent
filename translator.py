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
import fitz
import re
import json
import os

# Load environment variables
load_dotenv()

class PDFTranslator:
    def __init__(self):
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise Exception("Please install spaCy English model: python -m spacy download en_core_web_sm")
        
        # Load glossary
        try:
            with open("glossary.json", "r", encoding="utf-8") as f:
                self.glossary = json.load(f)
        except FileNotFoundError:
            self.glossary = {}
        
        # Initialize MongoDB connection
        try:
            self.client = MongoClient("mongodb+srv://vinaycheripally1:vinay123@cluster0.kq7rnjc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
            self.db = self.client["translations"]
            self.collection = self.db["memory"]
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            self.collection = None
        
        # Initialize sentence transformer
        self.model = SentenceTransformer("intfloat/e5-small")
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        
        # Setup tools and agent
        self._setup_tools()
        self._setup_agent()
    
    def _setup_tools(self):
        """Setup translation tools"""
        
        def critique_translation(input_dict):
            original = input_dict["original"]
            translation = input_dict["translation"]
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
            return self.llm.invoke([HumanMessage(content=critique_prompt)]).content

        def validate_translation_with_glossary(input_dict):
            original = input_dict["original"]
            translation = input_dict["translation"]
            issues = []
            for eng_term, telugu_term in self.glossary.items():
                if eng_term.lower() in original.lower():
                    if telugu_term not in translation:
                        issues.append(
                            f"Term '{eng_term}' found in English but Telugu equivalent '{telugu_term}' not found in translation."
                        )
            if not issues:
                return "No glossary compliance issues found."
            return "\n".join(issues)

        def get_examples(english, k=5):
            """Get similar examples from MongoDB"""
            if not self.collection:
                return []
            
            try:
                embedding = self.model.encode(english).tolist()
                results = self.collection.aggregate([
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
                    ans.append({i["english_text"]: i["telugu_text"]})
                return ans
            except Exception as e:
                print(f"Error getting examples: {e}")
                return []

        self.critique_tool = Tool.from_function(
            name="critique_translation",
            description=(
                "Provides a quality critique of the Telugu translation, including tone, clarity, and legal accuracy."
                "Input should be a dict with 'original' (English sentence) and 'translation' (Telugu translation). "
                "Returns comments on how good the translation is and suggests how to make it better."
            ),
            func=critique_translation,
        )

        self.glossary_validator_tool = Tool.from_function(
            name="validate_translation_with_glossary",
            description=(
                "Checks if the Telugu translation correctly uses terms from a legal glossary. "
                "Input should be a dict with 'original' (English sentence) and 'translation' (Telugu translation). "
                "Returns a string of issues if any glossary terms are missing in the translation."
            ),
            func=validate_translation_with_glossary,
        )

        self.examples_tool = Tool.from_function(
            name="get_examples",
            description="Useful to retrieve top-k similar legal sentence pairs (English-Telugu).",
            func=lambda input_text: get_examples(input_text),
        )

    def _setup_agent(self):
        """Setup the translation agent"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a legal translation assistant. Your job is to translate English legal sentences into formal Telugu using example translations.

**Important:** You will only translate the English text provided in the user's current input. Do not include any English explanatory text, prefixes, or suffixes like "Here is the translation:" or "The Telugu translation is:". Return only the pure Telugu text."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_function_messages(x.get("intermediate_steps", [])),
            }
            | prompt
            | self.llm
            | OpenAIFunctionsAgentOutputParser()
        )

        self.agent_executor = AgentExecutor(
            agent=agent, 
            tools=[self.examples_tool, self.glossary_validator_tool, self.critique_tool], 
            verbose=False
        )

    def chunk_text(self, text):
        """Split text into sentences using spaCy"""
        doc = self.nlp(text)
        return [sent.text for sent in doc.sents]

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from uploaded PDF file"""
        try:
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def translate_text(self, text, progress_callback=None):
        """Translate text to Telugu"""
        chunks = self.chunk_text(text)
        translated_chunks = []
        
        total_chunks = len(chunks)
        
        for i, chunk in enumerate(chunks):
            # Clean and filter chunks
            chunk = re.sub(r'\s+', ' ', chunk).strip()
            if len(chunk) < 10:
                continue
            
            try:
                result = self.agent_executor.invoke({
                    "input": "English: " + chunk,
                })
                translated_chunks.append(result["output"])
                
                # Update progress
                if progress_callback:
                    progress_callback(i + 1, total_chunks)
                    
            except Exception as e:
                print(f"Error translating chunk: {e}")
                translated_chunks.append(f"[Translation Error: {chunk}]")
        
        return "\n\n".join(translated_chunks)

    def translate_pdf(self, pdf_file, progress_callback=None):
        """Main function to translate PDF"""
        # Extract text
        text = self.extract_text_from_pdf(pdf_file)
        
        # Translate text
        translated_text = self.translate_text(text, progress_callback)
        
        return translated_text