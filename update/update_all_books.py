#!/usr/bin/env python3
"""
Script to update all biblical books with comprehensive information
Includes predefined data for major books and AI generation for others
"""

import sys
import os
import time
sys.path.append('.')
from enhanced_dictionary import EnhancedDictionary

def main():
    print("🔄 Starting comprehensive biblical book update...")
    print("=" * 80)
    
    # Initialize dictionary
    api_key = os.getenv('OPENAI_API_KEY')
    enhanced_dict = EnhancedDictionary(openai_api_key=api_key)
    
    # Complete list of biblical books
    books_to_process = [
        'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy',
        'Joshua', 'Judges', 'Ruth', '1 Samuel', '2 Samuel',
        '1 Kings', '2 Kings', '1 Chronicles', '2 Chronicles',
        'Ezra', 'Nehemiah', 'Esther', 'Job', 'Psalms',
        'Proverbs', 'Ecclesiastes', 'Song of Songs', 'Isaiah',
        'Jeremiah', 'Lamentations', 'Ezekiel', 'Daniel',
        'Hosea', 'Joel', 'Amos', 'Obadiah', 'Jonah',
        'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai',
        'Zechariah', 'Malachi', 'Matthew', 'Mark', 'Luke',
        'John', 'Acts', 'Romans', '1 Corinthians', '2 Corinthians',
        'Galatians', 'Ephesians', 'Philippians', 'Colossians',
        '1 Thessalonians', '2 Thessalonians', '1 Timothy', '2 Timothy',
        'Titus', 'Philemon', 'Hebrews', 'James', '1 Peter',
        '2 Peter', '1 John', '2 John', '3 John', 'Jude', 'Revelation'
    ]
    
    # Predefined data for major books
    predefined_books = {
        'Exodus': {
            'latin_name': 'Liber Exodus',
            'author': 'Traditionally attributed to Moses',
            'date_written': '13th-5th century BCE',
            'historical_context': 'Written to preserve the memory of Israel\'s liberation from Egypt and the establishment of the covenant at Sinai.',
            'summary': 'Exodus tells the story of Israel\'s liberation from slavery in Egypt, the giving of the Law at Mount Sinai, and the construction of the Tabernacle.',
            'theological_importance': 'Central to Jewish and Christian understanding of God as liberator and lawgiver. Establishes the covenant relationship and moral framework.',
            'literary_genre': 'Narrative and Law',
            'key_themes': [
                'Liberation from oppression',
                'Divine revelation and law',
                'Covenant relationship',
                'God\'s presence with his people',
                'Worship and sacrifice'
            ],
            'symbolism': [
                'The burning bush as divine presence',
                'The plagues as divine power over creation',
                'The Passover lamb as protection and sacrifice',
                'Mount Sinai as place of divine revelation'
            ],
            'language_notes': 'Contains many Hebrew legal and cultic terms preserved in Latin. "Pascha" for Passover, "tabernaculum" for the dwelling place of God.'
        },
        
        'Mark': {
            'latin_name': 'Evangelium secundum Marcum',
            'author': 'John Mark (traditionally)',
            'date_written': '65-70 CE',
            'historical_context': 'Written during or shortly before the Jewish War, possibly in Rome for a Gentile Christian audience.',
            'summary': 'The shortest Gospel, emphasizing Jesus\' actions over teachings. Presents Jesus as the suffering Son of God who calls disciples to take up their cross.',
            'theological_importance': 'Emphasizes the messianic secret and the necessity of suffering. Central to understanding the passion narrative.',
            'literary_genre': 'Gospel',
            'key_themes': [
                'Jesus as the suffering Son of God',
                'The messianic secret',
                'Discipleship and following Jesus',
                'The way of the cross',
                'Faith and understanding'
            ],
            'symbolism': [
                'The torn temple veil as access to God',
                'The empty tomb as victory over death',
                'The cross as the throne of the king',
                'Blindness and sight as spiritual metaphors'
            ],
            'language_notes': 'Contains many Latin terms for Roman institutions. "Centurio" for centurion, "praetorium" for governor\'s residence.'
        },
        
        'Luke': {
            'latin_name': 'Evangelium secundum Lucam',
            'author': 'Luke the Evangelist',
            'date_written': '80-85 CE',
            'historical_context': 'Written for a Gentile Christian audience, emphasizing Jesus\' universal mission and concern for the marginalized.',
            'summary': 'Luke presents Jesus as the Savior of all people, with special attention to women, the poor, and outcasts. Emphasizes prayer, the Holy Spirit, and joy.',
            'theological_importance': 'Demonstrates the universal scope of salvation and God\'s preferential option for the poor and marginalized.',
            'literary_genre': 'Gospel',
            'key_themes': [
                'Universal salvation',
                'God\'s concern for the poor and marginalized',
                'The role of women in salvation history',
                'Prayer and the Holy Spirit',
                'Joy and celebration'
            ],
            'symbolism': [
                'The manger as humility and accessibility',
                'The journey to Jerusalem as the path of salvation',
                'The banquet as God\'s inclusive kingdom',
                'The lost sheep, coin, and son as divine mercy'
            ],
            'language_notes': 'Excellent classical Latin style. Uses medical terminology reflecting the author\'s profession. "Magnificat" and "Nunc dimittis" are famous Latin canticles.'
        },
        
        'John': {
            'latin_name': 'Evangelium secundum Ioannem',
            'author': 'John the Evangelist (traditionally)',
            'date_written': '90-100 CE',
            'historical_context': 'Written for a mature Christian community, addressing theological questions about Jesus\' divine nature.',
            'summary': 'The most theological Gospel, presenting Jesus as the eternal Word of God. Emphasizes Jesus\' divine nature and the importance of faith.',
            'theological_importance': 'Central to Christian understanding of the Incarnation and the Trinity. Emphasizes eternal life through faith in Jesus.',
            'literary_genre': 'Gospel',
            'key_themes': [
                'Jesus as the Word of God',
                'Light versus darkness',
                'Eternal life through faith',
                'The unity of Father and Son',
                'Love as the Christian commandment'
            ],
            'symbolism': [
                'Light as divine revelation and truth',
                'Water as spiritual cleansing and life',
                'Bread as spiritual nourishment',
                'The vine as the relationship between Christ and believers'
            ],
            'language_notes': 'Contains the famous "Verbum" (Word) and many "Ego sum" (I am) statements. Rich in theological terminology and mystical language.'
        }
    }
    
    total_books = len(books_to_process)
    updated_count = 0
    ai_generated_count = 0
    predefined_count = 0
    error_count = 0
    skipped_count = 0
    
    for i, book_name in enumerate(books_to_process, 1):
        print(f"\n📖 Processing {book_name} ({i}/{total_books})...")
        
        try:
            # Check if book already exists with good data
            existing = enhanced_dict.get_book_from_cache(book_name)
            if existing and existing.source not in ['not_found', 'greb_partial']:
                print(f"   ✅ {book_name} already cached (source: {existing.source})")
                skipped_count += 1
                continue
            
            if book_name in predefined_books:
                # Use predefined data
                print(f"   📝 Using predefined data for {book_name}...")
                book_data = predefined_books[book_name]
                
                updated_book = enhanced_dict.update_book_information(book_name, book_data)
                print(f"   ✅ Predefined data saved for {book_name}")
                predefined_count += 1
                updated_count += 1
                
            else:
                # Use AI generation for other books
                print(f"   🤖 Generating AI analysis for {book_name}...")
                if enhanced_dict.openai_enabled:
                    try:
                        book_info = enhanced_dict.get_book_information(book_name)
                        if book_info.source not in ['not_found', 'greb_partial']:
                            print(f"   ✅ AI analysis completed for {book_name}")
                            ai_generated_count += 1
                            updated_count += 1
                            # Rate limiting between AI calls
                            time.sleep(3)
                        else:
                            print(f"   ⚠️  AI analysis failed for {book_name}")
                            error_count += 1
                    except Exception as e:
                        print(f"   ❌ Error generating AI analysis for {book_name}: {e}")
                        error_count += 1
                        time.sleep(5)  # Longer delay on error
                else:
                    print(f"   ⚠️  OpenAI not enabled, skipping {book_name}")
                    error_count += 1
                
        except Exception as e:
            print(f"   ❌ Error processing {book_name}: {e}")
            error_count += 1
        
        # Progress indicator every 10 books
        if i % 10 == 0:
            print(f"\n📊 Progress: {i}/{total_books} books processed")
    
    # Final statistics
    print("\n" + "=" * 80)
    print("📊 FINAL STATISTICS")
    print("=" * 80)
    print(f"📚 Total books processed: {total_books}")
    print(f"✅ Successfully updated: {updated_count}")
    print(f"📝 Predefined data: {predefined_count}")
    print(f"🤖 AI generated: {ai_generated_count}")
    print(f"⏭️  Already cached: {skipped_count}")
    print(f"❌ Errors: {error_count}")
    
    # Cache statistics
    try:
        cache_stats = enhanced_dict.get_cache_stats()
        book_count = 0
        import sqlite3
        conn = sqlite3.connect(enhanced_dict.cache_db)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM book_cache')
        book_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"\n💾 CACHE STATISTICS:")
        print(f"📖 Books cached: {book_count}")
        print(f"📝 Words cached: {cache_stats.get('total_cached', 0)}")
    except Exception as e:
        print(f"Error getting cache stats: {e}")
    
    print(f"\n🎉 Book update process completed!")
    print("📖 Use 'python enhanced_dictionary.py --book <BookName>' to view any book")

if __name__ == "__main__":
    main() 