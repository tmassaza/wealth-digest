import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY non trovata. "
        "Controlla di aver creato il file .env nella root del progetto."
    )

# Inizializzo il client Gemini
client = genai.Client(api_key=api_key)


customer_profile = """
Cliente con profilo di rischio moderato.

È interessato ai mercati europei, al settore energetico
e alle obbligazioni governative.

Nel portafoglio detiene anche titoli del settore energetico.

Preferisce ricevere informazioni riguardanti società,
mercati e fattori macroeconomici che possono influenzare
i suoi investimenti.
"""



articles = [
    {
        "id": 1,
        "title": "Il prezzo del petrolio sale dopo nuove tensioni geopolitiche",
        "date": "2026-08-24",
        "score": 0.94,
        "content": """
Il prezzo del petrolio è aumentato nelle ultime sedute
in seguito a nuove tensioni geopolitiche che hanno
alimentato i timori sulla disponibilità futura di greggio.

Gli operatori stanno monitorando l'evoluzione della situazione
e le possibili conseguenze sull'offerta globale.
""",
        "url": "https://example.com/article-1",
    },
    {
        "id": 2,
        "title": "Nuove prospettive per il settore energetico europeo",
        "date": "2026-08-23",
        "score": 0.89,
        "content": """
Il settore energetico europeo continua a essere influenzato
dall'evoluzione dei prezzi dell'energia e dalle politiche
comunitarie sulla transizione energetica.

Gli analisti stanno rivedendo le prospettive di alcune
società del comparto.
""",
        "url": "https://example.com/article-2",
    },
    {
        "id": 3,
        "title": "BCE mantiene i tassi e segnala cautela sull'inflazione",
        "date": "2026-08-22",
        "score": 0.84,
        "content": """
La Banca Centrale Europea ha mantenuto invariati i tassi
di interesse, sottolineando che l'evoluzione dell'inflazione
rimane un elemento centrale nelle prossime decisioni
di politica monetaria.
""",
        "url": "https://example.com/article-3",
    },
    {
        "id": 4,
        "title": "I mercati azionari europei chiudono in rialzo",
        "date": "2026-08-21",
        "score": 0.81,
        "content": """
I principali indici azionari europei hanno registrato
una seduta positiva, sostenuti dai titoli industriali
ed energetici.
""",
        "url": "https://example.com/article-4",
    },
    {
        "id": 5,
        "title": "Nuovi investimenti nelle infrastrutture energetiche",
        "date": "2026-08-20",
        "score": 0.77,
        "content": """
Diversi operatori europei hanno annunciato nuovi investimenti
nelle infrastrutture energetiche, con particolare attenzione
alle reti e alla sicurezza dell'approvvigionamento.
""",
        "url": "https://example.com/article-5",
    },
]



def build_prompt(profile: str, selected_articles: list[dict]) -> str:
    """
    Costruisce il prompt da inviare al modello generativo.
    """

    articles_text = ""

    for article in selected_articles:
        articles_text += f"""
ARTICOLO

ID: {article["id"]}
Titolo: {article["title"]}
Data: {article["date"]}
Score di rilevanza: {article["score"]}
URL: {article["url"]}

Contenuto:
{article["content"]}

----------------------------
"""

    prompt = f"""
Sei un assistente che prepara notifiche finanziarie
personalizzate per i clienti di una società di investimento.

PROFILO DEL CLIENTE

{profile}


ARTICOLI SELEZIONATI

{articles_text}


COMPITO

Genera una notifica personalizzata per questo cliente.

Per ogni articolo devi fornire:

1. Titolo
2. Data
3. Un sommario chiaro e conciso della notizia
4. Una spiegazione specifica del motivo per cui
   la notizia è rilevante per questo cliente
5. Il link originale dell'articolo


REGOLE

- Usa esclusivamente le informazioni fornite.
- Non inventare informazioni.
- Non modificare i titoli.
- Non modificare le date.
- Non inventare dati, numeri o eventi.
- Non dare consigli di investimento.
- Non suggerire di comprare, vendere o mantenere strumenti finanziari.
- Spiega la rilevanza della notizia facendo riferimento
  esclusivamente al profilo del cliente.
- Mantieni un linguaggio professionale e comprensibile.
- Tratta ogni articolo separatamente.
- Non aggiungere informazioni che non siano presenti
  negli articoli o nel profilo del cliente.


FORMATO DELLA RISPOSTA

# Notifica personalizzata

## 1. [Titolo articolo]
Data: [data]

Sommario: 
[sommario]

Perché è rilevante per il cliente:
[spiegazione]

Fonte: [URL]

Ripeti lo stesso formato per tutti gli articoli.
"""

    return prompt



def generate_notification(
    profile: str,
    selected_articles: list[dict],
) -> str:
    """
    Invia profilo cliente e articoli a Gemini
    e restituisce la notifica generata.
    """

    prompt = build_prompt(profile, selected_articles)

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError("Gemini non ha restituito alcun testo.")

    return response.text


def main() -> None:
    print()
    print("=" * 80)
    print("GENERAZIONE NOTIFICA PERSONALIZZATA")
    print("=" * 80)
    print()

    print(f"Cliente: profilo di rischio moderato")
    print(f"Articoli selezionati: {len(articles)}")
    print()
    print("Invio richiesta a Gemini...")
    print()

    notification = generate_notification(
        profile=customer_profile,
        selected_articles=articles,
    )

    print("=" * 80)
    print("NOTIFICA GENERATA")
    print("=" * 80)
    print()

    print(notification)

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()