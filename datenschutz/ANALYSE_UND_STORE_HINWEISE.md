# Interne Analyse und Hinweise zur Veröffentlichung

Stand: 15.11.2026. Grundlage ist der lokale Quellcode in `boximoxy` und
`boximoxy-backend`, nicht eine Prüfung des produktiven Servers oder der Anbieter-
Dashboards. Dieses Dokument ist für den Betreiber bestimmt und gehört **nicht**
in den Pages-Veröffentlichungsordner. Es enthält keine Zugangsdaten.

## 1. Was im Quellcode festgestellt wurde

| Bereich | Daten und Verhalten | Wesentliche Belege |
| --- | --- | --- |
| Lokales Inventar | SQLite/Drift bleibt lokal. Nach ausdrücklicher Einrichtung optionaler geräteübergreifender Abgleich: gesamter Inventarstand und Fotos werden auf dem Gerät Ende-zu-Ende verschlüsselt. | `boximoxy/lib/data/tables.dart`, `lib/features/sync/sync_client.dart`, `sync_crypto.dart` |
| Konto | Firebase Authentication; Google- und Apple-Anmeldung, Verknüpfung, UID/E-Mail und Token. Apple-Reauthentifizierung/Widerruf vor Kontolöschung. | `lib/features/account/firebase_account_service.dart`, `account_screen.dart` |
| Konto löschen | Vor Firebase-Auth-Löschung wird der authentifizierte Sync-Löschendpunkt für Cloud-Inventar und alle zugehörigen Cloud-Fotos aufgerufen. Keine Entschlüsselung erforderlich. Weitere Credit-/RevenueCat-/Feedbackdaten haben weiterhin keinen vollständigen kaskadierenden Löschprozess. | `firebase_account_service.dart`, `sync_controller.dart`, `src/inventory-sync.routes.ts` |
| E2EE-Sync | AES-256-GCM, HKDF-SHA256, zufälliger 256-Bit-Schlüssel, Gerätespeicher Android Keystore/iOS Keychain, manueller Wiederherstellungscode. Firestore enthält ausschließlich opake Inventar-Ciphertexte; der private Bucket enthält verschlüsselte Bilder mit HMAC-adressierten Objektnamen. UID-Zuordnung, IP, Größen, Zeiten, Versionen und öffentliche Schlüsselkennung bleiben sichtbar. Keine rückwirkende Verschlüsselung alter Klartextkopien. | `sync_crypto.dart`, `sync_key_store.dart`, `src/services/inventory-sync.service.ts` |
| KI-Bilder | Ausgewähltes JPEG, Modus und Sprache → eigener Backendprozess → OpenAI. OpenAI-Aufruf mit `store:false`. | `lib/widgets/image_recognition_input.dart`, `lib/features/inventory_api/inventory_client.dart`, `src/services/image-recognition.service.ts` |
| KI-Audio | Versendete Aufnahme → Backend → Deepgram; Transkript → OpenAI. Deepgram-Opt-out für Modellverbesserung ist gesetzt. | `src/app.ts`, `src/services/deepgram.service.ts`, `assistant.service.ts` |
| KI-Kontext | Text, begrenzte Historie, Raum-/Kategorienamen, Sitzung/Entwurf. Bei Erstellung wird ein eingeschränkter Payload verwendet. Nicht behaupten, dass niemals Inventarbezeichnungen übertragen würden. | `lib/features/assistant/assistant_store.dart: context`, `src/services/assistant.service.ts` |
| Audio lokal | Aufnahme zunächst im Speicher; versendete Nachrichten können vorübergehend Audio in der lokalen DB halten. Sitzungsbereinigung und Bereinigung beim DB-Öffnen. | `assistant_audio.dart`, `assistant_controller.dart: dispose`, `app_database.dart: beforeOpen` |
| Diktieren | Native Spracherkennung, kein erzwungenes `onDevice`-Verfahren. Daher keine Offline-/Lokalgarantie für Formulardiktat. | `lib/widgets/name_dictation_button.dart` |
| Käufe | RevenueCat-SDK, Firebase UID als angemeldete App-User-ID, Kauf-/Berechtigungs-/Guthabendaten. Keine zusätzliche E-Mail-Attributsetzung im untersuchten Gateway. | `lib/features/billing/billing_gateway.dart`, `billing_controller.dart` |
| Nutzungsdaten | Firestore-Zähler, Vorgangsstatus, HMAC-Nutzer-/IP-Schlüssel. Pseudonyme bleiben personenbezogen, soweit zuordenbar. | `src/services/usage.service.ts` |
| Credit-Abrechnung | Dokumente enthalten unter anderem UID, Fingerprint, Zustand, Zeitangaben; erfolgreiche `resultJson`-Antworten mit Ablaufwert nach 24 Stunden. Antwort kann Transkript und erkannte Inhalte enthalten. | `src/services/ai-credits.service.ts` |
| Bereinigung | Ein laufender Sweep entfernt abgelaufene Ergebnisinhalte. Er ist keine Garantie einer sekundengenauen Löschung; Metadaten werden dabei nicht komplett gelöscht. | `src/server.ts: sweepUsage`, `ai-credits.service.ts: recover` |
| Kostenprotokolle | Anfrage-/Provider-ID, Modell, Tokens, Audiozeit, Status, Kostenschätzung; Firestore oder stdout. Keine Inhaltsfelder im normalen Kostenereignis. | `src/services/ai-cost.service.ts` |
| Feedback | Öffentlicher Endpunkt mit Rate-Limits; Text, Sprache, Art, UUID, Zeitstempel in privater JSONL-Datei. Nicht automatisch Konto-E-Mail oder Inventar. Kein vollständiger Lösch-/Rotationsjob erkennbar. | `lib/features/feedback/feedback_client.dart`, `src/services/feedback.service.ts` |
| Backup/Drucken | Nutzer wählt Export-/Freigabe-/Druckdienst. ZIP-Sicherungen ohne zusätzliche Passwortverschlüsselung. Lokale Wiederherstellungsdatei mit vorherigem Inventar. | `lib/features/backup/*`, `lib/printing/*` |
| Analyse/Werbung | Keine Firebase-Analytics-/Crashlytics-Integration und kein Werbenetzwerk im geprüften App-Code. RevenueCat-Kaufstatistiken dennoch berücksichtigen. | `pubspec.yaml`, `lib/features/billing/*` |

Die lokal vorhandene Backend-Konfiguration aktiviert Firestore und KI-Credits.
Das ist **kein Nachweis** dafür, dass genau diese Konfiguration produktiv läuft.
Es wurden nur unkritische Konfigurationsschalter ausgewertet; Secrets wurden
nicht in diese Unterlagen übernommen. Keine Serververbindung wurde aufgebaut.

## 2. Vor der Veröffentlichung noch festzulegen

1. **Hosting:** tatsächlicher Anbieter, Vertragspartei, Land des Backendservers,
   Umfang und Frist der Reverse-Proxy-/Host-Protokolle. Aus einer IP-Adresse wird
   hier kein Hostinganbieter oder Serverland geraten.
2. **Firestore:** echte Datenbankregion; außerdem Google/Firebase-Vertrags- und
   Unterauftragsverarbeitungsbedingungen prüfen. Die Firestore-Region sagt allein
   nichts über Firebase Auth oder alle Unterauftragnehmer aus.
3. **Löschkonzept:** konkrete Fristen/Kriterien für Feedback/E-Mail, Logs,
   Nutzungs-/Quotenmetadaten, Kostenereignisse, Firebase- und RevenueCat-Daten.
   Die 24-Stunden-Ergebnisablaufzeit ist kein TTL für sämtliche Datensätze.
   Die bisherige Backend-Dokumentation nennt lediglich eine mögliche Frist für
   bestimmte Metadaten, keinen tatsächlich eingerichteten allgemeinen Löschjob.
4. **Kontolöschung:** den vollständigen Prozess für zuordenbare Daten festlegen
   und umsetzen, einschließlich Daten bei Dienstleistern, Ausnahmen und Umgang
   mit noch offenen Credit-Vorgängen. Ein dauerhaftes `freeUsed`-Merkmal ist
   ebenfalls ein Datensatz. Rechtmäßige Anti-Missbrauchsaufbewahrung prüfen,
   begrenzen und erläutern; nicht pauschal jedes Datum auf Dauer behalten.
5. **KI-Information/Einwilligung:** Apple verlangt die klare Information über
   die Weitergabe an KI-Dritte und ausdrückliche Erlaubnis vor der Weitergabe.
   Die bestehenden kurzen Hinweise und Kamera-/Mikrofonberechtigungen dürfen
   nicht ungeprüft als vollständige Umsetzung betrachtet werden. Die tatsächliche
   Einwilligungsoberfläche und eine etwaige Nachweisführung wurden hier nicht
   neu implementiert. [Apple, 5.1.2(i)](https://developer.apple.com/app-store/review/guidelines/)
6. **Internationale Transfers:** tatsächlich geltende Verträge, Auftragsverarbeitung,
   einschlägige Standardvertragsklauseln bzw. die konkret anwendbare Grundlage
   prüfen. Eine aktive Zertifizierung oder reine EU-Verarbeitung wird nicht
   unterstellt. Gewählte OpenAI-/Deepgram-Vertrags- und Datenoptionen bestätigen.
7. **Zielgruppe:** ausdrücklich festlegen, ob die App sich an Erwachsene, eine
   allgemeine Zielgruppe oder Kinder richtet. Altersangaben in Stores,
   Datenschutzhinweisen und Anbieterbedingungen müssen zusammenpassen. Keine
   Altersgrenze wurde ohne Betreiberentscheidung erfunden.
8. **Datenschutzlink:** im geprüften Settings-/Shop-/Kontocode ist kein fertig
   integrierter öffentlicher Link zu diesen neuen HTML-Seiten vorhanden.
   Nach Festlegung der Pages-URL muss er in der App erreichbar sein. Diese
   Textaufgabe hat App und Backend nicht geändert.

## 3. Orientierung für die Store-Angaben

Dies ist keine automatisch einreichbare oder pauschale Checkbox-Liste. Die
Angaben sind an den tatsächlich veröffentlichten Build, die SDK-Versionen und
aktivierten Provider-Funktionen anzupassen.

| Bereich | Bei der Bewertung berücksichtigen |
| --- | --- |
| Identität/Kontakt | Firebase-Nutzer-ID, Anbieter-ID und E-Mail; Konto-/Sicherheitsbezug. Anmeldung optional für manuelles Inventar. |
| Fotos/Video | Ausgewählte Fotos für KI werden übertragen. Lokal gespeicherte Fotos allein sind von dieser Übertragung zu unterscheiden. Kein Videoanalyse-Feature festgestellt. |
| Audio | Versendete Sprachaufnahmen und Transkripte; native Diktierdienste zusätzlich prüfen. |
| Sonstige Nutzerinhalte | Freitext, Feedback, KI-Nachrichten, Kontext/Entwürfe und erkannte Inhalte. Nicht „keine Datenerhebung“ angeben. |
| Käufe | Kaufhistorie, Transaktions- und Berechtigungsdaten sowie Credits. RevenueCat ordnet Kaufhistorie dem App-User-ID-Kontext zu. |
| Nutzung/Diagnose | Kontingent-/Missbrauchsdaten, Anfragezustand, technische Kostenmetadaten und eventuelle Hostprotokolle. Die konkrete Store-Kategorie nach deren Definition bestimmen. |
| Standort | Haus-/Büronamen sind Nutzereingaben, kein GPS-Tracking. IP-basierte oder von Anbietern abgeleitete Angaben und RevenueCat-Ländermetadaten separat prüfen; keine unbelegte „niemals Standortdaten“-Checkbox. |
| Tracking | Kein Werbe-/Cross-App-Tracking im untersuchten eigenen Code; aktivierte RevenueCat-Integrationen und veröffentlichte SDK-Konfiguration kontrollieren. |

Google unterscheidet „erhoben“, „geteilt“, Verarbeitung durch Dienstleister und
flüchtige Verarbeitung. Eine Dienstleister-Ausnahme von „geteilt“ bedeutet
nicht automatisch, dass keine Erhebung anzugeben ist. Auch kurzfristige
Off-Device-Verarbeitung ist im Fragebogen zu bewerten; der Firestore-Ergebniscache
ist außerdem nicht bloß eine Verarbeitung im Arbeitsspeicher.
[Google Data Safety](https://support.google.com/googleplay/android-developer/answer/10787469)

RevenueCat nennt für Apple insbesondere Kaufhistorie und bei eigener
App-User-ID Nutzerkennungen. Seine Dashboard-Funktionen können außerdem die
Angabe des Zwecks Analytics für Kaufdaten erfordern, auch ohne Firebase Analytics.
[RevenueCat App Privacy](https://www.revenuecat.com/docs/platform-resources/apple-platform-resources/apple-app-privacy)

Google verlangt bei Kontoerstellung einen In-App-Löschweg und eine externe
Möglichkeit, Konto-/Datenlöschung zu beantragen. Die Abschnitte
`de.html#delete-account` usw. bieten den externen Kontaktweg an; der Betreiber
muss E-Mail-Anträge tatsächlich bearbeiten und darf sie nicht auf eine erneute
App-Installation verweisen. Der aktuelle Firebase-only-Löschweg ist getrennt zu
vervollständigen. [Google Kontolöschung](https://support.google.com/googleplay/android-developer/answer/13327111)

Die Datenschutzseite sollte ohne Anmeldung öffentlich, erreichbar und lesbar
sein. Die benannte App/der Betreiber müssen zur Store-Angabe passen. Die hier
generierten HTML-Dateien sind dafür vorgesehen, aber erst nach Abschluss der
offenen Punkte. [Google Nutzerdaten](https://support.google.com/googleplay/android-developer/answer/10144311)

## 4. Anbieter- und Rechtsquellen

Recherche am 15.11.2026; keine Vertragsprüfung im jeweiligen Kundenkonto.

- [EU-Kommission: Informationspflichten und Datenschutz](https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/obligations_en)
- [EU-Kommission: Rechte betroffener Personen](https://commission.europa.eu/law/law-topic/data-protection/information-individuals_en)
- [DSGVO, amtlicher Text](https://eur-lex.europa.eu/eli/reg/2016/679/ojv)
- [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Google Play: Nutzerdaten](https://support.google.com/googleplay/android-developer/answer/10144311)
- [Google Play: Kontolöschung](https://support.google.com/googleplay/android-developer/answer/13327111)
- [Google Play: Data Safety](https://support.google.com/googleplay/android-developer/answer/10787469)
- [Firebase: Privacy and Security](https://firebase.google.com/support/privacy)
- [RevenueCat: App Privacy](https://www.revenuecat.com/docs/platform-resources/apple-platform-resources/apple-app-privacy)
- [OpenAI: API Data Controls](https://developers.openai.com/api/docs/guides/your-data)
- [Deepgram: Model Improvement Partnership / Opt-out](https://developers.deepgram.com/docs/the-deepgram-model-improvement-partnership-program)
- [GitHub Pages: Zugriffsdaten](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages#data-collection)
- [GitHub-Datenschutzhinweise](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement)

Die Hinweise über `store:false` und Deepgram-Opt-out beruhen zusätzlich direkt
auf den tatsächlichen API-Aufrufen im Backend. Sie sind keine Behauptung einer
vollständigen Zero-Data-Retention-Vereinbarung. Die Vertrags- und Sicherheits-
aufbewahrung der Anbieter muss unabhängig davon berücksichtigt werden.
