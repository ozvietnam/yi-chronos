// DOGFOOD-ONLY harness (tạm, xoá sau): mount GieoDuyenPanel với fixture display THẬT,
// không cần auth/API/xu. ?g=nam|nu chọn lá.
import { createApp } from "vue";
import "./styles/main.css";
import GieoDuyenPanel from "./components/GieoDuyenPanel.vue";
import payload from "../dogfood_td.json";

const g = new URLSearchParams(location.search).get("g") || "nam";
window.__DT__ = payload[g] || payload.nam;
createApp(GieoDuyenPanel).mount("#app");
