
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from sqlalchemy import create_engine

from app.db.base import Base
from app.db.models import Product


def seed_products() -> None:
    """Inserisce o aggiorna i 30 prodotti demo per il matching con gli articoli."""

    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    Base.metadata.create_all(bind=engine)

    products = [
        {
            "name": "ETF Azionario Globale Sviluppati",
            "theme": "Azioni globali, mercati sviluppati, diversificazione geografica, MSCI World",
            "description": "ETF azionario diversificato che replica un indice di società quotate nei principali mercati sviluppati.",
            "characteristics": "Esposizione azionaria globale; diversificazione tra paesi e settori; rischio di mercato e cambio; orizzonte di lungo periodo.",
        },
        {
            "name": "ETF Azionario USA Large Cap",
            "theme": "Mercato azionario statunitense, S&P 500, grandi capitalizzazioni, utili societari",
            "description": "ETF che offre esposizione a grandi società quotate negli Stati Uniti.",
            "characteristics": "Concentrazione sul mercato USA; esposizione a società large cap; sensibilità a tassi, utili e ciclo economico; rischio valutario per investitori in euro.",
        },
        {
            "name": "ETF Azionario Europa",
            "theme": "Azioni europee, Eurozona, economia europea, banche, industria",
            "description": "ETF azionario focalizzato sulle società quotate nei mercati europei.",
            "characteristics": "Diversificazione settoriale e geografica europea; sensibilità a crescita economica, politica monetaria BCE e risultati aziendali.",
        },
        {
            "name": "ETF Mercati Emergenti",
            "theme": "Mercati emergenti, Cina, India, Brasile, crescita demografica, valute emergenti",
            "description": "ETF che investe in società quotate nei principali mercati emergenti.",
            "characteristics": "Potenziale di crescita di lungo termine; maggiore rischio politico, valutario e di liquidità; volatilità elevata.",
        },
        {
            "name": "ETF Tecnologia Globale",
            "theme": "Tecnologia, software, cloud computing, trasformazione digitale, innovazione",
            "description": "ETF azionario dedicato alle imprese attive nei servizi e nelle infrastrutture tecnologiche.",
            "characteristics": "Esposizione settoriale; sensibilità alle valutazioni azionarie e ai tassi d'interesse; possibili concentrazioni in grandi società tecnologiche.",
        },
        {
            "name": "ETF Intelligenza Artificiale e Robotica",
            "theme": "Intelligenza artificiale, AI generativa, automazione, robotica, machine learning",
            "description": "ETF tematico dedicato alle imprese che sviluppano o utilizzano tecnologie di intelligenza artificiale e automazione.",
            "characteristics": "Investimento tematico; esposizione a innovazione e crescita; rischio di valutazioni elevate, obsolescenza tecnologica e concentrazione.",
        },
        {
            "name": "ETF Semiconduttori",
            "theme": "Semiconduttori, chip, microprocessori, data center, domanda legata all'AI",
            "description": "ETF azionario focalizzato sui produttori di semiconduttori e sulle aziende della relativa filiera.",
            "characteristics": "Settore ciclico; dipendenza dagli investimenti tecnologici; sensibilità a domanda globale, restrizioni commerciali e catene di fornitura.",
        },
        {
            "name": "ETF Cybersecurity",
            "theme": "Cybersecurity, sicurezza informatica, protezione dati, minacce digitali",
            "description": "ETF tematico dedicato alle imprese che offrono soluzioni di sicurezza informatica.",
            "characteristics": "Esposizione a un settore specializzato; crescita legata alla domanda di protezione digitale; rischio settoriale e valutativo.",
        },
        {
            "name": "ETF Energia Pulita",
            "theme": "Energie rinnovabili, transizione energetica, solare, eolico, decarbonizzazione",
            "description": "ETF azionario dedicato alle società attive nelle energie rinnovabili e nelle tecnologie per la transizione energetica.",
            "characteristics": "Esposizione tematica; dipendenza da incentivi, investimenti e politiche ambientali; sensibilità ai tassi e ai costi delle materie prime.",
        },
        {
            "name": "ETF Sanità Globale",
            "theme": "Sanità, farmaceutica, biotecnologie, dispositivi medici, invecchiamento demografico",
            "description": "ETF che investe in società internazionali operanti nei servizi sanitari e nelle scienze della vita.",
            "characteristics": "Esposizione a un settore con componenti difensive e innovative; rischi regolamentari, clinici e di mercato.",
        },
        {
            "name": "ETF Azionario Dividendi",
            "theme": "Dividendi, reddito azionario, società mature, distribuzione degli utili",
            "description": "ETF che seleziona società azionarie caratterizzate da una politica di distribuzione dei dividendi.",
            "characteristics": "Possibili flussi periodici di distribuzione; dividendi non garantiti; rischio azionario e settoriale; rendimento complessivo non assicurato.",
        },
        {
            "name": "ETF Azionario Minimum Volatility",
            "theme": "Bassa volatilità, investimento difensivo, stabilità relativa, gestione del rischio",
            "description": "ETF che seleziona o pondera titoli azionari con l'obiettivo di ridurre la volatilità rispetto al mercato di riferimento.",
            "characteristics": "Resta esposto al rischio azionario; può sottoperformare nei rialzi; volatilità ridotta non significa protezione del capitale.",
        },
        {
            "name": "Fondo Azionario Small Cap",
            "theme": "Piccole capitalizzazioni, small cap, imprese emergenti, crescita aziendale",
            "description": "Fondo azionario focalizzato su società di dimensioni relativamente contenute.",
            "characteristics": "Potenziale di crescita; liquidità generalmente inferiore rispetto alle large cap; volatilità e rischio d'impresa elevati.",
        },
        {
            "name": "Fondo Azionario Infrastructure",
            "theme": "Infrastrutture, reti elettriche, trasporti, telecomunicazioni, investimenti pubblici",
            "description": "Fondo azionario dedicato alle società che gestiscono o sviluppano infrastrutture essenziali.",
            "characteristics": "Esposizione a infrastrutture tradizionali e moderne; sensibilità a tassi, regolamentazione, debito e investimenti pubblici.",
        },
        {
            "name": "ETF Obbligazionario Governativo Euro",
            "theme": "Titoli di Stato europei, obbligazioni governative, rendimenti, politica monetaria BCE",
            "description": "ETF che investe in titoli di Stato denominati in euro emessi da governi.",
            "characteristics": "Rischio di tasso e duration; rischio di credito sovrano; rendimento influenzato dai tassi e dalla curva dei rendimenti.",
        },
        {
            "name": "ETF BTP Governativi Italiani",
            "theme": "BTP, debito pubblico italiano, spread BTP-Bund, rendimenti sovrani",
            "description": "ETF con esposizione a un paniere di titoli di Stato italiani.",
            "characteristics": "Esposizione al rischio sovrano italiano; sensibilità a spread e tassi d'interesse; rischio di perdita in conto capitale.",
        },
        {
            "name": "ETF Governativi Euro Breve Termine",
            "theme": "Obbligazioni a breve scadenza, duration contenuta, tassi a breve, stabilità relativa",
            "description": "ETF che investe in titoli di Stato denominati in euro con scadenze brevi.",
            "characteristics": "Sensibilità ai tassi generalmente inferiore rispetto a portafogli di lunga durata; rischio di mercato e credito comunque presente.",
        },
        {
            "name": "ETF Corporate Investment Grade Euro",
            "theme": "Obbligazioni corporate, investment grade, credito societario, spread creditizi",
            "description": "ETF obbligazionario investito in titoli societari denominati in euro con merito creditizio investment grade.",
            "characteristics": "Rischio di tasso e di credito; sensibilità agli spread; qualità creditizia mediamente più elevata rispetto all'high yield.",
        },
        {
            "name": "ETF High Yield Globale",
            "theme": "Obbligazioni high yield, credito speculativo, spread, rischio default",
            "description": "ETF obbligazionario con esposizione a obbligazioni societarie con rating inferiore all'investment grade.",
            "characteristics": "Rendimenti potenziali più elevati accompagnati da rischio di credito e default maggiore; sensibilità al ciclo economico.",
        },
        {
            "name": "ETF Obbligazionario Indicizzato all'Inflazione",
            "theme": "Inflazione, obbligazioni indicizzate, potere d'acquisto, rendimenti reali",
            "description": "ETF che investe in obbligazioni i cui pagamenti o valori nominali sono collegati a indici d'inflazione.",
            "characteristics": "Può contribuire a gestire il rischio inflazionistico; valore sensibile ai tassi reali, alla duration e alle aspettative d'inflazione.",
        },
        {
            "name": "Fondo Obbligazionario Globale Flessibile",
            "theme": "Obbligazioni globali, gestione attiva, duration flessibile, allocazione tra emittenti",
            "description": "Fondo obbligazionario a gestione attiva con possibilità di variare l'esposizione tra mercati e tipologie di debito.",
            "characteristics": "Flessibilità gestionale; risultati dipendenti dalle decisioni del gestore; rischi di tasso, credito, valuta e liquidità.",
        },
        {
            "name": "Fondo Monetario Euro",
            "theme": "Mercato monetario, liquidità, strumenti a breve termine, tassi monetari",
            "description": "Fondo che investe prevalentemente in strumenti monetari e obbligazioni a breve scadenza in euro.",
            "characteristics": "Volatilità normalmente contenuta, ma non nulla; rendimento legato ai tassi monetari; capitale non garantito salvo specifiche garanzie contrattuali.",
        },
        {
            "name": "Deposito Vincolato Demo",
            "theme": "Risparmio, deposito bancario, tasso concordato, vincolo temporale",
            "description": "Prodotto dimostrativo di deposito bancario con durata e remunerazione definite contrattualmente.",
            "characteristics": "Remunerazione contrattuale secondo le condizioni previste; possibili limitazioni al prelievo anticipato; verificare garanzie e condizioni applicabili.",
        },
        {
            "name": "Obbligazione Corporate a Tasso Fisso",
            "theme": "Obbligazioni societarie, cedole fisse, rendimento a scadenza, rischio emittente",
            "description": "Obbligazione emessa da una società che prevede pagamenti cedolari a tasso fisso secondo il contratto.",
            "characteristics": "Flussi cedolari prestabiliti salvo insolvenza; rischio di credito, tasso, liquidità e possibile perdita in caso di vendita anticipata.",
        },
        {
            "name": "Obbligazione Corporate a Tasso Variabile",
            "theme": "Obbligazioni a tasso variabile, Euribor, politica monetaria, cedole periodiche",
            "description": "Obbligazione societaria con cedole periodicamente ricalcolate secondo un parametro di riferimento e uno spread.",
            "characteristics": "Cedole variabili nel tempo; rischio di credito e liquidità; andamento influenzato dal parametro di riferimento e dalle condizioni contrattuali.",
        },
        {
            "name": "Obbligazione Governativa Indicizzata all'Inflazione",
            "theme": "Debito sovrano, inflazione, rivalutazione del capitale, rendimenti reali",
            "description": "Titolo di Stato con meccanismi di indicizzazione all'inflazione previsti dalle condizioni di emissione.",
            "characteristics": "Protezione dall'inflazione secondo le regole contrattuali; rischio sovrano e di mercato; prezzo variabile prima della scadenza.",
        },
        {
            "name": "Fondo Bilanciato Prudente",
            "theme": "Asset allocation prudente, diversificazione, obbligazioni prevalenti, contenimento del rischio",
            "description": "Fondo multi-asset con prevalenza obbligazionaria e una componente azionaria contenuta.",
            "characteristics": "Diversificazione tra classi di attivo; esposizione al rischio di mercato; profilo indicativamente prudente, non privo di perdite.",
        },
        {
            "name": "Fondo Bilanciato Dinamico",
            "theme": "Asset allocation dinamica, azioni e obbligazioni, crescita del capitale, diversificazione",
            "description": "Fondo multi-asset con componente azionaria significativa e investimenti obbligazionari complementari.",
            "characteristics": "Equilibrio tra crescita e diversificazione; volatilità dipendente dai pesi di portafoglio e dalle condizioni di mercato.",
        },
        {
            "name": "Fondo Multi-Asset Globale",
            "theme": "Diversificazione globale, azioni, obbligazioni, materie prime, allocazione strategica",
            "description": "Fondo che distribuisce gli investimenti tra diverse classi di attivo e aree geografiche.",
            "characteristics": "Ampia diversificazione; composizione e rischio dipendono dalla strategia; possibili esposizioni valutarie e perdite di mercato.",
        },
        {
            "name": "ETF Oro",
            "theme": "Oro, beni rifugio, incertezza geopolitica, inflazione, diversificazione",
            "description": "Strumento quotato che offre un'esposizione al prezzo dell'oro secondo la struttura e le modalità previste dal prodotto.",
            "characteristics": "Può diversificare un portafoglio; non genera normalmente cedole o dividendi; prezzo volatile e possibile rischio valutario o strutturale.",
        },
    ]

    with Session(engine) as session:
        existing_products = {
            product.name: product
            for product in session.scalars(
                select(Product).where(
                    Product.name.in_([item["name"] for item in products])
                )
            )
        }

        for payload in products:
            product = existing_products.get(payload["name"])

            if product is None:
                session.add(Product(**payload))
                continue

            # Aggiorna i campi descrittivi dei prodotti demo già presenti.
            for field in ("theme", "description", "characteristics"):
                setattr(product, field, payload[field])

        session.commit()


if __name__ == "__main__":
    seed_products()
