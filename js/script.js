document.getElementById("year").textContent = new Date().getFullYear();

const contactForm = document.getElementById("contact-form");
if (contactForm) {
  contactForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const data = new FormData(contactForm);
    const topic = data.get("topic") || "Question";
    const fromEmail = (data.get("from_email") || "").trim();
    const message = (data.get("message") || "").trim();

    const subject = `Group Contacts Exporter — ${topic}`;
    const bodyLines = [message, "", fromEmail ? `Reply to: ${fromEmail}` : ""].filter(Boolean);
    const body = bodyLines.join("\n");

    const mailto = `mailto:saurav.chaudhary70@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    window.location.href = mailto;
  });
}
