#!/usr/bin/env python3
"""
Setup script for Bhagavad Gita integration
This script helps configure the environment and run necessary migrations.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_env_vars():
    """Check if required environment variables are set"""
    env_file = Path(".env")
    
    print("🔍 Checking environment variables...")
    
    if not env_file.exists():
        print("❌ .env file not found. Creating one...")
        with open(".env", "w") as f:
            f.write("# Environment variables for Vulgate API\n")
            f.write("# Add your database URL here\n")
            f.write("DATABASE_URL=sqlite:///./app.db\n\n")
            f.write("# Add your OpenAI API key here\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n\n")
            f.write("# Add your RapidAPI key for Bhagavad Gita API here\n")
            f.write("RAPIDAPI_KEY=your_rapidapi_key_here\n\n")
        print("✅ Created .env file. Please edit it to add your API keys.")
        return False
    
    # Check if RAPIDAPI_KEY is set
    with open(".env", "r") as f:
        content = f.read()
        if "RAPIDAPI_KEY=your_rapidapi_key_here" in content or "RAPIDAPI_KEY=" not in content:
            print("⚠️  RAPIDAPI_KEY not configured in .env file")
            print("   Please get your RapidAPI key from: https://rapidapi.com/bhagavad-gita-bhagavad-gita-default/api/bhagavad-gita3")
            print("   And add it to your .env file: RAPIDAPI_KEY=your_actual_key_here")
            return False
    
    print("✅ Environment variables configured")
    return True


def install_dependencies():
    """Install required Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def run_migration():
    """Run the database migration"""
    print("🗄️  Running database migration...")
    try:
        # Change to the project directory
        os.chdir(Path(__file__).parent)
        
        # Run the migration
        subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], 
                      check=True, capture_output=True)
        print("✅ Database migration completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
        # Try to run the specific migration
        try:
            subprocess.run([sys.executable, "-m", "alembic", "upgrade", "add_source_to_books"], 
                          check=True, capture_output=True)
            print("✅ Specific migration completed successfully")
            return True
        except subprocess.CalledProcessError as e2:
            print(f"❌ Specific migration also failed: {e2}")
            return False


def test_api_connection():
    """Test the Bhagavad Gita API connection"""
    print("🔌 Testing Bhagavad Gita API connection...")
    
    try:
        import httpx
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv("RAPIDAPI_KEY")
        
        if not api_key or api_key == "your_rapidapi_key_here":
            print("⚠️  RapidAPI key not configured, skipping API test")
            return False
        
        # Test API connection
        import asyncio
        
        async def test_connection():
            headers = {
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": "bhagavad-gita3.p.rapidapi.com"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://bhagavad-gita3.p.rapidapi.com/v2/chapters/1/verses/1/",
                    headers=headers,
                    timeout=10.0
                )
                return response.status_code == 200
        
        if asyncio.run(test_connection()):
            print("✅ Bhagavad Gita API connection successful")
            return True
        else:
            print("❌ Bhagavad Gita API connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API connection: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up Bhagavad Gita Integration")
    print("=" * 50)
    
    success = True
    
    # Check environment variables
    if not check_env_vars():
        success = False
    
    # Install dependencies
    if not install_dependencies():
        success = False
    
    # Run migration
    if not run_migration():
        success = False
    
    # Test API connection
    test_api_connection()  # This is optional, don't fail on this
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Setup completed successfully!")
        print("\nYou can now use the following endpoints:")
        print("- Bible: /api/v1/texts/bible/Gn/1/1 (Genesis 1:1)")
        print("- Gita:  /api/v1/texts/gita/1/1 (Bhagavad Gita Chapter 1, Verse 1)")
        print("\nTo start the server:")
        print("cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("⚠️  Setup completed with some issues. Please check the errors above.")
        print("You may need to manually configure your .env file and run migrations.")
    
    return success


if __name__ == "__main__":
    main() 