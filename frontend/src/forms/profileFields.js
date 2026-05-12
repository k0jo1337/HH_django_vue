const commonProfileFields = [
  { name: "last_name", label: "Фамилия", type: "text", required: true, group: "name" },
  { name: "first_name", label: "Имя", type: "text", required: true, group: "name" },
  { name: "middle_name", label: "Отчество", type: "text", required: true, group: "name" },
  { name: "email", label: "Email", type: "email", required: true, group: "contacts" },
  { name: "phone", label: "Телефон", type: "tel", group: "contacts" },
  { name: "room_number", label: "Комната", type: "text", group: "contacts" },
  { name: "hostel", label: "Общежитие", type: "text", group: "contacts" },
  { name: "university", label: "Институт", type: "text", group: "contacts" },
];

export const profileInitialValues = Object.fromEntries(
  commonProfileFields.map((field) => [field.name, ""])
);

export const editableProfileFields = commonProfileFields;

export const registerInitialValues = {
  username: "",
  email: "",
  last_name: "",
  first_name: "",
  middle_name: "",
  has_no_middle_name: false,
  password: "",
  password_confirm: "",
};

export const registerFields = [
  { name: "username", label: "Логин", type: "text", required: true, autocomplete: "username" },
  { name: "email", label: "Email", type: "email", required: true, autocomplete: "email" },
  ...commonProfileFields.filter((field) =>
    ["last_name", "first_name", "middle_name"].includes(field.name)
  ),
  { name: "password", label: "Пароль", type: "password", required: true, autocomplete: "new-password" },
  { name: "password_confirm", label: "Повторите пароль", type: "password", required: true, autocomplete: "new-password" },
];
