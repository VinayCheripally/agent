"""
Setup script for the PDF Translator application
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def download_spacy_model():
    """Download spaCy English model"""
    print("Downloading spaCy English model...")
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    except subprocess.CalledProcessError:
        print("Failed to download spaCy model. Please run manually: python -m spacy download en_core_web_sm")

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists(".env"):
        print("Creating .env file template...")
        with open(".env", "w") as f:
            f.write("# Add your environment variables here\n")
            f.write("# GOOGLE_API_KEY=your_google_api_key_here\n")
        print("Please add your Google API key to the .env file")

def main():
    """Main setup function"""
    print("Setting up PDF Translator application...")
    
    try:
        install_requirements()
        download_spacy_model()
        check_env_file()
        
        print("\n✅ Setup completed successfully!")
        print("\n🚀 To run the application:")
        print("   streamlit run app.py")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()