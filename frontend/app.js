// ToxiGuard frontend — talks to /predict, animates the guardian, speaks the verdict.
(() => {
  const chatWindow = document.getElementById("chatWindow");
  const chatForm = document.getElementById("chatForm");
  const chatInput = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");

  const head = document.getElementById("guardianHead");
  const handGood = document.getElementById("handGood");
  const guardianLine = document.getElementById("guardianLine");
  const guardianSub = document.getElementById("guardianSub");
  const meterFill = document.getElementById("meterFill");
  const meterValue = document.getElementById("meterValue");
  const statusDot = document.getElementById("statusDot");
  const statusText = document.getElementById("statusText");
  const voiceToggle = document.getElementById("voiceToggle");

  const mouthAngry = document.getElementById("mouthAngry");
  const mouthSmile = document.getElementById("mouthSmile");
  const mouthWarn = document.getElementById("mouthWarn");
  const fangL = document.getElementById("fangL");
  const fangR = document.getElementById("fangR");
  const browL = document.getElementById("browL");
  const browR = document.getElementById("browR");

  // "No" and short reaction lines per language, spoken by speechSynthesis.
  const VOICE_LINES = {
    en: { no: "No! That is not allowed here.", warn: "Careful with that.", ok: "Good." },
    ta: { no: "இல்லை! இது அனுமதிக்கப்படாது.", warn: "கொஞ்சம் கவனமா பேசு.", ok: "நல்லது." },
    te: { no: "వద్దు! ఇది అనుమతించబడదు.", warn: "కొంచెం జాగ్రత్తగా మాట్లాడు.", ok: "మంచిది." },
    hi: { no: "नहीं! यह यहाँ मंज़ूर नहीं है.", warn: "थोड़ा ध्यान से बोलो.", ok: "बढ़िया." },
  };
  const SPEECH_LANG = { en: "en-IN", ta: "ta-IN", te: "te-IN", hi: "hi-IN" };

  function speak(text, langCode) {
    if (!voiceToggle.checked || !("speechSynthesis" in window) || !text) return;
    try {
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(text);
      utter.lang = SPEECH_LANG[langCode] || "en-IN";
      utter.rate = 0.98;
      utter.pitch = 0.85; // slightly deeper / "evil guardian" tone
      window.speechSynthesis.speak(utter);
    } catch (e) { /* speechSynthesis unsupported: fail silently */ }
  }

  function setMouth(mood) {
    mouthAngry.classList.add("hidden");
    mouthSmile.classList.add("hidden");
    mouthWarn.classList.add("hidden");
    fangL.classList.add("hidden");
    fangR.classList.add("hidden");

    if (mood === "toxic") {
      mouthAngry.classList.remove("hidden");
      fangL.classList.remove("hidden");
      fangR.classList.remove("hidden");
      browL.setAttribute("d", "M60 72 L94 92");
      browR.setAttribute("d", "M160 72 L126 92");
    } else if (mood === "warn") {
      mouthWarn.classList.remove("hidden");
      browL.setAttribute("d", "M62 76 L92 86");
      browR.setAttribute("d", "M158 76 L128 86");
    } else if (mood === "polite") {
      mouthSmile.classList.remove("hidden");
      browL.setAttribute("d", "M64 82 L94 78");
      browR.setAttribute("d", "M156 82 L126 78");
    } else {
      mouthAngry.classList.remove("hidden");
      browL.setAttribute("d", "M62 78 L92 90");
      browR.setAttribute("d", "M158 78 L128 90");
    }
  }

  function animateGuardian(mood) {
    head.classList.remove("shake", "nod", "angry-pulse");
    handGood.classList.add("hidden");
    handGood.classList.remove("thumbs");
    void head.offsetWidth; // restart animation

    setMouth(mood);

    if (mood === "toxic") {
      head.classList.add("shake", "angry-pulse");
      setTimeout(() => head.classList.remove("angry-pulse"), 1800);
    } else if (mood === "warn") {
      head.classList.add("shake");
    } else if (mood === "polite") {
      head.classList.add("nod");
      handGood.classList.remove("hidden");
      void handGood.offsetWidth;
      handGood.classList.add("thumbs");
    }
  }

  function updateMeter(pct) {
    meterFill.style.width = Math.min(100, Math.max(0, pct)) + "%";
    meterValue.textContent = pct.toFixed(0) + "%";
  }

  function updateSidebar(result) {
    if (result.mood === "toxic") {
      guardianLine.textContent = "NO! I caught that.";
      guardianSub.textContent = "That message was blocked.";
    } else if (result.mood === "warn") {
      guardianLine.textContent = "Hmm, watch your tone.";
      guardianSub.textContent = "That one was borderline.";
    } else {
      guardianLine.textContent = "Good human. Carry on.";
      guardianSub.textContent = "Speak normally. I'm watching.";
    }
    updateMeter(result.toxicity_score);
  }

  function addUserBubble(text) {
    const row = document.createElement("div");
    row.className = "msg user-msg";
    row.innerHTML = `<span class="avatar">🙂</span><div class="bubble"><p></p></div>`;
    row.querySelector("p").textContent = text;
    chatWindow.appendChild(row);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function addGuardianBubble(result) {
    const row = document.createElement("div");
    const verdictClass = result.mood === "toxic" ? "verdict-toxic"
                        : result.mood === "warn" ? "verdict-warn" : "verdict-safe";
    row.className = "msg guardian-msg " + verdictClass;

    const tagClass = result.mood === "toxic" ? "tag-toxic"
                    : result.mood === "warn" ? "tag-warn" : "tag-safe";

    let bodyText;
    if (result.mood === "toxic") {
      bodyText = `Message blocked before reaching the chat. (${result.language} detected)`;
    } else if (result.mood === "warn") {
      bodyText = `That's borderline — try rephrasing. (${result.language} detected)`;
    } else {
      bodyText = `Message allowed. Looking good! (${result.language} detected)`;
    }

    row.innerHTML = `
      <span class="avatar">👹</span>
      <div class="bubble">
        <span class="verdict-tag ${tagClass}">${result.level} · ${result.toxicity_score}%</span>
        <p>${bodyText}</p>
      </div>`;
    chatWindow.appendChild(row);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  async function checkHealth() {
    try {
      const res = await fetch("/api/health");
      if (res.ok) {
        statusDot.classList.add("online");
        statusDot.classList.remove("offline");
        statusText.textContent = "ONLINE";
      } else {
        throw new Error("bad status");
      }
    } catch (e) {
      statusDot.classList.add("offline");
      statusDot.classList.remove("online");
      statusText.textContent = "OFFLINE";
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;

    addUserBubble(text);
    chatInput.value = "";
    sendBtn.disabled = true;

    try {
      const res = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!res.ok) throw new Error("request failed");
      const result = await res.json();

      addGuardianBubble(result);
      updateSidebar(result);
      animateGuardian(result.mood);

      const lines = VOICE_LINES[result.lang_code] || VOICE_LINES.en;
      if (result.mood === "toxic") speak(lines.no, result.lang_code);
      else if (result.mood === "warn") speak(lines.warn, result.lang_code);
      // polite messages stay visual-only (thumbs up), matching the brief.

    } catch (err) {
      const row = document.createElement("div");
      row.className = "msg guardian-msg verdict-toxic";
      row.innerHTML = `<span class="avatar">👹</span><div class="bubble"><p>Couldn't reach the server. Is app.py still running?</p></div>`;
      chatWindow.appendChild(row);
    } finally {
      sendBtn.disabled = false;
      chatInput.focus();
    }
  }

  chatForm.addEventListener("submit", handleSubmit);
  checkHealth();
  setInterval(checkHealth, 15000);
})();
