/**
 * Verse Display Factory - Unified rendering for Bible and Gita verses
 * Ensures consistent display with proper word highlighting and translation boxes
 */

class VerseDisplayFactory {
    constructor() {
        this.displayComponents = new Map();
    }

    /**
     * Create a verse display component based on text type
     * @param {string} textType - 'bible' or 'gita'
     * @param {Object} verseData - The verse data to display
     * @param {Object} options - Display options
     * @returns {HTMLElement} - The rendered verse component
     */
    createVerseDisplay(textType, verseData, options = {}) {
        const componentKey = `${textType}_${verseData.reference || verseData.id}`;
        
        // Check if component already exists
        if (this.displayComponents.has(componentKey)) {
            return this.displayComponents.get(componentKey);
        }

        // Create unified verse display
        const verseElement = this.createUnifiedVerseDisplay(textType, verseData, options);
        
        // Cache the component
        this.displayComponents.set(componentKey, verseElement);
        
        return verseElement;
    }

    /**
     * Create unified verse display that works for both Bible and Gita
     */
    createUnifiedVerseDisplay(textType, verseData, options) {
        const container = document.createElement('div');
        container.className = `verse-display unified-display ${textType}-verse`;
        container.setAttribute('data-text-type', textType);
        container.setAttribute('data-reference', verseData.reference || `${verseData.book}_${verseData.chapter}_${verseData.verse}`);

        // Create verse header
        const header = this.createVerseHeader(textType, verseData);
        container.appendChild(header);

        // Create translation boxes (always 2 for consistency)
        const translationContainer = this.createTranslationContainer(textType, verseData, options);
        container.appendChild(translationContainer);

        // Add word highlighting functionality
        this.addWordHighlighting(container, textType, verseData);

        // Add navigation controls
        const controls = this.createNavigationControls(textType, verseData);
        container.appendChild(controls);

        return container;
    }

    /**
     * Create verse header with reference and metadata
     */
    createVerseHeader(textType, verseData) {
        const header = document.createElement('div');
        header.className = 'verse-header';

        const reference = document.createElement('h3');
        reference.className = 'verse-reference';
        
        if (textType === 'bible') {
            reference.textContent = `${verseData.book_name || verseData.book} ${verseData.chapter}:${verseData.verse}`;
        } else if (textType === 'gita') {
            reference.textContent = `Bhagavad Gita ${verseData.chapter}:${verseData.verse}`;
        }

        header.appendChild(reference);
        return header;
    }

    /**
     * Create translation container with consistent 2-box layout
     */
    createTranslationContainer(textType, verseData, options) {
        const container = document.createElement('div');
        container.className = 'translation-container';

        // Box 1: Original text (Sanskrit/Latin) with transliteration
        const originalBox = this.createOriginalTextBox(textType, verseData);
        container.appendChild(originalBox);

        // Box 2: Translation with word meanings
        const translationBox = this.createTranslationBox(textType, verseData);
        container.appendChild(translationBox);

        return container;
    }

    /**
     * Create original text box (Sanskrit/Latin + transliteration)
     */
    createOriginalTextBox(textType, verseData) {
        const box = document.createElement('div');
        box.className = 'original-text-box translation-box';

        // Original text
        const originalText = document.createElement('div');
        originalText.className = 'original-text clickable-words';
        
        if (textType === 'bible') {
            originalText.innerHTML = this.createClickableWords(verseData.latin_text || verseData.text, 'latin');
        } else if (textType === 'gita') {
            originalText.innerHTML = this.createClickableWords(verseData.sanskrit_text || verseData.text, 'sanskrit');
        }

        box.appendChild(originalText);

        // Transliteration (if available)
        if (verseData.transliteration) {
            const transliteration = document.createElement('div');
            transliteration.className = 'transliteration clickable-words';
            transliteration.innerHTML = this.createClickableWords(verseData.transliteration, 'transliteration');
            box.appendChild(transliteration);
        }

        return box;
    }

    /**
     * Create translation box with English translation and word meanings
     */
    createTranslationBox(textType, verseData) {
        const box = document.createElement('div');
        box.className = 'translation-text-box translation-box';

        // English translation
        const translation = document.createElement('div');
        translation.className = 'english-translation';
        translation.textContent = verseData.translation || verseData.english_text || 'Translation not available';
        box.appendChild(translation);

        // Word meanings (if available)
        if (verseData.word_meanings) {
            const wordMeanings = document.createElement('div');
            wordMeanings.className = 'word-meanings';
            wordMeanings.innerHTML = `<strong>Word meanings:</strong> ${verseData.word_meanings}`;
            box.appendChild(wordMeanings);
        }

        return box;
    }

    /**
     * Create clickable words with proper highlighting
     */
    createClickableWords(text, language) {
        if (!text) return '';

        // Split text into words while preserving punctuation
        const words = text.split(/(\s+|[.,;:!?।।्।])/);
        
        return words.map((word, index) => {
            if (word.trim() === '' || /^[.,;:!?।।्।\s]+$/.test(word)) {
                return word; // Return punctuation and spaces as-is
            }

            const cleanWord = word.replace(/[.,;:!?।।्।]/g, '').trim();
            if (cleanWord === '') return word;

            return `<span class="clickable-word" 
                          data-word="${cleanWord}" 
                          data-original="${word}"
                          data-language="${language}"
                          data-index="${index}"
                          onclick="handleWordClick(this)"
                          onmouseover="highlightWord(this)"
                          onmouseout="unhighlightWord(this)">
                        ${word}
                    </span>`;
        }).join('');
    }

    /**
     * Add word highlighting functionality
     */
    addWordHighlighting(container, textType, verseData) {
        const clickableWords = container.querySelectorAll('.clickable-word');
        
        clickableWords.forEach((wordElement, index) => {
            wordElement.addEventListener('click', (e) => {
                this.handleWordClick(e.target, textType, verseData, index);
            });

            wordElement.addEventListener('mouseover', (e) => {
                this.highlightWord(e.target);
            });

            wordElement.addEventListener('mouseout', (e) => {
                this.unhighlightWord(e.target);
            });
        });
    }

    /**
     * Handle word click events
     */
    handleWordClick(wordElement, textType, verseData, index) {
        const word = wordElement.getAttribute('data-word');
        const language = wordElement.getAttribute('data-language');
        
        console.log(`Word clicked: ${word} (${language}) in ${textType} verse`);
        
        // Highlight selected word
        this.clearWordHighlights();
        wordElement.classList.add('selected-word');
        
        // Trigger word analysis/lookup
        if (window.handleWordAnalysis) {
            window.handleWordAnalysis(word, language, textType, verseData, index);
        }
        
        // Update word navigation
        if (window.updateWordNavigation) {
            window.updateWordNavigation(index, wordElement);
        }
    }

    /**
     * Highlight word on hover
     */
    highlightWord(wordElement) {
        wordElement.classList.add('word-hover');
    }

    /**
     * Remove word highlight
     */
    unhighlightWord(wordElement) {
        wordElement.classList.remove('word-hover');
    }

    /**
     * Clear all word highlights
     */
    clearWordHighlights() {
        document.querySelectorAll('.selected-word').forEach(el => {
            el.classList.remove('selected-word');
        });
    }

    /**
     * Create navigation controls
     */
    createNavigationControls(textType, verseData) {
        const controls = document.createElement('div');
        controls.className = 'verse-navigation-controls';

        // Previous/Next verse buttons
        const prevButton = document.createElement('button');
        prevButton.className = 'nav-button prev-verse';
        prevButton.textContent = '← Previous';
        prevButton.onclick = () => this.navigateVerse(textType, verseData, -1);

        const nextButton = document.createElement('button');
        nextButton.className = 'nav-button next-verse';
        nextButton.textContent = 'Next →';
        nextButton.onclick = () => this.navigateVerse(textType, verseData, 1);

        controls.appendChild(prevButton);
        controls.appendChild(nextButton);

        return controls;
    }

    /**
     * Navigate to previous/next verse
     */
    navigateVerse(textType, verseData, direction) {
        if (window.navigateToVerse) {
            window.navigateToVerse(textType, verseData, direction);
        }
    }

    /**
     * Update existing verse display
     */
    updateVerseDisplay(textType, verseData, options = {}) {
        const componentKey = `${textType}_${verseData.reference || verseData.id}`;
        
        // Remove existing component
        if (this.displayComponents.has(componentKey)) {
            const existingElement = this.displayComponents.get(componentKey);
            if (existingElement.parentNode) {
                existingElement.parentNode.removeChild(existingElement);
            }
            this.displayComponents.delete(componentKey);
        }

        // Create new component
        return this.createVerseDisplay(textType, verseData, options);
    }

    /**
     * Clear all cached components
     */
    clearCache() {
        this.displayComponents.clear();
    }
}

// Global instance
window.verseDisplayFactory = new VerseDisplayFactory();

// Global helper functions for backward compatibility
window.handleWordClick = function(wordElement) {
    const container = wordElement.closest('.verse-display');
    const textType = container.getAttribute('data-text-type');
    const reference = container.getAttribute('data-reference');
    
    // Extract verse data from container or global state
    const verseData = window.currentVerseData || {};
    const index = parseInt(wordElement.getAttribute('data-index'));
    
    window.verseDisplayFactory.handleWordClick(wordElement, textType, verseData, index);
};

window.highlightWord = function(wordElement) {
    window.verseDisplayFactory.highlightWord(wordElement);
};

window.unhighlightWord = function(wordElement) {
    window.verseDisplayFactory.unhighlightWord(wordElement);
}; 