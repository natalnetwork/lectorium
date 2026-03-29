// ── Auth state ────────────────────────────────────────────────────────────────
const TOKEN_KEY = "lectorium.token";
const USERNAME_KEY = "lectorium.username";

let authToken = window.localStorage.getItem(TOKEN_KEY) || "";
let authUsername = window.localStorage.getItem(USERNAME_KEY) || "";

function authHeaders(extra = {}) {
    return { Authorization: `Bearer ${authToken}`, Accept: "application/json", ...extra };
}

function storeAuth(token, username) {
    authToken = token;
    authUsername = username;
    window.localStorage.setItem(TOKEN_KEY, token);
    window.localStorage.setItem(USERNAME_KEY, username);
}

function clearAuth() {
    authToken = "";
    authUsername = "";
    window.localStorage.removeItem(TOKEN_KEY);
    window.localStorage.removeItem(USERNAME_KEY);
}

// ── DOM refs ──────────────────────────────────────────────────────────────────
const authScreen = document.getElementById("auth-screen");
const appScreen = document.getElementById("app-screen");
const authError = document.getElementById("auth-error");

const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const loginUsernameEl = document.getElementById("login-username");
const loginPasswordEl = document.getElementById("login-password");
const loginBtn = document.getElementById("login-btn");
const regUsernameEl = document.getElementById("reg-username");
const regPasswordEl = document.getElementById("reg-password");
const registerBtn = document.getElementById("register-btn");
const showRegisterLink = document.getElementById("show-register");
const showLoginLink = document.getElementById("show-login");

const usernameDisplay = document.getElementById("username-display");
const logoutBtn = document.getElementById("logout-btn");

const uploadForm = document.getElementById("upload-form");
const uploadStatus = document.getElementById("upload-status");
const libraryEl = document.getElementById("library");
const readerEl = document.getElementById("reader");
const bookTitleEl = document.getElementById("book-title");
const playBtn = document.getElementById("play-btn");
const stopBtn = document.getElementById("stop-btn");
const prevBtn = document.getElementById("prev-btn");
const nextBtn = document.getElementById("next-btn");
const languageSelect = document.getElementById("language-select");
const voiceSelect = document.getElementById("voice-select");
const rateInput = document.getElementById("rate-input");

// ── UI helpers ────────────────────────────────────────────────────────────────
function showApp() {
    authScreen.classList.add("hidden");
    appScreen.classList.remove("hidden");
    usernameDisplay.textContent = authUsername;
}

function showAuth() {
    appScreen.classList.add("hidden");
    authScreen.classList.remove("hidden");
    loginForm.classList.remove("hidden");
    registerForm.classList.add("hidden");
    authError.classList.add("hidden");
    authError.textContent = "";
}

function showAuthError(message) {
    authError.textContent = message;
    authError.classList.remove("hidden");
}

// ── Auth actions ──────────────────────────────────────────────────────────────
async function doLogin() {
    const username = loginUsernameEl.value.trim();
    const password = loginPasswordEl.value;
    if (!username || !password) {
        showAuthError("Please enter username and password.");
        return;
    }
    try {
        const response = await fetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json", Accept: "application/json" },
            body: JSON.stringify({ username, password }),
        });
        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            showAuthError(data.detail || "Login failed.");
            return;
        }
        const data = await response.json();
        storeAuth(data.access_token, data.username);
        loginPasswordEl.value = "";
        showApp();
        await refreshLibrary();
    } catch {
        showAuthError("Network error. Please try again.");
    }
}

async function doRegister() {
    const username = regUsernameEl.value.trim();
    const password = regPasswordEl.value;
    if (!username || !password) {
        showAuthError("Please enter username and password.");
        return;
    }
    try {
        const response = await fetch("/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json", Accept: "application/json" },
            body: JSON.stringify({ username, password }),
        });
        if (!response.ok) {
            const data = await response.json().catch(() => ({}));
            showAuthError(data.detail || "Registration failed.");
            return;
        }
        const data = await response.json();
        storeAuth(data.access_token, data.username);
        regPasswordEl.value = "";
        showApp();
        await refreshLibrary();
    } catch {
        showAuthError("Network error. Please try again.");
    }
}

function doLogout() {
    stopSpeech();
    clearAuth();
    currentBook = null;
    currentChapterIndex = 0;
    showAuth();
}

// ── Reader state ──────────────────────────────────────────────────────────────
const LANGUAGE_STORAGE_KEY = "lectorium.language";
const VOICE_STORAGE_KEY = "lectorium.voice";
const RATE_STORAGE_KEY = "lectorium.rate";

let currentBook = null;
let currentChapterIndex = 0;
let currentUtterance = null;
let currentSpeechQueue = [];
let currentSpeechIndex = 0;
const coverCache = new Map();

// ── Cover helpers ─────────────────────────────────────────────────────────────
function hashString(value) {
    let hash = 0;
    if (!value) {
        return hash;
    }
    for (let i = 0; i < value.length; i += 1) {
        hash = (hash << 5) - hash + value.charCodeAt(i);
        hash |= 0;
    }
    return hash;
}

function createFallbackCover(title, author, seed) {
    const canvas = document.createElement("canvas");
    canvas.width = 300;
    canvas.height = 420;
    const ctx = canvas.getContext("2d");
    if (!ctx) {
        return "";
    }

    const palettes = [
        ["#0f172a", "#1e293b", "#38bdf8", "#f97316"],
        ["#111827", "#1f2937", "#a855f7", "#f472b6"],
        ["#0b1120", "#1f2937", "#22c55e", "#eab308"],
        ["#111827", "#0f172a", "#06b6d4", "#fb7185"],
    ];

    const paletteIndex = Math.abs(seed || 0) % palettes.length;
    const [bgStart, bgEnd, accent, accentAlt] = palettes[paletteIndex];

    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, bgStart);
    gradient.addColorStop(1, bgEnd);
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = "rgba(148, 163, 184, 0.25)";
    ctx.lineWidth = 6;
    ctx.strokeRect(12, 12, canvas.width - 24, canvas.height - 24);

    for (let i = 0; i < 7; i += 1) {
        const offset = 30 + i * 28;
        ctx.strokeStyle = i % 2 === 0 ? accent : accentAlt;
        ctx.globalAlpha = 0.25;
        ctx.lineWidth = 12;
        ctx.beginPath();
        ctx.moveTo(-40, offset);
        ctx.lineTo(canvas.width + 40, offset + 40);
        ctx.stroke();
    }
    ctx.globalAlpha = 1;

    const safeTitle = title || "Untitled";
    const safeAuthor = author || "Unknown author";

    ctx.fillStyle = "#e2e8f0";
    ctx.font = "bold 28px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    const words = safeTitle.split(" ").slice(0, 4);
    const lines = [];
    let line = "";
    for (const word of words) {
        const next = line ? `${line} ${word}` : word;
        if (ctx.measureText(next).width > 220 && line) {
            lines.push(line);
            line = word;
        } else {
            line = next;
        }
    }
    if (line) {
        lines.push(line);
    }

    const startY = canvas.height / 2 - lines.length * 18;
    lines.forEach((text, index) => {
        ctx.fillText(text, canvas.width / 2, startY + index * 36);
    });

    ctx.fillStyle = "#94a3b8";
    ctx.font = "16px system-ui, sans-serif";
    ctx.fillText(safeAuthor, canvas.width / 2, canvas.height - 60);

    return canvas.toDataURL("image/png");
}

function getCoverUrl(book) {
    if (!book) {
        return "";
    }
    if (book.cover_url) {
        return book.cover_url;
    }

    if (!coverCache.has(book.id)) {
        const seed = hashString(`${book.title || ""}-${book.author || ""}`);
        coverCache.set(book.id, createFallbackCover(book.title, book.author, seed));
    }
    return coverCache.get(book.id) || "";
}

// ── Speech ────────────────────────────────────────────────────────────────────
function stopSpeech() {
    if ("speechSynthesis" in window) {
        window.speechSynthesis.cancel();
    }
    currentUtterance = null;
    currentSpeechQueue = [];
    currentSpeechIndex = 0;
}

function getLanguageFilter() {
    if (!languageSelect) {
        return "all";
    }
    const value = languageSelect.value;
    if (value) {
        return value;
    }

    const stored = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
    return stored || "en";
}

function loadLanguagePreference() {
    if (!languageSelect) {
        return;
    }

    const stored = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (stored) {
        languageSelect.value = stored;
        return;
    }

    if (!languageSelect.value) {
        languageSelect.value = "en";
    }
}

function saveLanguagePreference() {
    if (!languageSelect) {
        return;
    }

    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, languageSelect.value || "all");
}

function loadVoicePreference() {
    const stored = window.localStorage.getItem(VOICE_STORAGE_KEY);
    if (stored) {
        voiceSelect.value = stored;
    }
}

function saveVoicePreference() {
    window.localStorage.setItem(VOICE_STORAGE_KEY, voiceSelect.value || "");
}

function loadRatePreference() {
    if (!rateInput) {
        return;
    }
    const stored = window.localStorage.getItem(RATE_STORAGE_KEY);
    if (stored) {
        rateInput.value = stored;
    }
}

function saveRatePreference() {
    if (!rateInput) {
        return;
    }
    window.localStorage.setItem(RATE_STORAGE_KEY, rateInput.value || "1");
}

function normalizeLang(lang) {
    return (lang || "").toLowerCase().replace("_", "-");
}

function matchesLanguage(voice, languageFilter) {
    if (!voice.lang) {
        return false;
    }

    const normalized = normalizeLang(voice.lang);
    const prefix = `${languageFilter.toLowerCase()}-`;
    return normalized === languageFilter.toLowerCase() || normalized.startsWith(prefix);
}

function filterVoices(voices, languageFilter) {
    if (languageFilter === "all") {
        return voices;
    }

    return voices.filter((voice) => matchesLanguage(voice, languageFilter));
}

function refreshVoices() {
    if (!("speechSynthesis" in window)) {
        return;
    }

    const voices = window.speechSynthesis.getVoices();
    const languageFilter = getLanguageFilter();
    const filteredVoices = filterVoices(voices, languageFilter);
    const selectedVoiceName = voiceSelect.value;
    voiceSelect.innerHTML = "";

    if (!filteredVoices.length) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "No voices available";
        voiceSelect.appendChild(option);
        return;
    }

    for (const voice of filteredVoices) {
        const option = document.createElement("option");
        option.value = voice.name;
        option.textContent = `${voice.name} (${voice.lang})`;
        voiceSelect.appendChild(option);
    }

    if (selectedVoiceName) {
        voiceSelect.value = selectedVoiceName;
    } else {
        loadVoicePreference();
    }

    if (!voiceSelect.value && voiceSelect.options.length) {
        voiceSelect.selectedIndex = 0;
    }
}

// ── Library & reader ──────────────────────────────────────────────────────────
async function refreshLibrary() {
    const response = await fetch("/api/books", { headers: authHeaders() });

    if (response.status === 401) {
        clearAuth();
        showAuth();
        return;
    }

    if (!response.ok) {
        throw new Error(`Failed to load library: ${response.status}`);
    }

    const books = await response.json();
    libraryEl.innerHTML = "";

    if (!books.length) {
        libraryEl.innerHTML = '<p class="muted">No books uploaded yet.</p>';
        return;
    }

    for (const book of books) {
        const item = document.createElement("div");
        item.className = "book-item";

        const cover = document.createElement("img");
        cover.className = "book-cover";
        cover.alt = book.title || "Book cover";
        cover.src = getCoverUrl(book);

        const meta = document.createElement("div");
        meta.className = "book-meta";

        const title = document.createElement("strong");
        title.textContent = book.title || "Untitled";

        const author = document.createElement("span");
        author.className = "muted";
        author.textContent = book.author || "Unknown author";

        meta.appendChild(title);
        meta.appendChild(author);

        const actions = document.createElement("div");
        actions.className = "book-actions";

        const deleteBtn = document.createElement("button");
        deleteBtn.type = "button";
        deleteBtn.className = "danger";
        deleteBtn.textContent = "Remove";
        deleteBtn.addEventListener("click", (event) => {
            event.stopPropagation();
            deleteBook(book.id, book.title);
        });

        actions.appendChild(deleteBtn);

        item.appendChild(cover);
        item.appendChild(meta);
        item.appendChild(actions);

        item.addEventListener("click", () => openBook(book.id));
        libraryEl.appendChild(item);
    }
}

async function deleteBook(bookId, bookTitle) {
    const title = bookTitle || "Untitled";
    const confirmDelete = window.confirm(`Remove "${title}"?`);
    if (!confirmDelete) {
        return;
    }

    try {
        const response = await fetch(`/api/books/${bookId}`, {
            method: "DELETE",
            headers: authHeaders(),
        });

        if (!response.ok) {
            uploadStatus.textContent = "Remove failed";
            return;
        }

        if (currentBook && currentBook.id === bookId) {
            stopSpeech();
            currentBook = null;
            currentChapterIndex = 0;
            renderCurrentChapter();
        }

        uploadStatus.textContent = `Removed: ${title}`;
        await refreshLibrary();
    } catch (error) {
        console.error("remove failed:", error);
        uploadStatus.textContent = "Remove failed";
    }
}

async function openBook(bookId) {
    stopSpeech();

    const response = await fetch(`/api/books/${bookId}`, { headers: authHeaders() });

    if (!response.ok) {
        console.error("Failed to load book", response.status);
        return;
    }

    currentBook = await response.json();
    currentChapterIndex = 0;
    renderCurrentChapter();
}

function renderCurrentChapter() {
    if (!currentBook || !currentBook.chapters || !currentBook.chapters.length) {
        bookTitleEl.textContent = "Select a book";
        readerEl.innerHTML = "";
        return;
    }

    const chapter = currentBook.chapters[currentChapterIndex];
    const safeTitle = currentBook.title || "Untitled";
    const safeAuthor = currentBook.author || "Unknown author";
    bookTitleEl.textContent = `${safeAuthor}: ${safeTitle}`;
    const temp = document.createElement("div");
    temp.innerHTML = chapter.html_content || "";

    const coverUrl = getCoverUrl(currentBook);
    if (coverUrl) {
        const images = temp.querySelectorAll("img");
        let replaced = false;

        images.forEach((img) => {
            const src = (img.getAttribute("src") || "").toLowerCase();
            if (src.includes("cover")) {
                img.setAttribute("src", coverUrl);
                replaced = true;
            }
        });

        if (!replaced && currentChapterIndex === 0) {
            const cover = document.createElement("img");
            cover.src = coverUrl;
            cover.alt = `${currentBook.title} cover`;
            cover.className = "reader-cover";
            temp.prepend(cover);
        }
    }

    readerEl.innerHTML =
        temp.innerHTML || "<p class='muted'>No chapter content available.</p>";
}

function getChapterText(chapterIndex) {
    if (!currentBook || !currentBook.chapters || !currentBook.chapters.length) {
        return "";
    }

    const chapter = currentBook.chapters[chapterIndex];
    const temp = document.createElement("div");
    temp.innerHTML = chapter.html_content || "";
    return (temp.textContent || temp.innerText || "").trim();
}

function findSpeakableChapterIndex(startIndex) {
    if (!currentBook || !currentBook.chapters) {
        return null;
    }

    for (let index = startIndex; index < currentBook.chapters.length; index += 1) {
        const text = getChapterText(index);
        if (text.length > 10) {
            return index;
        }
    }

    return null;
}

function splitTextIntoChunks(text, maxLength = 260) {
    const parts = text.split(/([.!?]+)\s+/);
    const chunks = [];
    let buffer = "";

    for (let index = 0; index < parts.length; index += 2) {
        const sentence = `${parts[index] || ""}${parts[index + 1] || ""}`.trim();
        if (!sentence) {
            continue;
        }

        if (buffer && buffer.length + sentence.length + 1 > maxLength) {
            chunks.push(buffer.trim());
            buffer = sentence;
        } else {
            buffer = buffer ? `${buffer} ${sentence}` : sentence;
        }
    }

    if (buffer.trim()) {
        chunks.push(buffer.trim());
    }

    return chunks;
}

function speakNextChunk(voice, rate) {
    if (!currentSpeechQueue.length || currentSpeechIndex >= currentSpeechQueue.length) {
        return;
    }

    const text = currentSpeechQueue[currentSpeechIndex];
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = rate;

    if (voice) {
        utterance.voice = voice;
    }

    utterance.onend = () => {
        currentSpeechIndex += 1;
        speakNextChunk(voice, rate);
    };

    utterance.onerror = () => {
        currentSpeechQueue = [];
        currentSpeechIndex = 0;
        currentUtterance = null;
    };

    currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
}

function getSelectedVoice() {
    const voices = window.speechSynthesis.getVoices();
    const selectedVoiceName = voiceSelect.value;
    return voices.find((voice) => voice.name === selectedVoiceName) || null;
}

function playCurrentChapter() {
    if (!("speechSynthesis" in window)) {
        uploadStatus.textContent = "Browser speech synthesis is not available.";
        return;
    }

    if (window.speechSynthesis.speaking) {
        return;
    }

    const speakableIndex = findSpeakableChapterIndex(currentChapterIndex);
    if (speakableIndex === null) {
        return;
    }

    if (speakableIndex !== currentChapterIndex) {
        currentChapterIndex = speakableIndex;
        renderCurrentChapter();
    }

    const text = getChapterText(currentChapterIndex);
    if (!text) {
        return;
    }

    stopSpeech();

    const selectedVoice = getSelectedVoice();

    currentSpeechQueue = splitTextIntoChunks(text);
    currentSpeechIndex = 0;

    if (!currentSpeechQueue.length) {
        return;
    }

    const rate = parseFloat(rateInput.value);
    window.setTimeout(() => {
        speakNextChunk(selectedVoice, rate);
    }, 50);
}

async function handleUploadSubmit(event) {
    event.preventDefault();

    const formData = new FormData(uploadForm);
    uploadStatus.textContent = "Uploading...";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            headers: authHeaders({ "X-Requested-With": "fetch" }),
            body: formData,
        });

        const contentType = response.headers.get("content-type") || "";
        const raw = await response.text();

        if (!response.ok) {
            uploadStatus.textContent = "Upload failed";
            return;
        }

        if (!contentType.includes("application/json")) {
            uploadStatus.textContent = "Upload returned non-JSON response";
            return;
        }

        const data = JSON.parse(raw);
        uploadStatus.textContent = `Uploaded: ${data.title || "Untitled"}`;
        uploadForm.reset();
        await refreshLibrary();
    } catch (error) {
        console.error("upload failed:", error);
        uploadStatus.textContent = "Upload failed";
    }
}

// ── Event binding ─────────────────────────────────────────────────────────────
function bindAuthEvents() {
    loginBtn.addEventListener("click", doLogin);
    registerBtn.addEventListener("click", doRegister);

    loginUsernameEl.addEventListener("keydown", (e) => { if (e.key === "Enter") doLogin(); });
    loginPasswordEl.addEventListener("keydown", (e) => { if (e.key === "Enter") doLogin(); });
    regUsernameEl.addEventListener("keydown", (e) => { if (e.key === "Enter") doRegister(); });
    regPasswordEl.addEventListener("keydown", (e) => { if (e.key === "Enter") doRegister(); });

    showRegisterLink.addEventListener("click", (e) => {
        e.preventDefault();
        authError.classList.add("hidden");
        loginForm.classList.add("hidden");
        registerForm.classList.remove("hidden");
    });

    showLoginLink.addEventListener("click", (e) => {
        e.preventDefault();
        authError.classList.add("hidden");
        registerForm.classList.add("hidden");
        loginForm.classList.remove("hidden");
    });

    logoutBtn.addEventListener("click", doLogout);
}

function bindAppEvents() {
    uploadForm.addEventListener("submit", handleUploadSubmit);

    playBtn.addEventListener("click", playCurrentChapter);
    stopBtn.addEventListener("click", stopSpeech);

    prevBtn.addEventListener("click", () => {
        if (!currentBook || currentChapterIndex <= 0) {
            return;
        }
        stopSpeech();
        currentChapterIndex -= 1;
        renderCurrentChapter();
    });

    nextBtn.addEventListener("click", () => {
        if (!currentBook || currentChapterIndex >= currentBook.chapters.length - 1) {
            return;
        }
        stopSpeech();
        currentChapterIndex += 1;
        renderCurrentChapter();
    });

    if (languageSelect) {
        languageSelect.addEventListener("change", () => {
            saveLanguagePreference();
            refreshVoices();
        });
        languageSelect.addEventListener("input", () => {
            saveLanguagePreference();
            refreshVoices();
        });
    }

    voiceSelect.addEventListener("change", saveVoicePreference);
    rateInput.addEventListener("change", saveRatePreference);
    rateInput.addEventListener("input", saveRatePreference);

    window.addEventListener("beforeunload", stopSpeech);
}

function initSpeech() {
    try {
        if ("speechSynthesis" in window) {
            loadLanguagePreference();
            loadRatePreference();
            window.speechSynthesis.onvoiceschanged = refreshVoices;
            refreshVoices();
        }
    } catch (error) {
        console.error("speech init failed:", error);
    }
}

// ── Boot ──────────────────────────────────────────────────────────────────────
async function initApp() {
    bindAuthEvents();
    bindAppEvents();

    if (authToken) {
        showApp();
        initSpeech();
        await refreshLibrary();
    } else {
        showAuth();
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initApp().catch((error) => {
        console.error("app init failed:", error);
    });
});
