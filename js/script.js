document.getElementById("year").textContent = new Date().getFullYear();

// Reuses the same EmailJS service/template/public key as the main Nexora AI
// site's contact form. No dedicated template for this project yet — the
// source tag below is how you tell this apart from nexoraai.co.in submissions.
const EMAILJS_SERVICE_ID = "service_x6rmiqm";
const EMAILJS_TEMPLATE_ID = "template_osokenc";
const EMAILJS_PUBLIC_KEY = "oE5oyAtF-MUZRXKxb";

if (window.emailjs) {
  emailjs.init({ publicKey: EMAILJS_PUBLIC_KEY });
}

const contactForm = document.getElementById("contact-form");
const contactStatus = document.getElementById("contact-status");
const contactSubmit = document.getElementById("contact-submit");

if (contactForm) {
  contactForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const data = new FormData(contactForm);
    const topic = data.get("topic") || "Question";
    const fromEmail = (data.get("from_email") || "").trim();
    const message = (data.get("message") || "").trim();

    contactSubmit.disabled = true;
    contactSubmit.textContent = "Sending…";
    contactStatus.textContent = "";
    contactStatus.className = "contact-status";

    emailjs
      .send(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, {
        from_name: `[Group Contacts Exporter] ${topic}`,
        from_email: fromEmail || "not provided",
        message: `Source: Group Contacts Exporter landing page\nTopic: ${topic}\n\n${message}`
      })
      .then(() => {
        contactStatus.textContent = "Sent — thanks, we'll get back to you.";
        contactStatus.className = "contact-status contact-status-success";
        contactForm.reset();
      })
      .catch((error) => {
        console.error("EmailJS send failed:", error);
        contactStatus.textContent = "Something went wrong. Email us directly at saurav.chaudhary70@gmail.com instead.";
        contactStatus.className = "contact-status contact-status-error";
      })
      .finally(() => {
        contactSubmit.disabled = false;
        contactSubmit.textContent = "Send";
      });
  });
}
