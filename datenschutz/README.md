# BoximoxAI – Datenschutzseiten

Die sechs vollständigen Sprachfassungen liegen als eigenständig lesbare,
statische HTML-Dateien im Ordner **`site`**:

- `site/index.html` – Sprachauswahl
- `site/de.html` – Deutsch
- `site/en.html` – English
- `site/es.html` – Español
- `site/it.html` – Italiano
- `site/fr.html` – Français
- `site/nl.html` – Nederlands

Die Betreiberangaben von Sam Haghnejad sind eingesetzt.
Jede Fassung enthält einen direkt erreichbaren Abschnitt
**`#delete-account`** mit einer E-Mail-Möglichkeit für Löschanfragen. Es wird
keine Nachricht automatisch versendet.

## Aktueller Status: inhaltlich ausgearbeiteter Entwurf

Der Serverstandort Helsinki (Finnland) und die Firestore-Region eur3 sind eingetragen.
Offen sind der Name des Hostinganbieters, Löschfristen, bestätigte
Drittlandgarantien sowie Zielgruppe/Minderjährige sind noch nicht bestätigt.
Der Fotoabgleich ist deaktiviert. Offene Angaben zum Betrieb sind in allen Sprachen **sichtbar markiert**. Eine fertige
Datenschutzerklärung darf diese offenen Stellen nicht enthalten.

Außerdem bestehen tatsächliche Veröffentlichungsthemen im App-/Backend-Code:
Die Kontolöschung fordert jetzt zuerst die Entfernung des Cloud-Inventars und der
Cloud-Fotos an und entfernt anschließend das Firebase-Anmeldekonto. Ein verlässlicher
Prozess für weitere verbundene Credit-, Kauf- und Feedbackdaten muss vor Veröffentlichung
eingerichtet werden. Die App fragt vor KI-Anfragen nach einer Freigabe. Sobald die
Datenschutzseite eine HTTPS-Adresse hat, wird sie beim Flutter-Build als
`--dart-define=BOXIMOXY_PRIVACY_URL=https://...` gesetzt. Dann erscheint der
Link in den Einstellungen und im Freigabedialog.
Details und Belege stehen in `ANALYSE_UND_STORE_HINWEISE.md`.

Die Texte beschreiben die geprüfte lokale Implementierung. Sie bestätigen keine
Produktivkonfiguration und stellen keine Zusage einer Store-Freigabe dar.
Rechtsgrundlagen, Verträge und echte Betriebsfristen müssen zum konkreten Betrieb
passen. Eine abschließende rechtliche Prüfung ist vor Veröffentlichung sinnvoll.

Die Fassungen berücksichtigen die neue optionale Ende-zu-Ende-verschlüsselte
Inventar-Synchronisierung (Protokoll 2). Sie erklären Schlüsselverwaltung,
Wiederherstellung, sichtbare technische Metadaten sowie die Abgrenzung zu
KI-Verarbeitung, lokalen Daten und ZIP-Exporten. Ein erfolgreicher lokaler Test
bestätigt weder die Produktivbereitstellung noch eine unabhängige Sicherheitsprüfung.

## Texte pflegen

Die lesbaren Texte stehen in `source/de.json` bis `source/nl.json`. Zentrale
Betreiberangaben und offene Angaben stehen in `source/settings.json`.

Eine Bestätigung kann entweder ein sprachneutraler String sein (etwa der Name
und das Land eines Hostinganbieters) oder ein Objekt mit allen sechs Sprachen:

```json
{
  "feedback_retention": {
    "de": "Hier die bestätigte und tatsächlich umgesetzte Frist eintragen.",
    "en": "Enter the confirmed retention period actually applied here.",
    "es": "Indica aquí el plazo confirmado y aplicado realmente.",
    "it": "Inserisci qui il periodo confermato ed effettivamente applicato.",
    "fr": "Indique ici la durée confirmée et réellement appliquée.",
    "nl": "Vul hier de bevestigde en daadwerkelijk toegepaste termijn in."
  }
}
```

Diese Beispielsätze sind keine Aufbewahrungsregelung und dürfen nicht als solche
übernommen werden. Nicht einfach eine gewünschte Frist eintragen, wenn sie nicht
auch technisch und organisatorisch durchgesetzt wird.

Nach Änderungen aus `D:\boximoxy_app`:

```powershell
python datenschutz/build_privacy.py
python datenschutz/build_privacy.py --check
```

Der Generator braucht nur die Python-Standardbibliothek. Er greift weder auf
App-Konfigurationen noch auf Secrets, das Internet oder den Server zu.

Die Freigabevariante verweigert die Erstellung, solange Pflichtangaben offen sind:

```powershell
python datenschutz/build_privacy.py --release
```

Erst bei vollständig ausgefüllten Angaben verschwindet der Entwurfshinweis.
Der Schalter prüft Vollständigkeit, nicht die Wahrheit von Betreiberangaben oder
die tatsächliche Umsetzung der Löschprozesse. Das Datum in `settings.json` bei
inhaltlichen Aktualisierungen ebenfalls anpassen.

## Später auf GitHub Pages veröffentlichen

Es wurde **nichts veröffentlicht**, kein Git-Remote eingerichtet und kein Server
geändert. Für eine spätere manuelle Veröffentlichung:

1. Offene Angaben und die genannten Veröffentlichungsthemen abschließen.
2. Die freigegebenen Seiten generieren und prüfen.
3. **Nur den Inhalt von `site`** in das dafür vorgesehene Pages-Repository bzw.
   dessen Veröffentlichungsordner übernehmen. Alle sieben HTML-Dateien gemeinsam
   hochladen; `index.html` verlinkt auf die Sprachdateien. Ein Backend ist unnötig.
4. GitHub Pages für diesen Ordner aktivieren und die öffentlich erreichbaren
   HTTPS-Adressen prüfen.
5. Die passende URL im App Store, in Google Play und in der App hinterlegen.

Beispielhafte URL-Struktur (Owner/Repository erst später festlegen):

```text
https://OWNER.github.io/REPOSITORY/index.html
https://OWNER.github.io/REPOSITORY/de.html
https://OWNER.github.io/REPOSITORY/de.html#delete-account
```

Die Dokumente setzen keine eigenen Cookies und laden keine externen Ressourcen.
Anbieterlinks werden erst beim Anklicken aufgerufen. GitHub selbst verarbeitet
beim Hosting Zugriffsdaten; dies wird in allen Sprachfassungen erläutert.

## Durchgeführte Prüfung

`build_privacy.py --check` prüft sechs Sprachen, identische Themenabdeckung,
Betreiberangaben, Sprachlinks, Abschnittsanker, UTF-8 und das Fehlen aktiver oder
eingebetteter Fremdinhalte. Der Release-Modus muss bei offenen Angaben scheitern.
Es wurden weder echte Käufe noch KI-Anfragen ausgelöst und keine Serverdaten
abgerufen. App- und Backend-Code wurden für diese Aufgabe nur gelesen.
