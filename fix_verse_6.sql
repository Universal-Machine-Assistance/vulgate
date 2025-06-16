-- Fix Bhagavad Gita Chapter 1, Verse 6 with complete transliteration
-- Run with: sqlite3 db/vulgate.db < fix_verse_6.sql

-- Update verse 6 with complete Sanskrit, transliteration, and word meanings
UPDATE verses SET 
    text = 'Bhagavad Gita Chapter 1, Verse 6

Sanskrit:
युधामन्युश्च विक्रान्त उत्तमौजाश्च वीर्यवान्।

सौभद्रो द्रौपदेयाश्च सर्व एव महारथाः।।1.6।।

Transliteration:
yudhāmanyuśhcha vikrānta uttamaujāśhcha vīryavān
saubhadro draupadeyāśhcha sarva eva mahā-rathāḥ

Word Meanings:
yudhāmanyuḥ—Yudhamanyu; cha—and; vikrāntaḥ—courageous; uttamaujāḥ—Uttamauja; cha—and; vīrya-vān—valiant; saubhadraḥ—the son of Subhadra; draupadeyāḥ—the sons of Draupadi; cha—and; sarve—all; eva—indeed; mahā-rathāḥ—warriors who could single handedly match the strength of ten thousand ordinary warriors

English Translation:
Yudhamanyu the courageous, Uttamauja the valiant, the son of Subhadra (Abhimanyu), and the sons of Draupadi—all of them are great chariot warriors.',
    updated_at = datetime('now')
WHERE book_id = (SELECT id FROM books WHERE source = 'gita' LIMIT 1)
  AND chapter = 1 
  AND verse_number = 6;

-- Verify the update
SELECT 'Verse 6 has been updated:' as info;
SELECT 
    b.name as book,
    v.chapter,
    v.verse_number,
    substr(v.text, 1, 150) || '...' as text_preview
FROM verses v 
JOIN books b ON v.book_id = b.id 
WHERE b.source = 'gita' 
  AND v.chapter = 1 
  AND v.verse_number = 6; 