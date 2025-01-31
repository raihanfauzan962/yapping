function playTTS(word) {
    const audio = new Audio(`/articles/text-to-speech/?word=${encodeURIComponent(word)}`);
    audio.play().catch(error => {
        console.error("Error playing audio:", error);
        alert("Unable to play the sound. Please check your browser settings.");
    });
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('span[style="color: green;"]').forEach(function (span) {
        span.style.cursor = "pointer";
        span.addEventListener('click', function () {
            const word = this.textContent.trim();
            playTTS(word);
        });
    });
});