# Legal PDF Translator

A Streamlit web application for translating legal documents from English to Telugu using AI-powered translation with legal terminology support.

## Features

- 📄 **PDF Upload & Processing**: Upload PDF documents and extract text automatically
- 🤖 **AI-Powered Translation**: Uses Google Gemini for high-quality translations
- 📚 **Legal Glossary**: Built-in legal terminology dictionary for accurate translations
- 🔍 **Translation Critique**: Quality assessment and improvement suggestions
- 📊 **Progress Tracking**: Real-time translation progress with chunk-by-chunk processing
- 💾 **Download Results**: Save translated documents as text files

## Setup

### Prerequisites

- Python 3.8+
- Google API key for Gemini
- MongoDB connection (for translation examples)

### Installation

1. **Clone or download the project files**

2. **Run the setup script**:
   ```bash
   python setup.py
   ```

3. **Configure environment variables**:
   - Add your Google API key to the `.env` file:
     ```
     GOOGLE_API_KEY=your_google_api_key_here
     ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Usage

1. **Initialize the Translator**:
   - Click the "Initialize Translator" button in the sidebar
   - Wait for the system to load all components

2. **Upload PDF**:
   - Use the file uploader to select your PDF document
   - Optionally preview the extracted text

3. **Translate**:
   - Click "Translate PDF" to start the translation process
   - Monitor progress in real-time

4. **Download Results**:
   - View the translated text in Telugu
   - Download the translation as a text file

## Project Structure

```
├── app.py                 # Main Streamlit application
├── translator.py          # Translation logic and PDF processing
├── main.py               # Original translation script
├── glossary.json         # Legal terminology dictionary
├── requirements.txt      # Python dependencies
├── setup.py             # Setup and installation script
└── README.md            # This file
```

## Components

### Translation Engine
- **LangChain Agents**: Orchestrates the translation process
- **Google Gemini**: Provides AI-powered translation
- **Sentence Transformers**: Finds similar translation examples
- **spaCy**: Handles text processing and sentence segmentation

### Tools
- **Critique Tool**: Analyzes translation quality
- **Glossary Validator**: Ensures legal terms are correctly translated
- **Examples Tool**: Retrieves similar translations from database

## Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Your Google Gemini API key

### MongoDB Connection
The application connects to MongoDB for translation examples. Update the connection string in `translator.py` if needed.

## Troubleshooting

### Common Issues

1. **spaCy Model Missing**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **MongoDB Connection Failed**:
   - Check your internet connection
   - Verify MongoDB connection string
   - The app will work without MongoDB but with reduced functionality

3. **Google API Key Issues**:
   - Ensure your API key is valid
   - Check that the Gemini API is enabled
   - Verify the key is correctly set in the `.env` file

## Features in Detail

### PDF Processing
- Extracts text from PDF files using PyMuPDF
- Handles multi-page documents
- Preserves document structure

### Translation Quality
- Uses legal terminology glossary for consistency
- Provides translation critique and suggestions
- Context-aware translation using similar examples

### User Interface
- Clean, intuitive Streamlit interface
- Real-time progress tracking
- File upload with drag-and-drop support
- Downloadable results

## License

This project is for educational and research purposes.