# Detaillierte Anforderungsliste nach § 203 StGB & BStBK Hinweisen für KMU

Diese Liste bricht die strafrechtlichen Anforderungen des **§ 203 StGB** sowie die berufsrechtlichen Vorgaben der **Bundessteuerberaterkammer (BStBK)** für IT-Dienstleister von Berufsgeheimnisträgern herunter.

## 1. Vertragliche & Personelle Voraussetzungen
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **1.1** | Mitwirkende Personen | Dienstleister gelten als "mitwirkende Personen". Sie müssen zur Verschwiegenheit verpflichtet werden. | Der IT-Mann ist wie eine Mitarbeiterin der Kanzlei. Er muss den Mund halten. | Haben alle IT-Mitarbeiter eine schriftliche Verschwiegenheitsverpflichtung unterzeichnet, die explizit auf die Strafbarkeit nach § 203 StGB hinweist? |
| **1.2** | Dienstleistervertrag (§ 203 Abs. 4) | Abschluss einer spezifischen Vereinbarung zur Einhaltung der Verschwiegenheit VOR Tätigkeit. | Ein normaler AV-Vertrag (DSGVO) reicht NICHT! Es braucht den "Zusatz zur Verschwiegenheit". | Existiert mit dem IT-Dienstleister eine gesonderte Vereinbarung gemäß § 203 Abs. 4 StGB, die über die DSGVO hinausgeht? |
| **1.3** | Unterauftragnehmer | Dienstleister dürfen Unterauftragnehmer (Subs) nur mit Zustimmung einschalten und müssen diese ebenfalls verpflichten. | Wenn der IT-Mann ein Ticket an Microsoft aufmacht: Darf er das? Kette der Verschwiegenheit. | Ist vertraglich geregelt, dass der IT-Dienstleister keine weiteren Subunternehmer ohne vorherige Zustimmung und Verpflichtung einschalten darf? |
| **1.4** | Weisungsgebundenheit | Der Berufsgeheimnisträger muss dem Dienstleister Weisungen zur Datensicherheit erteilen können. | Der Steuerberater ist Chef. Der Admin führt aus. | Enthält der Vertrag Regelungen, die dem Berufsgeheimnisträger umfassende Weisungs- und Kontrollrechte gegenüber dem Dienstleister einräumen? |

## 2. Technische Maßnahmen (Verschlüsselung & Zugriff)
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **2.1** | E-Mail Kommunikation | Verbot unverschlüsselter Übertragung von Berufsgeheimnissen. Nutzung von Portalen oder E2E-Encryption. | Keine BWA per "nackter" E-Mail an die Bank! PDF mit Passwort oder DATEV E-Mail-Verschlüsselung. | Ist technisch sichergestellt (z.B. durch Gateway-Regeln), dass E-Mails mit Mandantendaten niemals unverschlüsselt das Haus verlassen? |
| **2.2** | Cloud-Nutzung | Nutzung von Cloud-Diensten nur zulässig, wenn Provider Zugriff technisch ausschließt oder vertraglich § 203 akzeptiert. | Dropbox (US) ist kritisch. Microsoft 365 ist okay mit "Berufsgeheimnisträger-Zusatz". | Liegt für genutzte Cloud-Speicher (OneDrive, Google Drive) eine Bestätigung des Anbieters vor, dass die besonderen Anforderungen für Berufsgeheimnisträger erfüllt sind? |
| **2.3** | Fernwartung | Zugriff nur unter Aufsicht oder Protokollierung. Keine "unbeobachteten" Zugriffe auf Mandantendaten. | Admin darf nicht nachts alleine auf dem Server "stöbern". Kanzlei sollte zuschauen oder Logs prüfen. | Können Fernwartungszugriffe durch den Dienstleister lückenlos nachvollzogen werden (Session Recording / Logfiles), und finden diese idealerweise nur nach Freigabe statt? |
| **2.4** | Zugriffschutz Lokal | Interne Abschottung. Mitarbeiter dürfen nur Akten sehen, die sie bearbeiten ("Need-to-Know"). | Empfangsdame darf nicht die Scheidungsakte vom Promi lesen. Ordnerberechtigungen! | Ist das Dateisystem so berechtigt, dass Mitarbeiter keinen Zugriff auf Mandantenordner haben, für die sie fachlich nicht zuständig sind? |

## 3. Datenlöschung & Entsorgung
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **3.1** | Datenträgervernichtung | Zertifizierte Vernichtung von HDD/SSD und Papier (DIN 66399). Schutzklasse beachten. | Alte Laptops nicht verschenken! Festplatten schreddern (lassen). Nachweis aufbewahren. | Werden ausgemusterte Datenträger (Festplatten, USB-Sticks) nachweislich (Vernichtungsprotokoll) physikalisch zerstört, bevor sie das Haus verlassen? |
| **3.2** | Kopierer/Drucker | Löschung von Festplatten in Leasing-Geräten vor Rückgabe. | Der Großraumkopierer hat eine Festplatte, die alles speichert. Vor Rückgabe löschen! | Existiert ein Prozess, der sicherstellt, dass Festplatten in Multifunktionsgeräten vor der Rückgabe an den Leasinggeber sicher gelöscht werden? |

## 4. Beschlagnahmeschutz & Zeugnisverweigerung
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **4.1** | Zeugnisverweigerungsrecht | Dienstleister können sich auf das Zeugnisverweigerungsrecht des Berufsgeheimnisträgers berufen (§ 53a StPO). | Wenn die Polizei beim Admin steht: "Ich sage nix, § 53a StPO". | Wissen die Mitarbeiter des IT-Dienstleisters, dass sie im Fall einer Durchsuchung/Vernehmung ein abgeleitetes Zeugnisverweigerungsrecht haben? |
| **4.2** | Beschlagnahmefreiheit | Daten beim Dienstleister sind (teilweise) vor Beschlagnahme geschützt, wenn sie beim Mandanten geschützt wären. | Server im Rechenzentrum dürfen nicht einfach mitgenommen werden, wenn sie Anwaltsdaten enthalten. | Ist dem Rechenzentrumsbetreiber bekannt, dass auf den Systemen beschlagnahmegeschützte Daten von Berufsgeheimnisträgern liegen? |
