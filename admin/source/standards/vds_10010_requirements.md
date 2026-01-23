# Detaillierte Anforderungsliste nach VdS 10010 für KMU

Diese Liste bricht die VdS-Richtlinie 10010 ("Umsetzung der DSGVO für KMU") in granulare Maßnahmen auf.

## 1. Governance & Verantwortlichkeit
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **1.1** | Datenschutzbeauftragter (DSB) | Prüfung der Benennungspflicht (Art. 37 DSGVO / § 38 BDSG). Benennung und Veröffentlichung. | Brauchen wir einen? (Regel: >19 MA ständig mit Daten beschäftigt? Oder Kerngeschäft Datenhandel?). Wenn ja: Bestellen und an Behörde melden. | Wurde schriftlich geprüft (und das Ergebnis dokumentiert), ob ein Datenschutzbeauftragter bestellt werden muss? |
| **1.2** | Rechenschaftspflicht | Nachweis der Einhaltung aller Grundsätze (Art. 5 Abs. 2 DSGVO). | "Dokumentiere oder stirb". Wir müssen beweisen können, dass wir sauber arbeiten. | Liegt ein zentraler Datenschutz-Ordner (digital/analog) vor, der alle Nachweise bündelt? |
| **1.3** | Datenschutz-Leitlinie | Verpflichtung der Leitung auf Datenschutzgrundsätze. | Policy: "Wir verkaufen keine Kundendaten". | Ist der Umgang mit personenbezogenen Daten in einer für alle Mitarbeiter verbindlichen Richtlinie geregelt? |

## 2. Verzeichnis von Verarbeitungstätigkeiten (VVT)
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **2.1** | Vollständigkeit | Erfassung aller Verfahren (Art. 30 DSGVO). Personal, Vertrieb, Buchhaltung, Marketing, IT-Betrieb. | Liste aller Tätigkeiten: "Lohnabrechnung", "Kundenverwaltung", "Videoüberwachung", "Webshop". | Sind wirklich ALLE Prozesse im VVT erfasst, auch Nebentätigkeiten wie "WhatsApp-Kommunikation" oder "Videoüberwachung"? |
| **2.2** | Inhaltliche Tiefe | Angabe von Zweck, Rechtsgrundlage, Datenkategorien, Empfängern, Löschfristen, TOMs. | Warum machen wir das? Welche Daten? Wer kriegt sie? Wann löschen wir? Wie schützen wir sie? | Enthält das VVT zu jedem Verfahren eine konkrete Löschfrist (z.B. "10 Jahre nach Vertragsende") und eine Rechtsgrundlage? |
| **2.3** | Aktualität | Regelmäßige Überprüfung und Aktualisierung des VVT. | Wenn wir ein neues Tool (Slack, Zoom) einführen, muss das ins Verzeichnis. | Wann wurde das Verzeichnis der Verarbeitungstätigkeiten zuletzt auf Aktualität geprüft (Review-Datum)? |

## 3. Auftragsverarbeitung (AVV)
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **3.1** | Identifikation AV | Identifizierung aller Auftragsverarbeiter (Art. 28 DSGVO). Keine "Funktionsübertragung". | Wer verarbeitet Daten für uns? Hoster, Cloud-Provider, Lohnbüro, Aktenvernichter, IT-Wartung. | Gibt es eine vollständige Liste aller externen Dienstleister, die Zugriff auf personenbezogene Daten haben könnten? |
| **3.2** | Vertragsabschluss | Abschluss konformer AV-Verträge VOR Beginn der Verarbeitung. | Erst Vertrag unterschreiben, dann Daten hochladen. Vertrag muss Art. 28 Inhalte haben (Weisungsgebundenheit, Kontrollrechte). | Liegen für alle in der Liste identifizierten Dienstleister unterschriebene AV-Verträge (oder online bestätigte DPA) vor? |
| **3.3** | Kontrolle | Überprüfung der Garantien der AV (Zertifikate, Audits). | Nicht blind vertrauen. Zertifikat (ISO 27001) zeigen lassen oder Fragebogen schicken. | Wie kontrollieren Sie (mindestens jährlich), ob Ihre Auftragsverarbeiter die vereinbarten Sicherheitsstandards tatsächlich einhalten? |

## 4. Sicherheit der Verarbeitung (TOMs)
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **4.1** | Risikobasiertheit | Auswahl der Maßnahmen nach Risiko für die Rechte und Freiheiten natürlicher Personen. | Gesundheitsdaten brauchen mehr Schutz als B2B-Telefonnummern. | Wurden die technischen Maßnahmen speziell auf den Schutzbedarf der verarbeiteten Personendaten abgestimmt? |
| **4.2** | Verschlüsselung & Pseudonymisierung | Verschlüsselung von Laptops, Datenträgern, Übertragungswegen. | BitLocker an! SSL/TLS auf Webseite! E-Mail-Verschlüsselung. | Sind alle mobilen Endgeräte (Laptops, Tablets, Smartphones), die Personendaten speichern, festplattenverschlüsselt? |
| **4.3** | Vertraulichkeit, Integrität, Verfügbarkeit | Sicherstellung der Schutzziele (siehe VdS 10000). | Siehe VdS 10000: Zugriffsschutz, Backup, Virenscan. | (Verweis auf VdS 10000 Audit-Fragen) |
| **4.4** | Belastbarkeit der Systeme | Systeme müssen Lastspitzen aushalten (DDoS Schutz). Wiederherstellbarkeit. | Datenschutz heißt auch: Daten sind da, wenn man sie braucht. | Sind die Systeme gegen Verfügbarkeitsangriffe (z.B. Ransomware) gehärtet? |
| **4.5** | Evaluierung | Verfahren zur regelmäßigen Überprüfung der Wirksamkeit der TOMs. | Testen, ob die Verschlüsselung wirklich an ist. Penetrationstests. | Wie und wie oft testen Sie technisch, ob die getroffenen Sicherheitsmaßnahmen (z.B. Backup, Firewall) wirksam sind? |

## 5. Betroffenenrechte & Informationspflichten
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **5.1** | Information (Art. 13/14) | Information bei Erhebung (Datenschutzerklärung). Transparent, verständlich, leicht zugänglich. | Webseite muss DSE haben. E-Mail-Footer Link zur DSE. Arbeitsvertrag Info-Blatt. Kamera-Hinweisschild. | Erhalten Kunden und Mitarbeiter zum Zeitpunkt der Datenerhebung aktiv die gesetzlich geforderten Informationen (Datenschutzhinweise)? |
| **5.2** | Auskunft (Art. 15) | Prozess zur Beantwortung von Auskunftsanfragen innerhalb 1 Monat. Vollständige Kopie der Daten. | Wenn Kunde fragt, müssen wir liefern. "Alle E-Mails, alle DB-Einträge". Man muss wissen, wie man das exportiert. | Gibt es einen definierten Prozess, wie eine Auskunftsanfrage ("Alles was Sie über mich haben") fristgerecht und vollständig beantwortet wird? |
| **5.3** | Löschung (Art. 17) | Recht auf Vergessenwerden. Umsetzung von Löschkonzepten. Vernichtung von Datenträgern. | Wenn Zweck entfällt -> Löschen. Nicht "aufheben, vielleicht brauchen wir es noch". Alte Bewerbungen weg! | Können Daten auf Verlangen eines Betroffenen (bei berechtigtem Anspruch) spurlos aus allen Systemen (außer revisionssicheren Archiven) entfernt werden? |
| **5.4** | Widerruf Einwilligung | Einwilligungen müssen so einfach widerrufen werden können wie sie erteilt wurden. | Newsletter-Abmeldung: Ein Klick. Nicht "Brief schreiben". | Ist sichergestellt, dass ein Widerruf (z.B. Newsletter, Cookies) sofort technisch umgesetzt wird? |

## 6. Datenschutzvorfälle (Data Breaches)
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **6.1** | Erkennung | Mitarbeiter müssen Vorfälle erkennen und melden. | "Ups, falscher Empfänger im CC". "Laptop weg". Personal muss wissen: Das ist ein Vorfall! | Wurden Mitarbeiter an Beispielen geschult, was genau eine "Datenpanne" ist? |
| **6.2** | Bewertung | Risikobewertung binnen 72h (Risiko für Rechte und Freiheiten?). | Entscheidung: Ist es schlimm? Müssen wir melden? Dokumentation der Entscheidung! | Wer im Unternehmen hat die Kompetenz zu entscheiden, ob ein Vorfall meldepflichtig ist? |
| **6.3** | Meldung Aufsichtsbehörde | Meldung binnen 72h bei Risiko. | Formular der Behörde nutzen. Keine Angst vor Selbstanzeige (besser als vertuschen). | Sind die Kontaktdaten der zuständigen Datenschutzaufsichtsbehörde und das Meldeformular griffbereit? |
| **6.4** | Benachrichtigung Betroffene | Benachrichtigung bei *hohem* Risiko (Art. 34). | Wenn Passwörter geklaut wurden: Kunden warnen "Bitte PW ändern". | Gibt es Vorlagen für die Benachrichtigung von Kunden im Falle eines Datenlecks? |
