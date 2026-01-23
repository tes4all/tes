# Detaillierte Anforderungsliste nach DATEV Best Practices für KMU (Kanzleien)

Diese Liste bricht die technischen und organisatorischen Vorgaben der DATEV e.G. in prüfbare Maßnahmen herunter. Sie basiert auf den DATEV-Dokumenten zur Informationssicherheit und Systemplattform.

## 1. Systemplattform & Infrastruktur
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **1.1** | Betriebssysteme | Einsatz freigegebener OS-Versionen (Lifecycle beachten!). Keine "Home"-Editionen. | Nur Windows Server 2019/2022 und Windows 10/11 Pro/Enterprise. Veraltete Systeme (2012 R2) gefährden den Support und die Sicherheit. | Werden ausschließlich Betriebssysteme eingesetzt, die sich noch im offiziellen Microsoft-Supportzeitraum befinden und von DATEV freigegeben sind? |
| **1.2** | Hardware-Ressourcen | Ausreichende Dimensionierung gemäß DATEV Hardware-Empfehlung (CPU, RAM, DISK). | SQL braucht RAM! Terminalserver braucht CPU. Zu wenig Power = Wartezeit = Frust. Check Dok.-Nr. 0908081. | Entspricht die Server-Hardware den aktuellen DATEV-Empfehlungen (insb. Arbeitsspeicher für SQL-Server), um Performance-Engpässe zu vermeiden? |
| **1.3** | Virtualisierung | Nutzung unterstützter Hypervisor (Hyper-V, VMware). Keine "Exoten". Ressourcenreservierung. | Keine Dynamic Memory/Ballooning für SQL Server! Virtualisierung muss stabil laufen. Snapshots sind kein Backup für SQL! | Wurden für den SQL-Server in der virtuellen Umgebung feste Arbeitsspeicher-Ressourcen reserviert (kein Dynamic Memory), um Datenbankabstürze zu verhindern? |
| **1.4** | Terminalserver (WTS) | Einsatz dedizierter WTS für DATEV-Anwendungen. Office-Integration (64-bit Problematik). | DATEV läuft am besten im WTS-Betrieb. Achtung bei Office 32-bit vs 64-bit (DATEV Empfehlung beachten). | Laufen die DATEV-Anwendungen auf einem dedizierten Terminalserver (oder wahlweise lokalen Clients), der nicht gleichzeitig Domänencontroller oder Fileserver ist? |

## 2. Microsoft SQL Server (Das Herzstück)
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **2.1** | Instanz & Version | Korrekte Instanz (DATEV_DBEN), Collation (Latin1_General_CI_AS) und Patchlevel. | Nicht einfach "weiter, weiter" installieren. DATEV SQL-Manager nutzen. Updates (CUs) zeitnah einspielen. | Ist der Microsoft SQL Server auf dem aktuellen Patch-Stand (Cumulative Updates), den die DATEV freigegeben hat? |
| **2.2** | Speicherbegrenzung | Konfiguration "Max Server Memory" zur Verhinderung von OS-Instabilität. | SQL nimmt sich alles, wenn man ihn lässt. Begrenzen! (z.B. Total RAM minus 4GB für OS). | Ist der maximale Arbeitsspeicher des SQL-Servers ("Max Server Memory") fest konfiguriert, sodass dem Betriebssystem genügend Reserven bleiben? |
| **2.3** | Wartungspläne | Einrichtung regelmäßiger Reorganisation / Index-Wartung (DATEV SQL Manager). | Datenbanken fragmentieren. Nachts aufräumen lassen (Reorg), sonst wird alles langsam. | Laufen nächtliche Wartungspläne (Reorganisation, Statistiken aktualisieren) für die DATEV-Datenbanken? |
| **2.4** | Konsistenzprüfung | Regelmäßige DBCC CHECKDB Läufe zur Erkennung logischer Fehler. | Datenbank kann logisch kaputt sein, ohne dass man es merkt (bis zum Backup). Prüfen! | Wird regelmäßig (z.B. wöchentlich) eine logische Konsistenzprüfung der Datenbanken (DBCC) durchgeführt und protokolliert? |

## 3. Datensicherung & Wiederherstellung
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **3.1** | SQL-Dump vs. VSS | Sicherung muss SQL-Aware sein. Entweder SQL-Dumps (via DATEV Tool) oder VSS-Writer Backup. | Datei `ldf/mdf` kopieren reicht nicht im laufenden Betrieb! Das Backup ist sonst korrupt. | Nutzen Sie eine Backup-Software, die nachweislich den Microsoft SQL VSS Writer unterstützt, oder erstellen Sie vor der Sicherung SQL-Dumps? |
| **3.2** | Sicherungsumfang | Sicherung aller relevanten Daten: DBs, Konfig (WindvsW1), DMS-Dokumente (Filesystem!). | Nicht nur Datenbanken sichern! Auch den Ordner `DATEV\DATEN` (DMS-Ablage, Logbücher). | Umfasst die Datensicherung vollständig sowohl die SQL-Datenbanken als auch die physischen Dokumentenablagen (z.B. DMS-Repository im Dateisystem)? |
| **3.3** | Kommunikationsserver | Sicherung der DFÜ-Profile, Zertifikate und RZ-Kommunikationseinstellungen. | Wenn der CommServer weg ist, geht kein Elster-Versand mehr. RZ-Anbindung sichern. | Ist die Konfiguration des Kommunikationsservers (RZ-Anbindung, Benutzerverwaltung) in der Datensicherung enthalten? |
| **3.4** | Test-Restore | Test der Wiederherstellung inkl. "Einhängen" (Attach) der Datenbanken via SQL-Manager. | DATEV Restore ist Tricky. Datenbanken müssen im SQL detach/attach werden. Wissen Sie, wie das geht? | Wann wurde zuletzt eine DATEV-Datenbank testweise von einem Backup-Medium wiederhergestellt und erfolgreich im SQL-Manager eingebunden? |

## 4. Sicherheit & Zugriff
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **4.1** | Virenscanner | Konfiguration von Ausnahmen (Exceptions) gemäß DATEV Dok.-Nr. 1013887. | Scanner darf nicht in die Datenbankdateien (.mdf/.ldf) greifen, während SQL schreibt. Performance-Tod! | Sind die von DATEV vorgeschriebenen Ausnahmen (Pfade und Prozesse) im Virenscanner konfiguriert? |
| **4.2** | DATEV Benutzerverwaltung | Zentrale Verwaltung der Zugriffsrechte auf Programmebene. Kopplung an Windows-User. | "Müller" darf Lohn sehen, "Maier" nicht. Zentrale Steuerung in der NuSR. | Sind in der DATEV-Benutzerverwaltung (NuSR) die Zugriffsrechte auf sensible Bereiche (Lohn, Geschäftsleitungsmandate) restriktiv vergeben? |
| **4.3** | Rechteverwaltung Online | Steuerung der Zugriffe auf Cloud-Anwendungen (Unternehmen online, Meine Steuern). | Wer darf für Mandant X Belege sehen? Steuerung via SmartCard/Rechteverwaltung online. | Wird bei Austritt eines Mitarbeiters sofort der Zugriff in der "Rechteverwaltung online" (RZ-Zugriff) gesperrt? |
| **4.4** | SmartCard / mIDentity | Schutz der Authentisierungsmedien. Stick darf nicht stecken bleiben (außer am Server mit Lizenz). | Stick = Ausweis. Nicht verleihen. PIN geheim halten. Server-Stick (Betriebsstätten-mIDentity) sicher verwahren. | Wie ist sichergestellt, dass unbeaufsichtigte SmartCards/mIDentity-Sticks (insb. Master-Sticks) nicht von Unbefugten entwendet oder genutzt werden können? |
| **4.5** | Filesystem Berechtigungen | NTFS-Rechte auf dem zentralen Datenlaufwerk (DATEV-Pfad). | Nicht "Jeder Vollzugriff" auf `L:\DATEV`. DATEV setzt rechte per "Büroklammer" (Tool). Prüfen! | Sind die NTFS-Berechtigungen auf dem zentralen DATEV-Laufwerk so gesetzt, dass nur berechtigte Benutzergruppen Zugriff haben? |

## 5. Wartung & Pflege
| ID | Thema | Anforderung (Theorie) | Übersetzung für KMU | Audit-Frage |
| :--- | :--- | :--- | :--- | :--- |
| **5.1** | Installations-Manager | Regelmäßige Prüfung und Installation bereitgestellter Updates und Hotfixes. | DATEV liefert oft Updates (Steuerrecht!). Werden die automatisch geholt? Nachts installieren (Service-Release-Management). | Ist der Installations-Manager für den automatischen Abruf von Software-Updates konfiguriert und wer prüft den Installationsstatus? |
| **5.2** | Servicetool | Nutzung des DATEV Servicetools zur Systemanalyse (Health Check). | Das Servicetool prüft alles (RAM, Platte, Rechte). Ampel muss grün sein. | Wurde das DATEV Servicetool kürzlich ausgeführt und zeigt es für alle Systeme "grün" an? |
| **5.3** | Abkündigungen | Beachtung von Software-Abkündigungen (z.B. Umstieg auf DATEV Anwalt classic, Auslauf DMS classic). | DATEV kündigt Dinge ab. Man muss migrieren. Nicht auf toten Pferden reiten. | Ist Ihnen bekannt, welche DATEV-Programmkomponenten zum nächsten Jahreswechsel abgekündigt werden und besteht ein Migrationsplan? |
