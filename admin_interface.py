#!/usr/bin/env python3
"""
Admin Interface for Enhanced Dictionary Database Management

This provides a command-line interface for:
- Content management (books, words, verses)
- Version history and audit trails
- User management
- AI usage monitoring
- Bulk operations
"""

import os
import sys
import json
from typing import Dict, Any
from enhanced_dictionary import EnhancedDictionary, BookInfo, WordInfo

class AdminInterface:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        self.dictionary = EnhancedDictionary(openai_api_key=api_key)
        self.current_user = None
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authenticate admin user"""
        user_info = self.dictionary.authenticate_user(username, password)
        if user_info:
            self.current_user = user_info
            print(f"✅ Authenticated as {username} ({user_info['role']})")
            return True
        else:
            print("❌ Authentication failed")
            return False
    
    def show_menu(self):
        """Show main admin menu"""
        print("\n" + "="*60)
        print("📊 ENHANCED DICTIONARY ADMIN INTERFACE")
        print("="*60)
        
        if not self.current_user:
            print("1. Login")
            print("2. Create Admin User")
            print("3. Exit")
        else:
            print(f"👤 Logged in as: {self.current_user['username']} ({self.current_user['role']})")
            print("\n📚 CONTENT MANAGEMENT:")
            print("1. View Content Overview")
            print("2. Manage Books")
            print("3. Manage Words")
            print("4. Manage Verse Analyses")
            
            print("\n📜 VERSION HISTORY:")
            print("5. View Content History")
            print("6. Restore Previous Version")
            
            print("\n🤖 AI MANAGEMENT:")
            print("7. View AI Usage Stats")
            print("8. Bulk Regenerate Content")
            
            print("\n👥 USER MANAGEMENT:")
            if self.current_user['role'] == 'admin':
                print("9. Create New User")
                print("10. Manage Settings")
            
            print("\n11. Logout")
            print("12. Exit")
    
    def handle_content_overview(self):
        """Show content overview"""
        print("\n📊 CONTENT OVERVIEW")
        print("-" * 40)
        
        overview = self.dictionary.get_content_overview()
        
        print(f"📚 Books: {overview['books']['total']}")
        for source, count in overview['books']['by_source'].items():
            print(f"  - {source}: {count}")
        
        print(f"\n📖 Words: {overview['words']['total']}")
        for source, count in overview['words']['by_source'].items():
            print(f"  - {source}: {count}")
        
        print(f"\n📜 Verse Analyses: {overview['verse_analyses']}")
        
        print(f"\n🕐 Version History: {overview['version_history']['total']}")
        for content_type, count in overview['version_history']['by_type'].items():
            print(f"  - {content_type}: {count}")
        
        print(f"\n🤖 AI Usage (last 7 days):")
        print(f"  - Calls: {overview['ai_usage_last_7_days']['calls']}")
        print(f"  - Est. Cost: ${overview['ai_usage_last_7_days']['estimated_cost']:.4f}")
    
    def handle_book_management(self):
        """Book management submenu"""
        while True:
            print("\n📚 BOOK MANAGEMENT")
            print("-" * 30)
            print("1. List all books")
            print("2. View book details")
            print("3. Update book information")
            print("4. Generate new book analysis")
            print("5. Clear book cache")
            print("6. Back to main menu")
            
            choice = input("\nChoose option: ").strip()
            
            if choice == "1":
                self._list_books()
            elif choice == "2":
                self._view_book_details()
            elif choice == "3":
                self._update_book()
            elif choice == "4":
                self._generate_book_analysis()
            elif choice == "5":
                self._clear_book_cache()
            elif choice == "6":
                break
    
    def _list_books(self):
        """List all books in cache"""
        import sqlite3
        conn = sqlite3.connect(self.dictionary.cache_db)
        cursor = conn.cursor()
        cursor.execute('SELECT book_name, source, confidence FROM book_cache ORDER BY book_name')
        books = cursor.fetchall()
        conn.close()
        
        print(f"\n📚 Books in cache ({len(books)}):")
        for book_name, source, confidence in books:
            print(f"  - {book_name} (source: {source}, confidence: {confidence})")
    
    def _view_book_details(self):
        """View detailed book information"""
        book_name = input("Enter book name: ").strip()
        book_info = self.dictionary.get_book_from_cache(book_name)
        
        if book_info:
            print(f"\n📖 {book_info.book_name}")
            print(f"Latin: {book_info.latin_name}")
            print(f"Author: {book_info.author}")
            print(f"Date: {book_info.date_written}")
            print(f"Genre: {book_info.literary_genre}")
            print(f"Source: {book_info.source} (confidence: {book_info.confidence})")
            print(f"\nSummary: {book_info.summary[:200]}...")
        else:
            print(f"❌ Book '{book_name}' not found in cache")
    
    def _update_book(self):
        """Update book information"""
        book_name = input("Enter book name: ").strip()
        
        updates = {}
        fields = ["latin_name", "author", "date_written", "summary", "theological_importance"]
        
        print(f"\nUpdating {book_name} (press Enter to skip field):")
        for field in fields:
            value = input(f"{field}: ").strip()
            if value:
                updates[field] = value
        
        if updates:
            change_summary = input("Change summary: ").strip()
            self.dictionary.update_book_information(
                book_name, updates, 
                user_id=self.current_user['user_id'],
                change_summary=change_summary
            )
            print(f"✅ Updated {book_name}")
        else:
            print("No updates provided")
    
    def _generate_book_analysis(self):
        """Generate new book analysis"""
        book_name = input("Enter book name: ").strip()
        print(f"🤖 Generating analysis for {book_name}...")
        
        book_info = self.dictionary.generate_book_analysis(book_name)
        if book_info:
            self.dictionary.save_book_to_cache(book_info)
            print(f"✅ Generated and saved analysis for {book_name}")
        else:
            print(f"❌ Failed to generate analysis for {book_name}")
    
    def _clear_book_cache(self):
        """Clear book from cache"""
        book_name = input("Enter book name: ").strip()
        if self.dictionary.clear_book_cache(book_name):
            print(f"✅ Cleared {book_name} from cache")
        else:
            print(f"❌ Book '{book_name}' not found")
    
    def handle_version_history(self):
        """View content version history"""
        content_type = input("Content type (book/word/verse_analysis): ").strip()
        content_key = input("Content key (name/reference): ").strip()
        
        history = self.dictionary.get_content_history(content_type, content_key)
        
        if history:
            print(f"\n📜 Version History for {content_type}: {content_key}")
            print("-" * 50)
            
            for i, version in enumerate(history, 1):
                current_mark = " (CURRENT)" if version['is_current'] else ""
                print(f"{i}. {version['created_at']}{current_mark}")
                print(f"   By: {version['created_by']}")
                print(f"   Summary: {version['change_summary']}")
                print(f"   Version ID: {version['version_id']}")
                print()
        else:
            print(f"❌ No history found for {content_type}: {content_key}")
    
    def handle_ai_stats(self):
        """Show AI usage statistics"""
        days = input("Days to analyze (default 30): ").strip()
        days = int(days) if days.isdigit() else 30
        
        stats = self.dictionary.get_ai_usage_stats(days)
        
        print(f"\n🤖 AI USAGE STATS (last {stats['period_days']} days)")
        print("-" * 50)
        print(f"Total Calls: {stats['total_calls']}")
        print(f"Total Tokens: {stats['total_tokens']:,}")
        print(f"Estimated Cost: ${stats['total_cost_estimate']:.4f}")
        print(f"Successful Calls: {stats['successful_calls']}")
        print(f"Success Rate: {(stats['successful_calls']/max(stats['total_calls'], 1)*100):.1f}%")
        
        print(f"\n📊 By Content Type:")
        for type_stat in stats['by_content_type']:
            print(f"  {type_stat['type']}: {type_stat['calls']} calls, ${type_stat['cost']:.4f}")
        
        print(f"\n🤖 By Model:")
        for model_stat in stats['by_model']:
            print(f"  {model_stat['model']}: {model_stat['calls']} calls, ${model_stat['cost']:.4f}")
    
    def handle_bulk_regenerate(self):
        """Bulk regenerate content"""
        content_type = input("Content type to regenerate (book/word): ").strip()
        
        confirm = input(f"⚠️  This will regenerate ALL {content_type}s using AI. Continue? (yes/no): ").strip()
        if confirm.lower() != 'yes':
            print("Operation cancelled")
            return
        
        print(f"🤖 Starting bulk regeneration of {content_type}s...")
        results = self.dictionary.bulk_regenerate_content(
            content_type, 
            user_id=self.current_user['user_id']
        )
        
        print(f"\n✅ Bulk regeneration complete:")
        print(f"  Total items: {results['total_items']}")
        print(f"  Successful: {results['successful']}")
        print(f"  Failed: {results['failed']}")
        
        if results['errors']:
            print(f"\n❌ Errors:")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(results['errors']) > 5:
                print(f"  ... and {len(results['errors']) - 5} more")
    
    def create_admin_user(self):
        """Create new admin user"""
        print("\n👤 CREATE ADMIN USER")
        print("-" * 30)
        
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()
        role = input("Role (admin/editor/viewer): ").strip() or "viewer"
        
        try:
            user_id = self.dictionary.create_admin_user(username, email, password, role)
            print(f"✅ Created user {username} with ID: {user_id}")
        except ValueError as e:
            print(f"❌ Error: {e}")
    
    def run(self):
        """Main application loop"""
        print("🏛️  Enhanced Dictionary Admin Interface")
        print("      Gestio amplificata dictionarii")
        
        while True:
            self.show_menu()
            choice = input("\nChoose option: ").strip()
            
            if not self.current_user:
                if choice == "1":
                    username = input("Username: ").strip()
                    password = input("Password: ").strip()
                    self.authenticate(username, password)
                elif choice == "2":
                    self.create_admin_user()
                elif choice == "3":
                    print("Vale! (Farewell!)")
                    break
            else:
                if choice == "1":
                    self.handle_content_overview()
                elif choice == "2":
                    self.handle_book_management()
                elif choice == "3":
                    print("📖 Word management - Coming soon!")
                elif choice == "4":
                    print("📜 Verse analysis management - Coming soon!")
                elif choice == "5":
                    self.handle_version_history()
                elif choice == "6":
                    version_id = input("Version ID to restore: ").strip()
                    if self.dictionary.restore_content_version(version_id, self.current_user['user_id']):
                        print("✅ Version restored successfully")
                    else:
                        print("❌ Failed to restore version")
                elif choice == "7":
                    self.handle_ai_stats()
                elif choice == "8":
                    self.handle_bulk_regenerate()
                elif choice == "9" and self.current_user['role'] == 'admin':
                    self.create_admin_user()
                elif choice == "10" and self.current_user['role'] == 'admin':
                    print("⚙️  Settings management - Coming soon!")
                elif choice == "11":
                    self.current_user = None
                    print("👋 Logged out")
                elif choice == "12":
                    print("Vale! (Farewell!)")
                    break
                else:
                    print("❌ Invalid option")

if __name__ == "__main__":
    admin = AdminInterface()
    admin.run() 