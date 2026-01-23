# Detaillierte Anforderungsliste nach IDW RS FAIT 1 für KMU

Diese Liste bricht den IDW RS FAIT 1 ("Grundsätze ordnungsmäßiger Buchführung bei Einsatz von Informationstechnologie") in prüfungsrelevante Kontrollen herunter. Sie dient der Vorbereitung auf den Jahresabschlussprüfer (Wirtschaftsprüfer).

## 1. IT-Umfeld & Organisation (Governance)
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **1.1** | IT-Strategie | Ausrichtung der IT an den Unternehmenszielen. Risikomanagement. | IT darf kein Eigenleben führen. Sie muss die FiBu unterstützen. Risiken müssen bekannt sein. | Gibt es eine IT-Strategie, die sicherstellt, dass die IT-Systeme den Anforderungen der Buchhaltung dauerhaft genügen? |
| **1.2** | IT-Organigramm | Klare Zuweisung von Aufgaben, Kompetenzen und Verantwortlichkeiten. | Wer ist Admin? Wer ist Key-User? Wer darf Stammdaten ändern? Organigramm muss aktuell sein. | Ist aus dem Organigramm klar ersichtlich, wer für den Betrieb und die Sicherheit der finanzrelevanten Systeme verantwortlich ist? |
| **1.3** | Funktionstrennung (SoD) | Trennung unvereinbarer Tätigkeiten (Entwicklung vs. Betrieb, Erfassung vs. Freigabe). | Der Programmierer darf nicht in der Live-Datenbank buchen. Der Admin darf keine Überweisungen tätigen. | Wie wird systemseitig verhindert, dass IT-Administratoren unbemerkt fachliche Buchungen durchführen können? |
| **1.4** | Outsourcing-Steuerung | Überwachung ausgelagerter Bereiche (SaaS, Rechenzentrum). Nachweise (ISAE 3402 / PS 951). | Wenn DATEV genutzt wird: Holen Sie sich den Audit-Bericht (SOC Report) von DATEV. Sie sind verantwortlich! | Liegen aktuelle Prüfungsberichte (z.B. nach IDW PS 951 Typ 2) Ihrer IT-Dienstleister vor, und haben Sie diese inhaltlich gewürdigt ("gelesen und abgehakt")? |

## 2. IT-Infrastruktur & Betrieb
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **2.1** | Physische Sicherheit | Schutz vor Elementarschäden und unbefugtem Zutritt. | Serverraum zu. USV. Klimaanlage. Keine Putzmittel. (Siehe VdS 10000). | Ist der physische Zugang zu den Servern, auf denen Buchhaltungsdaten liegen, auf den notwendigen Personenkreis beschränkt? |
| **2.2** | Datensicherung | Konzept zur Sicherung und Wiederherstellung. Test der Wiederherstellbarkeit. Archivierung. | Backup muss laufen UND funktionieren. Altdatenzugriff sicherstellen. | Wurde im laufenden Wirtschaftsjahr min. einmal erfolgreich getestet, ob sich die Buchhaltungsdatenbank vollständig wiederherstellen lässt? |
| **2.3** | Job-Steuerung (Batch) | Geordnete Abwicklung von Hintergrundverarbeitung (Tagesabschluss, Läufe). Überwachung. | Wenn der nächtliche Import vom Webshop in die WaWi crasht: Merkt das einer? Protokollkontrolle! | Werden automatisierte Hintergrundjobs (z.B. Schnittstellenimporte, Backups) täglich auf Fehlerfreiheit kontrolliert? |
| **2.4** | Notfallvorsorge | Vorsorge für Systemausfälle (Business Continuity). Wiederanlaufpläne. | Wenn der Server steht: Wie lange dauert es? (Siehe BSI 200-4 / ISO 22301). | Existiert ein dokumentierter Notfallplan, der sicherstellt, dass die Buchführung auch bei längerem Systemausfall zeitnah wieder aufgenommen werden kann? |

## 3. Anwendungssysteme (Change Management)
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **3.1** | Programmentwicklung | Dokumentierte Vorgaben für Entwicklung/Customizing. Trennung Entwicklung/Test/Prod. | Nicht am offenen Herzen operieren. Jede Anpassung erst im Testsystem prüfen. | Existiert eine, von der Produktion getrennte, Testumgebung für Updates und Anpassungen an der ERP-Software? |
| **3.2** | Programmänderung (Change) | Genehmigungsverfahren für Änderungen. Test und Freigabe durch Fachbereich. | Bevor das Update installiert wird: Buchhaltung muss "Okay" geben (User Acceptance Test). | Gibt es ein Änderungsprotokoll, das nachweist, wer wann welches Software-Update autorisiert und freigegeben hat? |
| **3.3** | Notfalländerungen | Verfahren für dringende Änderungen (Emergency Fixes). Nachträgliche Dokumentation. | Wenn es brennt und der Admin "schnell mal" was patcht: Hinterher aufschreiben! | Wie wird sichergestellt, dass auch Ad-hoc-Eingriffe ("Emergency Fixes") nachträglich ordnungsgemäß dokumentiert werden? |
| **3.4** | Stammdatenänderung | Protokollierung und Freigabe von Stammdatenänderungen (Kreditoren/Debitoren). | Neue Bankverbindung beim Lieferanten? Vier-Augen-Prinzip! Änderungen loggen. | Können alle Änderungen an zahlungsrelevanten Stammdaten (IBAN, Adresse) über ein unveränderbares Protokoll ausgewertet werden? |

## 4. IT-Sicherheit & Zugriffsschutz
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **4.1** | Benutzerverwaltung | Formaler Prozess für Einrichtung, Änderung, Löschung von Usern. Rezertifizierung. | Antrag -> Chef unterschreibt -> Admin richtet ein. Kein Zuruf "Mach mal eben". Regelmäßig prüfen: Gibt's den noch? | Liegen zu allen aktiven Benutzern schriftliche (oder workflow-basierte) Anträge zur Rechtevergabe vor? |
| **4.2** | Authentisierung | Eindeutige Identifizierung (User-ID). Sichere Passwörter. | Keine Sammel-User ("Kasse1", "Admin"). Jeder Mitarbeiter braucht seinen eigenen Login. | Ist technisch sichergestellt, dass Passwörter Mindestkomplexität haben und nicht im Klartext übertragen werden? |
| **4.3** | Berechtigungskonzept | Vergabe nach "Need-to-Know". Rollenbasierte Vergabe (RBAC). | Nicht jedem "Alle Rechte" geben, weil es einfacher ist. Rollenkonzept (Buchhalter, Einkäufer, Controller). | Entsprechen die vergebenen Berechtigungen den aktuellen Aufgaben der Mitarbeiter (regelmäßige Rezertifizierung)? |
| **4.4** | Protokollierung (Logs) | Protokollierung sicherheitsrelevanter Ereignisse (Fehlversuche, Rechteänderungen). | Wer hat versucht, das Passwort zu raten? Wer hat Rechte erweitert? Logs auswerten! | Werden Protokolle über fehlgeschlagene Anmeldeversuche und Rechteänderungen generiert und regelmäßig ausgewertet? |

## 5. Datenverarbeitung (IPO - Input/Processing/Output)
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **5.1** | Eingabekontrollen | Plausibilitätsprüfungen, Formatchecks, Zwangsfelder, Dublettenprüfung. | Software darf "asdf" im Datumsfeld nicht schlucken. Muss meckern bei doppelter Rechnungsnummer. | Verhindert das System die Eingabe formal fehlerhafter Daten (z.B. Buchstaben in Betragsfeldern) durch Validierungsregeln? |
| **5.2** | Verarbeitungskontrollen | Kontrollsummen, Satzzähler bei Stapelverarbeitung. Automatische Buchungen. | Wenn 100 Sätze importiert werden, müssen 100 ankommen. Summenverprobung. | Wie stellen Sie bei Massenverarbeitungen (z.B. Abschreibungslauf) sicher, dass alle Datensätze vollständig und korrekt verarbeitet wurden? |
| **5.3** | Schnittstellenkontrollen | Überwachung von Schnittstellen (Vollständigkeit, Richtigkeit). Error-Handling. | Vom Webshop zur FiBu: Kommen alle Orders an? Was passiert mit Fehlern (Abbruch)? Protokoll! | Werden Schnittstellenprotokolle (Import/Export) arbeitstäglich auf Fehler geprüft und Abweichungen korrigiert? |
| **5.4** | Ausgabekontrollen | Abstimmung von Listen/Reports mit dem Hauptbuch. Verteilkontrolle. | Stimmt die USt-Liste mit dem Konto überein? Wer bekommt die Gehaltsliste (Drucker im Flur?)? | Wer prüft die Plausibilität der maschinell erstellten Berichte (z.B. BWA, Summen- und Saldenliste) vor der Weiterverarbeitung? |

## 6. Dokumentation
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **6.1** | Systemdokumentation | Technische Beschreibung der IT-Systeme (Hardware, Software, Netz, Schnittstellen). | Netzwerkplan. Softwareliste. Schnittstellenbeschreibung (Welches Feld wohin?). | Liegt eine Systemdokumentation vor, die einem sachverständigen Dritten ermöglicht, die technische Abwicklung der Buchführung zu verstehen? |
| **6.2** | Anwenderdokumentation | Bedienungsanleitungen, Arbeitsanweisungen für User. | Handbuch der Software. Internes Wiki "Wie buche ich Reisekosten?". | Haben die Anwender Zugriff auf aktuelle Bedienungsanleitungen und Arbeitsanweisungen für die eingesetzte Software? |
