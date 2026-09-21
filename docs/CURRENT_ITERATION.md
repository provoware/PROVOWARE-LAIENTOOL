# PROVOWARE â€“ Current Iteration

## M01 â€“ Info-Text-Konsistenz und Wartbarkeit

**Status:** ğŸŸ¢ REPOSITORY-BLOCK UMGESETZT
**Fortschritt:** `â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆ 100 %`

**Basis vor M01:** `fcbdd9048eb082cd86a73cff74bacc43dbf6d299`

Der I26-Merge war auf `main` bereits abgeschlossen. Der anschlieÃŸende `repo-quality`-Push-Lauf **#83** (`35633942745`) war vollstÃ¤ndig grÃ¼n. M01 verÃ¤ndert keine Produktlogik.

## A â€“ FESTER PLAN

**Ziel:** Informationsdateien und Repository-Wartbarkeit vollstÃ¤ndig prÃ¼fen, nachgewiesene Drift beheben und kÃ¼nftige Inkonsistenzen automatisiert frÃ¼her stoppen.

### Analysebefunde

- ğŸŸ¢ 14 Produktmodule unter `src/`, zusammen ca. 2.355 Python-Zeilen geprÃ¼ft.
- ğŸŸ¢ 17 Testdateien mit 143 Testmethoden; keine TODO/FIXME-HÃ¤ufung festgestellt.
- ğŸŸ¢ 8 Wartungs-/Evidence-Skripte vorhanden.
- ğŸŸ¡ `application_core.py` liegt bei rund 500 Zeilen: Beobachtungsschwelle, aber aktuell kein begrÃ¼ndeter Zwangsrefactor.
- ğŸ”´ README und TODO enthielten mehrere bereits Ã¼berholte â€CI ausstehend/Ã¼ber CI einfrierenâ€œ-Angaben.
- ğŸ”´ diese Datei meldete I26 Merge/Post-Merge noch als ausstehend, obwohl `main` und Lauf #83 grÃ¼n waren.
- ğŸ”´ `docs/REGRESSION_MATRIX.md` enthielt einen wÃ¶rtlichen `\n`-Trenner innerhalb der Tabelle.
- ğŸŸ¡ `scripts/repo_quality.py` fÃ¼hrte fast jede Iterationsdatei einzeln als Pflichtdatei; das erzeugte unnÃ¶tige Pflegekopplung.
- ğŸŸ¡ ein zentraler navigierbarer Dokumentationsindex fehlte.

### Umgesetzter Wartungsblock

- ğŸŸ¢ `docs/README.md` als Dokumentationsindex.
- ğŸŸ¢ `docs/MAINTENANCE.md` als dauerhafter Wartungsvertrag.
- ğŸŸ¢ README/TODO auf dauerhafte Capability-/OPEN-/LOCKED-Aussagen statt flÃ¼chtiger CI-Kopien umgestellt.
- ğŸŸ¢ Regressionsmatrix repariert.
- ğŸŸ¢ Repository-Gate modularisiert.
- ğŸŸ¢ alle Python-Dateien in `src/`, `scripts/`, `tests/` und `start.py` werden syntaktisch geprÃ¼ft.
- ğŸŸ¢ relative Markdown-Links werden auf existierende Ziele geprÃ¼ft.
- ğŸŸ¢ alle `docs/I??_*.md` mÃ¼ssen im Dokumentationsindex auffindbar sein.
- ğŸŸ¢ versehentliche wÃ¶rtliche Backslash-n-TabellenumbrÃ¼che werden blockiert.
- ğŸŸ¢ flÃ¼chtige CI-Statusformulierungen in README/TODO werden blockiert.

## B â€“ VARIABLE FOLGEAUFGABE

**Quelle:** Vollanalyse der Informationsarchitektur.

**Befund:** Der bisherige Prozess versuchte CI-/Merge-LivezustÃ¤nde in dauerhaften Dateien zu spiegeln. Dadurch entstand nach erfolgreichen Merges regelmÃ¤ÃŸig Statusdrift.

**MaÃŸnahme:** GitHub blee‰ĞEÕ•±±”›ñÈ…­ÑÕ•±±•¸AH´½]½É­™±½Ü´½5•É”µiÕÍÑ…¹ì‘…Õ•É¡…™Ñ”I•Á¼µQ•áÑ”ÍÁ•¥¡•É¸¹ÕÈ™…¡±¥ ‰•±•Ñ”iÕÍÓ‘¹‘”Õ¹¡¥ÍÑ½É¥Í¡”Ù¥‘•¹”¸((¨©MÑ…ÑÕÌè¨¨ƒÂ~~ˆ¥¸½Ù•É¹…¹”Õ¹5…¥¹Ñ•¹…¹”µY•ÉÑÉ…œƒñ‰•É›ñ¡ÉĞ¸((ŒŒM¥¡•É¡•¥ÑÍÉ•¹é”()4ÀÄÙ•Ë‘¹‘•ÉĞ…ÕÍÍ¡±¥—}±¥ ½­Õµ•¹Ñ…Ñ¥½¸°I•Á½Í¥Ñ½ÉäµAËñ™½‘”Õ¹AHµAÉ½é•ÍÍµ•Ñ…‘…Ñ•¸¸()-•¥¸è((´AÉ½‘Õ­ÑÙ•É¡…±Ñ•¸ì(´…Ñ•¤µá•ÕÑ½Èì(´A•ÉÍ¥ÍÑ•¹èì(´Õ…ÉµI=A8ì(´9•Ñéİ•É­Á™…¥´AÉ½‘Õ­Ğì(´•Á•¹‘•¹äµiÕİ…¡Ì¸((ŒŒá¥Ğµ…Ñ•Ì((Ä¸I•Á½Í¥Ñ½Éäµ½¹ÑÉ…ĞAML¸(È¸%¹™¼µQ•áĞµ%µÁ…ĞAML¸(Ì¸I•…µ½¹±äµ1½¬AML¸(Ğ¸Ù½±±ÍÓ‘¹‘¥”I•É•ÍÍ¥½¸µMÕ¥Ñ”AML¸(Ô¸½É”¥…¹½ÍÑ¥ŒAML¸(Ø¸¥…¹½ÍÑ¥ŒM¹…ÁÍ¡½ĞAML¸(Ü¸MÑ…ÉÑ•ÈµAÉ•™±¥¡Ğ-±…ÉÑ•áĞ½)M=8AML¸(à¸™¥¹…±•È¥™˜½¡¹”AÉ½‘Õ­Ñ±½¥¬¸(ä¸AHµ$AML¸(ÄÀ¸A½ÍĞµ5•É”µ5…¥¸µ$AML¸((ŒŒ;‘¡ÍÑ”‘É•¤Ù½É•Á±…¹Ñ”AÉ½‘Õ­ÑÍ¡É¥ÑÑ”((ŒŒŒ€Ä¸ƒÂ~RÔ$ÄÜµƒŠLÉ•…±•ÈU$µi¥•±ÍåÍÑ•µ±…Õ˜)]•¥Ñ•É¡¥¸•¥¹é¥•ÌÍ¥¡Ñ‰…É•ÌU$´½•ÍÍ¥‰¥±¥Ñäµ…Ñ”¸((ŒŒŒ€È¸ƒÂ~RÔ$ÈÔƒŠL‘…ÁÑ•Èµ%µÁ±•µ•¹Ñ¥•ÉÕ¹œ)ÉÍĞ¹… Ëñ¹•´É•…±•´$ÄÜµ	•™Õ¹¸((ŒŒŒ€Ì¸ƒÂ~RÔ$ÈÜƒŠL]É¥Ñ•ÈµÍÁ•é¥™¥Í¡•ÈÕ…É•¥Í¥½¸½AÉ½Ñ½ÑåÁ”)iÕ•ÉÍĞ•á…­Ñ”Õ…ÉµÉ¡¥Ñ•­ÑÕÈÕ¹9¼µ±½‰‰•ÈµA±…ÑÑ™½Éµ‰•İ•¥Ìì¹½ ­•¥¸ÁÉ½‘Õ­Ñ¥Ù•ÈáÁ½ÉĞµ‘…ÁÑ•È¸(