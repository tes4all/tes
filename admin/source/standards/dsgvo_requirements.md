# Detaillierte Anforderungsliste nach DSGVO (EU-Datenschutz-Grundverordnung)

Diese Liste bricht die gesetzlichen Anforderungen der DSGVO (engl. GDPR) in konkrete Prüfpunkte herunter. Sie unterscheidet sich von der VdS 10010 (Umsetzungs-Richtlinie) durch den direkten Fokus auf die Gesetzestexte (Artikel).

## 1. Grundsätze der Verarbeitung (Art. 5)
| ID | Thema | Anforderung (Gesetzestext abstrahiert) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **1.1** | Rechtmäßigkeit | Personenbezogene Daten müssen auf rechtmäßige Weise, nach Treu und Glauben und transparent verarbeitet werden. | Wir dürfen nichts heimlich machen. Und wir brauchen immer einen Grund (Vertrag, Gesetz oder Einwilligung). | Auf welche Rechtsgrundlage (z.B. Vertragserfüllung, berechtigtes Interesse, Einwilligung) stützen Sie die Verarbeitung jeder Datenkategorie? |
| **1.2** | Zweckbindung | Daten dürfen nur für festgelegte, eindeutige und legitime Zwecke erhoben werden. | Daten, die für das Gewinnspiel erhoben wurden, darf man nicht für Werbung nutzen (ohne extra Erlaubnis). | Ist sichergestellt, dass Daten nicht für Zwecke verwendet werden, die mit dem ursprünglichen Erhebungszweck unvereinbar sind? |
| **1.3** | Datenminimierung | Daten müssen dem Zweck angemessen und auf das notwendige Maß beschränkt sein. | Keine "Vorratsdatenspeicherung" nach dem Motto "Man könnte es ja mal brauchen". Nur Pflichtfelder abfragen. | Überprüfen Sie Eingabeformulare regelmäßig darauf, ob wirklich nur zwingend notwendige Daten abgefragt werden? |
| **1.4** | Richtigkeit | Daten müssen sachlich richtig und auf dem neuesten Stand sein. Unrichtige Daten sind zu löschen/berichtigen. | Wenn der Kunde umzieht, muss die Adresse geändert werden. Keine Datenbankleichen. | Gibt es Prozesse zur Aktualisierung von Stammdaten, um sicherzustellen, dass keine veralteten Informationen genutzt werden (z.B. Postrückläufer-Bearbeitung)? |
| **1.5** | Speicherbegrenzung | Speicherung nur so lange, wie es für den Zweck erforderlich ist. | Löschfristen beachten! Bewerbungsunterlagen nach 6 Monaten weg. Videoaufnahmen nach 48/72h weg. | Werden Daten, deren Aufbewahrungsfrist abgelaufen ist (z.B. abgelehnte Bewerber), automatisch oder prozessual gelöscht? |
| **1.6** | Integrität & Vertraulichkeit | Schutz vor unbefugter Verarbeitung und unbeabsichtigtem Verlust durch TOMs. | IT-Sicherheit ist Pflicht, keine Kür. Wer schlampt, handelt gesetzwidrig. (Siehe Art. 32). | Sind technische Maßnahmen (Verschlüsselung, Zugriffsschutz) implementiert, die ein dem Risiko angemessenes Schutzniveau gewährleisten? |

## 2. Rechte der Betroffenen (Art. 12-22)
| ID | Thema | Anforderung (Gesetzestext abstrahiert) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **2.1** | Transparenz (Art. 13/14) | Informationspflicht zum Zeitpunkt der Erhebung (Name Verantwortlicher, Zweck, Empfänger, Rechte). | Die "Datenschutzerklärung" muss da sein, BEVOR der Kunde seine Daten eingibt (Webseite, Vertrag). | Erhält der Betroffene zum Zeitpunkt der Datenerhebung aktiv alle Pflichtinformationen gemäß Art. 13 DSGVO (z.B. Merkblatt, Link)? |
| **2.2** | Auskunftsrecht (Art. 15) | Betroffene haben Recht auf Bestätigung und Kopie aller verarbeiteten Daten. Frist: 1 Monat. | Wenn Herr Müller schreibt "Was wisst ihr über mich?", muss der Laden laufen. Alle E-Mails, DB-Einträge, Notizen. | Können Sie innerhalb eines Monats eine vollständige Kopie aller personenbezogenen Daten einer Person aus allen Systemen exportieren? |
| **2.3** | Recht auf Löschung (Art. 17) | "Recht auf Vergessenwerden", wenn Zweck entfallen oder Einwilligung widerrufen. Ausnahme: Aufbewahrungspflichten. | Kunde kündigt -> Daten müssen weg (außer Rechnungen für Finanzamt). Sperrvermerk setzen! | Wie wird sichergestellt, dass bei einem legitimen Löschersuchen die Daten auch aus Backups oder Drittsystemen (z.B. Newsletter-Tool) verschwinden? |
| **2.4** | Widerrufsrecht (Art. 7) | Einwilligung muss so einfach widerrufen werden können, wie sie erteilt wurde. | Newsletter-Abmeldung muss 1 Klick sein. Wer anrufen muss zum Kündigen, verstößt gegen DSGVO. | Ist der Widerruf einer Einwilligung (z.B. für Marketing) technisch so einfach umsetzbar wie die Erteilung (One-Click-Unsubscribe)? |

## 3. Pflichten des Verantwortlichen & Auftragsverarbeiters
| ID | Thema | Anforderung (Gesetzestext abstrahiert) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **3.1** | Verantwortung (Art. 24) | Der Verantwortliche muss geeignete TOMs umsetzen und *nachweisen* können (Rechenschaftspflicht). | "Wir haben das immer schon so gemacht" zählt nicht. Dokumentieren, Protokollieren, Beweisen. | Liegen dokumentierte Nachweise (z.B. Logfiles, Wartungsprotokolle) vor, die belegen, dass die Sicherheitsmaßnahmen dauerhaft wirksam sind? |
| **3.2** | Privacy by Design (Art. 25) | Datenschutz durch Technikgestaltung und datenschutzfreundliche Voreinstellungen. | Häkchen dürfen nicht vorausgewählt sein (Opt-In statt Opt-Out). Profil darf nicht öffentlich sein per Default. | Sind Software-Systeme so vorkonfiguriert, dass standardmäßig nur die nötigsten Daten verarbeitet werden ("Privacy by Default")? |
| **3.3** | Auftragsverarbeiter (Art. 28) | Einsatz nur von Dienstleistern, die hinreichend Garantien bieten. Vertragspflicht. | Wer unsere Daten verarbeitet (Hoster, Aktenvernichter), braucht einen Knebelvertrag (AVV). Wir müssen ihn kontrollieren. | Liegen für alle externen Dienstleister gültige AV-Verträge vor und haben Sie deren Zuverlässigkeit vor Vertragsabschluss geprüft? |
| **3.4** | Verzeichnis (Art. 30) | Führung eines Verzeichnisses aller Verarbeitungstätigkeiten (VVT). | Das Inventar der Prozesse. Was machen wir wo mit wem? Muss für die Behörde bereitliegen. | Ist das Verzeichnis der Verarbeitungstätigkeiten (VVT) aktuell und enthält es alle Pflichtangaben (z.B. Löschfristen, Empfänger)? |

## 4. Sicherheit personenbezogener Daten (Art. 32)
| ID | Thema | Anforderung (Gesetzestext abstrahiert) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **4.1** | Angemessenheit | Maßnahmen müssen dem Risiko angemessen sein (Stand der Technik, Implementierungskosten). | Wir müssen kein Fort Knox bauen für eine E-Mail-Adresse, aber Patientendaten brauchen High-End-Schutz. | Wurde das Schutzniveau der IT-Maßnahmen (Verschlüsselung, Backups) explizit gegen das Risiko für die Betroffenen abgewogen? |
| **4.2** | Pseudonymisierung | Trennung von Identifikationsdaten und Nutzdaten wo immer möglich. | In der Test-Datenbank dürfen keine echten Namen stehen. "Kunde 12345" statt "Max Müller". | Werden personenbezogene Daten in Test- und Entwicklungsumgebungen konsequent anonymisiert oder pseudonymisiert? |
| **4.3** | Wiederherstellbarkeit | Fähigkeit, die Verfügbarkeit und den Zugang rasch wiederherzustellen. | Backup & Disaster Recovery. Wenn der Server brennt, dürfen die Kundendaten nicht weg sein. | Existiert ein getestetes Konzept, um die Verfügbarkeit der personenbezogenen Daten nach einem physischen oder technischen Zwischenfall zeitnah wiederherzustellen? |
| **4.4** | Überprüfung (Evaluierung) | Verfahren zur regelmäßigen Überprüfung, Bewertung und Evaluierung der Wirksamkeit der TOMs. | Nicht einmal einrichten und vergessen. Jedes Jahr prüfen: "Ist die Firewall noch dicht?". Penetrationstests. | Gibt es einen festgelegten Prozess zur regelmäßigen Evaluierung (Audit/Test) der Wirksamkeit aller technischen Schutzmaßnahmen? |

## 5. Datenschutz-Folgenabschätzung & Meldepflichten
| ID | Thema | Anforderung (Gesetzestext abstrahiert) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **5.1** | Meldung Panne (Art. 33) | Meldung von Verletzungen an die Behörde binnen 72 Std., es sei denn, Risiko ist unwahrscheinlich. | Laptop weg, USB-Stick weg, Hacking? Sofort Prozess starten. Uhr tickt (am Wochenende!). | Ist ein Notfallprozess etabliert, der sicherstellt, dass Datenpannen innerhalb von 72 Stunden erkannt, bewertet und ggf. gemeldet werden? |
| **5.2** | Info Betroffene (Art. 34) | Benachrichtigung der Betroffenen bei *hohem* Risiko für deren Rechte. | Wenn Kreditkartendaten geklaut wurden: Wir müssen alle Kunden anschreiben. "Achtung, Konto prüfen!". | Liegen Textbausteine oder Vorlagen bereit, um im Ernstfall schnell und transparent die betroffenen Personen informieren zu können? |
| **5.3** | DSFA (Art. 35) | Datenschutz-Folgenabschätzung bei voraussichtlich hohem Risiko (z.B. Videoüberwachung, Gesundheitsdaten). | Bevor wir KI oder Kameras einführen: Große Risikoanalyse machen. "Was könnte schiefgehen?". | Wurde für risikoreiche Verarbeitungen (z.B. umfangreiche Kameraüberwachung, Profiling) eine dokumentierte Datenschutz-Folgenabschätzung durchgeführt? |

## 6. Datenschutzbeauftragter (Art. 37-39)
| ID | Thema | Anforderung (Gesetzestext abstrahiert) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **6.1** | Benennung | Pflicht zur Benennung, wenn Kerntätigkeit umfangreiche Überwachung/sensible Daten ODER >19 MA ständig Daten verarbeiten (DE-Sonderregel § 38 BDSG). | Zählen: Wie viele Leute sitzen am PC und haben Zugriff auf Kundendaten? >19 -> DSB Pflicht. | Haben Sie geprüft, ob die gesetzlichen Schwellenwerte für die Benennung eines Datenschutzbeauftragten überschritten sind, und diesen ggf. bestellt? |
| **6.2** | Einbindung | DSB muss ordnungsgemäß und frühzeitig in alle relevanten Fragen eingebunden werden. | Nicht erst fragen, wenn das Kind im Brunnen liegt. Bei neuen Projekten (neue Software) sofort DSB fragen. | Wird der Datenschutzbeauftragte bereits in der Planungsphase neuer Projekte oder IT-Systeme konsultiert? |
