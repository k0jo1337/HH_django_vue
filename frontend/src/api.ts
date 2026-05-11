import axios from "axios";

const API_HOST = window.location.hostname || "localhost";

const api = axios.create({
  baseURL: `http://${API_HOST}:8000/api`,
  withCredentials: true,
  withXSRFToken: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

export default api;
