import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = 'http://localhost:8000';

export const useChat = () => {
    const [messages, setMessages] = useState([]);
    const [isRecording, setIsRecording] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId] = useState(() => localStorage.getItem('chat_session_id') || crypto.randomUUID());
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    useEffect(() => {
        localStorage.setItem('chat_session_id', sessionId);
    }, [sessionId]);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorderRef.current = new MediaRecorder(stream);
            audioChunksRef.current = [];

            mediaRecorderRef.current.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorderRef.current.onstop = async () => {
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
                await sendAudio(audioBlob);
            };

            mediaRecorderRef.current.start();
            setIsRecording(true);
        } catch (error) {
            console.error("Error accessing microphone:", error);
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            // Stop all tracks to release microphone
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
        }
    };

    const sendAudio = async (audioBlob) => {
        setIsLoading(true);
        const formData = new FormData();
        formData.append('file', audioBlob, 'voice.wav');
        formData.append('session_id', sessionId);

        // Add user "Voice Message" placeholder
        const userMsgId = Date.now();
        setMessages(prev => [...prev, { id: userMsgId, role: 'user', content: '🎤 Voice Message', type: 'audio' }]);

        try {
            const response = await axios.post(`${BACKEND_URL}/chat/audio`, formData, {
                responseType: 'blob'
            });

            // Extract text from header
            const responseText = response.headers['x-chat-response'];

            // Play audio
            const audioUrl = URL.createObjectURL(response.data);
            const audio = new Audio(audioUrl);
            audio.play();

            setMessages(prev => [...prev, {
                id: Date.now(),
                role: 'assistant',
                content: responseText || "Audio Response",
                audioUrl: audioUrl
            }]);

        } catch (error) {
            console.error("Error sending audio:", error);
            setMessages(prev => [...prev, { id: Date.now(), role: 'assistant', content: 'Error processing voice message.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    const sendText = async (text) => {
        if (!text.trim()) return;
        setIsLoading(true);
        setMessages(prev => [...prev, { id: Date.now(), role: 'user', content: text }]);

        try {
            const response = await axios.post(`${BACKEND_URL}/chat/text`, {
                session_id: sessionId,
                message: text
            });
            setMessages(prev => [...prev, { id: Date.now(), role: 'assistant', content: response.data.response }]);
        } catch (error) {
            console.error("Error sending text:", error);
        } finally {
            setIsLoading(false);
        }
    };

    return {
        messages,
        isRecording,
        isLoading,
        startRecording,
        stopRecording,
        sendText
    };
};
