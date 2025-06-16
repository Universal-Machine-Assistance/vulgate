/**
 * Example integration showing how to fix translation API calls
 * with proper source language detection using VerseBridge
 */

// Make sure VerseBridge is loaded first
if (typeof window.verseBridge === 'undefined') {
    console.error('❌ VerseBridge not loaded. Please include VerseBridge.js first.');
}

/**
 * Fixed translation function that properly detects source language
 */
async function translateVerseFixed(verseText, reference, targetLanguage = 'es') {
    try {
        // Use VerseBridge to prepare the request with proper source language
        const requestPayload = window.verseBridge.prepareTranslationRequest(
            verseText, 
            reference, 
            targetLanguage
        );

        console.log('📤 Sending translation request:', requestPayload);

        const response = await fetch('/api/v1/dictionary/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestPayload)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Translation failed: ${response.status} - ${errorText}`);
        }

        const result = await response.json();
        console.log('📥 Translation successful:', result);
        return result;

    } catch (error) {
        console.error('❌ Translation error:', error);
        throw error;
    }
}

/**
 * Fixed OpenAI analysis function with proper source language
 */
async function analyzeVerseFixed(verseText, reference, analysisLanguage = 'en') {
    try {
        // Use VerseBridge to prepare the request
        const requestPayload = window.verseBridge.prepareAnalysisRequest(
            verseText,
            reference,
            analysisLanguage
        );

        console.log('📤 Sending analysis request:', requestPayload);

        const response = await fetch('/api/v1/dictionary/analyze/verse/openai', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestPayload)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Analysis failed: ${response.status} - ${errorText}`);
        }

        const result = await response.json();
        console.log('📥 Analysis successful:', result);
        return result;

    } catch (error) {
        console.error('❌ Analysis error:', error);
        throw error;
    }
}

/**
 * Example usage and testing
 */
function testTranslationFixes() {
    console.log('🧪 Testing translation fixes...');

    // Test cases
    const testCases = [
        {
            text: "Vocavītque Deus firmamēntum, Cælum: et factum est vēspere et mane, dies secūndus.",
            reference: "Gn 1:8",
            expectedSource: "latin"
        },
        {
            text: "dhṛtarāṣṭra uvācha dharma-kṣetre kuru-kṣetre samavetā yuyutsavaḥ",
            reference: "a 1:1", 
            expectedSource: "sanskrit"
        }
    ];

    testCases.forEach(async (testCase, index) => {
        console.log(`\n🔍 Test ${index + 1}: ${testCase.reference}`);
        
        // Test source detection
        const sourceInfo = window.verseBridge.detectTextSource(testCase.reference, testCase.text);
        console.log(`   Detected source: ${sourceInfo.source} (${sourceInfo.language})`);
        console.log(`   Expected: ${testCase.expectedSource}`);
        
        if (sourceInfo.language === testCase.expectedSource) {
            console.log('   ✅ Source detection correct');
        } else {
            console.log('   ❌ Source detection incorrect');
        }

        // Test translation request preparation
        try {
            const translationPayload = window.verseBridge.prepareTranslationRequest(
                testCase.text,
                testCase.reference,
                'es'  // Spanish target
            );
            console.log('   ✅ Translation payload prepared correctly');
        } catch (error) {
            console.log('   ❌ Translation payload preparation failed:', error.message);
        }
    });
}

/**
 * Integration instructions for existing code
 */
function showIntegrationInstructions() {
    console.log(`
🛠️  INTEGRATION INSTRUCTIONS:

1. Include VerseBridge.js in your HTML:
   <script src="/static/js/VerseBridge.js"></script>

2. Replace your existing translation calls with:

   // OLD (problematic):
   fetch('/api/v1/dictionary/translate', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({
           verse: verseText,
           language: 'es'
       })
   });

   // NEW (fixed):
   const payload = window.verseBridge.prepareTranslationRequest(verseText, reference, 'es');
   fetch('/api/v1/dictionary/translate', {
       method: 'POST', 
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify(payload)
   });

3. Replace your existing analysis calls with:

   // OLD (problematic):
   fetch('/api/v1/dictionary/analyze/verse/openai', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'},
       body: JSON.stringify({
           verse: verseText,
           reference: reference
       })
   });

   // NEW (fixed):
   const payload = window.verseBridge.prepareAnalysisRequest(verseText, reference, 'en');
   fetch('/api/v1/dictionary/analyze/verse/openai', {
       method: 'POST',
       headers: {'Content-Type': 'application/json'}, 
       body: JSON.stringify(payload)
   });

4. The VerseBridge automatically:
   ✅ Detects source language (Latin vs Sanskrit)
   ✅ Validates required parameters
   ✅ Adds proper source_language field
   ✅ Logs requests for debugging
   ✅ Throws errors for invalid input

This will fix the 400 Bad Request errors you're seeing!
    `);
}

// Run tests when this file is loaded
if (typeof window !== 'undefined') {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                testTranslationFixes();
                showIntegrationInstructions();
            }, 1000);
        });
    } else {
        setTimeout(() => {
            testTranslationFixes();
            showIntegrationInstructions();
        }, 1000);
    }
}

// Export functions for use in your app
window.translateVerseFixed = translateVerseFixed;
window.analyzeVerseFixed = analyzeVerseFixed; 