# home_search/management/commands/import_classes.py
import os
import re
import pandas as pd
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from home_search.models import Class, CATEGORY_CHOICES


ALLOWED_CATS = {k for k, _ in CATEGORY_CHOICES}
ALIASES = {
    "ice": "ice-skating",
    "ice skating": "ice-skating",
    "iceskating": "ice-skating",
    "muay-thai": "muaythai",
    "muay thai": "muaythai",
}

# Common column name variants we’ll try to match (case-insensitive)
CANDIDATES = {
    "no": ["no", "number", "index", "row", "Unnamed: 0"],
    "category": ["category", "kategori", "class type", "Unnamed: 2"],
    "class_name": ["class name", "nama kelas", "title", "name", "Unnamed: 3"],
    "price": ["price", "harga", "cost", "fee", "Unnamed: 7"],
    "description": ["description", "deskripsi", "details", "Unnamed: 8"],
    "picture": ["picture", "image", "photo", "img", "image url", "link", "Unnamed: 9"],
}


def find_col(df: pd.DataFrame, keys: list[str]) -> Optional[str]:
    """Find a column in df whose name matches any in keys (case-insensitive/stripped)."""
    normalized = {c.strip().lower(): c for c in df.columns}
    for k in keys:
        k_norm = k.strip().lower()
        if k_norm in normalized:
            return normalized[k_norm]
    # try partial contains match
    for want in keys:
        want_norm = want.strip().lower()
        for c in df.columns:
            if want_norm in c.strip().lower():
                return c
    return None


def norm_cat(x: str) -> str:
    if x is None:
        return ""
    s = str(x).strip().lower()
    s = ALIASES.get(s, s)
    s = s.replace(" ", "-")
    return s


def parse_price(v) -> int:
    """Convert strings like 'Rp 400.000' or '400,000' or 400000 to int 400000."""
    if v is None:
        return 0
    if isinstance(v, (int, float)):
        try:
            return int(round(float(v)))
        except Exception:
            return 0
    s = str(v)
    # keep digits only
    digits = re.sub(r"[^\d]", "", s)
    return int(digits) if digits else 0


class Command(BaseCommand):
    help = "Import classes from an Excel sheet into home_search.Class (no owner is set)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            default="Dataset ReServe - PBP K5.xlsx",
            help="Path to the Excel file.",
        )
        parser.add_argument(
            "--sheet",
            default="Classes",
            help="Worksheet name (default: 'Classes').",
        )
        parser.add_argument(
            "--header-row",
            type=int,
            default=2,
            help="Zero-based header row index passed to pandas.read_excel(header=...). "
                 "If your sheet has proper headers on the first row, use 0.",
        )
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Delete all Class rows before importing.",
        )

    def handle(self, *args, **options):
        path = options["path"]
        sheet = options["sheet"]
        header_row = options["header_row"]
        truncate = options["truncate"]

        if not os.path.exists(path):
            raise CommandError(f"File not found: {path}")

        try:
            df = pd.read_excel(path, sheet_name=sheet, header=header_row)
        except Exception as e:
            raise CommandError(f"Failed to read Excel: {e}")

        # Resolve required columns
        col_no = find_col(df, CANDIDATES["no"])
        col_category = find_col(df, CANDIDATES["category"])
        col_name = find_col(df, CANDIDATES["class_name"])
        col_price = find_col(df, CANDIDATES["price"])
        col_desc = find_col(df, CANDIDATES["description"])
        col_pic = find_col(df, CANDIDATES["picture"])

        missing = [k for k, c in {
            "no": col_no, "category": col_category, "class_name": col_name,
            "price": col_price, "description": col_desc, "picture": col_pic
        }.items() if c is None]
        if missing:
            raise CommandError(
                "Could not find columns in the sheet for: " + ", ".join(missing) +
                "\nColumns present: " + ", ".join(map(str, df.columns))
            )

        # Some sheets repeat a second header row as data (e.g., value 'NO' in No column); drop those.
        df = df.copy()
        df = df[df[col_no].astype(str).str.upper() != "NO"]

        # Forward-fill categories if they are grouped
        df[col_category] = df[col_category].ffill()

        # Keep rows that have a class name
        df = df[df[col_name].notna()].copy()

        # Normalize columns
        df["__category"] = df[col_category].map(norm_cat)
        df["__name"] = df[col_name].astype(str).str.strip()
        df["__price"] = df[col_price].map(parse_price)
        df["__description"] = df[col_desc].fillna("").astype(str).str.strip()
        df["__image_url"] = df[col_pic].fillna("").astype(str).str.strip()

        if truncate:
            self.stdout.write(self.style.WARNING("Truncating home_search.Class ..."))
            Class.objects.all().delete()

        created = 0
        updated = 0
        skipped = 0

        for _, r in df.iterrows():
            name = r["__name"]
            cat = r["__category"]

            if not name:
                skipped += 1
                continue

            if cat not in ALLOWED_CATS:
                # Try aliasing one more time
                cat = ALIASES.get(cat, cat)
                if cat not in ALLOWED_CATS:
                    self.stdout.write(self.style.NOTICE(
                        f"Skip '{name}': unknown category '{r['__category']}'"))
                    skipped += 1
                    continue

            defaults = {
                "price": r["__price"],
                "description": r["__description"],
                "image_url": r["__image_url"],
                # IMPORTANT: we do NOT set owner here (Excel rows are external)
            }

            obj, made = Class.objects.update_or_create(
                name=name,
                category=cat,           # upsert key: (name, category)
                defaults=defaults,
            )
            if made:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. Created {created}, Updated {updated}, Skipped {skipped}."))
