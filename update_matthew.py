#!/usr/bin/env python3
"""
Script to update Matthew book information with comprehensive details
"""

import sys
import os
sys.path.append('.')
from enhanced_dictionary import EnhancedDictionary

def main():
    # Initialize dictionary
    api_key = os.getenv('OPENAI_API_KEY')
    enhanced_dict = EnhancedDictionary(openai_api_key=api_key)

    # Create comprehensive Matthew information
    matthew_updates = {
        'latin_name': 'Evangelium secundum Matthaeum',
        'author': 'Matthew the Evangelist (traditionally)',
        'date_written': '80-90 CE',
        'historical_context': 'Written for a Jewish-Christian community, likely in Antioch or Palestine. The Gospel was composed after the destruction of the Jerusalem Temple in 70 CE, during a time when early Christians were defining their relationship to Judaism.',
        'summary': 'Matthew\'s Gospel presents Jesus as the Jewish Messiah and the fulfillment of Old Testament prophecy. It emphasizes Jesus\' teachings, particularly the Sermon on the Mount, and demonstrates how Jesus fulfills the Law and the Prophets. The Gospel is structured around five major discourses and includes unique material such as the Magi, the flight to Egypt, and the Great Commission.',
        'theological_importance': 'Matthew establishes Jesus as the Son of David and Son of Abraham, emphasizing the continuity between the Old and New Covenants. Key themes include the Kingdom of Heaven, discipleship, and the church. Matthew\'s Gospel has been foundational for Christian understanding of Jesus\' ethical teachings and missionary mandate.',
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
            'The mountain as a place of divine revelation (Sermon on the Mount)',
            'The Temple as representing Jesus\' body and the new covenant'
        ],
        'language_notes': 'The Latin Vulgate preserves many Hebraisms and Aramaic terms. The phrase "Regnum caelorum" (Kingdom of Heaven) appears frequently, translating the Hebrew concept. Matthew uses "Emmanuel" (God with us) and preserves Jesus\' Aramaic words like "Eli, Eli, lema sabachthani."',
        'chapter_summaries': [
            {'chapter': '1', 'summary': 'Genealogy of Jesus from Abraham to Joseph, and the annunciation and birth of Jesus.'},
            {'chapter': '2', 'summary': 'Visit of the Magi, flight to Egypt, massacre of the innocents, and return to Nazareth.'},
            {'chapter': '3', 'summary': 'Ministry of John the Baptist and the baptism of Jesus.'},
            {'chapter': '4', 'summary': 'Temptation of Jesus in the wilderness and the beginning of his Galilean ministry.'},
            {'chapter': '5', 'summary': 'The Beatitudes and the beginning of the Sermon on the Mount.'},
            {'chapter': '6', 'summary': 'Teachings on prayer, fasting, and trust in God (including the Lord\'s Prayer).'},
            {'chapter': '7', 'summary': 'Conclusion of the Sermon on the Mount with teachings on judgment and discipleship.'},
            {'chapter': '8', 'summary': 'Healing miracles including the leper, centurion\'s servant, and calming the storm.'},
            {'chapter': '9', 'summary': 'More healings, calling of Matthew, and teachings about new wine and old wineskins.'},
            {'chapter': '10', 'summary': 'Commissioning of the twelve apostles and instructions for mission.'},
            {'chapter': '11', 'summary': 'Jesus\' response to John the Baptist and condemnation of unrepentant cities.'},
            {'chapter': '12', 'summary': 'Controversies over Sabbath observance and accusations of blasphemy.'},
            {'chapter': '13', 'summary': 'Parables of the Kingdom including the sower, wheat and tares, and hidden treasure.'},
            {'chapter': '14', 'summary': 'Death of John the Baptist, feeding of the 5000, and Jesus walking on water.'},
            {'chapter': '15', 'summary': 'Teachings on tradition versus God\'s commandments and healing of the Canaanite woman\'s daughter.'},
            {'chapter': '16', 'summary': 'Peter\'s confession of Jesus as the Messiah and the first prediction of the Passion.'},
            {'chapter': '17', 'summary': 'The Transfiguration and healing of the epileptic boy.'},
            {'chapter': '18', 'summary': 'Teachings on humility, forgiveness, and church discipline.'},
            {'chapter': '19', 'summary': 'Teachings on divorce, celibacy, and the rich young man.'},
            {'chapter': '20', 'summary': 'Parable of workers in the vineyard and third prediction of the Passion.'},
            {'chapter': '21', 'summary': 'Triumphal entry into Jerusalem, cleansing of the Temple, and cursing of the fig tree.'},
            {'chapter': '22', 'summary': 'Parables of the wedding feast and confrontations with religious leaders.'},
            {'chapter': '23', 'summary': 'Condemnation of the scribes and Pharisees ("Seven Woes").'},
            {'chapter': '24', 'summary': 'Prophecy of the destruction of Jerusalem and the Second Coming.'},
            {'chapter': '25', 'summary': 'Parables of the ten virgins, talents, and the final judgment.'},
            {'chapter': '26', 'summary': 'The Last Supper, betrayal by Judas, and arrest in Gethsemane.'},
            {'chapter': '27', 'summary': 'Trial before Pilate, crucifixion, death, and burial of Jesus.'},
            {'chapter': '28', 'summary': 'Resurrection of Jesus and the Great Commission to make disciples of all nations.'}
        ]
    }

    # Update Matthew information
    print('Updating Matthew information...')
    updated_matthew = enhanced_dict.update_book_information('Matthew', matthew_updates)
    print(f'✅ Successfully updated Matthew information!')
    print(f'📖 Book: {updated_matthew.book_name}')
    print(f'🏛️  Latin: {updated_matthew.latin_name}')
    print(f'✍️  Author: {updated_matthew.author}')
    print(f'📅 Date: {updated_matthew.date_written}')
    print(f'📚 Genre: {updated_matthew.literary_genre}')
    print(f'📊 Source: {updated_matthew.source}')
    print(f'🎯 Confidence: {updated_matthew.confidence}')
    print(f'📑 Chapters: {len(updated_matthew.chapter_summaries)}')

if __name__ == "__main__":
    main() 