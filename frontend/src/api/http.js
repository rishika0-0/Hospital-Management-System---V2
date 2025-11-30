import axios from "axios";

const http = axios.create({
    baseURL: "http://localhost:5000/api",
});

http.interceptors.request.use(config => {
    const auth = localStorage.getItem("authToken");
    if (auth) config.headers.Authorization = `Bearer ${auth}`;
    return config;
});

export default http;
