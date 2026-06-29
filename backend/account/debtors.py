import re
import zipfile
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher
from pathlib import PurePosixPath
from xml.etree import ElementTree


SPREADSHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
MAX_UNCOMPRESSED_SIZE = 25 * 1024 * 1024
MAX_ARCHIVE_ENTRIES = 1000


class DebtorsFileError(ValueError):
    pass


@dataclass(frozen=True)
class DebtorRow:
    row_number: int
    full_name: str
    room_number: str
    debit: Decimal
    credit: Decimal


def _tag(name):
    return f"{{{SPREADSHEET_NS}}}{name}"


def _column_number(cell_reference):
    letters = re.match(r"[A-Z]+", cell_reference or "")
    if not letters:
        return 0

    result = 0
    for letter in letters.group(0):
        result = result * 26 + ord(letter) - ord("A") + 1
    return result


def _read_shared_strings(archive):
    try:
        root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []

    return [
        "".join(node.text or "" for node in item.iter(_tag("t")))
        for item in root.findall(_tag("si"))
    ]


def _cell_value(cell, shared_strings):
    cell_type = cell.get("t")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.iter(_tag("t")))

    value_node = cell.find(_tag("v"))
    if value_node is None or value_node.text is None:
        return None

    value = value_node.text
    if cell_type == "s":
        try:
            return shared_strings[int(value)]
        except (ValueError, IndexError):
            raise DebtorsFileError("Файл содержит некорректную таблицу строк")
    return value


def _worksheet_rows(archive, worksheet_name, shared_strings):
    root = ElementTree.fromstring(archive.read(worksheet_name))
    rows = []

    for row in root.iter(_tag("row")):
        row_number = int(row.get("r", len(rows) + 1))
        values = {}
        for cell in row.findall(_tag("c")):
            column = _column_number(cell.get("r"))
            if column:
                values[column] = _cell_value(cell, shared_strings)
        rows.append((row_number, values))

    return rows


def _normalize_header(value):
    return re.sub(r"[^a-zа-я0-9]", "", str(value or "").lower().replace("ё", "е"))


def _find_column(values, predicate):
    for column, value in values.items():
        if predicate(_normalize_header(value)):
            return column
    return None


def _parse_decimal(value, row_number, title):
    if value is None or str(value).strip() == "":
        return Decimal("0")

    normalized = str(value).strip().replace("\u00a0", "").replace(" ", "").replace(",", ".")
    try:
        amount = Decimal(normalized)
    except InvalidOperation as exc:
        raise DebtorsFileError(
            f"Строка {row_number}: значение «{value}» в столбце «{title}» не является числом"
        ) from exc

    if amount < 0:
        raise DebtorsFileError(f"Строка {row_number}: сумма в столбце «{title}» не может быть отрицательной")
    return amount.quantize(Decimal("0.01"))


def _extract_rows(rows):
    for header_index, (header_row_number, header_values) in enumerate(rows):
        name_column = _find_column(
            header_values,
            lambda value: value in {"квартиросъемщик", "квартиросъёмщик", "фио"},
        )
        room_column = _find_column(
            header_values,
            lambda value: value in {"ком", "комната", "номеркомнаты", "комната№"}
            or value.startswith("№ком"),
        )
        ending_column = _find_column(
            header_values,
            lambda value: value in {"коностаток", "конечныйостаток"},
        )
        if not all((name_column, room_column, ending_column)):
            continue

        for subheader_index in range(header_index, min(header_index + 3, len(rows))):
            _, subheader_values = rows[subheader_index]
            debit_column = _find_column(
                {column: value for column, value in subheader_values.items() if ending_column <= column <= ending_column + 3},
                lambda value: value == "дебет",
            )
            credit_column = _find_column(
                {column: value for column, value in subheader_values.items() if ending_column <= column <= ending_column + 3},
                lambda value: value == "кредит",
            )
            if not debit_column or not credit_column:
                continue

            result = []
            for row_number, values in rows[subheader_index + 1:]:
                full_name = str(values.get(name_column) or "").strip()
                room_number = normalize_room(values.get(room_column))
                if not full_name or not room_number:
                    continue

                result.append(DebtorRow(
                    row_number=row_number,
                    full_name=full_name,
                    room_number=room_number,
                    debit=_parse_decimal(values.get(debit_column), row_number, "Дебет"),
                    credit=_parse_decimal(values.get(credit_column), row_number, "Кредит"),
                ))
            return result

    return None


def parse_debtors_xlsx(file_object):
    try:
        with zipfile.ZipFile(file_object) as archive:
            entries = archive.infolist()
            if len(entries) > MAX_ARCHIVE_ENTRIES or sum(item.file_size for item in entries) > MAX_UNCOMPRESSED_SIZE:
                raise DebtorsFileError("Excel-файл слишком большой после распаковки")

            shared_strings = _read_shared_strings(archive)
            worksheet_names = sorted(
                item.filename
                for item in entries
                if PurePosixPath(item.filename).parts[:2] == ("xl", "worksheets")
                and item.filename.endswith(".xml")
            )

            for worksheet_name in worksheet_names:
                extracted = _extract_rows(_worksheet_rows(archive, worksheet_name, shared_strings))
                if extracted is not None:
                    if not extracted:
                        raise DebtorsFileError("В таблице не найдено ни одного студента")
                    return extracted
    except zipfile.BadZipFile as exc:
        raise DebtorsFileError("Выбранный файл не является корректным Excel-файлом .xlsx") from exc
    except ElementTree.ParseError as exc:
        raise DebtorsFileError("Не удалось прочитать структуру Excel-файла") from exc

    raise DebtorsFileError(
        "Не найдены столбцы «Квартиросъемщик», «№ ком.» и «Кон. Остаток — Дебет/Кредит»"
    )


def normalize_room(value):
    value = str(value or "").strip()
    try:
        number = Decimal(value.replace(",", "."))
        if number == number.to_integral():
            return str(int(number))
    except InvalidOperation:
        pass
    return _normalize_header(value)


def normalize_name(value):
    return " ".join(re.findall(r"[a-zа-я0-9]+", str(value or "").lower().replace("ё", "е")))


def profile_full_name(profile):
    return " ".join(filter(None, (
        profile.user.last_name,
        profile.user.first_name,
        profile.middle_name,
    )))


def match_debtor_row(row, profiles):
    source_name = normalize_name(row.full_name)
    source_surname = source_name.split(" ", 1)[0]
    room_candidates = [
        profile for profile in profiles
        if normalize_room(profile.room_number) == row.room_number
    ]

    def score(profile):
        return SequenceMatcher(None, source_name, normalize_name(profile_full_name(profile))).ratio()

    exact_candidates = [
        profile for profile in room_candidates
        if normalize_name(profile_full_name(profile)) == source_name
    ]
    if len(exact_candidates) == 1:
        return exact_candidates[0], None

    ranked = sorted(((score(profile), profile) for profile in room_candidates), reverse=True, key=lambda item: item[0])
    if ranked:
        best_score, best_profile = ranked[0]
        best_surname = normalize_name(profile_full_name(best_profile)).split(" ", 1)[0]
        second_score = ranked[1][0] if len(ranked) > 1 else 0
        if (source_surname == best_surname or best_score >= 0.82) and best_score - second_score >= 0.05:
            return best_profile, None

    global_exact = [
        profile for profile in profiles
        if normalize_name(profile_full_name(profile)) == source_name
    ]
    if len(global_exact) == 1:
        return global_exact[0], None

    if not room_candidates:
        reason = "не найден студент с такой комнатой"
    else:
        reason = "ФИО не удалось однозначно сопоставить со студентом из этой комнаты"
    return None, reason
