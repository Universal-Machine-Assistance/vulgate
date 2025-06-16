#!/usr/bin/env python3
"""
Step 6: Replace sample Newton data with proper Principia structure.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def find_database():
    for db in ["db/vulgate.db", "vulgate.db", "word_cache.db", "backend/vulgate.db"]:
        p = Path(db)
        if p.exists() and p.stat().st_size > 1000:
            return p
    return None

def newton_book_id(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM books WHERE source = 'newton'")
    row = cur.fetchone()
    return row[0] if row else None

def setup_proper_structure():
    db_path = find_database()
    if not db_path:
        print("❌ Database not found.")
        return

    conn = sqlite3.connect(str(db_path))
    book_id = newton_book_id(conn)
    if not book_id:
        print("❌ Newton book missing (run Step 3).")
        conn.close()
        return

    cur = conn.cursor()
    
    # Clear existing Newton verses
    print("🔄 Clearing existing Newton sample data...")
    cur.execute("DELETE FROM verses WHERE book_id = ?", (book_id,))
    
    now = datetime.now()
    
    # Chapter 0: Title Page
    title_page = """PHILOSOPHIÆ
NATURALIS
P R I N C I P I A
MATHEMATICA
Autore IS. NEWTON, Trin. Coll. Cantab. Soc. Matheseos
Professore Lucasiano, & Societatis Regalis Sodali.
IMPRIMATUR.
S. PEPYS, Reg. Soc. PRÆSES.
Julii 5. 1686.
LONDINI,
Jussu Societatis Regiæ ac Typis Josephi Streater. Prostat apud
plures Bibliopolas. Anno MDCLXXXVII.
I L L U S T R I S S I M Æ
S O C I E T A T I R E G A L I
a Serenissimo
REGE CAROLO II.
AD
PHILOSOPHIAM PROMOVENDAM
F U N D A T Æ,
ET AUSPICIIS
POTENTISSIMI MONARCHÆ
J A C O B I II.
FLORENTI.
Tractatum hunc humillime D.D.D.
IS. NEWTON."""

    cur.execute("""
        INSERT INTO verses (
            book_id, chapter, verse_number, text,
            section_type, original_language,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (book_id, 0, 1, title_page, "title", "latin", now, now))

    # Chapter 1: P R Æ F A T I O
    preface_verses = [
        """Cum Veteres Mechanicam (uti Author est Pappus) in verum Naturalium
investigatione maximi fecerint, & recentiores, missis formis substantialibus &
qualitatibus occultis, Phænomena Naturæ ad leges Mathematicas revocare ag-
gressi sint: Visum est in hoc Tractatu Mathesin excolere quatenus ea ad Philo-
sophiam spectat. Mechanicam vero duplicem Veteres constituerunt: Rationalem
quæ per Demonstrationes accurate procedit, & Practicam.""",

        """Ad practicam spec-
tant Artes omnes Manuales, a quibus utiq; Mechanica nomen mutuata est. Cum
autem Artifices parum accurate operari soleant, fit ut Mechanica omnis a Ge-
ometria ita distinguatur, ut quicquid accuratum sit ad Geometriam referatur,
quicquid minus accuratum ad Mechanicam. Attamen errores non sunt Artis
sed Artificum. Qui minus accurate operatur, imperfectior est Mechanicus, & si
quis accuratissime operari posset, hic foret Mechanicus omnium perfectissimus.
Nam & Linearum rectarum & Circulorum descriptiones in quibus Geometria
fundatur, ad Mechanicam pertinent."""
    ]

    for i, verse in enumerate(preface_verses, 1):
        cur.execute("""
            INSERT INTO verses (
                book_id, chapter, verse_number, text,
                section_type, original_language,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (book_id, 1, i, verse, "preface", "latin", now, now))

    # Chapter 2: Poetry/Dedication
    poetry_verses = [
        """En tibi norma Poli, & divæ libramina Molis,
Computus atque Jovis; quas, dum primordia rerum
Pangeret, omniparens Leges violare Creator
Noluit, æternique operis fundamina fixit.
Intima panduntur victi penetralia cæli,
Nec latet extremos quæ Vis circumrotat Orbes.
Sol solio residens ad se jubet omnia prono
Tendere descensu, nec recto tramite currus
Sidereos patitur vastum per inane moveri;
Sed rapit immotis, se centro, singula Gyris.""",

        """Jam patet horrificis quæ sit via flexa Cometis;
Jam non miramur barbati Phænomena Astri.
Discimus hinc tandem qua causa argentea Phœbe
Passibus haud æquis graditur; cur subdita nulli
Hactenus Astronomo numerorum fræna recuset:
Cur remeant Nodi, curque Auges progrediuntur.
Discimus & quantis refluum vaga Cynthia Pontum
Viribus impellit, dum fractis fluctibus Ulvam
Deserit, ac Nautis suspectas nudat arenas;""",

        """Alternis vicibus suprema ad littora pulsans.
Quæ toties animos veterum torsere Sophorum,
Quæque Scholas frustra rauco certamine vexant
Obvia conspicimus nubem pellente Mathesi.
Jam dubios nulla caligine prægravat error
Queis Superum penetrare domos atque ardua Cœli
Scandere sublimis Genii concessit acumen.""",

        """Surgite Mortales, terrenas mittite curas
Atque hinc cœligenæ vires dignoscite Mentis
A pecudum vita longe lateque remotæ.
Qui scriptis jussit Tabulis compescere Cædes
Furta & Adulteria, & perjuræ crimina Fraudis;
Quive vagis populis circumdare mœnibus Urbes
Autor erat; Cererisve beavit munere gentes;"""
    ]

    for i, verse in enumerate(poetry_verses, 1):
        cur.execute("""
            INSERT INTO verses (
                book_id, chapter, verse_number, text,
                section_type, original_language,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (book_id, 2, i, verse, "poetry", "latin", now, now))

    # Chapter 3: Definitions
    definitions = [
        """Def. I.

Quantitas Materiæ est mensura ejusdem orta ex illius Densitate &
Magnitudine conjunctim. 

Aer duplo densior in duplo spatio quadruplus est. Idem intellige de Nive
et Pulveribus per compressionem vel liquefactionem condensatis. Et par est
ratio corporum omnium, quæ per causas quascunq; diversimode condensantur.
Medii interea, si quod fuerit, interstitia partium libere pervadentis, hic nullam
rationem habeo. Hanc autem quantitatem sub nomine corporis vel Massæ in
sequentibus passim intelligo. Innotescit ea per corporis cujusq; pondus. Nam
ponderi proportionalem esse reperi per experimenta pendulorum accuratissime
instituta, uti posthac docebitur.""",

        """Def. II.
Quantitas motus est mensura ejusdem orta ex Velocitate et quantitate Materiæ
conjunctim.
Motus totius est summa motuum in partibus singulis, adeoq; in corpore dup-
lo majore æquali cum Velocitate duplus est, et dupla cum Velocitate quadruplus.""",

        """Def. III.
Materiæ vis insita est potentia resistendi, qua corpus unumquodq;, quantum in
se est, perseverat in statu suo vel quiescendi vel movendi uniformiter in directum."""
    ]

    for i, definition in enumerate(definitions, 1):
        cur.execute("""
            INSERT INTO verses (
                book_id, chapter, verse_number, text,
                section_type, original_language,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (book_id, 3, i, definition, "definition", "latin", now, now))

    conn.commit()
    conn.close()
    
    total_verses = 1 + len(preface_verses) + len(poetry_verses) + len(definitions)
    print(f"✅ Inserted {total_verses} verses in proper Principia structure:")
    print(f"   Chapter 0 (Title): 1 verse")
    print(f"   Chapter 1 (Præfatio): {len(preface_verses)} verses") 
    print(f"   Chapter 2 (Poetry): {len(poetry_verses)} verses")
    print(f"   Chapter 3 (Definitiones): {len(definitions)} verses")

if __name__ == "__main__":
    setup_proper_structure() 