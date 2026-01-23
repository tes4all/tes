# Detaillierte Anforderungsliste nach NIS-2 Richtlinie & KRITIS

Diese Liste bricht die Anforderungen der **EU-Richtlinie NIS-2** (Network and Information Security Directive) und deren deutsche Umsetzung (BSIG-E) herunter.
**Besonderheit:** NIS-2 betrifft nicht mehr nur "Kritische Infrastrukturen" (KRITIS), sondern auch "Wichtige Einrichtungen" (ab 50 MA / 10 Mio € Umsatz in Sektoren wie IT-Dienstleister, Verarbeiter, Entsorger). Zudem gelten Pflichten für die Lieferkette (Supply Chain).

## 1. Governance & Verantwortlichkeit (Art. 20)
| ID | Thema | Anforderung (Gesetzestext abstrahiert) | Übersetzung für KMU / Zulieferer | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **1.1** | Billigung & Überwachung | Die Leitungsorgane müssen Risikomanagementmaßnahmen billigen und deren Umsetzung überwachen. | Der Chef haftet persönlich. Er darf IT-Sicherheit nicht mehr wegdelegieren ("Ich hab da keine Ahnung von"). Er muss unterschreiben. | Kann die Geschäftsleitung nachweisen, dass sie die aktuellen Cybersicherheitsmaßnahmen offiziell freigegeben hat und regelmäßig überwacht? |
| **1.2** | Schulung der Leitung | Mitglieder der Leitungsorgane müssen an Schulungen teilnehmen, um Risiken bewerten zu können. | Zwangsschulung für den Chef. Kein "Ich hab keine Zeit". Er muss wissen, was Phishing ist. | Liegen Zertifikate vor, die bestätigen, dass die gesamte Geschäftsführung regelmäßig an IT-Sicherheitsschulungen teilnimmt? |
| **1.3** | Haftung | Leitungsorgane haften für Verstöße gegen die Pflichten zur Risikomanagementumsetzung. | Wenn der Chef die IT ignoriert und es kracht, zahlt er ggf. mit Privatvermögen (Bußgelder!). | Ist der Geschäftsleitung bewusst, dass sie bei Verstößen gegen NIS-2-Pflichten persönlich haftbar gemacht werden kann? |

## 2. Risikomanagement (Art. 21 - Gefahrenübergreifender Ansatz)
| ID | Thema | Anforderung (Gesetzestext abstrahiert) | Übersetzung für KMU / Zulieferer | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **2.1** | All-Gefahren-Ansatz | Maßnahmen müssen physische Umwelt schützen (Diebstahl, Feuer, Wasser, Zutritt) und logische Systeme. | Nicht nur Hacker. Auch Brandschutz, Zutrittskontrolle, Stromausfall. Ein ganzheitliches Konzept. | Deckt das Risikomanagement neben Cyberangriffen auch physische Gefahren wie Feuer, Wasser, Stromausfall und Zutritt ab? |
| **2.2** | Bewältigung von Vorfällen | Konzepte für die Bewältigung von Sicherheitsvorfällen (Incident Handling). | Wir brauchen einen konkreten Plan: Was tun, wenn es brennt? (Siehe ISO 22301 / BSI 200-4). | Gibt es einen definierten und getesteten Prozess für die Reaktion auf Sicherheitsvorfälle (Incident Response Plan)? |
| **2.3** | Business Continuity | Aufrechterhaltung des Betriebs (Backup-Management, Disaster Recovery, Krisenmanagement). | Wenn alles steht: Wie arbeiten wir weiter? Backup muss funktionieren und sicher sein (Offline). | Ist sichergestellt (durch Tests), dass der Geschäftsbetrieb auch bei Ausfall der IT-Systeme zumindest eingeschränkt fortgeführt werden kann (BCM)? |
| **2.4** | Sicherheit der Lieferkette | Sicherheit der Lieferkette (Supply Chain Security). Prüfung der Zulieferer/Dienstleister. | Wir sind nur so sicher wie unser MSP. Überprüfung des IT-Dienstleisters. Haben wir sichere Software? | Haben Sie Ihre Software-Lieferanten und IT-Dienstleister einer Sicherheitsbewertung unterzogen (z.B. Fragebogen, Zertifikate)? |
| **2.5** | Schwachstellenmanagement | Sicherheit bei Erwerb, Entwicklung und Wartung von Systemen. Offenlegung von Schwachstellen. | Patch-Management! Systeme aktuell halten. Sicherheitslücken schließen, bevor sie ausgenutzt werden. | Existiert ein Prozess, der sicherstellt, dass kritische Sicherheitsupdates für alle Systeme (auch Netzwerkgeräte) zeitnah (z.B. < 72h) eingespielt werden? |

## 3. Technische Maßnahmen & Hygiene (Art. 21)
| ID | Thema | Anforderung (Gesetzestext abstrahiert) | Übersetzung für KMU / Zulieferer | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **3.1** | Cyberhygiene | Grundlegende Cyberhygiene (Passwörter, Updates, Backups). Schulung der Mitarbeiter. | Das 1x1 der IT: Keine Passwörter am Monitor. Kein Admin-Recht für User. Regelmäßige Schulungen. | Werden grundlegende Hygienemaßnahmen wie "Kein Standardpasswort", "Mitarbeiterschulung" und "Least Privilege" konsequent umgesetzt? |
| **3.2** | Kryptografie | Konzepte für Verfahren der Kryptografie und Verschlüsselung (Ende-zu-Ende). | Daten verschlüsseln! Laptops (BitLocker), E-Mails, VPN. Und zwar mit sicheren Algorithmen. | Sind alle sensiblen Daten (auf Laptops, mobilen Datenträgern und bei der Übertragung) mit aktuellen Verfahren verschlüsselt? |
| **3.3** | Personalsicherheit | Personalsicherheit, Zugriffskontrolle und Asset Management. | Wer hat Zugriff? Wenn einer kündigt: Sofort sperren. Inventarliste führen. | Ist der Zugriff auf kritische Systeme durch technische Maßnahmen (MFA, Rollenkonzept) strikt auf befugte Personen begrenzt? |
| **3.4** | MFA (Authentifizierung) | Einsatz von Multi-Faktor-Authentifizierung (MFA) oder kontinuierlichen Authentifizierungslösungen. | Passwort reicht nicht mehr. MFA für Admin-Zugänge, VPN und Cloud ist Pflicht. | Ist für alle Fernzugriffe (VPN, RPD, Cloud) und privilegierten Konten (Admins) zwingend eine Multi-Faktor-Authentifizierung (MFA) aktiviert? |
| **3.5** | Sichere Kommunikation | Verwendung gesicherter Sprach-, Video- und Textkommunikation sowie Notfallkommunikation. | Keine WhatsApp-Gruppen für Firmendaten. Sichere Messenger (Threema/Signal Work) oder Teams. Notfall-Handy bereit? | Nutzen Sie für die interne Kommunikation (Sprache/Text) ausschließlich freigegebene, verschlüsselte Kanäle und gibt es ein System für den Notfall? |

## 4. Meldepflichten (Art. 23 - Streng!)
| ID | Thema | Anforderung (Gesetzestext abstrahiert) | Übersetzung für KMU / Zulieferer | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **4.1** | Frühwarnung (24h) | "Erheblicher Sicherheitsvorfall" muss binnen 24 Stunden als Frühwarnung ans CSIRT/BSI gemeldet werden. | Wenn es richtig knallt (Ausfall, Datenverlust): Sofort melden. Schneller als Datenschutz (24h vs 72h)! | Ist der Prozess so aufgesetzt, dass ein erheblicher Vorfall rund um die Uhr (24/7) erkannt und binnen 24 Stunden an das BSI gemeldet werden kann? |
| **4.2** | Meldung (72h) | Aktualisierung der Meldung binnen 72 Stunden (Bewertung des Schweregrads und der Auswirkungen). | Nach einem Tag wissen wir mehr. Update an die Behörde: "Ist es schlimm? Sabotage?". | Sind Verantwortlichkeiten definiert, wer die detaillierte Folgemeldung (Bewertung der Auswirkungen) innerhalb von 72 Stunden erstellt? |
| **4.3** | Abschlussbericht (1 Monat) | Spätestens einen Monat nach Vorfall: Ausführlicher Bericht (Ursache, Maßnahmen, grenzüberschreitende Auswirkungen). | Wenn der Staub sich legt: Manöverkritik. Was war die Ursache? Was haben wir getan? | Ist sichergestellt, dass Vorfälle so dokumentiert werden (Forensik), dass nach einem Monat ein qualifizierter Abschlussbericht erstellt werden kann? |
| **4.4** | Kundeninformation | Pflicht zur Unterrichtung der Empfänger des Dienstes (Kunden) bei Gefahr. | Wir müssen den Kunden sagen: "Achtung, wir haben ein Problem, schützt euch!". | Gibt es Vorlagen, um Kunden unverzüglich über laufende Bedrohungen oder Vorfälle informieren zu können? |

## 5. Zuweisung und Registrierung
| ID | Thema | Anforderung (Gesetzestext abstrahiert) | Übersetzung für KMU / Zulieferer | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **5.1** | Registrierung | Betroffene Einrichtungen müssen sich beim BSI registrieren (Stammdaten, Kontaktstelle). | Wir müssen uns beim BSI "melden", wenn wir unter NIS-2 fallen. Wir werden nicht angeschrieben! Holschuld. | Haben Sie geprüft, ob Ihr Unternehmen als "Wesentliche" oder "Wichtige" Einrichtung unter NIS-2 fällt, und eine Registrierung beim BSI vorbereitet? |
| **5.2** | Kontaktstelle | Benennung einer funktionsfähigen Kontaktstelle (Erreichbarkeit). | Das BSI muss uns erreichen können. Nicht "info@firma.de", die keiner liest. | Existiert eine zentrale Kontaktstelle (Funktionspostfach/Telefonnummer), über die das BSI Sie im Krisenfall jederzeit erreichen kann? |
