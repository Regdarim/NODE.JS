#!/usr/bin/env python3
"""Build Antik Holz Profis lead-gen Excel from research/leads_raw.json."""
import json
import re
from pathlib import Path
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from enrichment_data import ENRICH  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "research" / "leads_raw.json"
OUT = ROOT / f"Antik_Holz_Leads_PL_100_ENRICHED_{date.today().isoformat()}.xlsx"

CATEGORY_PL = {
    "hurtownia_drewna": "Hurtownia drewna / dystrybutor",
    "stolarnia_pracownia": "Stolarnia / pracownia",
    "renowacja_zabytkow": "Renowacja zabytków",
    "elewacja_drewniana": "Elewacje drewniane",
    "producent_podlog": "Producent podłóg",
    "producent_mebli_stare_drewno": "Producent mebli (stare drewno)",
    "architekt_wnetrz": "Architekt wnętrz",
    "boutique_hotel_pensjonat": "Boutique hotel / pensjonat",
    "dom_z_bali_szkieletowy": "Dom z bali / szkieletowy",
    "producent_drzwi": "Producent drzwi",
    "sklep_mebli_loft": "Sklep mebli loft/rustykalnych",
}

# Personalization templates per category - cold call/email opener hooks
PERSONALIZATION = {
    "hurtownia_drewna": "Antik Holz wprost zaprasza do sieci dystrybutorów - autentyczne stare deski/belki rozszerzyłyby waszą ofertę o segment premium 'reclaimed wood', który gwałtownie rośnie wśród architektów. Możliwa współpraca jako oficjalny partner regionalny.",
    "stolarnia_pracownia": "Wasze meble na wymiar premium - autentyczne 100-letnie deski sosnowe/jodłowe (nie postarzane, prawdziwe) podniosą cenę sprzedaży i przyciągną klientów szukających unikatów z historią. Antik Holz dostarcza certyfikowany surowiec wprost od producenta.",
    "renowacja_zabytkow": "Do prac konserwatorskich wymagających autentycznego drewna z epoki - Antik Holz ma w stałej ofercie deski rozbiórkowe sosna/świerk/jodła z polskich obiektów. Pochodzenie udokumentowane, drewno fitosanitarne (bez szkodników), gotowe do natychmiastowego montażu.",
    "elewacja_drewniana": "Wasze realizacje elewacji wentylowanych - Antik Holz dostarcza stare deski elewacyjne z naturalną patyną, której nie da się odtworzyć opaleniem czy szczotkowaniem nowej deski. Bezpośredni efekt 'zabytek' bez czekania 20 lat na zwietrzenie.",
    "producent_podlog": "Wasza klasa 'rustic/aged' bazuje pewnie na postarzanym nowym dębie. Antik Holz dostarcza autentyczne stare deski jodłowe/sosnowe/świerkowe z polskich rozbiórek - alternatywa premium dla najbardziej wymagających klientów (boutique hotele, lofty premium).",
    "producent_mebli_stare_drewno": "Robicie meble loft/rustykalne - jeśli kupujecie surowiec na zewnątrz, Antik Holz to największy producent starego drewna w Europie (5 mln m² przetworzone), pełna paleta: deski obiciowe, blaty, belki na nogi stołów. Dostępność od ręki + dostawa B2B w całej Polsce.",
    "architekt_wnetrz": "W projektach loftowych/rustykalnych/boutique - autentyczne stare drewno (nie imitacja) od polskiego producenta. Antik Holz ma showroom w Fałkowie, można odwiedzić z klientem. Próbki wysyłane do studia projektowego gratis na zapytanie architektoniczne.",
    "boutique_hotel_pensjonat": "Wasz obiekt buduje przewagę na klimacie i autentyczności. Antik Holz dostarcza materiały, które robią różnicę w doświadczeniu gościa: drzwi z duszą, podłogi z historią, deski elewacyjne z 100-letnią patyną. Wykorzystywane w boutique hotelach w Tatrach, Karkonoszach, Beskidach.",
    "dom_z_bali_szkieletowy": "Wasi klienci budują z duszą - belki sufitowe, podłogi i elewacje ze starego drewna podniosą wartość projektu o 15-30%. Antik Holz dostarcza belki dębowe i sosnowe rozbiórkowe na konstrukcje widoczne (sufity kasetonowe, słupy konstrukcyjne).",
    "producent_drzwi": "Trend 'drzwi loftowe z desek rozbiórkowych' rośnie. Antik Holz właśnie wprowadził linię 'Drzwi z duszą' - alternatywnie sprzedaje też same deski jako surowiec do waszej produkcji (jeśli macie własną).",
    "sklep_mebli_loft": "Możliwa współpraca private label - Antik Holz produkuje meble ze starego drewna na zamówienie sklepów detalicznych. Dropshipping lub stałe zatowarowanie z marżą salonu.",
}


def normalize_phone(s: str) -> str:
    if not s:
        return ""
    # Remove duplicate whitespace, keep + and digits
    return re.sub(r"\s+", " ", s).strip()


def main():
    data = json.loads(RAW.read_text(encoding="utf-8"))
    target = data["target_company"]
    cats = data["categories"]
    leads_raw = data["leads"]

    # Filter excluded competitors
    leads = [l for l in leads_raw if not l.get("exclude")]

    # Score each lead
    scored = []
    for l in leads:
        cat = l["category"]
        base_score = cats.get(cat, {}).get("icp_fit_default", 5)
        # Bonus signals
        score = base_score
        if l.get("phone_hint"):
            score += 0  # already in data
        if l.get("contact_person_hint"):
            score += 0.5  # named decision-maker on website
        if l.get("email_hint") and "@" in l.get("email_hint", ""):
            score += 0  # already in data
        # Cap 10
        score = min(10, score)

        scored.append({
            "lead": l,
            "score": score,
        })

    # Sort: score desc, then category priority, then name
    scored.sort(key=lambda x: (-x["score"], x["lead"]["category"], x["lead"]["company_name"]))

    # Take top 100
    top = scored[:100]

    # Build workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Leady Antik Holz PL"

    # Title row
    ws["A1"] = f"Lead-gen Antik Holz Profis — 100 leadów cold call/cold email (PL) — {date.today().isoformat()}"
    ws["A1"].font = Font(size=14, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill("solid", fgColor="2F4858")
    ws.merge_cells("A1:L1")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 30

    # Info row
    ws["A2"] = (
        f"Target: {target['name']} — {target['hq']} | Produkty: stare drewno (deski, belki, panele, drzwi z odzysku) | "
        f"Źródło danych: Exa MCP, 12 zapytań mikro-wertykalnych | Sortowanie: ICP Fit malejąco"
    )
    ws["A2"].font = Font(size=10, italic=True, color="555555")
    ws.merge_cells("A2:L2")
    ws["A2"].alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.row_dimensions[2].height = 35

    # Header
    headers = [
        "Lp",
        "Firma",
        "Strona WWW",
        "Branża",
        "Lokalizacja",
        "Decydent",
        "Stanowisko",
        "LinkedIn",
        "Email",
        "Telefon",
        "ICP Fit (1-10)",
        "Personalizacja / Trigger (cold outreach)",
    ]
    for col_idx, h in enumerate(headers, start=1):
        c = ws.cell(row=4, column=col_idx, value=h)
        c.font = Font(bold=True, color="FFFFFF", size=11)
        c.fill = PatternFill("solid", fgColor="4A6FA5")
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = Border(
            left=Side(style="thin", color="888888"),
            right=Side(style="thin", color="888888"),
            top=Side(style="thin", color="888888"),
            bottom=Side(style="medium", color="2F4858"),
        )
    ws.row_dimensions[4].height = 32

    # Data rows
    fill_high = PatternFill("solid", fgColor="C8E6C9")     # ICP 8-10 green
    fill_mid = PatternFill("solid", fgColor="FFF9C4")      # ICP 5-7 yellow
    fill_low = PatternFill("solid", fgColor="FFCDD2")      # ICP 1-4 red
    fill_alt = PatternFill("solid", fgColor="F5F7FA")      # alternating row
    border_thin = Border(
        left=Side(style="thin", color="DDDDDD"),
        right=Side(style="thin", color="DDDDDD"),
        top=Side(style="thin", color="DDDDDD"),
        bottom=Side(style="thin", color="DDDDDD"),
    )

    row = 5
    for idx, item in enumerate(top, start=1):
        l = item["lead"]
        score = item["score"]
        cat_pl = CATEGORY_PL.get(l["category"], l["category"])

        company = l.get("company_name", "")
        website = l.get("website", "")
        location = l.get("location_hint", "")

        # Apply enrichment data (Exa web_fetch on /kontakt pages)
        enrich = ENRICH.get(company, {})

        decydent = enrich.get("contact_person") or l.get("contact_person_hint", "")
        stanowisko = enrich.get("position", "")
        # Try to split if contact_person_hint contains "(stanowisko)"
        m = re.match(r"^(.*?)\s*\((.*?)\)\s*$", decydent)
        if m:
            decydent = m.group(1).strip()
            if not stanowisko:
                stanowisko = m.group(2).strip()
        elif decydent and not stanowisko:
            stanowisko = "Właściciel / Założyciel"

        linkedin = ""
        email = enrich.get("email") or l.get("email_hint", "")
        phone = normalize_phone(enrich.get("phone") or l.get("phone_hint", ""))
        # Address override from enrichment (more reliable)
        if enrich.get("address"):
            location = enrich["address"]
        # Append phone_extra to phone if any
        if enrich.get("phone_extra"):
            phone = (phone + " | " + enrich["phone_extra"]) if phone else enrich["phone_extra"]
        personalizacja = PERSONALIZATION.get(l["category"], "")
        notes = l.get("notes", "")
        if notes:
            personalizacja = f"{personalizacja}\n\nKontekst: {notes}"

        score_str = f"{int(score)}" if score == int(score) else f"{score:.1f}"

        values = [
            idx,
            company,
            website,
            cat_pl,
            location,
            decydent or "—  do uzupełnienia ręcznie",
            stanowisko or "—",
            linkedin or "—  szukaj na LinkedIn Sales Nav",
            email or "—  sprawdź na stronie /kontakt",
            phone or "—  sprawdź na stronie /kontakt",
            score_str,
            personalizacja,
        ]

        for col_idx, v in enumerate(values, start=1):
            c = ws.cell(row=row, column=col_idx, value=v)
            c.alignment = Alignment(vertical="top", wrap_text=True)
            c.border = border_thin
            if col_idx == 3 and website:
                c.hyperlink = website if website.startswith("http") else f"https://{website}"
                c.font = Font(color="1A5490", underline="single")

        # ICP fit coloring
        icp_cell = ws.cell(row=row, column=11)
        icp_cell.alignment = Alignment(horizontal="center", vertical="center")
        icp_cell.font = Font(bold=True, size=12)
        if score >= 8:
            icp_cell.fill = fill_high
        elif score >= 5:
            icp_cell.fill = fill_mid
        else:
            icp_cell.fill = fill_low

        # Alternating row background (skip if ICP already colored that col)
        if idx % 2 == 0:
            for col_idx in range(1, 13):
                if col_idx != 11:
                    ws.cell(row=row, column=col_idx).fill = fill_alt

        # Row height for wrapped text
        ws.row_dimensions[row].height = 95

        row += 1

    # Column widths
    widths = {
        "A": 5,    # Lp
        "B": 32,   # Firma
        "C": 32,   # WWW
        "D": 24,   # Branża
        "E": 28,   # Lokalizacja
        "F": 22,   # Decydent
        "G": 22,   # Stanowisko
        "H": 22,   # LinkedIn
        "I": 30,   # Email
        "J": 30,   # Telefon
        "K": 10,   # ICP fit
        "L": 60,   # Personalizacja
    }
    for col, w in widths.items():
        ws.column_dimensions[col].width = w

    ws.freeze_panes = "A5"

    # Summary sheet
    ws2 = wb.create_sheet("Podsumowanie")
    ws2["A1"] = "Podsumowanie kampanii cold outreach"
    ws2["A1"].font = Font(size=14, bold=True)
    ws2.merge_cells("A1:C1")

    ws2["A3"] = "Target"
    ws2["A3"].font = Font(bold=True)
    ws2["B3"] = target["name"]
    ws2["A4"] = "HQ"
    ws2["A4"].font = Font(bold=True)
    ws2["B4"] = target["hq"]
    ws2["A5"] = "URL"
    ws2["A5"].font = Font(bold=True)
    ws2["B5"] = target["url"]
    ws2["A6"] = "Liczba leadów"
    ws2["A6"].font = Font(bold=True)
    ws2["B6"] = len(top)
    ws2["A7"] = "Data generacji"
    ws2["A7"].font = Font(bold=True)
    ws2["B7"] = date.today().isoformat()

    # Per-category breakdown
    ws2["A9"] = "Podział kategorii w top 100"
    ws2["A9"].font = Font(bold=True, size=12)
    ws2.merge_cells("A9:C9")

    ws2["A10"] = "Kategoria"
    ws2["B10"] = "Liczba"
    ws2["C10"] = "Średni ICP Fit"
    for c in ["A10", "B10", "C10"]:
        ws2[c].font = Font(bold=True, color="FFFFFF")
        ws2[c].fill = PatternFill("solid", fgColor="4A6FA5")
        ws2[c].alignment = Alignment(horizontal="center")

    cat_stats = {}
    for item in top:
        cat = item["lead"]["category"]
        cat_stats.setdefault(cat, []).append(item["score"])

    sorted_cats = sorted(cat_stats.items(), key=lambda x: -sum(x[1]) / len(x[1]))
    r = 11
    for cat, scores in sorted_cats:
        ws2.cell(row=r, column=1, value=CATEGORY_PL.get(cat, cat))
        ws2.cell(row=r, column=2, value=len(scores)).alignment = Alignment(horizontal="center")
        avg = sum(scores) / len(scores)
        ws2.cell(row=r, column=3, value=round(avg, 1)).alignment = Alignment(horizontal="center")
        r += 1

    # ICP distribution
    r += 2
    ws2.cell(row=r, column=1, value="Rozkład ICP Fit").font = Font(bold=True, size=12)
    r += 1
    high = sum(1 for it in top if it["score"] >= 8)
    mid = sum(1 for it in top if 5 <= it["score"] < 8)
    low = sum(1 for it in top if it["score"] < 5)
    ws2.cell(row=r, column=1, value="ICP 8-10 (priorytet 1)")
    ws2.cell(row=r, column=2, value=high).fill = fill_high
    ws2.cell(row=r, column=2).alignment = Alignment(horizontal="center")
    r += 1
    ws2.cell(row=r, column=1, value="ICP 5-7 (priorytet 2)")
    ws2.cell(row=r, column=2, value=mid).fill = fill_mid
    ws2.cell(row=r, column=2).alignment = Alignment(horizontal="center")
    r += 1
    ws2.cell(row=r, column=1, value="ICP 1-4 (priorytet 3)")
    ws2.cell(row=r, column=2, value=low).fill = fill_low
    ws2.cell(row=r, column=2).alignment = Alignment(horizontal="center")

    # Methodology note
    r += 3
    ws2.cell(row=r, column=1, value="Metodologia").font = Font(bold=True, size=12)
    r += 1
    notes_text = (
        "Dane zebrane przez Exa MCP web_search w 12 zapytaniach mikro-wertykalnych pokrywających "
        "ICP Antik Holz: hurtownie drewna, stolarnie, architekci, boutique hotele, producenci podłóg/drzwi/mebli, "
        "firmy elewacji drewnianych, renowacja zabytków, firmy budowy domów z bali, sklepy detaliczne loft. "
        "\n\nUwaga: Dane kontaktowe (email, telefon) pochodzą ze stron firmowych dostępnych publicznie. "
        "Imię decydenta i LinkedIn URL wymagają dodatkowego enrichmentu (Tavily/Firecrawl/SerpAPI - "
        "blokowane w obecnym network policy). "
        "\n\nWykluczeni z listy konkurenci Antik Holz: Holy-Wood, Regalia, Retrowood, Manufaktura Eco-Deco-Art "
        "(każdy z nich ma własne pozyskanie starego drewna)."
    )
    ws2.cell(row=r, column=1, value=notes_text).alignment = Alignment(wrap_text=True, vertical="top")
    ws2.merge_cells(start_row=r, start_column=1, end_row=r + 8, end_column=4)
    for rr in range(r, r + 9):
        ws2.row_dimensions[rr].height = 18

    ws2.column_dimensions["A"].width = 35
    ws2.column_dimensions["B"].width = 18
    ws2.column_dimensions["C"].width = 18
    ws2.column_dimensions["D"].width = 35

    wb.save(OUT)
    print(f"✓ Zapisano: {OUT}")
    print(f"  Leadów w pliku: {len(top)}")
    print(f"  Kategorii: {len(cat_stats)}")
    print(f"  ICP 8-10: {high} | 5-7: {mid} | 1-4: {low}")


if __name__ == "__main__":
    main()
