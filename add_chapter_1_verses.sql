-- Add all 47 verses for Bhagavad Gita Chapter 1
-- Run this with: sqlite3 db/vulgate.db < add_chapter_1_verses.sql

-- First, let's see what we have
SELECT 'Current Gita verses in Chapter 1:' as info;
SELECT chapter, verse_number, substr(text, 1, 50) || '...' as preview 
FROM verses v 
JOIN books b ON v.book_id = b.id 
WHERE b.source = 'gita' AND v.chapter = 1 
ORDER BY v.verse_number;

-- Get the book ID for Gita
-- We'll use this in our inserts

-- Update verse 1:1 with complete text
UPDATE verses 
SET text = 'धृतराष्ट्र उवाच
धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः।
मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय॥

dhṛitarāśhtra uvācha
dharma-kṣhetre kuru-kṣhetre samavetā yuyutsavaḥ
māmakāḥ pāṇḍavāśhchaiva kimakurvata sañjaya

Dhritarashtra said:
O Sanjaya, after my sons and the sons of Pandu assembled in the place of pilgrimage at Kurukshetra, desiring to fight, what did they do?',
    updated_at = datetime('now')
WHERE book_id = (SELECT id FROM books WHERE source = 'gita' LIMIT 1)
  AND chapter = 1 
  AND verse_number = 1;

-- Add verses 3-46 as placeholders (we already have 1, 2, 47)
INSERT OR IGNORE INTO verses (book_id, chapter, verse_number, text, created_at)
SELECT 
    (SELECT id FROM books WHERE source = 'gita' LIMIT 1) as book_id,
    1 as chapter,
    3 as verse_number,
    'पश्यैतां पाण्डुपुत्राणामाचार्य महतीं चमूम्।
व्यूढां द्रुपदपुत्रेण तव शिष्येण धीमता॥

paśhyaitāṁ pāṇḍu-putrāṇām āchārya mahatīṁ chamūm
vyūḍhāṁ drupada-putreṇa tava śhiṣhyeṇa dhīmatā

Behold, O Teacher! This mighty army of the sons of Pandu, arrayed for battle by your intelligent disciple, the son of Drupada.' as text,
    datetime('now') as created_at;

-- Add placeholder verses for 4-46
INSERT OR IGNORE INTO verses (book_id, chapter, verse_number, text, created_at)
VALUES 
((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 4, 'Bhagavad Gita Chapter 1, Verse 4

[Sanskrit text to be added]
[Transliteration to be added]  
[Translation to be added]

This is verse 4 of 47 in the first chapter of the Bhagavad Gita.', datetime('now')),

((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 5, 'Bhagavad Gita Chapter 1, Verse 5

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 5 of 47 in the first chapter of the Bhagavad Gita.', datetime('now')),

((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 6, 'Bhagavad Gita Chapter 1, Verse 6

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 6 of 47 in the first chapter of the Bhagavad Gita.', datetime('now')),

((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 7, 'Bhagavad Gita Chapter 1, Verse 7

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 7 of 47 in the first chapter of the Bhagavad Gita.', datetime('now')),

((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 8, 'Bhagavad Gita Chapter 1, Verse 8

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 8 of 47 in the first chapter of the Bhagavad Gita.', datetime('now')),

((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 9, 'Bhagavad Gita Chapter 1, Verse 9

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 9 of 47 in the first chapter of the Bhagavad Gita.', datetime('now')),

((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 10, 'Bhagavad Gita Chapter 1, Verse 10

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 10 of 47 in the first chapter of the Bhagavad Gita.', datetime('now'));

-- Continue with more verses (11-20)
INSERT OR IGNORE INTO verses (book_id, chapter, verse_number, text, created_at)
VALUES 
((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 11, 'Bhagavad Gita Chapter 1, Verse 11

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 11 of 47 in the first chapter of the Bhagavad Gita.', datetime('now')),

((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 12, 'Bhagavad Gita Chapter 1, Verse 12

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 12 of 47 in the first chapter of the Bhagavad Gita.', datetime('now')),

((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 13, 'Bhagavad Gita Chapter 1, Verse 13

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 13 of 47 in the first chapter of the Bhagavad Gita.', datetime('now')),

((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 14, 'Bhagavad Gita Chapter 1, Verse 14

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 14 of 47 in the first chapter of the Bhagavad Gita.', datetime('now')),

((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 15, 'Bhagavad Gita Chapter 1, Verse 15

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 15 of 47 in the first chapter of the Bhagavad Gita.', datetime('now')),

((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 16, 'Bhagavad Gita Chapter 1, Verse 16

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 16 of 47 in the first chapter of the Bhagavad Gita.', datetime('now')),

((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 17, 'Bhagavad Gita Chapter 1, Verse 17

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 17 of 47 in the first chapter of the Bhagavad Gita.', datetime('now')),

((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 18, 'Bhagavad Gita Chapter 1, Verse 18

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 18 of 47 in the first chapter of the Bhagavad Gita.', datetime('now')),

((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 19, 'Bhagavad Gita Chapter 1, Verse 19

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 19 of 47 in the first chapter of the Bhagavad Gita.', datetime('now')),

((SELECT id FROM books WHERE source = 'gita' LIMIT 1), 1, 20, 'Bhagavad Gita Chapter 1, Verse 20

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse 20 of 47 in the first chapter of the Bhagavad Gita.', datetime('now'));

-- Continue with verses 21-47 (we'll add the rest as placeholders)
INSERT OR IGNORE INTO verses (book_id, chapter, verse_number, text, created_at)
SELECT 
    (SELECT id FROM books WHERE source = 'gita' LIMIT 1) as book_id,
    1 as chapter,
    num as verse_number,
    'Bhagavad Gita Chapter 1, Verse ' || num || '

[Sanskrit text to be added]
[Transliteration to be added]
[Translation to be added]

This is verse ' || num || ' of 47 in the first chapter of the Bhagavad Gita.' as text,
    datetime('now') as created_at
FROM (
    SELECT 21 as num UNION SELECT 22 UNION SELECT 23 UNION SELECT 24 UNION SELECT 25 UNION
    SELECT 26 UNION SELECT 27 UNION SELECT 28 UNION SELECT 29 UNION SELECT 30 UNION
    SELECT 31 UNION SELECT 32 UNION SELECT 33 UNION SELECT 34 UNION SELECT 35 UNION
    SELECT 36 UNION SELECT 37 UNION SELECT 38 UNION SELECT 39 UNION SELECT 40 UNION
    SELECT 41 UNION SELECT 42 UNION SELECT 43 UNION SELECT 44 UNION SELECT 45 UNION SELECT 46
);

-- Update verse 47 with complete text
UPDATE verses 
SET text = 'सञ्जय उवाच
एवमुक्त्वा हृषीकेशं गुडाकेशः परन्तप।
न योत्स्य इति गोविन्दमुक्त्वा तूष्णीं बभूव ह॥

sañjaya uvācha
evam uktvā hṛiṣhīkeśhaṁ guḍākeśhaḥ parantapa
na yotsya iti govindam uktvā tūṣhṇīṁ babhūva ha

Sanjaya said:
Having spoken thus to Hrishikesha, Gudakesha, the chastiser of enemies, said "I will not fight" to Govinda, and became silent.',
    updated_at = datetime('now')
WHERE book_id = (SELECT id FROM books WHERE source = 'gita' LIMIT 1)
  AND chapter = 1 
  AND verse_number = 47;

-- Show final count
SELECT 'Final count of Chapter 1 verses:' as info;
SELECT COUNT(*) as total_verses 
FROM verses v 
JOIN books b ON v.book_id = b.id 
WHERE b.source = 'gita' AND v.chapter = 1;

SELECT 'Sample verses:' as info;
SELECT verse_number, substr(text, 1, 100) || '...' as preview 
FROM verses v 
JOIN books b ON v.book_id = b.id 
WHERE b.source = 'gita' AND v.chapter = 1 
  AND verse_number IN (1, 25, 47)
ORDER BY v.verse_number; 