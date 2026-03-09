const uploadForm = document.getElementById("upload-form");
const uploadStatus = document.getElementById("upload-status");
const libraryEl = document.getElementById("library");
const readerEl = document.getElementById("reader");
const bookTitleEl = document.getElementById("book-title");
const playBtn = document.getElementById("play-btn");
const pauseBtn = document.getElementById("pause-btn");
const stopBtn = document.getElementById("stop-btn");
const prevBtn = document.getElementById("prev-btn");
const nextBtn = document.getElementById("next-btn");
const languageSelect = document.getElementById("language-select");
const voiceSelect = document.getElementById("voice-select");
const rateInput = document.getElementById("rate-input");

const LANGUAGE_STORAGE_KEY = "lectorium.language";
const VOICE_STORAGE_KEY = "lectorium.voice";
const RATE_STORAGE_KEY = "lectorium.rate";

let currentBook = null;
let currentChapterIndex = 0;
let currentUtterance = null;
let currentSpeechQueue = [];
let currentSpeechIndex = 0;

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

async function refreshLibrary() {
    const response = await fetch("/api/books", {
        headers: {
            Accept: "application/json",
        },
    });

    console.log("refreshLibrary status:", response.status);

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
        cover.src = book.cover_url || "";

        const meta = document.createElement("div");
        meta.className = "book-meta";

        const title = document.createElement("strong");
        title.textContent = book.title || "Untitled";

        const author = document.createElement("span");
        author.className = "muted";
        author.textContent = book.author || "Unknown author";

        meta.appendChild(title);
        meta.appendChild(author);

        item.appendChild(cover);
        item.appendChild(meta);

        item.addEventListener("click", () => openBook(book.id));
        libraryEl.appendChild(item);
    }
}

async function openBook(bookId) {
    stopSpeech();

    const response = await fetch(`/api/books/${bookId}`, {
        headers: {
            Accept: "application/json",
        },
    });

    console.log("openBook status:", response.status);

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
    const chapterTitle = chapter.title || `Chapter ${currentChapterIndex + 1}`;
    bookTitleEl.textContent = `${currentBook.title} — ${chapterTitle}`;
    readerEl.innerHTML =
        chapter.html_content || "<p class='muted'>No chapter content available.</p>";
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

function splitTextIntoChunks(text, maxLength = 1200) {
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

function playCurrentChapter() {
    if (!("speechSynthesis" in window)) {
        uploadStatus.textContent = "Browser speech synthesis is not available.";
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

    const voices = window.speechSynthesis.getVoices();
    const selectedVoiceName = voiceSelect.value;
    const selectedVoice = voices.find((voice) => voice.name === selectedVoiceName);

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
    console.log("upload submit intercepted");

    const formData = new FormData(uploadForm);
    uploadStatus.textContent = "Uploading...";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            headers: {
                "X-Requested-With": "fetch",
                Accept: "application/json",
            },
            body: formData,
        });

        console.log("upload response status:", response.status);

        const contentType = response.headers.get("content-type") || "";
        const raw = await response.text();
        console.log("upload raw response:", raw);

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

function bindEvents() {
    uploadForm.addEventListener("submit", handleUploadSubmit);

    playBtn.addEventListener("click", playCurrentChapter);

    pauseBtn.addEventListener("click", () => {
        if ("speechSynthesis" in window) {
            window.speechSynthesis.pause();
        }
    });

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

async function initApp() {
    bindEvents();
    initSpeech();
    await refreshLibrary();
}

document.addEventListener("DOMContentLoaded", () => {
    initApp().catch((error) => {
        console.error("app init failed:", error);
    });
});
