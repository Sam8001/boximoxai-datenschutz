"""Build self-contained privacy pages. Standard library only; no network access."""
from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parent
LANGS = ("de", "en", "es", "it", "fr", "nl")
IDS = ("overview", "controller", "local", "family", "account", "ai", "permissions",
       "purchases", "feedback", "security", "retention", "transfers",
       "delete-account", "rights", "website", "updates")
FIELDS = ("backend_hosting", "firestore_region", "feedback_retention",
          "technical_retention", "billing_retention", "transfer_safeguards", "audience", "storage_region")
LABELS = {
    "de": ["Backend-Anbieter und Land", "Firestore-Region", "Frist für Feedback und Kontakt", "Frist für Protokolle und Nutzung", "Frist für Konto und Abrechnung", "bestätigte internationale Übermittlungsgarantien", "Zielgruppe und Minderjährige"],
    "en": ["backend provider and country", "Firestore region", "feedback and contact retention", "logs and usage retention", "account and billing retention", "confirmed international transfer safeguards", "intended audience and minors"],
    "es": ["proveedor y país del servidor", "región de Firestore", "conservación de comentarios y consultas", "conservación de registros y uso", "conservación de cuenta y facturación", "garantías internacionales confirmadas", "público destinatario y menores"],
    "it": ["fornitore e paese del backend", "regione Firestore", "conservazione di feedback e contatti", "conservazione di log e utilizzo", "conservazione di account e contabilizzazione", "garanzie confermate per i trasferimenti internazionali", "destinatari e minori"],
    "fr": ["hébergeur et pays du serveur", "région Firestore", "conservation des commentaires et contacts", "conservation des journaux et usages", "conservation des comptes et facturation", "garanties internationales confirmées", "public visé et mineurs"],
    "nl": ["backendaanbieder en land", "Firestore-regio", "bewaring van feedback en contact", "bewaring van logs en gebruik", "bewaring van account en afrekening", "bevestigde internationale doorgiftewaarborgen", "doelgroep en minderjarigen"],
}
for _language, _label in {
    "de": "Region des verschlüsselten Foto-Speichers", "en": "encrypted photo storage region",
    "es": "región del almacenamiento de fotos cifradas", "it": "regione di archiviazione delle foto crittografate",
    "fr": "région du stockage des photos chiffrées", "nl": "regio voor versleutelde foto-opslag",
}.items():
    LABELS[_language].append(_label)
REQUESTS = {
    "de": ("Löschung für BoximoxAI beantragen", "Antrag auf Konto- und Datenlöschung – BoximoxAI", "Ich möchte die Löschung meines BoximoxAI-Kontos und der zugehörigen personenbezogenen Daten beantragen.\n\nKonto-E-Mail oder Nutzerkennung (soweit bekannt):\n"),
    "en": ("Request deletion for BoximoxAI", "Account and data deletion request – BoximoxAI", "I would like to request deletion of my BoximoxAI account and associated personal data.\n\nAccount email or user ID (if known):\n"),
    "es": ("Solicitar eliminación para BoximoxAI", "Solicitud de eliminación de cuenta y datos – BoximoxAI", "Quiero solicitar la eliminación de mi cuenta de BoximoxAI y de los datos personales asociados.\n\nCorreo de la cuenta o identificador (si lo conozco):\n"),
    "it": ("Chiedi la cancellazione per BoximoxAI", "Richiesta di cancellazione di account e dati – BoximoxAI", "Desidero richiedere la cancellazione del mio account BoximoxAI e dei dati personali associati.\n\nEmail dell'account o identificativo (se noto):\n"),
    "fr": ("Demander la suppression pour BoximoxAI", "Demande de suppression du compte et des données – BoximoxAI", "Je souhaite demander la suppression de mon compte BoximoxAI et des données personnelles associées.\n\nEmail du compte ou identifiant (si connu) :\n"),
    "nl": ("Verwijdering voor BoximoxAI aanvragen", "Verzoek tot verwijdering van account en gegevens – BoximoxAI", "Ik wil verwijdering aanvragen van mijn BoximoxAI-account en bijbehorende persoonsgegevens.\n\nAccountmailadres of gebruikers-ID (indien bekend):\n"),
}
COUNTRY = {"de": "Deutschland", "en": "Germany", "es": "Alemania", "it": "Germania", "fr": "Allemagne", "nl": "Duitsland"}
SKIP = {"de": "Zum Inhalt", "en": "Skip to content", "es": "Ir al contenido", "it": "Vai al contenuto", "fr": "Aller au contenu", "nl": "Naar de inhoud"}
LINKS = (
    ("Google / Firebase", "https://firebase.google.com/support/privacy"),
    ("Firebase Data Processing Terms", "https://firebase.google.com/terms/data-processing-terms/"),
    ("Firebase SCCs", "https://firebase.google.com/terms/firebase-sccs"),
    ("Google Cloud DPA", "https://cloud.google.com/terms/data-processing-addendum"),
    ("Google", "https://policies.google.com/privacy"),
    ("Apple", "https://www.apple.com/legal/privacy/"),
    ("RevenueCat", "https://www.revenuecat.com/privacy/"),
    ("RevenueCat DPA", "https://www.revenuecat.com/dpa"),
    ("OpenAI", "https://openai.com/policies/privacy-policy/"),
    ("OpenAI DPA", "https://openai.com/policies/data-processing-addendum/"),
    ("OpenAI API", "https://developers.openai.com/api/docs/guides/your-data"),
    ("Deepgram", "https://deepgram.com/privacy"),
    ("GitHub", "https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement"),
    ("GitHub Pages", "https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages"),
    ("LDI NRW", "https://www.ldi.nrw.de/"),
)
CSS = """
:root{color-scheme:light dark;--bg:#f5f7fb;--surface:#fff;--ink:#172337;--muted:#46566d;--line:#d5deeb;--accent:#075ec6;--note:#fff4d6}
*{box-sizing:border-box}html{scroll-padding-top:1rem}body{margin:0;background:var(--bg);color:var(--ink);font:1rem/1.7 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
main,header,footer{max-width:56rem;margin:auto;padding:1.5rem}header{padding-top:2.5rem}main{background:var(--surface);border:1px solid var(--line);border-radius:1rem}footer{padding-bottom:3rem}
h1{font-size:clamp(1.8rem,5vw,2.6rem);line-height:1.2;margin:.8rem 0}h2{font-size:1.35rem;line-height:1.4;margin:2.2rem 0 .6rem}p{margin:.8rem 0}a{color:var(--accent);text-underline-offset:.18em;overflow-wrap:anywhere}a:hover{text-decoration-thickness:2px}a:focus-visible{outline:3px solid var(--accent);outline-offset:4px}address{font-style:normal;overflow-wrap:anywhere}
nav ul,.providers{display:flex;flex-wrap:wrap;gap:.5rem 1.2rem;list-style:none;padding:0}nav a{display:inline-block;padding:.25rem 0}.meta{color:var(--muted)}.notice{padding:1rem;border:1px solid #9a700e;border-radius:.7rem;background:var(--note)}.pending{background:var(--note);color:var(--ink);padding:.08rem .2rem;border-bottom:2px dotted #9a700e;overflow-wrap:anywhere}.contact{padding:1rem;background:var(--bg);border-radius:.6rem}.skip{position:absolute;left:1rem;top:-5rem;background:var(--surface);padding:.5rem}.skip:focus{top:1rem}.language-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,18rem),1fr));gap:1rem;list-style:none;padding:0}.language-list li{padding:1rem;border:1px solid var(--line);border-radius:.6rem}.language-list p{margin:.4rem 0}
@media(prefers-color-scheme:dark){:root{--bg:#101722;--surface:#192335;--ink:#eaf0fa;--muted:#b3c1d5;--line:#40516a;--accent:#90c0ff;--note:#3b301b}}
@media(max-width:40rem){main,header,footer{padding:1.1rem}main{border-radius:0;border-left:0;border-right:0}}
@media print{body,main{background:#fff;color:#000}header,main,footer{max-width:none;border:0}nav,.skip{display:none}a{color:#000}h2{break-after:avoid}.contact{break-inside:avoid}.pending{border:1px solid #000}.notice{border:2px solid #000}}
"""


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def confirmation(settings: dict, field: str, lang: str):
    value = settings["confirmed"].get(field)
    if isinstance(value, dict):
        value = value.get(lang)
    return value.strip() if isinstance(value, str) else None


def rich(text: str, settings: dict, content: dict) -> str:
    def replace(match):
        field = match.group(1)
        if field not in FIELDS:
            raise ValueError(f"Unknown field: {field}")
        value = confirmation(settings, field, content["lang"])
        if value:
            return esc(value)
        label = LABELS[content["lang"]][FIELDS.index(field)]
        return f'<mark class="pending">{esc(content["pending"])}: {esc(label)}</mark>'
    # Escape first; only the renderer can add HTML.
    return re.sub(r"\[\[([a-z_]+)\]\]", replace, esc(text))


def email_link(settings: dict, lang: str) -> str:
    label, subject, body = REQUESTS[lang]
    href = f'mailto:{settings["email"]}?subject={quote(subject)}&body={quote(body)}'
    return f'<p><a href="{esc(href)}">{esc(label)}</a></p>'


def contact(settings: dict, lang: str) -> str:
    lines = [settings["controller"], *settings["address"][:-1], COUNTRY[lang]]
    return '<address class="contact">' + '<br>'.join(map(esc, lines)) + '<br>' + f'<a href="mailto:{esc(settings["email"])}">{esc(settings["email"])}</a></address>'


def shell(lang: str, title: str, intro: str, body: str, settings: dict,
          content: dict, translations: dict, pending: bool) -> str:
    links = ''.join(f'<li><a href="{code}.html" lang="{code}" hreflang="{code}"'
                    f'{" aria-current=\"page\"" if code == lang else ""}>{esc(translations[code]["language"])}</a></li>' for code in LANGS)
    alternates = ''.join(f'<link rel="alternate" hreflang="{code}" href="{code}.html">' for code in LANGS)
    robots = '<meta name="robots" content="noindex,nofollow">' if pending else ''
    banner = f'<aside class="notice" role="note">{esc(content["draft"])}</aside>' if pending else ''
    return f'''<!doctype html>
<html lang="{lang}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{esc(intro)}"><meta name="referrer" content="no-referrer">{robots}
<title>{esc(title)}</title>{alternates}<style>{CSS}</style></head>
<body><a class="skip" href="#main">{esc(SKIP[lang])}</a>
<header><a href="index.html">BoximoxAI</a><nav aria-label="{esc(content["languages"])}"><ul>{links}</ul></nav>
<h1>{esc(title)}</h1><p>{esc(intro)}</p><p class="meta">{esc(content["updated_label"])}: <time datetime="{esc(settings["updated"])}">{esc(settings["updated"])}</time></p>{banner}</header>
<main id="main">{body}</main><footer><p>{esc(content["contact_label"])}</p>{contact(settings, lang)}</footer></body></html>
'''


def build() -> tuple[dict[str, str], list[str]]:
    settings = json.loads((ROOT / "source/settings.json").read_text(encoding="utf-8"))
    translations = {code: json.loads((ROOT / f"source/{code}.json").read_text(encoding="utf-8")) for code in LANGS}
    missing = [f'{code}:{field}' for code in LANGS for field in FIELDS if not confirmation(settings, field, code)]
    pages = {}
    for code, content in translations.items():
        if content["lang"] != code or tuple(section["id"] for section in content["sections"]) != IDS:
            raise ValueError(f"Inconsistent language/sections: {code}")
        toc = f'<nav aria-label="{esc(content["contents"])}"><h2>{esc(content["contents"])}</h2><ol>'
        toc += ''.join(f'<li><a href="#{section["id"]}">{esc(section["title"])}</a></li>' for section in content["sections"]) + '</ol></nav>'
        sections = []
        for section in content["sections"]:
            paragraphs = ''.join(f'<p>{rich(p, settings, content)}</p>' for p in section["paragraphs"])
            extra = contact(settings, code) if section["id"] == "controller" else ''
            if section["id"] == "delete-account":
                extra = email_link(settings, code)
            if section["id"] == "updates":
                extra = '<ul class="providers">' + ''.join(f'<li><a href="{esc(url)}" rel="noreferrer">{esc(name)}</a></li>' for name, url in LINKS) + '</ul>'
            sections.append(f'<section aria-labelledby="heading-{section["id"]}"><h2 id="{section["id"]}"><span id="heading-{section["id"]}">{esc(section["title"])}</span></h2>{paragraphs}{extra}</section>')
        pages[f'{code}.html'] = shell(code, content["title"], content["intro"], toc + ''.join(sections), settings, content, translations, bool(missing))
    choices = '<ul class="language-list">' + ''.join(
        f'<li lang="{code}"><h2><a href="{code}.html" hreflang="{code}">{esc(c["language"])}</a></h2><p>{esc(c["title"])}</p><p><a href="{code}.html#delete-account">{esc(REQUESTS[code][0])}</a></p></li>'
        for code, c in translations.items()) + '</ul>'
    pages['index.html'] = shell('en', 'BoximoxAI · Privacy / Datenschutz',
                               'Deutsch · English · Español · Italiano · Français · Nederlands',
                               choices, settings, translations['en'], translations, bool(missing))
    return pages, missing


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.tags = [], [], []
        self.lang = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        if tag == 'html':
            self.lang = attrs.get('lang')
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if 'href' in attrs:
            self.links.append(attrs['href'])
        if 'src' in attrs or any(key.startswith('on') for key in attrs):
            raise ValueError('External/embedded resources or event handlers are not allowed')


def validate(pages: dict[str, str]):
    settings = json.loads((ROOT / "source/settings.json").read_text(encoding="utf-8"))
    parsed = {}
    for name, source in pages.items():
        parser = PageParser()
        parser.feed(source)
        parser.close()
        if parser.lang not in LANGS or len(set(parser.ids)) != len(parser.ids):
            raise ValueError(f'Language or duplicate IDs: {name}')
        if any(tag in parser.tags for tag in ('script', 'iframe', 'form', 'img', 'object', 'embed')):
            raise ValueError(f'Active or embedded content: {name}')
        if '\ufffd' in source or '[[' in source or 'charset="utf-8"' not in source:
            raise ValueError(f'Encoding or unresolved template: {name}')
        if name != 'index.html' and not set(IDS).issubset(parser.ids):
            raise ValueError(f'Missing sections: {name}')
        if any(esc(value) not in source for value in [settings["email"], settings["controller"]]) or 'Vaalser Straße 257C' not in source:
            raise ValueError(f'Missing contact information: {name}')
        parsed[name] = parser
    for name, parser in parsed.items():
        for href in parser.links:
            target = urlsplit(href)
            if target.scheme:
                if target.scheme not in ('https', 'mailto'):
                    raise ValueError(f'Unexpected URL scheme: {href}')
                continue
            page = target.path or name
            if page not in parsed or (target.fragment and target.fragment not in parsed[page].ids):
                raise ValueError(f'Broken link: {name}: {href}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Validate sources and compare generated files')
    parser.add_argument('--release', action='store_true', help='Refuse to build if required confirmations are missing')
    args = parser.parse_args()
    pages, missing = build()
    validate(pages)
    if args.release and missing:
        raise SystemExit('Release blocked: confirm all fields in source/settings.json. Missing: ' + ', '.join(missing))
    if args.check:
        for name, source in pages.items():
            if (ROOT / 'site' / name).read_text(encoding='utf-8') != source:
                raise SystemExit(f'Outdated generated page: {name}')
    else:
        (ROOT / 'site').mkdir(exist_ok=True)
        for name, source in pages.items():
            (ROOT / 'site' / name).write_text(source, encoding='utf-8', newline='\n')
        (ROOT / 'site/.nojekyll').write_text('', encoding='utf-8')
    print(f'{len(pages)} static HTML pages validated; {len(LANGS)} languages, {len(IDS)} sections each; no active content.')
    if missing:
        print('Draft: unresolved operator confirmations: ' + ', '.join(dict.fromkeys(item.split(':', 1)[1] for item in missing)))
    else:
        print('Operator fields complete. Review deployment and provider contracts before publication.')


if __name__ == '__main__':
    main()
