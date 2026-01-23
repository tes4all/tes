# Detaillierte Anforderungsliste nach VdS 10000 für KMU

Diese Liste bricht die VdS-Richtlinie 10000 ("Informationssicherheitsmanagementsystem für KMU") in granulare Maßnahmen auf. Sie ist speziell für kleinere Unternehmen gedacht, die ISO 27001 als zu mächtig empfinden.

## 1. Organisation & Management
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **1.1** | Verantwortung Leitung | Die Geschäftsleitung trägt die Gesamtverantwortung für die Informationssicherheit. | Chefbüro muss Sicherheit vorleben. Ressourcen bereitstellen. | Kann die Geschäftsleitung darlegen, wie sie ihrer Verantwortung für die Informationssicherheit (Budget, Personal) nachkommt? |
| **1.2** | Informationssicherheitsbeauftragter | Benennung eines ISB (intern oder extern) als Koordinator. | Ein Kümmerer. Muss nicht Vollzeit sein, aber muss benannt sein. | Wer ist der offizielle Ansprechpartner für IT-Sicherheit (ISB) und hat diese Person direkten Zugang zur Geschäftsleitung? |
| **1.3** | Leitlinie | Schriftliche Leitlinie zur Informationssicherheit. Bekanntmachung im Unternehmen. | Ein Dokument "Wir nehmen Sicherheit ernst". Alle müssen es lesen. | Haben alle Mitarbeiter die Sicherheitsleitlinie zur Kenntnis genommen (z.B. per Unterschrift oder Intranet-Bestätigung)? |
| **1.4** | Inventarisierung (Assets) | Führung eines aktuellen Inventarverzeichnisses (Hardware, Software, mobile Geräte). | Liste aller PCs, Server, Handys, Drucker inkl. Standort und Verantwortlichem. "Schatten-IT" finden. | Entspricht die Inventarliste der Realität (Stichprobe: Griff in den Schrank oder Blick unter den Tisch)? |
| **1.5** | Dienstleistersteuerung | Übersicht aller IT-Dienstleister. Regelungen zur Sicherheit bei Fremdfirmen. | Wer darf an unsere Systeme? Wartungsverträge prüfen. Fernwartungsregeln. | Gibt es eine aktuelle Liste aller externen Dienstleister mit Zugriff auf IT-Systeme inkl. Ansprechpartner und Vertragsstatus? |

## 2. Physische Sicherheit
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **2.1** | Zutrittsschutz Gebäude | Schutz vor unbefugtem Zutritt (Schlüssel, Karten, Empfang). | Tür zu! Besucher nicht allein herumlaufen lassen. Schlüsselverwaltung. | Ist der Zutritt zum Firmengebäude so geregelt, dass betriebsfremde Personen nicht unbemerkt in sensible Bereiche gelangen können? |
| **2.2** | Serverraum-Sicherheit | Erhöhter Schutz für zentrale IT (eigener Brandabschnitt, Zutrittskontrolle, Klimatisierung). | Server nicht unterm Schreibtisch oder in der Teeküche. Abgeschlossener Raum. Keine Putzmittel dort lagern. | Ist der Serverraum ständig verschlossen und haben nur befugte IT-Administratoren einen Schlüssel/Zutrittskarte? |
| **2.3** | Brandschutz | Rauchmelder, Feuerlöscher (geeignet für Elektronik). Ggf. Brandmeldeanlage. | CO2-Löscher statt Schaum (Schaum macht alles kaputt). Melder müssen funktionieren. | Sind im Serverraum Rauchmelder installiert, die im Alarmfall aktiv jemanden benachrichtigen (nicht nur piepen, wenn keiner da ist)? |
| **2.4** | Stromversorgung | USV für Server zum sauberen Herunterfahren bei Stromausfall. Überspannungsschutz. | Batteriepack (USV). Hält 10 Minuten. Reicht zum Runterfahren. Muss gewartet werden (Akku-Test). | Wann wurde die USV (Unterbrechungsfreie Stromversorgung) zuletzt einem Funktionstest (Stecker ziehen) unterzogen? |
| **2.5** | Cabling & Patching | Saubere Verkabelung. Schutz vor Beschädigung. Beschriftung. | Kein Kabelsalat im Gang (Stolperfalle). Beschriftete Dosen und Patchfelder. | Sind Netzwerkdosen und Patchfelder so beschriftet, dass im Notfall Verbindungen eindeutig identifiziert werden können? |

## 3. Netzwerksicherheit
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **3.1** | Netzwerksegmentierung | Trennung von Netzen (z.B. Server, Clients, Gäste, Produktion, VoIP). | Das Gäste-WLAN darf NICHT auf den File-Server kommen. VLANs nutzen. | Ist das Gäste-WLAN technisch vollständig vom internen Firmennetzwerk isoliert (VLAN/Firewall)? |
| **3.2** | Firewall | Einsatz einer Firewall am Übergang zum Internet. "Deny-All"-Strategie. | Türsteher zum Internet. Alles verbieten, was nicht explizit erlaubt ist. Regelmäßige Prüfung der Regeln. | Werden die Firewall-Regeln regelmäßig (mind. jährlich) überprüft und nicht mehr benötigte Freigaben gelöscht? |
| **3.3** | Fernzugriff (VPN) | Sichere Anbindung von Home-Office/Außendienst. Verschlüsselung (VPN). 2-Faktor-Auth. | Kein RDP direkt ins Internet! Nur via VPN. Und VPN nur mit Zertifikat oder 2FA. | Ist der Fernzugriff (VPN) zwingend durch eine Zwei-Faktor-Authentifizierung oder Zertifikate abgesichert? |
| **3.4** | WLAN-Sicherheit | WPA2/WPA3 Verschlüsselung. Starke Passwörter. Keine offenen Netze. | Kein "WLAN123" Passwort. Enterprise-Auth (Radius) ist besser als Pre-Shared-Key bei vielen Usern. | Ist das interne WLAN mit einem starken Passwort (oder besser 802.1X Authentifizierung) gesichert, das regelmäßig gewechselt wird? |

## 4. Systemsicherheit (Server & Clients)
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **4.1** | Malware-Schutz | Virenscanner auf allen Systemen (Server, Client, ggf. Mobile). Zentrale Verwaltung. | Virenscanner muss überall laufen und sich automatisch aktualisieren. Meldung an Admin bei Fund. | Meldet die Antiviren-Lösung Infektionen automatisch an eine zentrale Stelle (Admin), oder bleibt der Alarm lokal beim User unbemerkt? |
| **4.2** | Patch-Management | Zeitnahes Einspielen von Sicherheitsupdates (OS & Anwendungen). Entfernen alter Software. | Windows Updates auf "Auto". Adobe, Chrome, Java, Firefox auch patchen! Alte Java-Versionen deinstallieren. | Nutzen Sie eine Softwareverteilung (Patch-Management), um sicherzustellen, dass Drittanbietersoftware (Browser, Reader) aktuell gehalten wird? |
| **4.3** | Härtung | Deaktivierung unnötiger Dienste und Benutzer. Standardpasswörter ändern. | Drucker haben oft Standardpasswörter -> ändern! Nicht genutzte Ports am Switch abschalten. | Wurden auf allen Netzwerkgeräten (Drucker, Router, IOT) die Standard-Passwörter des Herstellers geändert? |
| **4.4** | Identitätsmanagement | Jeder Nutzer hat eigene Kennung. Passwortrichtlinie (Länge, Komplexität). Sperren bei Inaktivität. | Kein "Praktikant1". Passwörter nicht auf Post-its. Bildschirmsperre nach 5 Min. | Erzwingt das System komplexe Passwörter und eine automatische Bildschirmsperre bei Inaktivität? |
| **4.5** | Admin-Rechte | Trennung von Admin- und User-Accounts. Admins nur für Admin-Tätigkeiten nutzen. | Nicht als "Domain Admin" surfen und E-Mails lesen. Admin hat zwei Accounts: "Müller" und "adm-Müller". | Arbeiten Administratoren im Tagesgeschäft (E-Mail, Web) mit einem normalen Benutzerkonto ohne Admin-Rechte? |

## 5. Datensicherung & Notfall
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **5.1** | Datensicherungskonzept | Regelung: Was wird wann wie lange gesichert? Verantwortlichkeiten. | Schriftlicher Plan: "Server A wird täglich um 22h gesichert, 14 Tage aufbewahrt." | Gibt es ein schriftliches Datensicherungskonzept, das festlegt, welche Daten wie oft und auf welches Medium gesichert werden? |
| **5.2** | Auslagerung | Räumlich getrennte Aufbewahrung mindestens eines Datensatzes. | Wenn das Haus abbrennt, muss ein Backup woanders sein (Banktresor, Cloud, Chef zuhause). | Befindet sich zu jedem Zeitpunkt eine aktuelle Datensicherung an einem anderen Brandabschnitt oder externen Standort? |
| **5.3** | Wiederherstellungstest | Regelmäßige Tests der Rücksicherbarkeit (Daten und Systeme). | Nicht nur "Backup erfolgreich" Log lesen. Wirklich mal eine Datei oder den ganzen Server zurückholen. | Wann wurde zuletzt protokolliert eine erfolgreiche Wiederherstellung (Test-Restore) durchgeführt? |
| **5.4** | Meldewege | Bekanntgabe von Meldewegen für Sicherheitsvorfälle (Ansprechpartner). | Wen rufe ich an, wenn mein PC komische Dinge tut? Nicht selbst basteln! | Wissen die Mitarbeiter, dass sie bei IT-Auffälligkeiten sofort den Support/ISB informieren müssen und nicht selbst Neustarts versuchen sollen? |

## 6. Personal & Sensibilisierung
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **6.1** | Verpflichtung | Mitarbeiter müssen auf Vertraulichkeit und Einhaltung der Richtlinien verpflichtet werden. | Unterschrift im Arbeitsvertrag oder Zusatzvereinbarung. | Haben alle Mitarbeiter (auch Externe/Praktikanten) eine Vertraulichkeitserklärung unterzeichnet? |
| **6.2** | Schulung | Regelmäßige Schulungen zu IT-Sicherheitsthemen (Phishing, Social Engineering). | Einmal im Jahr alle in den Meetingraum oder E-Learning. "Nicht auf CEO-Fraud reinfallen". | Finden mindestens jährlich IT-Sicherheitsschulungen für alle Mitarbeiter statt und wird die Teilnahme dokumentiert? |
| **6.3** | Austrittsprozess | Entzug von Berechtigungen und Rückgabe von Assets bei Austritt. | Wenn einer geht: Sofort Account sperren. Laptop, Handy, Schlüssel einsammeln. Checkliste Austritt! | Gibt es eine Checkliste "Mitarbeiteraustritt", die sicherstellt, dass am letzten Arbeitstag alle zugriffe (auch VPN/Cloud) gesperrt werden? |
