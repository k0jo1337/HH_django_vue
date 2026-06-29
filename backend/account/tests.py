from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from account.debtors import parse_debtors_xlsx
from account.models import UserProfile


def make_debtors_xlsx(full_name="Игнатов Алесандр Вадимовч", room="968", debit=None, credit="292.23"):
    def string_cell(reference, value):
        return f'<c r="{reference}" t="inlineStr"><is><t>{value}</t></is></c>'

    def number_cell(reference, value):
        return "" if value is None else f'<c r="{reference}"><v>{value}</v></c>'

    worksheet = f'''<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    <row r="6">
      {string_cell("B6", "Квартиросъемщик")}
      {string_cell("C6", "№ ком.")}
      {string_cell("M6", "Кон. Остаток")}
    </row>
    <row r="7">
      {string_cell("M7", "Дебет")}
      {string_cell("N7", "Кредит")}
    </row>
    <row r="8">
      {string_cell("B8", full_name)}
      {number_cell("C8", room)}
      {number_cell("M8", debit)}
      {number_cell("N8", credit)}
    </row>
  </sheetData>
</worksheet>'''

    result = BytesIO()
    with ZipFile(result, "w", ZIP_DEFLATED) as archive:
        archive.writestr("xl/worksheets/sheet1.xml", worksheet)
    return result.getvalue()


class DebtorsXlsxTests(TestCase):
    def test_parser_reads_ending_credit(self):
        rows = parse_debtors_xlsx(BytesIO(make_debtors_xlsx()))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].room_number, "968")
        self.assertEqual(str(rows[0].debit), "0")
        self.assertEqual(str(rows[0].credit), "292.23")

    def test_parser_reads_ending_debit(self):
        rows = parse_debtors_xlsx(BytesIO(make_debtors_xlsx(debit="160", credit=None)))

        self.assertEqual(str(rows[0].debit), "160.00")
        self.assertEqual(str(rows[0].credit), "0")

    def test_employee_upload_matches_typo_by_name_and_room(self):
        employee = User.objects.create_user(username="employee", password="password")
        employee.groups.add(Group.objects.get(name="Сотрудник"))
        student = User.objects.create_user(
            username="student",
            password="password",
            last_name="Игнатов",
            first_name="Александр",
        )
        profile = UserProfile.objects.create(
            user=student,
            middle_name="Вадимович",
            room_number="968",
        )
        self.client.force_login(employee)

        response = self.client.post(
            reverse("upload_debtors"),
            {"file": SimpleUploadedFile("balances.xlsx", make_debtors_xlsx())},
        )

        self.assertEqual(response.status_code, 200)
        profile.refresh_from_db()
        self.assertEqual(str(profile.balance_debit), "0.00")
        self.assertEqual(str(profile.balance_credit), "292.23")
        self.assertEqual(response.json()["updated"], 1)

    def test_student_cannot_upload_balances(self):
        student = User.objects.create_user(username="student", password="password")
        self.client.force_login(student)

        response = self.client.post(
            reverse("upload_debtors"),
            {"file": SimpleUploadedFile("balances.xlsx", make_debtors_xlsx())},
        )

        self.assertEqual(response.status_code, 403)
