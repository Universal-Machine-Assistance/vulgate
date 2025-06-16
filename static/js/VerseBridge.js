/**
 * VerseBridge - Utility for handling different text sources and languages
 * Ensures proper source language detection for API calls
 */

class VerseBridge {
    constructor() {
        this.textSources = {
            'bible': {
                language: 'latin',
                displayName: 'Bible (Vulgate)',
                sourceCode: 'bible'
            },
            'gita': {
                language: 'sanskrit', 
                displayName: 'Bhagavad Gita',
                sourceCode: 'gita'
            }
        };
    }

    /**
     * Detect text source and language from verse reference or content
     * @param {string} reference - Verse reference like "Gn 1:1" or "a 1:1"
     * @param {string} content - Verse text content (optional)
     * @returns {Object} - {source, language, sourceCode}
     */
    detectTextSource(reference, content = "") {
        // Parse reference to determine source
        if (reference) {
            // Gita references use "a" as book abbreviation
            if (reference.startsWith('a ') || reference.includes('Bhagavad Gita')) {
                return {
                    source: 'gita',
                    language: 'sanskrit',
                    sourceCode: 'gita',
                    displayName: 'Bhagavad Gita'
                };
            }
            
            // Bible references use standard abbreviations (Gn, Ex, etc.)
            const bibleAbbreviations = ['Gn', 'Ex', 'Lv', 'Nm', 'Dt', 'Jos', 'Jdg', 'Rt', '1Sa', '2Sa', '1Ki', '2Ki', '1Ch', '2Ch', 'Ezr', 'Neh', 'Est', 'Job', 'Ps', 'Pr', 'Qo', 'Sg', 'Is', 'Jr', 'Lm', 'Ezk', 'Dn', 'Hos', 'Jl', 'Am', 'Ob', 'Jon', 'Mi', 'Na', 'Hab', 'Zep', 'Hg', 'Zec', 'Mal', 'Mt', 'Mk', 'Lk', 'Jn', 'Ac', 'Rm', '1Co', '2Co', 'Ga', 'Eph', 'Ph', 'Col', '1Th', '2Th', '1Tm', '2Tm', 'Tt', 'Phm', 'Heb', 'Jas', '1P', '2P', '1Jn', '2Jn', '3Jn', 'Jude', 'Rv'];
            
            for (const abbr of bibleAbbreviations) {
                if (reference.startsWith(abbr + ' ')) {
                    return {
                        source: 'bible',
                        language: 'latin',
                        sourceCode: 'bible',
                        displayName: 'Bible (Vulgate)'
                    };
                }
            }
        }

        // Fallback to content analysis if reference detection fails
        if (content) {
            return this.detectLanguageFromContent(content);
        }

        // Default to Bible if unsure
        return {
            source: 'bible',
            language: 'latin', 
            sourceCode: 'bible',
            displayName: 'Bible (Vulgate)'
        };
    }

    /**
     * Detect language from text content
     * @param {string} content - Text content to analyze
     * @returns {Object} - {source, language, sourceCode}
     */
    detectLanguageFromContent(content) {
        // Check for Devanagari script (Sanskrit)
        const hasDevanagari = /[\u0900-\u097F]/.test(content);
        
        // Sanskrit transliteration patterns
        const sanskritPatterns = [
            'uvācha', 'arjunaḥ', 'kṛiṣhṇa', 'bhagavān', 'dharma', 'karma', 'yoga',
            'saṅkhye', 'dhṛitarāṣhṭra', 'pāṇḍava', 'kaurava', 'kurukṣhetra',
            'ṁ', 'ḥ', 'ṛi', 'ṣh', 'ñ', 'ā', 'ī', 'ū', 'ē', 'ō'
        ];
        
        const hasSanskritMarkers = sanskritPatterns.some(pattern => content.includes(pattern));
        const diacriticalCount = (content.match(/[ṁḥṛiṣhñāīūēō]/g) || []).length;
        
        if (hasDevanagari || hasSanskritMarkers || diacriticalCount >= 3) {
            return {
                source: 'gita',
                language: 'sanskrit',
                sourceCode: 'gita',
                displayName: 'Bhagavad Gita'
            };
        }

        return {
            source: 'bible',
            language: 'latin',
            sourceCode: 'bible', 
            displayName: 'Bible (Vulgate)'
        };
    }

    /**
     * Prepare translation request payload with proper source language
     * @param {string} verseText - The text to translate
     * @param {string} reference - Verse reference
     * @param {string} targetLanguage - Target language code
     * @param {Object} options - Additional options
     * @returns {Object} - Complete request payload
     */
    prepareTranslationRequest(verseText, reference, targetLanguage = 'en', options = {}) {
        if (!verseText || !verseText.trim()) {
            throw new Error('Verse text is required for translation');
        }

        const sourceInfo = this.detectTextSource(reference, verseText);
        
        const payload = {
            verse: verseText.trim(),
            language: targetLanguage,
            reference: reference || '',
            source_language: sourceInfo.language,
            text_source: sourceInfo.sourceCode,
            ...options
        };

        console.log(`🔍 Translation request prepared:`, {
            sourceLanguage: sourceInfo.language,
            textSource: sourceInfo.sourceCode,
            targetLanguage: targetLanguage,
            reference: reference
        });

        return payload;
    }

    /**
     * Prepare OpenAI analysis request with proper source language
     * @param {string} verseText - The text to analyze
     * @param {string} reference - Verse reference  
     * @param {string} analysisLanguage - Analysis language code
     * @returns {Object} - Complete request payload
     */
    prepareAnalysisRequest(verseText, reference, analysisLanguage = 'en') {
        if (!verseText || !verseText.trim()) {
            throw new Error('Verse text is required for analysis');
        }

        const sourceInfo = this.detectTextSource(reference, verseText);
        
        const payload = {
            verse: verseText.trim(),
            reference: reference || '',
            analysis_language: analysisLanguage,
            source_language: sourceInfo.language,
            text_source: sourceInfo.sourceCode
        };

        console.log(`🔍 Analysis request prepared:`, {
            sourceLanguage: sourceInfo.language,
            textSource: sourceInfo.sourceCode,
            analysisLanguage: analysisLanguage,
            reference: reference
        });

        return payload;
    }

    /**
     * Get proper API endpoint based on text source
     * @param {string} reference - Verse reference
     * @param {string} content - Text content (optional)
     * @returns {Object} - {source, bookAbbr, endpoint}
     */
    getApiEndpoint(reference, content = "") {
        const sourceInfo = this.detectTextSource(reference, content);
        
        if (sourceInfo.source === 'gita') {
            return {
                source: 'gita',
                bookAbbr: 'a',
                baseUrl: '/api/v1/texts/gita/a',
                sourceLanguage: 'sanskrit'
            };
        } else {
            // Extract book abbreviation from Bible reference
            const match = reference.match(/^([A-Za-z0-9]+)\s+/);
            const bookAbbr = match ? match[1] : 'Gn';
            
            return {
                source: 'bible',
                bookAbbr: bookAbbr,
                baseUrl: `/api/v1/texts/bible/${bookAbbr}`,
                sourceLanguage: 'latin'
            };
        }
    }

    /**
     * Format verse reference for display
     * @param {string} reference - Raw reference
     * @param {Object} verseData - Verse data object
     * @returns {string} - Formatted reference
     */
    formatReference(reference, verseData = {}) {
        const sourceInfo = this.detectTextSource(reference);
        
        if (sourceInfo.source === 'gita') {
            return `Bhagavad Gita ${verseData.chapter || ''}:${verseData.verse_number || ''}`;
        } else {
            return reference || `${verseData.book_abbreviation || ''} ${verseData.chapter || ''}:${verseData.verse_number || ''}`;
        }
    }
}

// Global instance
window.verseBridge = new VerseBridge();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VerseBridge;
} 