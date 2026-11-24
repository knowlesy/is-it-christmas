(() => {
  const TIMEZONE = "Europe/London";
  const DEFAULT_FEED_URL = "https://knowlesy.github.io/is-it-christmas/feed.xml";

  function getLondonDateParts(now) {
    const formatter = new Intl.DateTimeFormat("en-CA", {
      timeZone: TIMEZONE,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    });
    const parts = formatter.formatToParts(now);
    const map = {};
    for (const part of parts) {
      if (part.type !== "literal") {
        map[part.type] = Number(part.value);
      }
    }
    return { year: map.year, month: map.month, day: map.day };
  }

  function parseOverrideDate() {
    const params = new URLSearchParams(window.location.search);
    const raw = params.get("date");
    if (!raw || !/^\d{4}-\d{2}-\d{2}$/.test(raw)) {
      return null;
    }
    const [year, month, day] = raw.split("-").map(Number);
    const probe = new Date(Date.UTC(year, month - 1, day));
    if (
      probe.getUTCFullYear() !== year ||
      probe.getUTCMonth() + 1 !== month ||
      probe.getUTCDate() !== day
    ) {
      return null;
    }
    return { year, month, day, isPreview: true };
  }

  function daysBetween(from, to) {
    const start = Date.UTC(from.year, from.month - 1, from.day);
    const end = Date.UTC(to.year, to.month - 1, to.day);
    return Math.round((end - start) / 86400000);
  }

  function resolveFeedUrl() {
    if (window.location.protocol === "http:" || window.location.protocol === "https:") {
      return new URL("feed.xml", window.location.href).href;
    }
    return DEFAULT_FEED_URL;
  }

  function render() {
    const override = parseOverrideDate();
    const current = override || { ...getLondonDateParts(new Date()), isPreview: false };
    const isChristmas = current.month === 12 && current.day === 25;

    const answerEl = document.getElementById("answer");
    const subtextEl = document.getElementById("subtext");
    const statusEl = document.getElementById("feed-status");
    const slackCmdEl = document.getElementById("slack-command");
    const copyBtn = document.getElementById("copy-slack-btn");

    const answer = isChristmas ? "YES" : "NO";
    answerEl.textContent = answer;
    document.title = `Is it Christmas? ${answer}`;
    document.body.classList.toggle("is-christmas", isChristmas);

    const formattedDate = new Intl.DateTimeFormat("en-GB", {
      day: "numeric",
      month: "long",
      year: "numeric",
      timeZone: "UTC",
    }).format(new Date(Date.UTC(current.year, current.month - 1, current.day)));

    if (isChristmas) {
      subtextEl.textContent = `Merry Christmas! (${formattedDate})`;
    } else if (current.month === 12 && current.day < 25) {
      const left = 25 - current.day;
      subtextEl.textContent = `${formattedDate} — ${left} ${left === 1 ? "day" : "days"} to go.`;
    } else {
      subtextEl.textContent = current.isPreview ? `Previewing ${formattedDate}` : "";
    }

    if (current.month === 12 && current.day >= 1 && current.day <= 25) {
      statusEl.textContent = "RSS feed active · Daily 09:00 UK time (1–25 Dec)";
    } else if (current.month === 12 && current.day > 25) {
      statusEl.textContent = "RSS feed paused after 25 Dec · Resumes 1 Dec next year";
    } else {
      const daysUntilDec1 = daysBetween(current, { year: current.year, month: 12, day: 1 });
      statusEl.textContent = `RSS feed starts 1 Dec (${daysUntilDec1} ${daysUntilDec1 === 1 ? "day" : "days"} away) · 09:00 UK time`;
    }

    const feedUrl = resolveFeedUrl();
    const slackCommand = `/feed subscribe ${feedUrl}`;
    slackCmdEl.textContent = slackCommand;

    copyBtn.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(slackCommand);
        copyBtn.textContent = "Copied!";
        window.setTimeout(() => {
          copyBtn.textContent = "Copy Slack /feed command";
        }, 1800);
      } catch {
        window.prompt("Copy this Slack command:", slackCommand);
      }
    });
  }

  render();
})();
