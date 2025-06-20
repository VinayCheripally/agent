import streamlit as st
import io
import time
from translator import PDFTranslator

# Page configuration
st.set_page_config(
    page_title="Legal PDF Translator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with improved sidebar styling
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .upload-section {
        border: 2px dashed #cccccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .translation-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
        color: #1565c0;
    }
    
    /* Sidebar specific styling */
    .css-1d391kg {
        background-color: #2e3440 !important;
    }
    
    .css-1lcbmhc {
        background-color: #2e3440 !important;
    }
    
    /* Sidebar text styling */
    .css-1d391kg .css-10trblm {
        color: #eceff4 !important;
    }
    
    .css-1d391kg h1, 
    .css-1d391kg h2, 
    .css-1d391kg h3, 
    .css-1d391kg h4, 
    .css-1d391kg h5, 
    .css-1d391kg h6 {
        color: #eceff4 !important;
    }
    
    .css-1d391kg p, 
    .css-1d391kg li, 
    .css-1d391kg span {
        color: #d8dee9 !important;
    }
    
    /* Sidebar button styling */
    .css-1d391kg .stButton > button {
        background-color: #5e81ac !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .css-1d391kg .stButton > button:hover {
        background-color: #81a1c1 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }
    
    /* Sidebar info boxes */
    .css-1d391kg .info-box {
        background-color: #3b4252 !important;
        border-left: 4px solid #88c0d0 !important;
        color: #eceff4 !important;
    }
    
    .css-1d391kg .info-box h4 {
        color: #88c0d0 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .css-1d391kg .info-box ul, 
    .css-1d391kg .info-box ol {
        color: #d8dee9 !important;
    }
    
    .css-1d391kg .info-box li {
        color: #d8dee9 !important;
        margin-bottom: 0.25rem !important;
    }
    
    /* Sidebar divider */
    .css-1d391kg hr {
        border-color: #4c566a !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Alternative sidebar selectors for different Streamlit versions */
    .stSidebar {
        background-color: #2e3440 !important;
    }
    
    .stSidebar .stMarkdown {
        color: #eceff4 !important;
    }
    
    .stSidebar .stMarkdown h1, 
    .stSidebar .stMarkdown h2, 
    .stSidebar .stMarkdown h3, 
    .stSidebar .stMarkdown h4 {
        color: #eceff4 !important;
    }
    
    .stSidebar .stMarkdown p, 
    .stSidebar .stMarkdown li {
        color: #d8dee9 !important;
    }
    
    /* Dark theme info boxes in sidebar */
    .sidebar-info-box {
        background-color: #3b4252 !important;
        border-left: 4px solid #88c0d0 !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        border-radius: 5px !important;
        color: #eceff4 !important;
    }
    
    .sidebar-info-box h4 {
        color: #88c0d0 !important;
        margin-bottom: 0.5rem !important;
    }
    
    .sidebar-info-box ul, 
    .sidebar-info-box ol {
        color: #d8dee9 !important;
        margin-left: 1rem !important;
    }
    
    .sidebar-info-box li {
        color: #d8dee9 !important;
        margin-bottom: 0.25rem !important;
    }
    
    /* Main content area improvements */
    .stApp > header {
        background-color: transparent !important;
    }
    
    .stApp {
        background-color: #fafafa !important;
    }
    
    /* Button improvements */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'translator' not in st.session_state:
    st.session_state.translator = None
if 'translation_result' not in st.session_state:
    st.session_state.translation_result = None
if 'original_text' not in st.session_state:
    st.session_state.original_text = None

def initialize_translator():
    """Initialize the translator with error handling"""
    try:
        with st.spinner("Initializing translation system..."):
            translator = PDFTranslator()
        st.session_state.translator = translator
        return True
    except Exception as e:
        st.error(f"Failed to initialize translator: {str(e)}")
        return False

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📄 Legal PDF Translator</h1>
        <p>English to Telugu Legal Document Translation</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar with improved styling
    with st.sidebar:
        st.markdown('<h2 style="color: #eceff4; margin-bottom: 1rem;">🔧 Settings</h2>', unsafe_allow_html=True)
        
        # Initialize translator button
        if st.button("🚀 Initialize Translator", type="primary"):
            if initialize_translator():
                st.success("✅ Translator initialized successfully!")
            
        st.markdown('<hr style="border-color: #4c566a; margin: 1.5rem 0;">', unsafe_allow_html=True)
        
        # Information with dark theme
        st.markdown("""
        <div class="sidebar-info-box">
            <h4>📋 How to use:</h4>
            <ol>
                <li>Click "Initialize Translator" first</li>
                <li>Upload your PDF file</li>
                <li>Click "Translate PDF"</li>
                <li>Download the translated text</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<hr style="border-color: #4c566a; margin: 1.5rem 0;">', unsafe_allow_html=True)
        
        # Features with dark theme
        st.markdown("""
        <div class="sidebar-info-box">
            <h4>✨ Features:</h4>
            <ul>
                <li>Legal terminology glossary</li>
                <li>Translation quality critique</li>
                <li>Context-aware translation</li>
                <li>Downloadable results</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload PDF")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a legal document in PDF format for translation"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Display file info
            file_size = len(uploaded_file.getvalue()) / 1024  # KB
            st.info(f"📊 File size: {file_size:.2f} KB")
            
            # Preview option
            if st.checkbox("🔍 Preview extracted text"):
                if st.session_state.translator:
                    try:
                        # Reset file pointer
                        uploaded_file.seek(0)
                        preview_text = st.session_state.translator.extract_text_from_pdf(uploaded_file)
                        st.text_area("Extracted Text Preview", preview_text[:1000] + "..." if len(preview_text) > 1000 else preview_text, height=200)
                        st.session_state.original_text = preview_text
                    except Exception as e:
                        st.error(f"Error extracting text: {str(e)}")
                else:
                    st.warning("⚠️ Please initialize the translator first")
            
            # Translation button
            if st.button("🔄 Translate PDF", type="primary", disabled=st.session_state.translator is None):
                if st.session_state.translator is None:
                    st.error("❌ Please initialize the translator first")
                else:
                    try:
                        # Reset file pointer
                        uploaded_file.seek(0)
                        
                        # Progress tracking
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        def update_progress(current, total):
                            progress = current / total
                            progress_bar.progress(progress)
                            status_text.text(f"Translating... {current}/{total} chunks processed")
                        
                        # Perform translation
                        with st.spinner("Translating document..."):
                            translation_result = st.session_state.translator.translate_pdf(
                                uploaded_file, 
                                progress_callback=update_progress
                            )
                        
                        st.session_state.translation_result = translation_result
                        progress_bar.progress(1.0)
                        status_text.text("✅ Translation completed!")
                        
                        st.success("🎉 Translation completed successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Translation failed: {str(e)}")

    with col2:
        st.header("📥 Translation Result")
        
        if st.session_state.translation_result:
            # Display translation
            st.markdown('<div class="translation-box">', unsafe_allow_html=True)
            st.subheader("Telugu Translation:")
            st.text_area(
                "Translated Text",
                st.session_state.translation_result,
                height=400,
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Download button
            st.download_button(
                label="📥 Download Translation",
                data=st.session_state.translation_result,
                file_name="translated_document.txt",
                mime="text/plain",
                type="primary"
            )
            
            # Statistics
            original_length = len(st.session_state.original_text) if st.session_state.original_text else 0
            translated_length = len(st.session_state.translation_result)
            
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("Original Length", f"{original_length:,} chars")
            with col_stat2:
                st.metric("Translated Length", f"{translated_length:,} chars")
                
        else:
            st.info("🔄 Upload a PDF and click 'Translate PDF' to see results here")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🔧 Built with Streamlit | 🤖 Powered by Google Gemini | 📚 Enhanced with Legal Glossary</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()