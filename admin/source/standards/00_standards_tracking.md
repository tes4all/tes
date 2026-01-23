# Standards Version Tracking (v0.1)

Diese Datei dient der Versionsverwaltung der erstellen Anforderungskataloge ("Requirements").
Ziel ist es, den aktuellen Stand ("v0.1 - Best Practice Wissen") später gezielt mit kostenpflichtigen Originalwerken oder neuen Norm-Versionen abzugleichen ("Delta-Analyse"), ohne Urheberrechte zu verletzen.

## Strategie für Versions-Updates
1. **Struktur-Mapping:** Die IDs in den Markdown-Dateien sollten beim Update auf die offiziellen Kapitelnummern der Normen gemappt werden (z.B. "Unser ID 1.1" entspricht "Norm Kapitel 5.2.1").
2. **Inhalts-Abstraktion:** Auch in zukünftigen Versionen muss der Text eine "Übersetzung" oder "Audit-Frage" bleiben und darf kein 1:1 Zitat der Normtexte sein (Schutz des geistigen Eigentums der Normungsinstitute).
3. **Change-Log:** Änderungen an Anforderungen (z.B. "Passwortlänge geändert von 8 auf 12") lösen eine Info an die Kunden aus.

## Status-Übersicht der Kataloge

| Datei | Basis-Standard / Quelle | Status (Aktuell) | Struktur-Kompatibilität | To-Do bei Update auf "Buch-Version" |
| :--- | :--- | :--- | :--- | :--- |
| **bsi_200_4_requirements.md** | BSI Standard 200-4 | v0.1 (Community Baseline) | Eigene Kapitelstruktur (1-5) | IDs auf offizielle BSI-Kapitel (3. Initiierung, 6. Betrieb etc.) umschlüsseln. BSI-Texte sind Open Data (dl-de/by-2-0), daher risikoarm. |
| **gobd_requirements.md** | GoBD (BMF Schreiben) | v0.1 (Praxis-Fokus) | Maßnahmen-orientiert | Abgleich mit den Rn. (Randnummern) des BMF-Schreibens. GoBD ist amtliches Werk (§ 5 UrhG), daher strukturidentisch nutzbar. |
| **iso_22301_requirements.md** | ISO 22301:2019 | v0.1 (HLS PDCA) | ISO HLS (Kapitel 4-10) | Struktur ist bereits ISO-konform (High Level Structure). Audit-Fragen gegen Normtext "Shall"-Anforderungen prüfen. |
| **vds_10000_requirements.md** | VdS 10000 (VdS Schadenverhütung) | v0.1 (KMU Fokus) | Themen-Cluster | IDs an die offiziellen Maßnahmen-Kapitel der VdS-Richtlinie anpassen. Texte zwingend paraphrasieren (proprietär!). |
| **vds_10010_requirements.md** | VdS 10010 (DSGVO Umsetzung) | v0.1 (DSGVO Fokus) | Themen-Cluster | Abgleich mit VdS-Kapiteln. Fokus auf DSGVO-Artikel (Art. 30, 32) beibehalten, da diese Gesetz (frei) sind. |
| **dsgvo_requirements.md** | Datenschutz-Grundverordnung (EU-DSGVO) | v0.1 (Gesetzestext) | Artikel-Struktur (Art. 5-39) | Direktabgleich mit den Artikeln der Verordnung. Da EU-Verordnung, ist der Text als amtliches Werk gemeinfrei nutzbar. |
| **idw_rs_fait_1_requirements.md** | IDW RS FAIT 1 | v0.1 (Prüfungssicht) | Prüffeldern (IT-Umfeld etc.) | Abgleich mit den offiziellen Textziffern (Tz.) des Standards. |
| **datev_best_practices_requirements.md** | DATEV Hilfe-Center / Best Practices | v0.1 (Tech-Stack) | Tech-Cluster (SQL, OS) | Prüfen neuer DATEV-Doks (z.B. bei SQL 2022 Release). Sehr dynamisch, da technische Abhängigkeit. |
| **marisk_at_7_3_requirements.md** | MaRisk (BaFin) | v0.1 (AT 7.3 Fokus) | AT 7.3 Struktur (Tz. 1-7) | Struktur ist bereits sehr nah am Originaltext (BaFin Rundschreiben sind amtliche Werke). |
| **stgb_203_bstbk_requirements.md** | § 203 StGB / Berufsrecht | v0.1 (Juristischer Fokus) | Gesetzliche Anforderungen | Stabil. Änderungen nur bei StGB-Novellen oder neuen Kammerhinweisen. |
| **nis2_requirements.md** | NIS-2 Richtlinie / BSIG (KRITIS) | v0.1 (Gesetz/BSIG) | Artikel-Struktur (Governance, Risk) | Abgleich mit finalem deutschen BSIG-Umsetzungsgesetz. Als Gesetzestext gemeinfrei (§ 5 UrhG), Umsetzungspflichten für KMU/MSP beachten. |

## Versions-Historie

*   **v0.1 (23.01.2026):** Initiale Erstellung der Kataloge basierend auf Best-Practice-Wissen und öffentlich verfügbaren Zusammenfassungen der Standards. Fokus auf "Übersetzung für KMU".
*   **vX.X (Geplant):** Abgleich mit physischen Standardwerken/Büchern. Erweiterung der ID-Spalte um "Referenz-ID Original".
