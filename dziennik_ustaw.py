"""
Monitoring Dziennika Ustaw pod kątem przedsiębiorców.

Pobiera akty ogłoszone danego dnia z API ELI (Kancelaria Sejmu),
analizuje je modelem Claude i zwraca gotowe body HTML do maila.

Optymalizacja kosztów — dwuetapowy filtr:
  ETAP 1: jedno tanie zapytanie z samymi tytułami -> lista kandydatów
  ETAP 2: pełna treść pobierana i analizowana tylko dla kandydatów

Wymagania:  pip install requests anthropic
Zmienna środowiskowa: ANTHROPIC_API_KEY
"""
from lib.mail import *
from lib.mail_config import MAIL_TO
import os
import re
import datetime as dt
from datetime import datetime, timedelta

import requests
from anthropic import Anthropic

API = "https://api.sejm.gov.pl/eli/acts"
MODEL = "claude-sonnet-5"
MAX_ZNAKOW_TEKSTU = 40_000   # limit treści aktu wysyłanej do modelu


# --------------------------------------------------------------------------
# Pobieranie danych z API ELI
# --------------------------------------------------------------------------

def _tekst(odp) -> str:
    """Pierwszy blok tekstowy z odpowiedzi (pomija bloki myślenia)."""
    return next(b.text for b in odp.content if b.type == "text").strip()


def _akty_z_dnia(data: dt.date) -> list[dict]:
    """Zwraca listę aktów Dz.U. ogłoszonych danego dnia."""
    r = requests.get(f"{API}/DU/{data.year}", timeout=30)
    r.raise_for_status()
    items = r.json().get("items", [])
    return [a for a in items if a.get("promulgation") == data.isoformat()]


def _tresc_aktu(akt: dict) -> str:
    """Pobiera tekst aktu (HTML -> czysty tekst). Pusty string gdy brak."""
    url = f"{API}/DU/{akt['year']}/{akt['pos']}/text.html"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
    except requests.RequestException:
        return ""
    tekst = re.sub(r"<[^>]+>", " ", r.text)
    tekst = re.sub(r"\s+", " ", tekst).strip()
    return tekst[:MAX_ZNAKOW_TEKSTU]


# --------------------------------------------------------------------------
# ETAP 1 — tani triage po samych tytułach
# --------------------------------------------------------------------------

PROMPT_TRIAGE = """Poniżej lista aktów prawnych ogłoszonych dziś w Dzienniku Ustaw RP.

Wskaż te, które MOGĄ dotyczyć przedsiębiorców — nakładać obowiązki lub zmieniać
warunki prowadzenia działalności: podatki, ZUS, kadry i płace, e-fakturowanie,
obrót towarowy i celny, licencje i koncesje, ochrona danych, raportowanie,
zamówienia publiczne, branżowe wymogi techniczne itp.

Pomijaj akty czysto wewnątrzadministracyjne: wybory lokalne, odznaczenia,
nominacje, sprawy wojskowe i organizacja urzędów bez wpływu na firmy.

W razie wątpliwości WŁĄCZ akt do listy — pełną treść i tak zweryfikujemy dalej.

LISTA:
{lista}

Odpowiedz wyłącznie numerami pozycji z listy, oddzielonymi przecinkami
(np. "2, 5, 7"). Jeśli żaden akt nie kwalifikuje się, odpowiedz: BRAK"""


def _wybierz_kandydatow(klient: Anthropic, akty: list[dict]) -> list[dict]:
    """Jedno zapytanie na wszystkie tytuły. Zwraca odfiltrowane akty."""
    if not akty:
        return []

    lista = "\n".join(
        f"{i}. [{a.get('type', '—')}] {a.get('title', '—')}"
        for i, a in enumerate(akty, start=1)
    )

    odp = klient.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": PROMPT_TRIAGE.format(lista=lista)}],
    )
    wynik = _tekst(odp)
    if wynik.upper().startswith("BRAK"):
        return []

    numery = {int(n) for n in re.findall(r"\d+", wynik) if 1 <= int(n) <= len(akty)}
    return [a for i, a in enumerate(akty, start=1) if i in numery]


# --------------------------------------------------------------------------
# ETAP 2 — pełna analiza tylko dla kandydatów
# --------------------------------------------------------------------------

PROMPT_ANALIZA = """Jesteś analitykiem prawno-biznesowym w firmie IT.

Oceń poniższy akt prawny z Dziennika Ustaw RP.

Pozycja: Dz.U. {rok} poz. {pos}
Typ: {typ}
Tytuł: {tytul}
Data ogłoszenia: {ogloszenie}
Wejście w życie: {wejscie}

TREŚĆ AKTU:
{tresc}

KROK 1. Zweryfikuj, czy akt realnie dotyczy przedsiębiorców — nakłada obowiązki,
zmienia procedury, koszty lub warunki prowadzenia działalności.
Jeśli po lekturze treści okaże się, że NIE dotyczy, odpowiedz jednym słowem: POMIŃ

KROK 2. Jeśli dotyczy, zwróć fragment HTML (bez <html> i <body>)
w dokładnie takiej strukturze:

<h3>Dz.U. {rok} poz. {pos} — [skrócony tytuł]</h3>
<p><strong>Wchodzi w życie:</strong> [data lub zasada vacatio legis]</p>
<p><strong>Streszczenie:</strong> [3-5 zdań własnymi słowami, bez cytatów]</p>
<p><strong>Wpływ na przedsiębiorców:</strong> [kogo dotyczy — branża i wielkość
firmy, jakie nowe obowiązki lub ułatwienia, od kiedy, ryzyko przy
niedostosowaniu]</p>
<p><strong>Szansa sprzedażowa IT:</strong> [jakie rozwiązanie informatyczne
ułatwiłoby spełnienie wymogów, do kogo kierować ofertę — konkretna rola
decyzyjna, jak pilna jest potrzeba w świetle vacatio legis]</p>

Nie dodawaj nic poza tym fragmentem. Pisz zwięźle i konkretnie."""


def _analizuj(klient: Anthropic, akt: dict) -> str | None:
    """Zwraca fragment HTML albo None, gdy akt nie dotyczy przedsiębiorców."""
    odp = klient.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": PROMPT_ANALIZA.format(
                rok=akt["year"],
                pos=akt["pos"],
                typ=akt.get("type", "—"),
                tytul=akt.get("title", "—"),
                ogloszenie=akt.get("announcementDate", "—"),
                wejscie=akt.get("entryIntoForce", "—"),
                tresc=_tresc_aktu(akt) or "[nie udało się pobrać treści]",
            ),
        }],
    )
    wynik = _tekst(odp)
    if wynik.upper() == "POMIŃ":
        return None

    link = f"{API}/DU/{akt['year']}/{akt['pos']}/text.pdf"
    return f'{wynik}<p><a href="{link}">Pełny tekst aktu (PDF)</a></p>'


# --------------------------------------------------------------------------
# Funkcja główna
# --------------------------------------------------------------------------

def raport_html(data: dt.date | None = None) -> str | None:
    """
    Zwraca body HTML z analizą aktów ogłoszonych danego dnia.
    Domyślnie: wczoraj. Zwraca None, gdy nic nie dotyczy przedsiębiorców.
    """
    data = data or dt.date.today() - dt.timedelta(days=1)
    klient = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    akty = _akty_z_dnia(data)
    kandydaci = _wybierz_kandydatow(klient, akty)

    sekcje = [html for a in kandydaci if (html := _analizuj(klient, a))]

    if not sekcje:
        return None

    return f"""<div style="font-family:system-ui,sans-serif;max-width:680px;line-height:1.55">
<h2>Dziennik Ustaw — {data.strftime('%d.%m.%Y')}</h2>
<p>Ogłoszonych aktów: {len(akty)} &middot; wstępnie zakwalifikowanych:
{len(kandydaci)} &middot; istotnych dla przedsiębiorców: {len(sekcje)}.</p>
<hr>
{'<hr>'.join(sekcje)}
</div>"""


MAIL_SUBJECT = 'Nowe akty w Dzienniku Ustaw'
REFDATE = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

html = raport_html()
header = f'<h2>Ustawy i rozporządzenia z potencjałem sprzedaży - {REFDATE}</h2>'

msg_html = f'<html><head>{header}</head><body>{html}</body></html>'
smtp_client = SMTP()
smtp_client.send_email(MAIL_TO, MAIL_SUBJECT + REFDATE, msg_html_content=msg_html)
smtp_client.close()