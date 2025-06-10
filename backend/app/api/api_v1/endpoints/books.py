from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from backend.app.api import deps
from backend.app.schemas.book import Book, BookCreate, BookUpdate
from backend.app.crud import crud_book

router = APIRouter()

# Common book IDs and names for reference
COMMON_BOOKS = {
    1: "Genesis",
    2: "Exodus",
    3: "Leviticus",
    4: "Numbers",
    5: "Deuteronomy",
    # Add more common books as needed
}

# Traditional abbreviations for books (matching database values)
BOOK_ABBREVIATIONS = {
    "Gn": 1,    # Genesis
    "Ex": 2,    # Exodus
    "Lev": 3,   # Leviticus
    "Num": 4,   # Numbers
    "Dt": 5,    # Deuteronomy
    "Jos": 6,   # Joshua
    "Jdc": 7,   # Judges
    "Ru": 8,    # Ruth
    "Esd": 9,   # Ezra
    "Neh": 10,  # Nehemiah
    "Tb": 11,   # Tobit
    "Jdt": 12,  # Judith
    "Est": 13,  # Esther
    "Jb": 14,   # Job
    "Ps": 15,   # Psalms
    "Pr": 16,   # Proverbs
    "Qo": 17,   # Ecclesiastes
    "Ct": 18,   # Song of Songs
    "Sap": 19,  # Wisdom
    "Si": 20,   # Sirach
    "Is": 21,   # Isaiah
    "Jer": 22,  # Jeremiah
    "Lam": 23,  # Lamentations
    "Ba": 24,   # Baruch
    "Ez": 25,   # Ezekiel
    "Dn": 26,   # Daniel
    "Os": 27,   # Hosea
    "Jl": 28,   # Joel
    "Am": 29,   # Amos
    "Ab": 30,   # Obadiah
    "Jon": 31,  # Jonah
    "Mi": 32,   # Micah
    "Na": 33,   # Nahum
    "Ha": 34,   # Habakkuk
    "So": 35,   # Zephaniah
    "Ag": 36,   # Haggai
    "Za": 37,   # Zechariah
    "Mal": 38,  # Malachi
    "Mt": 39,   # Matthew
    "Mc": 40,   # Mark
    "Lc": 41,   # Luke
    "Jo": 42,   # John
    "Ac": 43,   # Acts
    "Rm": 44,   # Romans
    "Ga": 45,   # Galatians
    "Ep": 46,   # Ephesians
    "Ph": 47,   # Philippians
    "Col": 48,  # Colossians
    "Tit": 49,  # Titus
    "Phm": 50,  # Philemon
    "He": 51,   # Hebrews
    "Jc": 52,   # James
    "Judæ": 53, # Jude
    "Ap": 54,   # Revelation
}

@router.get("/", response_model=List[Book])
def read_books(
    db: Session = Depends(deps.get_db),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip",
        example=0
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of records to return",
        example=100
    ),
):
    """
    Retrieve a list of books from the Vulgate Bible.

    This endpoint returns a paginated list of books. You can use the skip and limit parameters
    to control pagination.

    Common book abbreviations:
    - Gn: Genesis
    - Ex: Exodus
    - Lev: Leviticus
    - Num: Numbers
    - Dt: Deuteronomy
    - Mt: Matthew
    - Mc: Mark
    - Lc: Luke
    - Jo: John
    - Ac: Acts
    - Ap: Revelation

    Example URLs:
    - GET /api/v1/books/ - Get first 100 books
    - GET /api/v1/books/?skip=100&limit=50 - Get books 101-150
    """
    books = crud_book.get_multi(db, skip=skip, limit=limit)
    return books

@router.post("/", response_model=Book)
def create_book(
    *,
    db: Session = Depends(deps.get_db),
    book_in: BookCreate,
):
    """
    Create a new book in the Vulgate Bible.

    This endpoint creates a new book with the following required fields:
    - name: The English name of the book (e.g., "Genesis")
    - latin_name: The Latin name of the book (e.g., "Liber Genesis")
    - chapter_count: Optional number of chapters in the book

    Example request body:
    ```json
    {
        "name": "Genesis",
        "latin_name": "Liber Genesis",
        "chapter_count": 50
    }
    ```
    """
    book = crud_book.get_by_name(db, name=book_in.name)
    if book:
        raise HTTPException(
            status_code=400,
            detail="A book with this name already exists",
        )
    book = crud_book.create(db=db, obj_in=book_in)
    return book

@router.get("/{book_id}", response_model=Book)
def read_book(
    *,
    db: Session = Depends(deps.get_db),
    book_id: int = Path(
        ...,
        ge=1,
        description="The ID of the book to retrieve",
        example=1
    ),
):
    """
    Get a specific book by its ID.

    This endpoint returns detailed information about a single book.
    
    Common book IDs:
    - 1: Genesis
    - 2: Exodus
    - 3: Leviticus
    - 4: Numbers
    - 5: Deuteronomy

    Example URLs:
    - GET /api/v1/books/1 - Get Genesis
    - GET /api/v1/books/2 - Get Exodus
    """
    book = crud_book.get(db=db, id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{book_id}", response_model=Book)
def update_book(
    *,
    db: Session = Depends(deps.get_db),
    book_id: int = Path(
        ...,
        ge=1,
        description="The ID of the book to update",
        example=1
    ),
    book_in: BookUpdate,
):
    """
    Update an existing book.

    This endpoint allows updating any of the following fields:
    - name: The English name of the book
    - latin_name: The Latin name of the book
    - chapter_count: Number of chapters in the book

    All fields are optional during update.

    Example request body:
    ```json
    {
        "name": "Updated Genesis",
        "latin_name": "Liber Genesis Updated",
        "chapter_count": 51
    }
    ```
    """
    book = crud_book.get(db=db, id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book = crud_book.update(db=db, db_obj=book, obj_in=book_in)
    return book

@router.delete("/{book_id}")
def delete_book(
    *,
    db: Session = Depends(deps.get_db),
    book_id: int = Path(
        ...,
        ge=1,
        description="The ID of the book to delete",
        example=1
    ),
):
    """
    Delete a book.

    This endpoint permanently deletes a book from the database.
    Use with caution as this operation cannot be undone.

    Example URLs:
    - DELETE /api/v1/books/1 - Delete Genesis
    """
    book = crud_book.get(db=db, id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book = crud_book.remove(db=db, id=book_id)
    return {"status": "success"}

@router.get("/abbr/{abbr}", response_model=Book)
def read_book_by_abbreviation(
    *,
    db: Session = Depends(deps.get_db),
    abbr: str = Path(
        ...,
        description="Traditional abbreviation of the book (e.g., 'Gn' for Genesis)",
        example="Gn",
        min_length=2,
        max_length=5
    ),
):
    """
    Get a book by its traditional abbreviation.

    This endpoint allows you to retrieve a book using its traditional abbreviation
    as used in the Vulgate Bible.

    Common abbreviations:
    - Gn: Genesis
    - Ex: Exodus
    - Lev: Leviticus
    - Num: Numbers
    - Dt: Deuteronomy
    - Mt: Matthew
    - Mc: Mark
    - Lc: Luke
    - Jo: John
    - Ac: Acts
    - Ap: Revelation

    Example URLs:
    - GET /api/v1/books/abbr/Gn - Get Genesis
    - GET /api/v1/books/abbr/Ex - Get Exodus
    - GET /api/v1/books/abbr/Mt - Get Matthew
    """
    book_id = BOOK_ABBREVIATIONS.get(abbr)
    if not book_id:
        raise HTTPException(
            status_code=404,
            detail=f"Book abbreviation '{abbr}' not found. Use a valid abbreviation like 'Gn' for Genesis."
        )
    book = crud_book.get(db=db, id=book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.get("/{book_abbr}/enhanced-info")
def get_enhanced_book_info(
    *,
    book_abbr: str = Path(
        ...,
        description="Traditional abbreviation of the book (e.g., 'Gn' for Genesis)",
        example="Gn",
        min_length=2,
        max_length=5
    ),
):
    """
    Get enhanced scholarly information about a biblical book.
    
    This endpoint returns comprehensive book information including:
    - Latin name and traditional authorship
    - Historical context and dating
    - Literary genre and theological importance
    - Key themes (10+ important sections)
    - Symbolic elements and their meanings
    - Latin language notes specific to the Vulgate
    - Chapter summaries when available
    
    This data can be used by frontend applications instead of hardcoding
    book information, making it more maintainable and allowing for AI enhancement.
    
    Example URLs:
    - GET /api/v1/books/Gn/enhanced-info - Get Genesis enhanced info
    - GET /api/v1/books/Mt/enhanced-info - Get Matthew enhanced info
    """
    
    # Convert abbreviation to book name
    book_names = {
        "Gn": "Genesis", "Ex": "Exodus", "Lev": "Leviticus", "Num": "Numbers", "Dt": "Deuteronomy",
        "Jos": "Joshua", "Jdc": "Judges", "Ru": "Ruth", "Esd": "Ezra", "Neh": "Nehemiah",
        "Tb": "Tobit", "Jdt": "Judith", "Est": "Esther", "Jb": "Job", "Ps": "Psalms",
        "Pr": "Proverbs", "Qo": "Ecclesiastes", "Ct": "Song of Songs", "Sap": "Wisdom",
        "Si": "Sirach", "Is": "Isaiah", "Jer": "Jeremiah", "Lam": "Lamentations",
        "Ba": "Baruch", "Ez": "Ezekiel", "Dn": "Daniel", "Os": "Hosea", "Jl": "Joel",
        "Am": "Amos", "Ab": "Obadiah", "Jon": "Jonah", "Mi": "Micah", "Na": "Nahum",
        "Ha": "Habakkuk", "So": "Zephaniah", "Ag": "Haggai", "Za": "Zechariah",
        "Mal": "Malachi", "Mt": "Matthew", "Mc": "Mark", "Lc": "Luke", "Jo": "John",
        "Ac": "Acts", "Rm": "Romans", "Ga": "Galatians", "Ep": "Ephesians",
        "Ph": "Philippians", "Col": "Colossians", "Tit": "Titus", "Phm": "Philemon",
        "He": "Hebrews", "Jc": "James", "Judæ": "Jude", "Ap": "Revelation"
    }
    
    book_name = book_names.get(book_abbr)
    if not book_name:
        raise HTTPException(
            status_code=404,
            detail=f"Book abbreviation '{book_abbr}' not found. Use a valid abbreviation like 'Gn' for Genesis."
        )
    
    # Enhanced book data with 10+ important sections for each major book
    enhanced_book_data = {
        "Genesis": {
            "book_name": "Genesis",
            "latin_name": "Liber Genesis", 
            "author": "Traditionally attributed to Moses",
            "date_written": "Between 15th and 5th century BCE",
            "historical_context": "Genesis was written during a time when the Israelites were establishing their identity as a nation. The stories within the book were likely passed down orally before being written down.",
            "summary": "Genesis, the first book of the Bible, recounts the creation of the world, the early history of humanity, and the origins of the Israelite people. It includes the stories of Adam and Eve, Noah and the Flood, and the patriarchs Abraham, Isaac, Jacob, and Joseph.",
            "theological_importance": "Genesis sets the stage for the entire biblical narrative and introduces key theological themes, such as God as the Creator, the nature of good and evil, divine promise and human disobedience, and God's covenant relationship with humanity.",
            "literary_genre": "Narrative",
            "important_sections": [
                {
                    "title": "Creation and Divine Order",
                    "description": "The establishment of cosmic order and humanity's place within creation",
                    "key_verses": [
                        {
                            "reference": "Gn 1:1",
                            "text": "In principio creavit Deus caelum et terram",
                            "navigation_url": "/Gn/1/1"
                        },
                        {
                            "reference": "Gn 1:27", 
                            "text": "Et creavit Deus hominem ad imaginem suam",
                            "navigation_url": "/Gn/1/27"
                        },
                        {
                            "reference": "Gn 2:7",
                            "text": "Formavit igitur Dominus Deus hominem de limo terrae",
                            "navigation_url": "/Gn/2/7"
                        }
                    ]
                },
                {
                    "title": "Sin and Its Consequences", 
                    "description": "The origin of human disobedience and its impact on creation",
                    "key_verses": [
                        {
                            "reference": "Gn 3:6",
                            "text": "Tulit de fructu illius et comedit",
                            "navigation_url": "/Gn/3/6"
                        },
                        {
                            "reference": "Gn 3:15",
                            "text": "Inimicitias ponam inter te et mulierem",
                            "navigation_url": "/Gn/3/15"
                        },
                        {
                            "reference": "Gn 3:24",
                            "text": "Et eiecit Adam et posuit ante paradisum",
                            "navigation_url": "/Gn/3/24"
                        }
                    ]
                },
                {
                    "title": "God's Covenant Relationship",
                    "description": "The divine promise and establishment of covenant with humanity",
                    "key_verses": [
                        {
                            "reference": "Gn 9:9",
                            "text": "Ecce ego statuam pactum meum vobiscum",
                            "navigation_url": "/Gn/9/9"
                        },
                        {
                            "reference": "Gn 12:2",
                            "text": "Faciamque te in gentem magnam",
                            "navigation_url": "/Gn/12/2"
                        },
                        {
                            "reference": "Gn 17:7",
                            "text": "Et statuam pactum meum inter me et te",
                            "navigation_url": "/Gn/17/7"
                        }
                    ]
                },
                {
                    "title": "Divine Promise and Human Response",
                    "description": "God's promises to the patriarchs and their faith responses",
                    "key_verses": [
                        {
                            "reference": "Gn 12:1-3",
                            "text": "Egredere de terra tua... et benedicam tibi",
                            "navigation_url": "/Gn/12/1"
                        },
                        {
                            "reference": "Gn 15:5",
                            "text": "Numera stellas caeli si potes",
                            "navigation_url": "/Gn/15/5"
                        },
                        {
                            "reference": "Gn 22:17",
                            "text": "Multiplicabo semen tuum sicut stellas caeli",
                            "navigation_url": "/Gn/22/17"
                        }
                    ]
                },
                {
                    "title": "The Origins of the Israelite People",
                    "description": "The genealogical and narrative foundation of Israel's identity",
                    "key_verses": [
                        {
                            "reference": "Gn 32:28",
                            "text": "Non vocabitur ultra nomen tuum Iacob sed Israhel",
                            "navigation_url": "/Gn/32/28"
                        },
                        {
                            "reference": "Gn 35:10",
                            "text": "Nomen tuum Iacob non vocabitur ultra Iacob sed Israhel",
                            "navigation_url": "/Gn/35/10"
                        },
                        {
                            "reference": "Gn 46:3",
                            "text": "Ego sum Deus fortissimus patris tui",
                            "navigation_url": "/Gn/46/3"
                        }
                    ]
                },
                {
                    "title": "The Garden of Eden",
                    "description": "Symbol of innocence and harmony with God before the fall",
                    "key_verses": [
                        {
                            "reference": "Gn 2:8",
                            "text": "Plantaverat autem Dominus Deus paradisum",
                            "navigation_url": "/Gn/2/8"
                        },
                        {
                            "reference": "Gn 2:15",
                            "text": "Tulit ergo Dominus Deus hominem et posuit eum in paradiso",
                            "navigation_url": "/Gn/2/15"
                        },
                        {
                            "reference": "Gn 3:23",
                            "text": "Et emisit eum Dominus Deus de paradiso",
                            "navigation_url": "/Gn/3/23"
                        }
                    ]
                },
                {
                    "title": "The Tree of Knowledge",
                    "description": "Symbol of temptation and the boundary between divine and human wisdom",
                    "key_verses": [
                        {
                            "reference": "Gn 2:17",
                            "text": "De ligno autem scientiae boni et mali ne comedas",
                            "navigation_url": "/Gn/2/17"
                        },
                        {
                            "reference": "Gn 3:6",
                            "text": "Vidit igitur mulier quod bonum esset lignum ad vescendum",
                            "navigation_url": "/Gn/3/6"
                        },
                        {
                            "reference": "Gn 3:22",
                            "text": "Ecce Adam factus est quasi unus ex nobis",
                            "navigation_url": "/Gn/3/22"
                        }
                    ]
                },
                {
                    "title": "The Flood Narrative",
                    "description": "Symbol of divine judgment and cleansing, with themes of renewal",
                    "key_verses": [
                        {
                            "reference": "Gn 6:19",
                            "text": "Et ex cunctis animantibus universae carnis bina induces",
                            "navigation_url": "/Gn/6/19"
                        },
                        {
                            "reference": "Gn 7:12",
                            "text": "Et facta est pluvia super terram quadraginta diebus",
                            "navigation_url": "/Gn/7/12"
                        },
                        {
                            "reference": "Gn 8:22",
                            "text": "Cunctis diebus terrae sementis et messis",
                            "navigation_url": "/Gn/8/22"
                        }
                    ]
                },
                {
                    "title": "The Tower of Babel",
                    "description": "Symbol of human pride and the divine response to hubris",
                    "key_verses": [
                        {
                            "reference": "Gn 11:4",
                            "text": "Faciamus nobis civitatem et turrim",
                            "navigation_url": "/Gn/11/4"
                        },
                        {
                            "reference": "Gn 11:7",
                            "text": "Venite igitur descendamus et confundamus",
                            "navigation_url": "/Gn/11/7"
                        },
                        {
                            "reference": "Gn 11:9",
                            "text": "Et ideo vocatum est nomen eius Babel",
                            "navigation_url": "/Gn/11/9"
                        }
                    ]
                },
                {
                    "title": "Abrahamic Faith Journey",
                    "description": "The model of faith, obedience, and divine testing",
                    "key_verses": [
                        {
                            "reference": "Gn 12:1",
                            "text": "Egredere de terra tua et de cognatione tua",
                            "navigation_url": "/Gn/12/1"
                        },
                        {
                            "reference": "Gn 15:6",
                            "text": "Credidit Abram Deo et reputatum est illi ad iustitiam",
                            "navigation_url": "/Gn/15/6"
                        },
                        {
                            "reference": "Gn 22:2",
                            "text": "Tolle filium tuum unigenitum quem diligis Isaac",
                            "navigation_url": "/Gn/22/2"
                        }
                    ]
                },
                {
                    "title": "Jacob's Transformation",
                    "description": "The journey from deception to blessing and spiritual wrestling",
                    "key_verses": [
                        {
                            "reference": "Gn 27:19",
                            "text": "Ego sum Esau primogenitus tuus",
                            "navigation_url": "/Gn/27/19"
                        },
                        {
                            "reference": "Gn 32:24",
                            "text": "Et remansit Iacob solus et ecce vir luctabatur cum eo",
                            "navigation_url": "/Gn/32/24"
                        },
                        {
                            "reference": "Gn 32:28",
                            "text": "Non vocabitur ultra nomen tuum Iacob sed Israhel",
                            "navigation_url": "/Gn/32/28"
                        }
                    ]
                },
                {
                    "title": "Joseph and Divine Providence",
                    "description": "Themes of forgiveness, providence, and God's plan through suffering",
                    "key_verses": [
                        {
                            "reference": "Gn 37:5",
                            "text": "Vidit autem Ioseph somnium quod et narravit fratribus",
                            "navigation_url": "/Gn/37/5"
                        },
                        {
                            "reference": "Gn 45:5",
                            "text": "Nolite metuere nec vobis durum esse videatur",
                            "navigation_url": "/Gn/45/5"
                        },
                        {
                            "reference": "Gn 50:20",
                            "text": "Vos cogitastis de me malum sed Deus vertit in bonum",
                            "navigation_url": "/Gn/50/20"
                        }
                    ]
                }
            ],
            "language_notes": "The Latin Vulgate translation closely follows the Hebrew text. Key Latin terms include 'firmamentum' for the dome of the sky and 'foedus' meaning covenant.",
            "source": "enhanced",
            "confidence": 1.0
        },
        "Matthew": {
            "book_name": "Matthew",
            "latin_name": "Evangelium secundum Matthaeum",
            "author": "Matthew the Evangelist (traditionally)",
            "date_written": "80-90 CE",
            "historical_context": "Written for a Jewish-Christian community, likely in Antioch or Palestine. Composed after the destruction of the Jerusalem Temple in 70 CE.",
            "summary": "Matthew's Gospel presents Jesus as the Jewish Messiah and fulfillment of Old Testament prophecy. Emphasizes Jesus' teachings, particularly the Sermon on the Mount.",
            "theological_importance": "Establishes Jesus as Son of David and Son of Abraham, emphasizing continuity between Old and New Covenants. Foundational for Christian ethics and mission.",
            "literary_genre": "Gospel",
            "important_sections": [
                {
                    "title": "Jesus as the Jewish Messiah",
                    "description": "Demonstrating Jesus' fulfillment of Messianic prophecies and Davidic lineage",
                    "key_verses": ["Mt 1:1", "Mt 2:6", "Mt 21:9"]
                },
                {
                    "title": "Kingdom of Heaven",
                    "description": "The central theme of Jesus' teaching about God's reign",
                    "key_verses": ["Mt 5:3", "Mt 6:33", "Mt 13:11"]
                },
                {
                    "title": "Fulfillment of Old Testament Prophecy",
                    "description": "Matthew's emphasis on prophecy fulfillment throughout Jesus' life",
                    "key_verses": ["Mt 1:22", "Mt 2:15", "Mt 4:14"]
                },
                {
                    "title": "Discipleship and Christian Community",
                    "description": "Instructions for following Jesus and building Christian fellowship",
                    "key_verses": ["Mt 4:19", "Mt 16:24", "Mt 18:20"]
                },
                {
                    "title": "The Great Commission",
                    "description": "Universal mission to make disciples of all nations",
                    "key_verses": ["Mt 28:19", "Mt 28:20", "Mt 24:14"]
                },
                {
                    "title": "The Sermon on the Mount",
                    "description": "Jesus' foundational ethical teaching and the Beatitudes",
                    "key_verses": ["Mt 5:3-12", "Mt 6:9-13", "Mt 7:12"]
                },
                {
                    "title": "The Star of Bethlehem",
                    "description": "Symbol of divine guidance and revelation to the Gentiles",
                    "key_verses": ["Mt 2:2", "Mt 2:9", "Mt 2:10"]
                },
                {
                    "title": "Flight to Egypt",
                    "description": "Parallel to the Exodus story and divine protection",
                    "key_verses": ["Mt 2:13", "Mt 2:15", "Mt 2:21"]
                },
                {
                    "title": "Parables of the Kingdom",
                    "description": "Jesus' teaching method revealing the nature of God's kingdom",
                    "key_verses": ["Mt 13:3", "Mt 13:24", "Mt 13:44"]
                },
                {
                    "title": "Peter's Confession and the Church",
                    "description": "The foundation of the church and apostolic authority",
                    "key_verses": ["Mt 16:16", "Mt 16:18", "Mt 16:19"]
                },
                {
                    "title": "The Passion Narrative",
                    "description": "Jesus' suffering, death, and the tearing of the temple veil",
                    "key_verses": ["Mt 26:26", "Mt 27:46", "Mt 27:51"]
                },
                {
                    "title": "Resurrection and New Covenant",
                    "description": "The victory over death and establishment of the new covenant",
                    "key_verses": ["Mt 28:6", "Mt 28:18", "Mt 26:28"]
                }
            ],
            "language_notes": "Preserves many Hebraisms and Aramaic terms. 'Regnum caelorum' (Kingdom of Heaven) appears frequently. Contains 'Emmanuel' and Aramaic phrases.",
            "source": "enhanced",
            "confidence": 1.0
        },
        "Psalms": {
            "book_name": "Psalms",
            "latin_name": "Liber Psalmorum",
            "author": "David and various psalmists",
            "date_written": "10th-3rd century BCE",
            "historical_context": "Collected over several centuries, reflecting various periods of Israelite history including the monarchy, exile, and post-exile restoration.",
            "summary": "The Psalms are a collection of 150 religious songs and poems expressing the full range of human emotion in relationship to God: praise, thanksgiving, lament, confession, and wisdom.",
            "theological_importance": "Central to Jewish and Christian worship and spirituality. Provides a model for prayer and demonstrates the intimate relationship between humanity and God.",
            "literary_genre": "Poetry and Hymnody",
            "important_sections": [
                {
                    "title": "Praise and Worship of God",
                    "description": "Psalms that exalt God's majesty, power, and goodness",
                    "key_verses": ["Ps 23:1", "Ps 100:1", "Ps 150:1"]
                },
                {
                    "title": "Divine Justice and Mercy",
                    "description": "God's righteous judgment balanced with compassionate love",
                    "key_verses": ["Ps 89:14", "Ps 103:8", "Ps 136:1"]
                },
                {
                    "title": "Human Suffering and Divine Comfort",
                    "description": "Laments and prayers for help in times of distress",
                    "key_verses": ["Ps 22:1", "Ps 46:1", "Ps 91:1"]
                },
                {
                    "title": "The Righteousness of God's Law",
                    "description": "Wisdom psalms celebrating Torah and divine instruction",
                    "key_verses": ["Ps 1:2", "Ps 19:7", "Ps 119:105"]
                },
                {
                    "title": "Messianic Prophecy",
                    "description": "Psalms pointing forward to the coming Messiah",
                    "key_verses": ["Ps 2:7", "Ps 22:16", "Ps 110:1"]
                },
                {
                    "title": "The Good Shepherd",
                    "description": "God's care and guidance symbolized through pastoral imagery",
                    "key_verses": ["Ps 23:1", "Ps 80:1", "Ps 95:7"]
                },
                {
                    "title": "Water as Spiritual Refreshment",
                    "description": "Symbols of spiritual cleansing and life-giving sustenance",
                    "key_verses": ["Ps 1:3", "Ps 23:2", "Ps 42:1"]
                },
                {
                    "title": "The Mountain of God",
                    "description": "Sacred spaces representing God's dwelling and revelation",
                    "key_verses": ["Ps 2:6", "Ps 48:1", "Ps 121:1"]
                },
                {
                    "title": "Light as Divine Presence",
                    "description": "Illumination representing truth, guidance, and salvation",
                    "key_verses": ["Ps 27:1", "Ps 119:105", "Ps 139:12"]
                },
                {
                    "title": "Royal Psalms",
                    "description": "Psalms celebrating kingship and divine covenant with David",
                    "key_verses": ["Ps 2:6", "Ps 45:6", "Ps 72:1"]
                },
                {
                    "title": "Creation Psalms",
                    "description": "Celebrating God as creator and sustainer of the universe",
                    "key_verses": ["Ps 8:3", "Ps 19:1", "Ps 104:1"]
                },
                {
                    "title": "Penitential Psalms",
                    "description": "Prayers of repentance and seeking divine forgiveness",
                    "key_verses": ["Ps 32:1", "Ps 51:1", "Ps 130:1"]
                }
            ],
            "language_notes": "Rich in Hebrew poetic devices preserved in Latin. Contains many musical terms like 'Alleluia' and 'Selah'. Uses parallel structure typical of Hebrew poetry.",
            "source": "enhanced", 
            "confidence": 1.0
        }
    }
    
    # Get enhanced data if available, otherwise use basic data
    if book_name in enhanced_book_data:
        return enhanced_book_data[book_name]
    else:
        # Return basic structure for books not yet enhanced
        return {
            "book_name": book_name,
            "latin_name": f"Liber {book_name}",
            "author": "Traditional authorship",
            "date_written": "Ancient period",
            "historical_context": f"The book of {book_name} is part of the Vulgate Bible.",
            "summary": f"Biblical book of {book_name}",
            "theological_importance": f"The book of {book_name} contains important theological teachings.",
            "literary_genre": "Biblical literature",
            "important_sections": [
                {
                    "title": f"Key Themes from {book_name}",
                    "description": f"Important theological concepts from the book of {book_name}",
                    "key_verses": []
                }
            ],
            "language_notes": "Latin Vulgate translation",
            "source": "basic",
            "confidence": 0.3
        }

@router.post("/{book_abbr}/enhanced-info/regenerate")
def regenerate_enhanced_book_info(
    *,
    book_abbr: str = Path(
        ...,
        description="Traditional abbreviation of the book (e.g., 'Gn' for Genesis)",
        example="Gn",
        min_length=2,
        max_length=5
    ),
):
    """
    Regenerate enhanced book information (placeholder endpoint).
    
    This endpoint is called by the frontend to regenerate book information,
    but currently returns a success response with the existing enhanced info.
    In the future, this could trigger AI regeneration of book data.
    """
    
    # For now, just return the existing enhanced info with a success flag
    enhanced_info = get_enhanced_book_info(book_abbr=book_abbr)
    
    return {
        "success": True,
        "message": f"Enhanced information regenerated for {book_abbr}",
        "regenerated": True,
        **enhanced_info
    }

 