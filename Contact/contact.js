document.getElementById('contactForm').addEventListener('submit', function(e) {
    e.preventDefault();

    // Get form data
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const message = document.getElementById('message').value;

    // Simple form validation (check if fields are empty)
    if (name === "" || email === "" || message === "") {
        document.getElementById('formResponse').textContent = "Please fill out all fields.";
        document.getElementById('formResponse').style.color = "red";
    } else {
        // Mock form submission message
        document.getElementById('formResponse').textContent = `Thank you, ${name}. Your message has been sent!`;
        document.getElementById('formResponse').style.color = "green";

        // Clear form fields after submission
        document.getElementById('contactForm').reset();
    }
});
