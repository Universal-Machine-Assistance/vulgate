import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

// TypeScript interfaces
interface KeyVerse {
  reference: string;
  text: string;
  navigation_url: string;
}

interface ImportantSection {
  title: string;
  description: string;
  key_verses: KeyVerse[];
}

interface BookData {
  book_name: string;
  latin_name: string;
  important_sections: ImportantSection[];
}

interface ThemeVerse {
  book: string;
  book_abbr: string;
  reference: string;
  text: string;
  navigation_url: string;
  context: string;
}

interface ThemeData {
  theme: string;
  latin_title: string;
  description: string;
  total_verses: number;
  verses: ThemeVerse[];
  success: boolean;
}

interface ImportantSectionsProps {
  bookAbbr: string;
  API_BASE_URL: string;
}

const ImportantSections: React.FC<ImportantSectionsProps> = ({ bookAbbr, API_BASE_URL }) => {
  const [bookData, setBookData] = useState<BookData | null>(null);
  const [themeData, setThemeData] = useState<ThemeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [themeLoading, setThemeLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedTheme, setSelectedTheme] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchBookData = async () => {
      try {
        setLoading(true);
        // 🔥 Updated API call to use enhanced-info endpoint
        const response = await fetch(`${API_BASE_URL}/books/${bookAbbr}/enhanced-info`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setBookData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch book data');
      } finally {
        setLoading(false);
      }
    };

    fetchBookData();
  }, [bookAbbr, API_BASE_URL]);

  // 🔥 Function to extract theme name from section title for API calls
  const extractThemeName = (title: string): string | null => {
    const themeMap: { [key: string]: string } = {
      // Family related
      'family': 'family',
      'marriage': 'family',
      'brotherhood': 'family',
      'children': 'family',
      'parents': 'family',
      
      // Faith related  
      'faith': 'faith',
      'belief': 'faith',
      'trust': 'faith',
      'abrahamic': 'faith',
      
      // Creation related
      'creation': 'creation',
      'garden': 'creation',
      'tree': 'creation',
      
      // Covenant related
      'covenant': 'covenant',
      'promise': 'covenant',
      
      // Salvation related
      'salvation': 'salvation',
      'messianic': 'salvation',
      'redemption': 'salvation',
      
      // Love related
      'love': 'love',
      'dilectio': 'love',
      'caritas': 'love',
      
      // Justice related
      'justice': 'justice',
      'righteousness': 'justice',
      
      // Wisdom related
      'wisdom': 'wisdom',
      'knowledge': 'wisdom',
      
      // Forgiveness related
      'forgiveness': 'forgiveness',
      'mercy': 'forgiveness',
      'reconciliation': 'forgiveness',
      
      // Sacrifice related
      'sacrifice': 'sacrifice',
      'offering': 'sacrifice',
      'atonement': 'sacrifice'
    };

    const titleLower = title.toLowerCase();
    for (const [key, theme] of Object.entries(themeMap)) {
      if (titleLower.includes(key)) {
        return theme;
      }
    }
    return null;
  };

  // 🔥 New function to handle theme clicks
  const handleThemeClick = async (sectionTitle: string) => {
    const themeName = extractThemeName(sectionTitle);
    if (!themeName) return;

    try {
      setThemeLoading(true);
      setSelectedTheme(themeName);
      
      const response = await fetch(`${API_BASE_URL}/themes/${themeName}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch theme data: ${response.status}`);
      }
      
      const data = await response.json();
      setThemeData(data);
    } catch (err) {
      console.error('Failed to fetch theme data:', err);
      setError('Failed to load theme data');
    } finally {
      setThemeLoading(false);
    }
  };

  // 🔥 Navigation handler for verse clicks
  const handleVerseClick = (navigationUrl: string) => {
    navigate(navigationUrl);
  };

  // 🔥 Close theme view
  const closeThemeView = () => {
    setSelectedTheme(null);
    setThemeData(null);
  };

  if (loading) return <div className="loading">Loading important sections...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!bookData) return <div className="no-data">No book data available</div>;

  // 🔥 Theme view when a theme is selected
  if (selectedTheme && themeData) {
    return (
      <div className="important-sections">
        <div className="theme-header">
          <button onClick={closeThemeView} className="back-button">
            ← Back to {bookData.latin_name}
          </button>
          <h2>Thema: {themeData.latin_title} ({themeData.theme})</h2>
          <p className="theme-description">{themeData.description}</p>
          <p className="verse-count">Total verses: {themeData.total_verses}</p>
        </div>

        <div className="theme-verses">
          <h3>Versus per Omnes Libros (Verses Across All Books):</h3>
          {themeData.verses.map((verse, index) => (
            <div key={index} className="theme-verse-item">
              <div className="verse-book-header">
                <strong>{verse.book} ({verse.book_abbr})</strong>
                <span className="verse-context"> - {verse.context}</span>
              </div>
              <div 
                className="verse-content clickable"
                onClick={() => handleVerseClick(verse.navigation_url)}
                style={{ cursor: 'pointer' }}
              >
                <div className="verse-reference">
                  <strong>{verse.reference}</strong>
                </div>
                <div className="verse-text">
                  "{verse.text}"
                </div>
                <div className="navigation-hint">
                  → Click to navigate to {verse.reference}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // 🔥 Regular book view with clickable themes
  return (
    <div className="important-sections">
      <h2>Themata Principalia - {bookData.latin_name}</h2>
      
      {bookData.important_sections?.map((section, index) => {
        const themeName = extractThemeName(section.title);
        const isThemeClickable = themeName !== null;
        
        return (
          <div key={index} className="section-card">
            <h3 
              className={`section-title ${isThemeClickable ? 'clickable-theme' : ''}`}
              onClick={() => isThemeClickable && handleThemeClick(section.title)}
              style={{ 
                cursor: isThemeClickable ? 'pointer' : 'default',
                color: isThemeClickable ? '#0066cc' : 'inherit'
              }}
              title={isThemeClickable ? `Click to see all verses about "${section.title}" across the Bible` : ''}
            >
              {section.title}
              {isThemeClickable && ' 🔗'}
            </h3>
            <p className="section-description">{section.description}</p>
            
            <div className="key-verses">
              <h4>Versus Principales:</h4>
              {section.key_verses?.map((verse, verseIndex) => (
                <div 
                  key={verseIndex} 
                  className="verse-item clickable"
                  onClick={() => handleVerseClick(verse.navigation_url)}
                  style={{ cursor: 'pointer' }}
                >
                  <div className="verse-reference">
                    <strong>{verse.reference}</strong>
                  </div>
                  <div className="verse-text">
                    "{verse.text}"
                  </div>
                  <div className="navigation-hint">
                    → Click to navigate to {verse.reference}
                  </div>
                </div>
              ))}
            </div>

            {isThemeClickable && (
              <div className="theme-link-hint">
                💡 Click the theme title above to see all related verses across the Bible
              </div>
            )}
          </div>
        );
      })}
      
      {themeLoading && (
        <div className="theme-loading">Loading theme data...</div>
      )}
    </div>
  );
};

export default ImportantSections; 