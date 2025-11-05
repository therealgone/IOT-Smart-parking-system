// Configure with your ThingSpeak channel details
const CHANNEL_ID = "3148931"; // set to your channel
const READ_API_KEY = "04FY223U16A1SJEW"; // if private, provide read key

const LAST_FEED_URL = `https://api.thingspeak.com/channels/${CHANNEL_ID}/feeds/last.json?api_key=${READ_API_KEY}`;
const CHANNEL_URL = `https://thingspeak.com/channels/${CHANNEL_ID}`;

function updateSlot(id, value) {
  const el = document.getElementById(id);
  const isOcc = String(value) === "1";
  el.classList.toggle("occupied", isOcc);
  el.classList.toggle("available", !isOcc);
  const state = el.querySelector('.state');
  if (state) state.textContent = isOcc ? "Occupied" : "Available";
}

async function fetchData() {
  try {
    const res = await fetch(LAST_FEED_URL, { cache: "no-store" });
    const data = await res.json();
    updateSlot("slot1", data.field1);
    updateSlot("slot2", data.field2);
    updateSlot("slot3", data.field3);
    updateSlot("slot4", data.field4);
    // compute available (value == 0)
    const values = [data.field1, data.field2, data.field3, data.field4];
    const available = values.reduce((acc, v) => acc + (String(v) === '0' ? 1 : 0), 0);
    const availableEl = document.getElementById('availableCount');
    if (availableEl) availableEl.textContent = String(available);
    const lastUpdated = document.getElementById("lastUpdated");
    lastUpdated.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
  } catch (e) {
    console.error("Failed to fetch ThingSpeak data", e);
  }
}

function init() {
  const link = document.getElementById("tsLink");
  link.href = CHANNEL_URL;
  fetchData();
  setInterval(fetchData, 5000);
}

document.addEventListener("DOMContentLoaded", init);

