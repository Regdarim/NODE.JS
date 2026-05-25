# Research: Antik Holz Profis — 100 leadów cold call/cold email (PL)

## Cel
Wygenerować profesjonalny plik Excel z 100 leadami z Polski dla firmy **Antik Holz Profis** (antikholzprofis.com, Fałków) — producent i hurtowy sprzedawca starego drewna B2B na rynek europejski.

## Stan researchu

Plik `leads_raw.json` zawiera **137 unikalnych polskich firm** zebranych w poprzedniej sesji przez Exa MCP (`web_search_exa` × 12 zapytań mikro-wertykalnych).

Podział kategorii:

| Kategoria | Liczba | ICP fit (domyślny) |
|---|---:|---:|
| hurtownia_drewna | 16 | 9 |
| dom_z_bali_szkieletowy | 15 | 6 |
| renowacja_zabytkow | 14 | 8 |
| stolarnia_pracownia | 14 | 8 |
| boutique_hotel_pensjonat | 13 | 6 |
| producent_drzwi | 12 | 5 |
| sklep_mebli_loft | 12 | 4 |
| producent_podlog | 11 | 7 |
| architekt_wnetrz | 10 | 7 |
| elewacja_drewniana | 10 | 8 |
| producent_mebli_stare_drewno | 10 | 7 (4 wykluczeni - konkurenci) |

**Wykluczeni konkurenci** (do pominięcia w finalnym Excelu): Holy-Wood, Regalia, Retrowood, Eco-Deco-Art.

## Co dalej (instrukcje dla nowej sesji Claude)

Po wpisaniu przez użytkownika `kontynuuj`:

1. **Sprawdź dostępność API** (powinno działać po zmianie network policy environment):
   ```bash
   curl -s -o /dev/null -w "Tavily: %{http_code}\n" https://api.tavily.com/
   curl -s -o /dev/null -w "Firecrawl: %{http_code}\n" https://api.firecrawl.dev/
   ```

2. **Wczytaj** `research/leads_raw.json` — zawiera URL, kategorię, kontekstowy opis dla każdej firmy oraz wskazówki kontaktowe (`phone_hint`, `email_hint`, `contact_person_hint`) wyłapane już z Exa.

3. **Wzbogać każdą firmę** używając Tavily (priorytet) lub Firecrawl jako fallback:
   - `Tavily /extract` na URL firmy + `/kontakt` → pełny markdown → regex wyciąga email/tel
   - `Tavily /search` zapytanie `"{nazwa firmy} CEO właściciel założyciel"` → imię decydenta
   - `Tavily /search` zapytanie `"{nazwa firmy} LinkedIn"` → URL profilu firmy
   - SerpAPI Google jako triangulacja jeśli Tavily nie ma trafień

4. **Score ICP fit** (1–10) dla każdej firmy — kryteria w `categories.*.ideal_for` w JSON.

5. **Personalizacja / trigger event** — 1-2 zdaniowy haczyk z realnej realizacji widocznej na stronie firmy (np. "Niedawno otwarliście butikowy hotel w Karpaczu z drewnianymi elewacjami — Antik Holz dostarcza autentyczne stuletnie deski elewacyjne, które dałyby budynkowi historyczną patynę").

6. **Wygeneruj plik `.xlsx`** używając `openpyxl`:
   - Kolumny: Lp | Firma | WWW | Branża | Lokalizacja | Decydent | Stanowisko | LinkedIn | Email | Telefon | ICP Fit | Personalizacja
   - Header: bold, tło szare
   - Conditional formatting ICP Fit: 8-10 zielony, 5-7 żółty, 1-4 czerwony
   - Sort: po ICP Fit malejąco
   - Limit: 100 firm (top fit, z wykluczeniem konkurentów)

7. **Wyślij plik** przez `SendUserFile` + zacommituj do brancha + zaktualizuj PR.

## Konfiguracja na start

Wymagane przy nowej sesji:
- Network policy environment z dostępem do `api.tavily.com`, `mcp.tavily.com`, `api.firecrawl.dev` (opcjonalnie też `serpapi.com`)
- Klucze API — użytkownik poda na nowo w nowej sesji lub przez secret env vars (`TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `SERPAPI_KEY`, `EXA_API_KEY`). **Nie commitować kluczy do repo.**
