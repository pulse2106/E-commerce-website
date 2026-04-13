function togglePassword() {
    const passwordField = document.getElementById("password");
    const eyeOpen = document.getElementById("eye-open");
    const eyeClosed = document.getElementById("eye-closed");
    
    if (passwordField.type === "password") {
        passwordField.type = "text";
        eyeOpen.style.display = "none";
        eyeClosed.style.display = "block";
    } else {
        passwordField.type = "password";
        eyeOpen.style.display = "block";
        eyeClosed.style.display = "none";
    }
}