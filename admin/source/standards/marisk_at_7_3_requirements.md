# Detaillierte Anforderungsliste nach MaRisk AT 7.3 (Notfallkonzept) für KMU

Diese Liste bricht die Anforderungen der "Mindestanforderungen an das Risikomanagement" (MaRisk), Modul **AT 7.3**, in prüfungsrelevante Punkte herunter. Sie ist relevant für Finanzdienstleister und deren IT-Dienstleister (Auslagerungsunternehmen).

## 1. Governance & Prozess
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **1.1** | Notfallkonzept | Einrichtung eines angemessenen Notfallkonzepts. | Kein Papiertiger. Ein lebendes Handbuch. Muss Teil des Risikomanagements sein. | Ist das Notfallkonzept als dauerhafter Prozess (und nicht als einmaliges Projekt) im Unternehmen implementiert? |
| **1.2** | Aktualität | Anlassbezogene Überprüfung und Anpassung der Pläne. Jährlicher Review. | Wenn wir umziehen oder eine neue Cloud nutzen: Plan anpassen! Mindestens einmal im Jahr drüberschauen. | Wann wurde das Notfallkonzept zuletzt inhaltlich überprüft und an die aktuelle Geschäftsstruktur angepasst? |
| **1.3** | Zeitkritische Aktivitäten | Identifikation zeitkritischer Aktivitäten und Prozesse. | Was muss SOFORT wieder gehen? (Zahlungsverkehr, Wertpapierhandel). Alles andere ist zweitrangig. | Wurden alle Geschäftsprozesse analysiert und explizit als "zeitkritisch" oder "nicht zeitkritisch" klassifiziert? |

## 2. Szenario-Analysen (4 Dimensionen)
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **2.1** | Ausfall IT-Systeme | Maßnahmen bei Ausfall wesentlicher IT-Systeme. | Server tot, Netzwerk tot, Software-Fehler, Cyber-Attacke. Plan B muss stehen. | Liegen konkrete Handlungsanweisungen für den Totalausfall der zentralen IT-Infrastruktur (z.B. Kernbankensystem/ERP) vor? |
| **2.2** | Ausfall Gebäude | Maßnahmen bei Unbenutzbarkeit von Gebäuden (Infrastruktur). | Brand, Wasserschaden, Bombenfund, Pandemie (Betretungsverbot). Wo arbeiten wir? | Ist vertraglich (Ausweichstandort) oder technisch (Home-Office) gesichert, dass bei Gebäudesperrung zeitkritische Prozesse weiterlaufen? |
| **2.3** | Ausfall Personal | Maßnahmen bei Ausfall von notwendigem Personal. | Pandemie, Streik, Kündigungswelle. Wenn Schlüsselpersonen fehlen. Vertreterregelung. | Gibt es eine dokumentierte Vertretungsregelung für alle Mitarbeiter in schlüsselkritischen Funktionen? |
| **2.4** | Ausfall Dienstleister | Maßnahmen bei Ausfall von Dienstleistern (Auslagerung). | Was, wenn der Hoster pleitegeht oder gehackt wird? Exit-Strategie. | Wurde für jeden kritischen Dienstleister analysiert, welche Auswirkungen dessen Ausfall hat und wie dieser kompensiert werden kann (Provider-Redundanz)? |

## 3. Wiederanlauf & Geschäftsfortführung
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **3.1** | RTO (Wiederanlaufzeit) | Festlegung von Wiederanlaufzeiten für zeitkritische Aktivitäten. | Zahlungsverkehr muss in 4h wieder gehen. Eignet sich die Technik dafür? | Sind für alle kritischen Prozesse konkrete Zeiten (in Stunden) definiert, bis wann sie zwingend wieder verfügbar sein müssen? |
| **3.2** | Geschäftsfortführung (Notbetrieb) | Verfahren zur Fortführung des Geschäftsbetriebs (ggf. eingeschränkt) während der Störung. | Notkasse, manuelle Belege. "Wir arbeiten weiter, auch wenn es langsamer geht". | Existieren Arbeitsanweisungen für den manuellen Notbetrieb, um die Zeit bis zur technischen Wiederherstellung zu überbrücken? |
| **3.3** | Wiederanlaufpläne | Technische Pläne zur Wiederinbetriebnahme der Systeme. | Detaillierte Checklisten für die IT-Abteilung. Reihenfolge beim Hochfahren. | Liegen aktuelle, technische Wiederanlaufpläne vor, mit denen auch externe Experten die Systeme wiederherstellen könnten? |
| **3.4** | Rückkehr Normalbetrieb | Verfahren für die Rückkehr zum Normalbetrieb. Nachpflege von Daten. | Wie kommen die Handzettel ins System? Wer kontrolliert auf Doppelerfassung? | Ist der Prozess der Datennacherfassung nach einem Notbetrieb (Re-Sync) definiert und ressourcentechnisch eingeplant? |

## 4. Kommunikation
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **4.1** | Interne Kommunikation | Sicherstellung der internen Kommunikation bei Ausfall der Standardkanäle. | Wenn VoIP und E-Mail tot sind: Satellitentelefon? Private Handys? Boten? | Wie erreichen Sie Ihre Mitarbeiter und den Krisenstab, wenn das interne Netzwerk und die Telefonanlage ausgefallen sind? |
| **4.2** | Externe Kommunikation | Erreichbarkeit für Kunden und Partner. Meldung an Aufsicht. | Kunden müssen wissen, was los ist (Reputation!). BaFin/Bundesbank informieren. | Sind Vorlagen für Pressemitteilungen und Kundeninformationen vorbereitet und rechtlich geprüft? |
| **4.3** | Erreichbarkeitslisten | Aktuelle Kontaktlisten (Mitarbeiter, Dienstleister, Behörden). Verfügbarkeit offline. | Liste muss ausgedruckt sein! Nicht auf dem Server speichern, der gerade brennt. | Wo befindet sich die gedruckte Notfall-Kontaktliste, und wann wurde diese zuletzt auf Richtigkeit der Nummern geprüft? |

## 5. Überprüfung & Tests
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **5.1** | Regelmäßige Tests | Mindestens jährliche Überprüfung der Wirksamkeit und Angemessenheit. | "Wir haben getestet". Einmal im Jahr Pflicht. Verschiedene Szenarien. | Können Sie anhand von Protokollen nachweisen, dass das Notfallkonzept in den letzten 12 Monaten erfolgreich getestet wurde? |
| **5.2** | Testumfang | Tests müssen auch das Zusammenwirken mit Dienstleistern und Personalabdeckung umfassen. | Nicht nur Server neustarten. Auch gucken: Kommt der Dienstleister wirklich? Klappt Home-Office? | Wurde bei den Tests auch das Zusammenspiel mit externen IT-Dienstleistern und die Erreichbarkeit der Hotline praktisch überprüft? |
| **5.3** | Berichterstattung | Ergebnisse der Tests sind zu dokumentieren und an die Geschäftsleitung zu berichten. | Testprotokoll: Was ging schief? Was muss verbessert werden? Bericht an Vorstand. | Liegt der Geschäftsleitung ein Bericht über die Testergebnisse vor, der auch aufgedeckte Mängel und Maßnahmen enthält? |
| **5.4** | Mängelbehebung | Zeitnahe Beseitigung festgestellter Mängel aus Tests. | Wenn Backup zu langsam war: SSDs kaufen. Sofort. Nicht auf Budget nächstes Jahr warten. | Wurden alle Mängel, die im letzten Notfalltest festgestellt wurden, inzwischen nachweislich behoben? |

## 6. Datensicherung (Backup)
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **6.1** | Backup-Strategie | Datensicherungen müssen den zeitgerechten Wiederanlauf ermöglichen. | Backup-Technologie muss zur RTO passen. Tape ist evtl. zu langsam. | Ist durch Messungen belegt, dass die physikalische Rückspielzeit (Restore) der Daten innerhalb der geforderten RTO-Zeit liegt? |
| **6.2** | Trennung (Lagerung) | Räumlich getrennte Aufbewahrung der Sicherungsmedien. Kein Zugriff aus dem Netz (Air Gap). | Backup nicht im gleichen Brandabschnitt lagern. Schutz vor Ransomware (Offline). | Ist sichergestellt, dass die Backup-Datenräumlich getrennt vom Produktionssystem lagern und vor logischem Zugriff (Verschlüsselungstrojaner) geschützt sind? |
