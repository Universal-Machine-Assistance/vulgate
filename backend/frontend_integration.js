// Frontend Integration for Translation Word Lookup
// Replace the external dictionaryapi.dev calls with this function

async function lookupTranslationWord(word, language) {
    try {
        console.log(`🔍 Looking up ${language} word: ${word}`);
        
        const response = await fetch('/api/v1/dictionary/lookup/translation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                word: word,
                language: language
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log(`✅ Found definition for ${word}:`, result);
            
            return {
                success: true,
                word: result.word,
                language: result.language,
                definition: result.definition,
                partOfSpeech: result.partOfSpeech,
                etymology: result.etymology,
                pronunciation: result.pronunciation,
                examples: result.examples || [],
                source: result.source,
                confidence: result.confidence,
                cached: result.source.includes('cache')
            };
        } else {
            console.error(`❌ API error ${response.status}:`, await response.text());
            return {
                success: false,
                error: `API error: ${response.status}`
            };
        }
    } catch (error) {
        console.error(`❌ Request failed for ${word}:`, error);
        return {
            success: false,
            error: error.message
        };
    }
}

// Example usage to replace the failing dictionaryapi.dev calls:
/*
// OLD CODE (replace this):
const response = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/${language}/${word}`);

// NEW CODE (use this instead):
const result = await lookupTranslationWord(word, language);
if (result.success) {
    console.log('Definition:', result.definition);
    // Use result.definition, result.partOfSpeech, etc.
} else {
    console.log('No definition found:', result.error);
}
*/

// For your specific case with 'escuridão':
// const result = await lookupTranslationWord('escuridão', 'pt');

export { lookupTranslationWord }; 