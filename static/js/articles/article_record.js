let mediaRecorder;
let audioChunks = [];
let recognition;

const startButton = document.getElementById('start-btn');
const stopButton = document.getElementById('stop-btn');
const submitButton = document.getElementById('submit-btn');
const audioFileInput = document.getElementById('audio-file');
const audioForm = document.getElementById('audio-form');
const audioPreview = document.getElementById('audio-preview');
const audioMessage = document.getElementById('audio-message');
const speechTranscript = document.getElementById('speech-transcript');
const loadingOverlay = document.getElementById('loading-overlay');

startButton.onclick = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  
  mediaRecorder.ondataavailable = event => {
    audioChunks.push(event.data);
  };
  
  mediaRecorder.onstop = () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    const audioUrl = URL.createObjectURL(audioBlob);

    // Hide the message and display the audio preview
    audioMessage.style.display = 'none';
    audioPreview.style.display = 'block';
    audioPreview.src = audioUrl;
    
    // Create a file object from the audio blob
    const file = new File([audioBlob], 'recording.wav', { type: 'audio/wav' });
    audioFileInput.files = new DataTransfer().files;  // Clear previous files
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    audioFileInput.files = dataTransfer.files;

    submitButton.disabled = false;
  };
  
  mediaRecorder.start();
  startButton.disabled = true;
  stopButton.disabled = false;
  
  // Initialize speech recognition
  if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;  // Keep recognizing speech until stop
    recognition.interimResults = true; // Show partial results
    recognition.lang = 'en-US'; // Language setting
    
    recognition.onresult = event => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      // Update the transcript as the user speaks
      speechTranscript.textContent = transcript;
    };

    recognition.start();
  }
};

stopButton.onclick = () => {
  mediaRecorder.stop();
  recognition.stop();  // Stop speech recognition
  startButton.disabled = false;
  stopButton.disabled = true;
};

submitButton.onclick = () => {
  // Show loading overlay
  loadingOverlay.style.display = 'flex';
  // Disable all buttons
  document.querySelectorAll('.control-btn').forEach(btn => btn.disabled = true);
  // Submit form after slight delay to ensure UI updates
  setTimeout(() => {
      audioForm.submit();
  }, 100);
};