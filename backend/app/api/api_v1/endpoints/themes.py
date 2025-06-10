from fastapi import APIRouter, HTTPException, Path

router = APIRouter()

@router.get("/{theme_name}")
def get_theme_verses(
    theme_name: str = Path(
        ...,
        description="Name of the theme to search for (e.g., 'family', 'covenant', 'salvation')",
        example="covenant"
    )
):
    """
    Get all verses across the Bible that relate to a specific theme.
    
    Returns a collection of verses from different books that share the same 
    theological theme, allowing for thematic study across the entire Bible.
    """
    
    # Comprehensive thematic database with cross-references
    thematic_database = {
        "covenant": {
            "latin_title": "Foedus",
            "description": "Divine covenant relationship between God and humanity",
            "verses": [
                {
                    "book": "Genesis",
                    "book_abbr": "Gn", 
                    "reference": "Gn 9:9",
                    "text": "Ecce ego statuam pactum meum vobiscum",
                    "navigation_url": "/Gn/9/9",
                    "context": "Noah's covenant after the flood"
                },
                {
                    "book": "Genesis",
                    "book_abbr": "Gn",
                    "reference": "Gn 12:2",
                    "text": "Faciamque te in gentem magnam",
                    "navigation_url": "/Gn/12/2", 
                    "context": "Abrahamic covenant promise"
                },
                {
                    "book": "Genesis", 
                    "book_abbr": "Gn",
                    "reference": "Gn 17:7",
                    "text": "Et statuam pactum meum inter me et te",
                    "navigation_url": "/Gn/17/7",
                    "context": "Covenant of circumcision"
                },
                {
                    "book": "Exodus",
                    "book_abbr": "Ex", 
                    "reference": "Ex 19:5",
                    "text": "Si audieritis vocem meam et custodieritis pactum meum",
                    "navigation_url": "/Ex/19/5",
                    "context": "Sinai covenant conditions"
                },
                {
                    "book": "Matthew",
                    "book_abbr": "Mt",
                    "reference": "Mt 26:28", 
                    "text": "Hic est enim sanguis meus novi testamenti",
                    "navigation_url": "/Mt/26/28",
                    "context": "New covenant in Christ's blood"
                }
            ]
        },
        "creation": {
            "latin_title": "Creatio",
            "description": "God as creator and sustainer of all things",
            "verses": [
                {
                    "book": "Genesis",
                    "book_abbr": "Gn",
                    "reference": "Gn 1:1", 
                    "text": "In principio creavit Deus caelum et terram",
                    "navigation_url": "/Gn/1/1",
                    "context": "Beginning of creation"
                },
                {
                    "book": "Genesis",
                    "book_abbr": "Gn",
                    "reference": "Gn 1:27",
                    "text": "Et creavit Deus hominem ad imaginem suam",
                    "navigation_url": "/Gn/1/27",
                    "context": "Human creation in God's image"
                },
                {
                    "book": "Psalms",
                    "book_abbr": "Ps",
                    "reference": "Ps 8:3",
                    "text": "Quoniam videbo caelos tuos opera digitorum tuorum",
                    "navigation_url": "/Ps/8/3",
                    "context": "Creation as God's handiwork"
                },
                {
                    "book": "Psalms",
                    "book_abbr": "Ps", 
                    "reference": "Ps 19:1",
                    "text": "Caeli enarrant gloriam Dei",
                    "navigation_url": "/Ps/19/1",
                    "context": "Creation declares God's glory"
                },
                {
                    "book": "John",
                    "book_abbr": "Jo",
                    "reference": "Jo 1:3",
                    "text": "Omnia per ipsum facta sunt",
                    "navigation_url": "/Jo/1/3",
                    "context": "Christ as agent of creation"
                }
            ]
        },
        "family": {
            "latin_title": "Familia",
            "description": "Family relationships and domestic life in biblical perspective",
            "verses": [
                {
                    "book": "Genesis",
                    "book_abbr": "Gn",
                    "reference": "Gn 2:24",
                    "text": "Quam ob rem relinquet homo patrem suum et matrem",
                    "navigation_url": "/Gn/2/24",
                    "context": "Foundation of marriage"
                },
                {
                    "book": "Genesis",
                    "book_abbr": "Gn", 
                    "reference": "Gn 4:9",
                    "text": "Numquid custos fratris mei sum ego",
                    "navigation_url": "/Gn/4/9",
                    "context": "Cain and Abel - brotherhood responsibility"
                },
                {
                    "book": "Exodus",
                    "book_abbr": "Ex",
                    "reference": "Ex 20:12",
                    "text": "Honora patrem tuum et matrem tuam",
                    "navigation_url": "/Ex/20/12",
                    "context": "Fifth commandment - honoring parents"
                },
                {
                    "book": "Proverbs",
                    "book_abbr": "Pr",
                    "reference": "Pr 22:6",
                    "text": "Adolescens iuxta viam suam etiam cum senuerit non recedet ab ea",
                    "navigation_url": "/Pr/22/6",
                    "context": "Training children"
                },
                {
                    "book": "Ephesians",
                    "book_abbr": "Ep",
                    "reference": "Ep 6:1",
                    "text": "Filii oboedite parentibus vestris in Domino",
                    "navigation_url": "/Ep/6/1",
                    "context": "Children's obedience to parents"
                }
            ]
        },
        "faith": {
            "latin_title": "Fides", 
            "description": "Trust and belief in God throughout salvation history",
            "verses": [
                {
                    "book": "Genesis",
                    "book_abbr": "Gn",
                    "reference": "Gn 15:6",
                    "text": "Credidit Abram Deo et reputatum est illi ad iustitiam",
                    "navigation_url": "/Gn/15/6",
                    "context": "Abraham's faith counted as righteousness"
                },
                {
                    "book": "Habakkuk",
                    "book_abbr": "Ha",
                    "reference": "Ha 2:4",
                    "text": "Iustus autem in fide sua vivet",
                    "navigation_url": "/Ha/2/4",
                    "context": "The righteous live by faith"
                },
                {
                    "book": "Matthew",
                    "book_abbr": "Mt",
                    "reference": "Mt 17:20",
                    "text": "Si habueritis fidem sicut granum sinapis",
                    "navigation_url": "/Mt/17/20",
                    "context": "Faith like a mustard seed"
                },
                {
                    "book": "Romans",
                    "book_abbr": "Rm",
                    "reference": "Rm 1:17",
                    "text": "Iustus ex fide vivit",
                    "navigation_url": "/Rm/1/17",
                    "context": "Justification by faith"
                },
                {
                    "book": "Hebrews",
                    "book_abbr": "He",
                    "reference": "He 11:1",
                    "text": "Est autem fides sperandarum substantia rerum",
                    "navigation_url": "/He/11/1",
                    "context": "Definition of faith"
                }
            ]
        },
        "salvation": {
            "latin_title": "Salus",
            "description": "Divine rescue and redemption of humanity",
            "verses": [
                {
                    "book": "Genesis",
                    "book_abbr": "Gn",
                    "reference": "Gn 3:15",
                    "text": "Inimicitias ponam inter te et mulierem",
                    "navigation_url": "/Gn/3/15",
                    "context": "First messianic promise"
                },
                {
                    "book": "Exodus",
                    "book_abbr": "Ex",
                    "reference": "Ex 14:13",
                    "text": "Videbitis salutem Domini quam facturus est vobis hodie",
                    "navigation_url": "/Ex/14/13",
                    "context": "Salvation at the Red Sea"
                },
                {
                    "book": "Isaiah",
                    "book_abbr": "Is",
                    "reference": "Is 53:5",
                    "text": "Ipse vulneratus est propter iniquitates nostras",
                    "navigation_url": "/Is/53/5",
                    "context": "Suffering servant brings healing"
                },
                {
                    "book": "Luke",
                    "book_abbr": "Lc",
                    "reference": "Lc 2:11",
                    "text": "Quia natus est vobis hodie salvator",
                    "navigation_url": "/Lc/2/11",
                    "context": "Birth of the Savior"
                },
                {
                    "book": "John",
                    "book_abbr": "Jo",
                    "reference": "Jo 3:16",
                    "text": "Sic enim Deus dilexit mundum ut Filium suum unigenitum daret",
                    "navigation_url": "/Jo/3/16",
                    "context": "God's love and salvation"
                }
            ]
        },
        "love": {
            "latin_title": "Amor",
            "description": "Divine love and human love in relationship",
            "verses": [
                {
                    "book": "Song of Songs",
                    "book_abbr": "Ct",
                    "reference": "Ct 8:6",
                    "text": "Fortis est ut mors dilectio",
                    "navigation_url": "/Ct/8/6",
                    "context": "Love is strong as death"
                },
                {
                    "book": "Matthew",
                    "book_abbr": "Mt",
                    "reference": "Mt 22:37",
                    "text": "Diliges Dominum Deum tuum ex toto corde tuo",
                    "navigation_url": "/Mt/22/37",
                    "context": "Greatest commandment"
                },
                {
                    "book": "John",
                    "book_abbr": "Jo",
                    "reference": "Jo 13:34",
                    "text": "Mandatum novum do vobis ut diligatis invicem",
                    "navigation_url": "/Jo/13/34",
                    "context": "New commandment to love"
                },
                {
                    "book": "1 Corinthians",
                    "book_abbr": "1Co",
                    "reference": "1Co 13:4",
                    "text": "Caritas patiens est benigna est caritas",
                    "navigation_url": "/1Co/13/4",
                    "context": "Nature of love"
                },
                {
                    "book": "1 John",
                    "book_abbr": "1Jo",
                    "reference": "1Jo 4:8",
                    "text": "Deus caritas est",
                    "navigation_url": "/1Jo/4/8",
                    "context": "God is love"
                }
            ]
        },
        "justice": {
            "latin_title": "Iustitia",
            "description": "Divine justice and righteousness", 
            "verses": [
                {
                    "book": "Genesis",
                    "book_abbr": "Gn",
                    "reference": "Gn 18:25",
                    "text": "Numquid qui iudicat omnem terram non faciet quod iustum est",
                    "navigation_url": "/Gn/18/25",
                    "context": "God as righteous judge"
                },
                {
                    "book": "Psalms",
                    "book_abbr": "Ps",
                    "reference": "Ps 89:14",
                    "text": "Iustitia et iudicium praeparatio sedis tuae",
                    "navigation_url": "/Ps/89/14",
                    "context": "Justice as foundation of God's throne"
                },
                {
                    "book": "Isaiah",
                    "book_abbr": "Is",
                    "reference": "Is 1:17",
                    "text": "Discite benefacere quaerite iudicium",
                    "navigation_url": "/Is/1/17",
                    "context": "Learn to do good, seek justice"
                },
                {
                    "book": "Matthew",
                    "book_abbr": "Mt",
                    "reference": "Mt 5:6",
                    "text": "Beati qui esuriunt et sitiunt iustitiam",
                    "navigation_url": "/Mt/5/6",
                    "context": "Blessed are those who hunger for righteousness"
                },
                {
                    "book": "Romans",
                    "book_abbr": "Rm",
                    "reference": "Rm 3:21",
                    "text": "Nunc autem sine lege iustitia Dei manifestata est",
                    "navigation_url": "/Rm/3/21",
                    "context": "God's righteousness revealed"
                }
            ]
        },
        "wisdom": {
            "latin_title": "Sapientia",
            "description": "Divine wisdom and human understanding",
            "verses": [
                {
                    "book": "Proverbs",
                    "book_abbr": "Pr",
                    "reference": "Pr 1:7",
                    "text": "Timor Domini principium sapientiae",
                    "navigation_url": "/Pr/1/7",
                    "context": "Fear of the Lord is beginning of wisdom"
                },
                {
                    "book": "Proverbs",
                    "book_abbr": "Pr",
                    "reference": "Pr 9:10",
                    "text": "Initium sapientiae timor Domini",
                    "navigation_url": "/Pr/9/10",
                    "context": "Beginning of wisdom"
                },
                {
                    "book": "Ecclesiastes",
                    "book_abbr": "Qo",
                    "reference": "Qo 12:13",
                    "text": "Deum time et mandata eius observa",
                    "navigation_url": "/Qo/12/13",
                    "context": "Conclusion of wisdom"
                },
                {
                    "book": "Matthew",
                    "book_abbr": "Mt",
                    "reference": "Mt 11:25",
                    "text": "Abscondisti haec a sapientibus et revelasti ea parvulis",
                    "navigation_url": "/Mt/11/25",
                    "context": "Hidden from wise, revealed to little ones"
                },
                {
                    "book": "1 Corinthians",
                    "book_abbr": "1Co",
                    "reference": "1Co 1:24",
                    "text": "Christum Dei virtutem et Dei sapientiam",
                    "navigation_url": "/1Co/1/24",
                    "context": "Christ as God's wisdom"
                }
            ]
        },
        "forgiveness": {
            "latin_title": "Venia",
            "description": "Divine mercy and human reconciliation",
            "verses": [
                {
                    "book": "Genesis",
                    "book_abbr": "Gn",
                    "reference": "Gn 50:20",
                    "text": "Vos cogitastis de me malum sed Deus vertit in bonum",
                    "navigation_url": "/Gn/50/20",
                    "context": "Joseph forgives his brothers"
                },
                {
                    "book": "Psalms",
                    "book_abbr": "Ps",
                    "reference": "Ps 51:1",
                    "text": "Miserere mei Deus secundum magnam misericordiam tuam",
                    "navigation_url": "/Ps/51/1",
                    "context": "David's prayer for forgiveness"
                },
                {
                    "book": "Isaiah",
                    "book_abbr": "Is",
                    "reference": "Is 1:18",
                    "text": "Si fuerint peccata vestra ut coccinum quasi nix dealbabuntur",
                    "navigation_url": "/Is/1/18",
                    "context": "Sins made white as snow"
                },
                {
                    "book": "Matthew",
                    "book_abbr": "Mt",
                    "reference": "Mt 6:14",
                    "text": "Si dimiseritis hominibus peccata eorum dimittet et vobis Pater vester",
                    "navigation_url": "/Mt/6/14",
                    "context": "Forgiving others"
                },
                {
                    "book": "Luke",
                    "book_abbr": "Lc",
                    "reference": "Lc 23:34",
                    "text": "Pater dimitte illis non enim sciunt quid faciunt",
                    "navigation_url": "/Lc/23/34",
                    "context": "Christ forgives from the cross"
                }
            ]
        },
        "sacrifice": {
            "latin_title": "Sacrificium",
            "description": "Offerings to God and self-sacrifice",
            "verses": [
                {
                    "book": "Genesis",
                    "book_abbr": "Gn",
                    "reference": "Gn 22:2",
                    "text": "Tolle filium tuum unigenitum quem diligis Isaac",
                    "navigation_url": "/Gn/22/2",
                    "context": "Abraham's sacrifice of Isaac"
                },
                {
                    "book": "Leviticus",
                    "book_abbr": "Lev",
                    "reference": "Lev 16:30",
                    "text": "In hac die expiatio erit vestri atque mundatio",
                    "navigation_url": "/Lev/16/30",
                    "context": "Day of Atonement"
                },
                {
                    "book": "Psalms",
                    "book_abbr": "Ps",
                    "reference": "Ps 51:17",
                    "text": "Sacrificium Deo spiritus contribulatus",
                    "navigation_url": "/Ps/51/17",
                    "context": "Broken spirit as sacrifice"
                },
                {
                    "book": "John",
                    "book_abbr": "Jo",
                    "reference": "Jo 15:13",
                    "text": "Maiorem hac dilectionem nemo habet",
                    "navigation_url": "/Jo/15/13",
                    "context": "Greater love has no one"
                },
                {
                    "book": "Hebrews",
                    "book_abbr": "He",
                    "reference": "He 9:12",
                    "text": "Per proprium sanguinem introivit semel in sancta",
                    "navigation_url": "/He/9/12",
                    "context": "Christ's blood sacrifice"
                }
            ]
        }
    }
    
    theme_data = thematic_database.get(theme_name.lower())
    if not theme_data:
        available_themes = list(thematic_database.keys())
        raise HTTPException(
            status_code=404, 
            detail=f"Theme '{theme_name}' not found. Available themes: {', '.join(available_themes)}"
        )
    
    return {
        "theme": theme_name,
        "latin_title": theme_data["latin_title"],
        "description": theme_data["description"],
        "total_verses": len(theme_data["verses"]),
        "verses": theme_data["verses"],
        "success": True
    }

@router.get("/")
def get_available_themes():
    """
    Get a list of all available themes for cross-referencing.
    """
    themes = [
        {"name": "covenant", "latin": "Foedus", "description": "Divine covenant relationship"},
        {"name": "creation", "latin": "Creatio", "description": "God as creator and sustainer"},
        {"name": "family", "latin": "Familia", "description": "Family relationships and domestic life"},
        {"name": "faith", "latin": "Fides", "description": "Trust and belief in God"},
        {"name": "salvation", "latin": "Salus", "description": "Divine rescue and redemption"},
        {"name": "love", "latin": "Amor", "description": "Divine and human love"},
        {"name": "justice", "latin": "Iustitia", "description": "Divine justice and righteousness"},
        {"name": "wisdom", "latin": "Sapientia", "description": "Divine wisdom and understanding"},
        {"name": "forgiveness", "latin": "Venia", "description": "Divine mercy and reconciliation"},
        {"name": "sacrifice", "latin": "Sacrificium", "description": "Offerings and self-sacrifice"}
    ]
    
    return {
        "available_themes": themes,
        "total_count": len(themes),
        "success": True
    } 