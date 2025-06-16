-- Manual SQL commands to set up Bhagavad Gita integration
-- Run these commands in SQLite to fix schema and add Gita data

-- First, add missing columns to books table if they don't exist
ALTER TABLE books ADD COLUMN abbreviation VARCHAR(10);
ALTER TABLE books ADD COLUMN updated_at DATETIME;
ALTER TABLE books ADD COLUMN source VARCHAR(50) DEFAULT 'bible';
ALTER TABLE books ADD COLUMN source_id VARCHAR(50);

-- Add language_code column to cache tables if they exist
-- (This addresses the server startup error)
-- Note: These might fail if tables don't exist, which is fine
ALTER TABLE word_cache ADD COLUMN language_code VARCHAR(10) DEFAULT 'en';
ALTER TABLE verse_analysis_cache ADD COLUMN language_code VARCHAR(10) DEFAULT 'en';

-- Insert Bhagavad Gita book
INSERT OR REPLACE INTO books (
    id, name, latin_name, abbreviation, chapter_count, 
    source, source_id, created_at, updated_at
) VALUES (
    999, 'Bhagavad Gita', 'Bhagavad Gita', 'a', 18, 
    'gita', 'bhagavad_gita', datetime('now'), datetime('now')
);

-- Insert sample Bhagavad Gita verses
INSERT OR REPLACE INTO verses (book_id, chapter, verse_number, text, created_at) VALUES
(999, 1, 1, 'धृतराष्ट्र उवाच
dhṛtarāṣṭra uvāca
Dhritarashtra said:', datetime('now')),

(999, 1, 2, 'धर्मक्षेत्रे कुरुक्षेत्रे समवेता युयुत्सवः।
मामकाः पाण्डवाश्चैव किमकुर्वत सञ्जय॥
dharma-kṣetre kuru-kṣetre samavetā yuyutsavaḥ
māmakāḥ pāṇḍavāś caiva kim akurvata sañjaya
O Sanjaya, after my sons and the sons of Pandu assembled in the place of pilgrimage at Kurukshetra, desiring to fight, what did they do?', datetime('now')),

(999, 2, 1, 'सञ्जय उवाच
sañjaya uvāca
Sanjaya said:', datetime('now')),

(999, 2, 2, 'तं तथा कृपयाविष्टमश्रुपूर्णाकुलेक्षणम्।
विषीदन्तमिदं वाक्यमुवाच मधुसूदनः॥
taṃ tathā kṛpayāviṣṭam aśru-pūrṇākulekṣaṇam
viṣīdantam idaṃ vākyam uvāca madhusūdanaḥ
Seeing Arjuna filled with compassion, his eyes full of tears and despondent, Madhusudana spoke these words.', datetime('now')),

(999, 2, 11, 'अशोच्यानन्वशोचस्त्वं प्रज्ञावादांश्च भाषसे।
गतासूनगतासूंश्च नानुशोचन्ति पण्डिताः॥
aśocyān anvaśocas tvaṃ prajñā-vādāṃś ca bhāṣase
gatāsūn agatāsūṃś ca nānuśocanti paṇḍitāḥ
You grieve for those who are not to be grieved for, yet you speak words of wisdom. The wise grieve neither for the living nor for the dead.', datetime('now')),

(999, 2, 47, 'कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।
मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥
karmaṇy evādhikāras te mā phaleṣu kadācana
mā karma-phala-hetur bhūr mā te saṅgo ''stv akarmaṇi
You have a right to perform your prescribed duty, but not to the fruits of action. Never consider yourself the cause of the results of your activities, and never be attached to not doing your duty.', datetime('now')),

(999, 3, 1, 'अर्जुन उवाच
arjuna uvāca
Arjuna said:', datetime('now')),

(999, 3, 2, 'ज्यायसी चेत्कर्मणस्ते मता बुद्धिर्जनार्दन।
तत्किं कर्मणि घोरे मां नियोजयसि केशव॥
jyāyasī cet karmaṇas te matā buddhir janārdana
tat kiṃ karmaṇi ghore māṃ niyojayasi keśava
If You consider knowledge superior to action, O Janardana, then why do You engage me in this terrible action, O Keshava?', datetime('now')),

(999, 4, 7, 'यदा यदा हि धर्मस्य ग्लानिर्भवति भारत।
अभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम्॥
yadā yadā hi dharmasya glānir bhavati bhārata
abhyutthānam adharmasya tadātmānaṃ sṛjāmy aham
Whenever and wherever there is a decline in religious practice, O descendant of Bharata, and a predominant rise of irreligion—at that time I descend Myself.', datetime('now')),

(999, 4, 8, 'परित्राणाय साधूनां विनाशाय च दुष्कृताम्।
धर्मसंस्थापनार्थाय सम्भवामि युगे युगे॥
paritrāṇāya sādhūnāṃ vināśāya ca duṣkṛtām
dharma-saṃsthāpanārthāya sambhavāmi yuge yuge
To deliver the pious and to annihilate the miscreants, as well as to reestablish the principles of religion, I Myself appear, millennium after millennium.', datetime('now'));

-- Update existing books to have abbreviations if they don't
UPDATE books SET abbreviation = 'Gn' WHERE name LIKE '%Genesis%' AND (abbreviation IS NULL OR abbreviation = '');
UPDATE books SET abbreviation = 'Ex' WHERE name LIKE '%Exodus%' AND (abbreviation IS NULL OR abbreviation = '');
UPDATE books SET abbreviation = 'Mt' WHERE name LIKE '%Matthew%' AND (abbreviation IS NULL OR abbreviation = '');

-- Set updated_at for all books
UPDATE books SET updated_at = datetime('now') WHERE updated_at IS NULL;

-- Verify the setup
SELECT 'Books with Gita source:' as info;
SELECT id, name, abbreviation, source FROM books WHERE source = 'gita';

SELECT 'Sample Gita verses:' as info;
SELECT b.name, v.chapter, v.verse_number, substr(v.text, 1, 100) || '...' as text_preview 
FROM verses v 
JOIN books b ON v.book_id = b.id 
WHERE b.source = 'gita' 
ORDER BY v.chapter, v.verse_number 
LIMIT 5; 