#!/usr/bin/env python3
"""
Script to update major biblical books with predefined comprehensive information
This script focuses on the most important books without requiring AI calls
"""

import sys
import os
sys.path.append('.')
from enhanced_dictionary import EnhancedDictionary

def main():
    print("📚 Updating major biblical books with predefined data...")
    print("=" * 60)
    
    # Initialize dictionary
    api_key = os.getenv('OPENAI_API_KEY')
    enhanced_dict = EnhancedDictionary(openai_api_key=api_key)
    
    # Major books with comprehensive predefined data
    major_books = {
        'Genesis': {
            'latin_name': 'Liber Genesis',
            'author': 'Traditionally attributed to Moses',
            'date_written': 'Between 15th and 5th century BCE',
            'historical_context': 'Genesis was written during a time when the Israelites were establishing their identity as a nation. The stories within the book were likely passed down orally before being written down.',
            'summary': 'Genesis, the first book of the Bible, recounts the creation of the world, the early history of humanity, and the origins of the Israelite people. It includes the stories of Adam and Eve, Noah and the Flood, and the patriarchs Abraham, Isaac, Jacob, and Joseph.',
            'theological_importance': 'Genesis sets the stage for the entire biblical narrative and introduces key theological themes, such as God as the Creator, the nature of good and evil, divine promise and human disobedience, and God\'s covenant relationship with humanity.',
            'literary_genre': 'Narrative',
            'key_themes': [
                'Creation and divine order',
                'Sin and its consequences',
                'God\'s covenant relationship with humanity',
                'Divine promise and human response',
                'The origins and identity of the Israelite people'
            ],
            'symbolism': [
                'The Garden of Eden as a symbol of innocence and harmony with God',
                'The tree of knowledge as a symbol of temptation and human disobedience',
                'The flood as a symbol of divine judgment and cleansing',
                'The Tower of Babel as a symbol of human pride and divine punishment'
            ],
            'language_notes': 'The Latin Vulgate translation closely follows the Hebrew text. Key Latin terms include "firmamentum" for the dome of the sky and "foedus" meaning covenant.'
        },
        
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
        
        'Psalms': {
            'latin_name': 'Liber Psalmorum',
            'author': 'David and various psalmists',
            'date_written': '10th-3rd century BCE',
            'historical_context': 'Collected over several centuries, reflecting various periods of Israelite history including the monarchy, exile, and post-exile restoration.',
            'summary': 'The Psalms are a collection of 150 religious songs and poems expressing the full range of human emotion in relationship to God: praise, thanksgiving, lament, confession, and wisdom.',
            'theological_importance': 'Central to Jewish and Christian worship and spirituality. Provides a model for prayer and demonstrates the intimate relationship between humanity and God.',
            'literary_genre': 'Poetry and Hymnody',
            'key_themes': [
                'Praise and worship of God',
                'Divine justice and mercy',
                'Human suffering and divine comfort',
                'The righteousness of God\'s law',
                'Messianic prophecy'
            ],
            'symbolism': [
                'The shepherd as God\'s care and guidance',
                'Water as spiritual refreshment and cleansing',
                'The mountain as God\'s dwelling place',
                'Light as divine presence and truth'
            ],
            'language_notes': 'Rich in Hebrew poetic devices preserved in Latin. Contains many musical terms like "Alleluia" and "Selah". Uses parallel structure typical of Hebrew poetry.'
        },
        
        'Isaiah': {
            'latin_name': 'Liber Isaiae Prophetae',
            'author': 'Isaiah and later disciples',
            'date_written': '8th-6th century BCE',
            'historical_context': 'Spans the Assyrian crisis, Babylonian exile, and Persian restoration. Addresses themes of judgment and hope during national crisis.',
            'summary': 'Isaiah contains prophecies of judgment against sin and idolatry, but also promises of restoration and the coming of the Messiah. Known for its sublime poetry and theological depth.',
            'theological_importance': 'Central to understanding Messianic prophecy and God\'s plan of salvation. Frequently quoted in the New Testament regarding Jesus.',
            'literary_genre': 'Prophetic Literature',
            'key_themes': [
                'God\'s holiness and justice',
                'Judgment and restoration',
                'The suffering servant',
                'Messianic prophecy',
                'Universal salvation'
            ],
            'symbolism': [
                'Fire as purification and judgment',
                'The remnant as God\'s faithful people',
                'The highway as God\'s path of return',
                'The servant as God\'s chosen one'
            ],
            'language_notes': 'Contains the famous "Ecce virgo" (Behold, a virgin) and "Puer natus est" (A child is born). Rich in prophetic and liturgical language.'
        },
        
        'Matthew': {
            'latin_name': 'Evangelium secundum Matthaeum',
            'author': 'Matthew the Evangelist (traditionally)',
            'date_written': '80-90 CE',
            'historical_context': 'Written for a Jewish-Christian community, likely in Antioch or Palestine. Composed after the destruction of the Jerusalem Temple in 70 CE.',
            'summary': 'Matthew\'s Gospel presents Jesus as the Jewish Messiah and fulfillment of Old Testament prophecy. Emphasizes Jesus\' teachings, particularly the Sermon on the Mount.',
            'theological_importance': 'Establishes Jesus as Son of David and Son of Abraham, emphasizing continuity between Old and New Covenants. Foundational for Christian ethics and mission.',
            'literary_genre': 'Gospel',
            'key_themes': [
                'Jesus as the Jewish Messiah',
                'Kingdom of Heaven',
                'Fulfillment of Old Testament prophecy',
                'Discipleship and Christian community',
                'The Great Commission and universal mission'
            ],
            'symbolism': [
                'The star of Bethlehem as divine guidance and revelation',
                'Egypt as a place of refuge and parallel to Exodus',
                'The mountain as a place of divine revelation',
                'The Temple as representing Jesus\' body and the new covenant'
            ],
            'language_notes': 'Preserves many Hebraisms and Aramaic terms. "Regnum caelorum" (Kingdom of Heaven) appears frequently. Contains "Emmanuel" and Aramaic phrases.'
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
        },
        
        'Romans': {
            'latin_name': 'Epistula ad Romanos',
            'author': 'Paul the Apostle',
            'date_written': '57-58 CE',
            'historical_context': 'Written to the Christian community in Rome, which Paul had not yet visited. Presents a systematic exposition of Christian doctrine.',
            'summary': 'Paul\'s most theological letter, presenting the gospel as God\'s power for salvation. Addresses themes of sin, justification by faith, and Christian living.',
            'theological_importance': 'Foundational for Christian doctrine, especially Protestant theology. Central to understanding justification by faith and the universality of sin and salvation.',
            'literary_genre': 'Epistle',
            'key_themes': [
                'Justification by faith',
                'The universality of sin',
                'God\'s righteousness',
                'Life in the Spirit',
                'God\'s plan for Israel and Gentiles'
            ],
            'symbolism': [
                'The olive tree as God\'s covenant people',
                'Slavery and freedom as spiritual states',
                'Death and resurrection as spiritual transformation',
                'The body as the church community'
            ],
            'language_notes': 'Contains key theological terms like "iustificatio" (justification) and "adoptio" (adoption). Rich in legal and commercial metaphors.'
        }
    }
    
    updated_count = 0
    skipped_count = 0
    
    for book_name, book_data in major_books.items():
        print(f"\n📖 Processing {book_name}...")
        
        try:
            # Check if book already exists with good data
            existing = enhanced_dict.get_book_from_cache(book_name)
            if existing and existing.source not in ['not_found', 'greb_partial']:
                print(f"   ✅ {book_name} already cached (source: {existing.source})")
                skipped_count += 1
                continue
            
            # Update with predefined data
            print(f"   📝 Updating with comprehensive data...")
            updated_book = enhanced_dict.update_book_information(book_name, book_data)
            print(f"   ✅ {book_name} updated successfully")
            updated_count += 1
            
        except Exception as e:
            print(f"   ❌ Error processing {book_name}: {e}")
    
    # Final statistics
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"📚 Major books processed: {len(major_books)}")
    print(f"✅ Successfully updated: {updated_count}")
    print(f"⏭️  Already cached: {skipped_count}")
    
    # Cache statistics
    try:
        import sqlite3
        conn = sqlite3.connect(enhanced_dict.cache_db)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM book_cache')
        book_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"\n💾 CACHE STATUS:")
        print(f"📖 Total books cached: {book_count}")
    except Exception as e:
        print(f"Error getting cache stats: {e}")
    
    print(f"\n🎉 Major books update completed!")
    print("📖 Test with: python enhanced_dictionary.py --book Genesis")

if __name__ == "__main__":
    main() 