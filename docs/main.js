const prompt =
  "Install this skill globally: https://github.com/Ezra-Black/EB-Flow";

const copyButtons = document.querySelectorAll("[data-copy]");
const toast = document.querySelector("[data-toast]");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

async function copyInstallPrompt() {
  try {
    await navigator.clipboard.writeText(prompt);
  } catch {
    const range = document.createRange();
    const node = document.getElementById("install-prompt");
    if (!node) return;
    range.selectNodeContents(node);
    const selection = window.getSelection();
    selection?.removeAllRanges();
    selection?.addRange(range);
    document.execCommand("copy");
    selection?.removeAllRanges();
  }

  if (!toast) return;
  toast.hidden = false;
  toast.classList.add("show");
  window.setTimeout(() => {
    toast.classList.remove("show");
  }, 1600);
}

copyButtons.forEach((button) => {
  button.addEventListener("click", copyInstallPrompt);
});

function setupReveals() {
  const nodes = document.querySelectorAll(".reveal");
  if (!nodes.length) return;

  if (reduceMotion || !("IntersectionObserver" in window)) {
    nodes.forEach((node) => node.classList.add("is-in"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-in");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.16, rootMargin: "0px 0px -8% 0px" }
  );

  nodes.forEach((node) => observer.observe(node));
}

function setupWordReveal() {
  const line = document.querySelector("[data-word-reveal]");
  if (!line) return;

  const text = line.textContent.trim().replace(/\s+/g, " ");
  const words = text.split(" ");
  line.textContent = "";

  words.forEach((word, index) => {
    const span = document.createElement("span");
    span.className = "word";
    span.textContent = word;
    line.appendChild(span);
    if (index < words.length - 1) {
      line.appendChild(document.createTextNode(" "));
    }
  });

  const wordNodes = [...line.querySelectorAll(".word")];

  if (reduceMotion || !("IntersectionObserver" in window)) {
    wordNodes.forEach((word) => word.classList.add("is-on"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        wordNodes.forEach((word, index) => {
          window.setTimeout(() => {
            word.classList.add("is-on");
          }, index * 70);
        });
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.45 }
  );

  observer.observe(line);
}

setupReveals();
setupWordReveal();
