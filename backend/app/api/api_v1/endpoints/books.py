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
        description="Traditional abbreviation of the book (e.g., 'Gn' for Genesis, 'a' for Gita)",
        example="Gn",
        min_length=1,  # Changed from 2 to 1 to allow 'a' for Gita
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
    # Handle special case for Gita
    if abbr == "a":
        return get_gita_by_abbreviation()
    
    book_id = BOOK_ABBREVIATIONS.get(abbr)
    if not book_id:
        raise HTTPException(
            status_code=404,
            detail=f"Book abbreviation '{abbr}' not found. Use a valid abbreviation like 'Gn' for Genesis or 'a' for Gita."
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
        description="Traditional abbreviation of the book (e.g., 'Gn' for Genesis, 'a' for Gita)",
        example="Gn",
        min_length=1,  # Changed from 2 to 1 to allow 'a' for Gita
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
    
    # Handle special case for Gita
    if book_abbr == "a":
        return get_gita_enhanced_info()
    
    # Convert abbreviation to book name for Bible books
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
            detail=f"Book abbreviation '{book_abbr}' not found. Use a valid abbreviation like 'Gn' for Genesis or 'a' for Gita."
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

@router.get("/gita/chapters")
def get_gita_chapters_info():
    """
    Get comprehensive information about all Bhagavad Gita chapters.
    
    Returns detailed information for each of the 18 chapters including:
    - Sanskrit name and English translation
    - Chapter theme and significance
    - Key teachings and philosophical concepts
    - Important verses within each chapter
    
    This provides the same level of detail for Gita chapters as the Bible books.
    """
    
    gita_chapters = {
        1: {
            "chapter_number": 1,
            "sanskrit_name": "अर्जुन विषाद योग",
            "english_name": "Arjuna Visada Yoga",
            "translation": "The Yoga of Arjuna's Dejection",
            "theme": "Setting and Moral Crisis",
            "description": "The first chapter of the Bhagavad Gita - \"Arjuna Vishada Yoga\" introduces the setup, the setting, the characters and the circumstances that led to the epic battle of Mahabharata, fought between the Pandavas and the Kauravas. It outlines the reasons that led to the revelation of the Bhagavad Gita. As both armies stand ready for the battle, the mighty warrior Arjuna, on observing the warriors on both sides becomes increasingly sad and depressed due to the fear of losing his relatives and friends and the consequent sins attributed to killing his own relatives. So, he surrenders to Lord Krishna, seeking a solution. Thus, follows the wisdom of the Bhagavad Gita.",
            "key_teachings": [
                "The moral dilemma of duty versus personal attachment",
                "The nature of righteous action in difficult circumstances", 
                "The importance of seeking divine guidance in times of crisis",
                "The conflict between emotional attachment and dharmic duty"
            ],
            "verse_count": 47,
            "significance": "Establishes the fundamental question that drives the entire Gita: How should one act when faced with moral conflict?"
        },
        2: {
            "chapter_number": 2,
            "sanskrit_name": "सांख्य योग",
            "english_name": "Sankhya Yoga",
            "translation": "The Yoga of Knowledge",
            "theme": "Immortality of the Soul",
            "description": "In this chapter, Krishna begins his teachings by explaining the immortal nature of the soul. He introduces the fundamental concepts of the eternal soul (atman) versus the temporary body, and explains why grief over death is misplaced. This chapter lays the philosophical foundation for the entire Gita by establishing the distinction between the eternal and the temporary.",
            "key_teachings": [
                "The soul is eternal and indestructible",
                "The body is temporary, the soul is permanent",
                "Death is merely a change of garments for the soul",
                "Introduction to the concept of dharma and duty",
                "The path of selfless action (Nishkama Karma)"
            ],
            "verse_count": 72,
            "significance": "Provides the metaphysical foundation for all subsequent teachings about duty, action, and liberation."
        },
        3: {
            "chapter_number": 3,
            "sanskrit_name": "कर्म योग",
            "english_name": "Karma Yoga", 
            "translation": "The Yoga of Action",
            "theme": "Selfless Action",
            "description": "Krishna explains the importance of performing one's duty without attachment to results. This chapter introduces the concept of Karma Yoga - the path of selfless action. Krishna emphasizes that action is inevitable and that the key is to act without ego and attachment to outcomes.",
            "key_teachings": [
                "Action is better than inaction",
                "Perform duty without attachment to results",
                "The concept of yajna (sacrifice) in daily life",
                "How desire and anger obstruct spiritual progress",
                "The importance of following one's dharma"
            ],
            "verse_count": 43,
            "significance": "Establishes Karma Yoga as a practical path to liberation through selfless action."
        },
        4: {
            "chapter_number": 4,
            "sanskrit_name": "ज्ञान कर्म संन्यास योग",
            "english_name": "Jnana Karma Sannyasa Yoga",
            "translation": "The Yoga of Knowledge and Renunciation of Action",
            "theme": "Divine Incarnation and Sacred Knowledge",
            "description": "Krishna reveals his divine nature and explains the concept of avatar - divine incarnation. He discusses the ancient tradition of spiritual knowledge and how it becomes lost over time, necessitating divine intervention. The chapter also explores the relationship between knowledge and action.",
            "key_teachings": [
                "The concept of divine incarnation (avatar)",
                "The cyclical nature of spiritual knowledge",
                "The relationship between knowledge and action",
                "How to see inaction in action and action in inaction",
                "The purifying power of spiritual knowledge"
            ],
            "verse_count": 42,
            "significance": "Reveals Krishna's divine identity and the cosmic purpose behind the Gita's teachings."
        },
        5: {
            "chapter_number": 5,
            "sanskrit_name": "कर्म संन्यास योग",
            "english_name": "Karma Sannyasa Yoga",
            "translation": "The Yoga of Renunciation of Action",
            "theme": "True Renunciation",
            "description": "Krishna clarifies the apparent contradiction between the path of action (Karma Yoga) and the path of renunciation (Sannyasa). He explains that true renunciation is not the abandonment of action, but the abandonment of attachment to the fruits of action.",
            "key_teachings": [
                "True renunciation vs. mere abandonment of action",
                "The unity of Karma Yoga and Sannyasa",
                "How to remain unaffected by success and failure",
                "The state of the liberated soul",
                "Inner purification through selfless action"
            ],
            "verse_count": 29,
            "significance": "Resolves the apparent conflict between action and renunciation, showing their essential unity."
        },
        6: {
            "chapter_number": 6,
            "sanskrit_name": "आत्म संयम योग",
            "english_name": "Atma Samyama Yoga",
            "translation": "The Yoga of Self-Control",
            "theme": "Meditation and Mind Control",
            "description": "This chapter focuses on the practice of meditation and the control of the mind. Krishna provides detailed instructions on how to practice meditation, the qualities needed for successful meditation, and how to deal with the restless mind.",
            "key_teachings": [
                "The practice of meditation (dhyana)",
                "How to control the restless mind",
                "The qualities of a successful meditator",
                "The fate of the unsuccessful yogi",
                "The supreme goal of yoga - union with the Divine"
            ],
            "verse_count": 47,
            "significance": "Provides practical guidance for meditation and mental discipline as paths to self-realization."
        },
        7: {
            "chapter_number": 7,
            "sanskrit_name": "ज्ञान विज्ञान योग",
            "english_name": "Jnana Vijnana Yoga",
            "translation": "The Yoga of Knowledge and Realization",
            "theme": "Divine Nature and Manifestation",
            "description": "Krishna explains his divine nature in greater detail, describing how he manifests in the world while remaining transcendent. He discusses the different types of devotees and how people with different temperaments approach the Divine.",
            "key_teachings": [
                "The two aspects of divine nature - material and spiritual",
                "How the Divine manifests in creation",
                "The four types of devotees",
                "Why people worship other deities",
                "The rarity of true spiritual knowledge"
            ],
            "verse_count": 30,
            "significance": "Deepens understanding of the Divine nature and the various paths people take toward God."
        },
        8: {
            "chapter_number": 8,
            "sanskrit_name": "अक्षर ब्रह्म योग",
            "english_name": "Akshara Brahma Yoga",
            "translation": "The Yoga of the Imperishable Brahman",
            "theme": "Death and the Afterlife",
            "description": "Krishna explains what happens at the time of death and how one's state of consciousness at death determines their next destination. He discusses the cosmic cycles of creation and destruction, and the paths souls take after death.",
            "key_teachings": [
                "The importance of one's final thoughts at death",
                "The cosmic cycles of creation and destruction",
                "The path of light and the path of darkness after death",
                "How to remember the Divine at the time of death",
                "The ultimate destination of the soul"
            ],
            "verse_count": 28,
            "significance": "Addresses fundamental questions about death, afterlife, and the soul's journey."
        },
        9: {
            "chapter_number": 9,
            "sanskrit_name": "राज विद्या राज गुह्य योग",
            "english_name": "Raja Vidya Raja Guhya Yoga",
            "translation": "The Yoga of Royal Knowledge and Royal Secret",
            "theme": "Supreme Knowledge and Devotion",
            "description": "Krishna reveals the most confidential knowledge - the supreme secret of devotion. He explains how he pervades the entire universe while remaining transcendent, and describes the power of pure devotional service.",
            "key_teachings": [
                "The supreme secret of spiritual life",
                "How the Divine pervades yet transcends creation",
                "The power of pure devotion",
                "Why some people cannot perceive the Divine",
                "The simplicity of true devotional service"
            ],
            "verse_count": 34,
            "significance": "Reveals the highest spiritual knowledge and the supremacy of devotional service."
        },
        10: {
            "chapter_number": 10,
            "sanskrit_name": "विभूति योग",
            "english_name": "Vibhuti Yoga",
            "translation": "The Yoga of Divine Glories",
            "theme": "Divine Manifestations",
            "description": "Krishna describes his various manifestations and glories in the world. He explains how he can be recognized in the most excellent examples of every category of existence, from the natural world to human achievements.",
            "key_teachings": [
                "How to recognize the Divine in creation",
                "The most excellent manifestations of divinity",
                "The source of all power and beauty",
                "How devotion leads to divine knowledge",
                "The infinite nature of divine manifestations"
            ],
            "verse_count": 42,
            "significance": "Helps devotees recognize and connect with the Divine presence in all aspects of life."
        },
        11: {
            "chapter_number": 11,
            "sanskrit_name": "विश्वरूप दर्शन योग",
            "english_name": "Vishvarupa Darshana Yoga",
            "translation": "The Yoga of the Vision of the Universal Form",
            "theme": "Cosmic Vision",
            "description": "The most dramatic chapter of the Gita, where Krishna reveals his cosmic universal form to Arjuna. This vision shows the Divine as the source, sustainer, and destroyer of all existence, inspiring both awe and terror in Arjuna.",
            "key_teachings": [
                "The cosmic universal form of the Divine",
                "The Divine as creator, sustainer, and destroyer",
                "The overwhelming nature of divine reality",
                "The need for divine grace to perceive ultimate truth",
                "The personal form as more accessible than the cosmic form"
            ],
            "verse_count": 55,
            "significance": "Provides the climactic vision of divine reality and establishes Krishna's supreme divinity."
        },
        12: {
            "chapter_number": 12,
            "sanskrit_name": "भक्ति योग",
            "english_name": "Bhakti Yoga",
            "translation": "The Yoga of Devotion",
            "theme": "Pure Devotional Service",
            "description": "After the overwhelming cosmic vision, Krishna returns to discussing the more accessible path of personal devotion. He describes the qualities of a true devotee and explains why the personal aspect of the Divine is easier to approach than the impersonal.",
            "key_teachings": [
                "The superiority of personal devotion over impersonal meditation",
                "The qualities of a perfect devotee",
                "How to develop pure devotional service",
                "The accessibility of the personal form of God",
                "The gradual development of spiritual consciousness"
            ],
            "verse_count": 20,
            "significance": "Establishes devotional service as the most accessible and effective spiritual path."
        },
        13: {
            "chapter_number": 13,
            "sanskrit_name": "क्षेत्र क्षेत्रज्ञ विभाग योग",
            "english_name": "Kshetra Kshetrajna Vibhaga Yoga",
            "translation": "The Yoga of Distinction between the Field and the Knower of the Field",
            "theme": "Matter and Spirit",
            "description": "Krishna explains the distinction between the material body (the field) and the conscious soul (the knower of the field). This chapter provides a detailed analysis of the components of material nature and the transcendent position of consciousness.",
            "key_teachings": [
                "The distinction between matter and consciousness",
                "The components of material nature",
                "The transcendent position of the soul",
                "How to perceive the Divine in all beings",
                "The path to liberation through knowledge"
            ],
            "verse_count": 35,
            "significance": "Provides crucial philosophical understanding of the relationship between matter, consciousness, and the Divine."
        },
        14: {
            "chapter_number": 14,
            "sanskrit_name": "गुणत्रय विभाग योग",
            "english_name": "Gunatraya Vibhaga Yoga",
            "translation": "The Yoga of the Division of the Three Gunas",
            "theme": "The Three Modes of Nature",
            "description": "Krishna explains the three fundamental qualities or modes of material nature: goodness (sattva), passion (rajas), and ignorance (tamas). He describes how these modes influence human behavior and consciousness, and how to transcend them.",
            "key_teachings": [
                "The three modes of material nature",
                "How the modes influence human behavior",
                "The characteristics of each mode",
                "How to transcend the modes of nature",
                "The state of one who has transcended the modes"
            ],
            "verse_count": 27,
            "significance": "Provides essential understanding of how material nature operates and how to achieve liberation from its influence."
        },
        15: {
            "chapter_number": 15,
            "sanskrit_name": "पुरुषोत्तम योग",
            "english_name": "Purushottama Yoga",
            "translation": "The Yoga of the Supreme Person",
            "theme": "The Supreme Personality",
            "description": "Krishna describes himself as the Supreme Person (Purushottama) who transcends both the fallible and infallible aspects of existence. He uses the metaphor of the cosmic tree to explain the material world and how to detach from it.",
            "key_teachings": [
                "The Supreme Person beyond fallible and infallible",
                "The cosmic tree metaphor for material existence",
                "How to detach from material entanglement",
                "The supreme destination of the soul",
                "The confidential nature of this knowledge"
            ],
            "verse_count": 20,
            "significance": "Establishes Krishna's position as the Supreme Personality of Godhead and the ultimate goal of spiritual life."
        },
        16: {
            "chapter_number": 16,
            "sanskrit_name": "दैवासुर सम्पद् विभाग योग",
            "english_name": "Daivasura Sampad Vibhaga Yoga",
            "translation": "The Yoga of the Division between Divine and Demoniac Natures",
            "theme": "Divine and Demoniac Qualities",
            "description": "Krishna describes the divine and demoniac natures that exist within human beings. He explains the characteristics of those with divine qualities versus those with demoniac tendencies, and the destinations of each type.",
            "key_teachings": [
                "Divine qualities that lead to liberation",
                "Demoniac qualities that lead to bondage",
                "The importance of following scriptural guidance",
                "How pride and ego lead to spiritual downfall",
                "The ultimate fate of divine and demoniac natures"
            ],
            "verse_count": 24,
            "significance": "Provides clear guidance on spiritual and material qualities, helping practitioners understand what to cultivate and what to avoid."
        },
        17: {
            "chapter_number": 17,
            "sanskrit_name": "श्रद्धात्रय विभाग योग",
            "english_name": "Shraddhatraya Vibhaga Yoga",
            "translation": "The Yoga of the Division of the Three Types of Faith",
            "theme": "Faith and Its Expressions",
            "description": "Krishna explains how the three modes of nature influence different types of faith, worship, food preferences, charity, and austerity. He shows how one's faith determines their spiritual practices and ultimate destination.",
            "key_teachings": [
                "Three types of faith corresponding to the three modes",
                "How faith influences worship and spiritual practice",
                "The three types of food and their effects",
                "Proper and improper forms of charity and austerity",
                "The sacred syllable Om and its significance"
            ],
            "verse_count": 28,
            "significance": "Demonstrates how the modes of nature influence all aspects of spiritual and material life."
        },
        18: {
            "chapter_number": 18,
            "sanskrit_name": "मोक्ष संन्यास योग",
            "english_name": "Moksha Sannyasa Yoga",
            "translation": "The Yoga of Liberation through Renunciation",
            "theme": "Final Instructions and Liberation",
            "description": "The concluding chapter where Krishna summarizes the main teachings of the Gita. He gives final instructions on renunciation, devotion, and surrender. The chapter ends with Krishna's promise of liberation for those who surrender to him completely.",
            "key_teachings": [
                "The difference between renunciation and abandonment",
                "How the modes of nature influence action and knowledge",
                "The supreme instruction to surrender to Krishna",
                "The promise of liberation through surrender",
                "The confidential nature of the Gita's message"
            ],
            "verse_count": 78,
            "significance": "Provides the culminating message of the Gita and Krishna's final promise of liberation to sincere devotees."
        }
    }
    
    return {
        "source": "gita",
        "book_name": "Bhagavad Gita",
        "total_chapters": 18,
        "chapters": gita_chapters
    }

@router.get("/gita/chapters/{chapter_number}")
def get_gita_chapter_info(
    chapter_number: int = Path(
        ...,
        ge=1,
        le=18,
        description="Chapter number (1-18)",
        example=1
    )
):
    """
    Get detailed information about a specific Bhagavad Gita chapter.
    
    Returns comprehensive information including:
    - Sanskrit and English names
    - Chapter theme and description
    - Key teachings and philosophical concepts
    - Verse count and significance
    
    Example URLs:
    - GET /api/v1/books/gita/chapters/1 - Get Chapter 1 (Arjuna Visada Yoga)
    - GET /api/v1/books/gita/chapters/11 - Get Chapter 11 (Universal Form)
    """
    
    # Get all chapter data
    all_chapters_response = get_gita_chapters_info()
    chapters = all_chapters_response["chapters"]
    
    if chapter_number not in chapters:
        raise HTTPException(
            status_code=404,
            detail=f"Chapter {chapter_number} not found. Valid chapters are 1-18."
        )
    
    chapter_info = chapters[chapter_number]
    
    # Add navigation URLs for frontend
    chapter_info["navigation_url"] = f"/gita/a/{chapter_number}"
    chapter_info["api_url"] = f"/api/v1/texts/gita/a/{chapter_number}"
    
    return chapter_info

@router.get("/a/enhanced-info")
def get_gita_enhanced_info():
    """
    Get enhanced information about the Bhagavad Gita book.
    
    This endpoint provides comprehensive information about the Gita
    similar to how Bible books provide enhanced information.
    Handles the frontend request for /api/v1/books/a/enhanced-info
    """
    
    return {
        "book_name": "Bhagavad Gita",
        "sanskrit_name": "भगवद्गीता", 
        "latin_name": "Bhagavad Gita",
        "author": "Traditionally attributed to Vyasa",
        "date_written": "5th century BCE to 2nd century CE",
        "historical_context": "The Bhagavad Gita is part of the epic Mahabharata and was composed during a time of great philosophical and spiritual development in ancient India. It represents a synthesis of various schools of Hindu philosophy.",
        "summary": "The Bhagavad Gita is a 700-verse Hindu scripture that is part of the epic Mahabharata. It consists of a conversation between Prince Arjuna and his guide Krishna on the battlefield of Kurukshetra. Faced with a fratricidal war, Arjuna is filled with moral dilemma and despair about fighting his own cousins. Krishna counsels Arjuna to fulfill his duty as a warrior and prince, and elaborates on a variety of philosophical concepts.",
        "theological_importance": "The Gita addresses the moral and philosophical dilemmas faced by human beings, and presents multiple paths to spiritual realization including devotion (bhakti), action (karma), and knowledge (jnana). It is considered one of the most important texts in Hindu philosophy.",
        "literary_genre": "Philosophical dialogue and spiritual instruction",
        "important_sections": [
            {
                "title": "The Moral Crisis of Duty",
                "description": "Arjuna's dilemma about fighting in battle against relatives and teachers",
                "key_chapters": [1, 2]
            },
            {
                "title": "The Nature of the Soul",
                "description": "Krishna's teaching about the eternal, indestructible nature of the soul",
                "key_chapters": [2, 13]
            },
            {
                "title": "Paths to Liberation",
                "description": "The three main yogas: Karma (action), Jnana (knowledge), and Bhakti (devotion)",
                "key_chapters": [3, 4, 5, 12]
            },
            {
                "title": "The Universal Form",
                "description": "Krishna reveals his cosmic, universal form to Arjuna",
                "key_chapters": [11]
            },
            {
                "title": "Divine Qualities vs Demonic Qualities",
                "description": "Distinction between divine and demonic natures in human beings",
                "key_chapters": [16]
            },
            {
                "title": "The Supreme Secret",
                "description": "The ultimate teaching of surrender and devotion to the Divine",
                "key_chapters": [9, 18]
            }
        ],
        "language_notes": "Originally composed in Sanskrit, the Gita uses classical Sanskrit verse forms. Key terms include 'dharma' (duty/righteousness), 'karma' (action), 'yoga' (union/discipline), and 'moksha' (liberation).",
        "chapter_count": 18,
        "total_verses": 700,
        "source": "enhanced",
        "confidence": 1.0
    }

@router.get("/abbr/a")
def get_gita_by_abbreviation():
    """
    Get Bhagavad Gita book information by abbreviation 'a'.
    
    This handles the frontend request for /api/v1/books/abbr/a
    and returns basic book information for the Gita.
    """
    
    return {
        "id": 55,  # This should match the actual Gita book ID in your database
        "name": "Bhagavad Gita",
        "latin_name": "Bhagavad Gita",
        "sanskrit_name": "भगवद्गीता",
        "abbreviation": "a",
        "chapter_count": 18,
        "source": "gita",
        "created_at": "2025-06-14T11:53:27"
    }

 