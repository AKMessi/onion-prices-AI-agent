// Wait for the DOM to be fully loaded before running script
document.addEventListener("DOMContentLoaded", () => {
    
    const micButton = document.getElementById('micButton');
    const status = document.getElementById('status');
    let isRecording = false;

    // Check for browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const synthesis = window.speechSynthesis;

    if (!SpeechRecognition || !synthesis) {
        status.textContent = "क्षमस्व, आपला ब्राउझर व्हॉइस रेकॉर्डिंगला सपोर्ट करत नाही.";
        micButton.disabled = true;
        micButton.classList.add('opacity-50', 'cursor-not-allowed');
        return; // Stop the script if not supported
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'mr-IN'; // Marathi (India)
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    micButton.addEventListener('click', () => {
        if (isRecording) {
            recognition.stop();
        } else {
            try {
                recognition.start();
            } catch (error) {
                console.error("Error starting recognition:", error);
                status.textContent = "सुरुवात करताना त्रुटी आली.";
            }
        }
    });

    recognition.onstart = () => {
        isRecording = true;
        status.textContent = "ऐकत आहे... बोला...";
        micButton.classList.add('is-recording', 'bg-red-600');
        micButton.classList.remove('bg-blue-600');
    };

    recognition.onend = () => {
        isRecording = false;
        // Don't change status on 'onend' because 'onresult' happens first.
        // Let 'onresult' or 'onerror' handle the status text.
        micButton.classList.remove('is-recording', 'bg-red-600');
        micButton.classList.add('bg-blue-600');
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        if (event.error === 'not-allowed') {
            status.textContent = "मायक्रोफोनची परवानगी नाकारली.";
        } else if (event.error === 'language-not-supported') {
            status.textContent = "मराठी भाषा सपोर्टेड नाही.";
        } else if (event.error === 'no-speech') {
             status.textContent = "मला काही ऐकू आले नाही.";
        } else {
            status.textContent = `एक त्रुटी आली: ${event.error}`;
        }
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript.toLowerCase();
        status.textContent = `तुम्ही म्हणालात: "${transcript}"`;
        processCommand(transcript);
    };

    function processCommand(transcript) {
        if (transcript.includes("कांदा") || transcript.includes("kanda")) {
            getPrices('kanda');
        } else if (transcript.includes("वाटाणा") || transcript.includes("vatana")) {
            getPrices('vatana');
        } else {
            speak("क्षमस्व, मला समजले नाही. कृपया 'कांदा भाव' किंवा 'वाटाणा भाव' विचारा.");
        }
    }

    function getPrices(commodity) {
        // --- THIS IS THE MOCK DATA ---
        const mockData = {
            kanda: [
                { place: "संगमनेर", min: 2200, max: 2800 },
                { place: "नाशिक", min: 2400, max: 3000 },
                { place: "सिन्नर", min: 2300, max: 2950 }
            ],
            vatana: [
                { place: "संगमनेर", min: 4500, max: 5100 },
                { place: "नाशिक", min: 4800, max: 5300 },
                { place: "पुणे", min: 4700, max: 5200 }
            ]
        };
        // --- END OF MOCK DATA ---

        const prices = mockData[commodity];
        const date = new Date().toLocaleDateString('mr-IN', { day: 'numeric', month: 'long', year: 'numeric' });
        
        let responseText = `नमस्कार. आज ${date} आहे. `;
        
        if (commodity === 'kanda') {
            responseText += "आजचे कांद्याचे बाजार भाव (प्रति क्विंटल) असे आहेत: ";
        } else {
            responseText += "आजचे वाटाण्याचे बाजार भाव (प्रति क्विंटल) असे आहेत: ";
        }

        prices.forEach(item => {
            responseText += `${item.place}, कमीत कमी ${item.min} रुपये, जास्तीत जास्त ${item.max} रुपये. `;
        });

        speak(responseText);
    }

    // --- REVISED VOICE LOADING AND SPEAK FUNCTION ---
    let marathiVoice = null;

    function loadVoices() {
        const voices = synthesis.getVoices();
        marathiVoice = voices.find(voice => voice.lang === 'mr-IN');
        
        if (marathiVoice) {
            console.log('Marathi voice found:', marathiVoice.name);
        } else {
            console.log('Marathi (mr-IN) voice not found.');
        }
    }

    function speak(text) {
        if (synthesis.speaking) {
            synthesis.cancel();
        }
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        if (marathiVoice) {
            utterance.voice = marathiVoice;
        }
        
        utterance.lang = 'mr-IN'; 
        utterance.pitch = 1;
        utterance.rate = 0.9;
        utterance.volume = 1;
        
        utterance.onend = () => {
            status.textContent = "पुन्हा विचारण्यासाठी बटण दाबा.";
        };

        synthesis.speak(utterance);
    }

    // Load voices initially and set up the listener
    loadVoices();
    if (synthesis.onvoiceschanged !== undefined) {
        synthesis.onvoiceschanged = loadVoices;
    }

}); // End of DOMContentLoaded