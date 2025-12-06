import React, { useRef, useEffect } from 'react';
import { Mic, Send, StopCircle, Bot, User } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import ReactMarkdown from 'react-markdown';

const ChatInterface = () => {
    const { messages, isRecording, isLoading, startRecording, stopRecording, sendText } = useChat();
    const [inputText, setInputText] = React.useState('');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendText = (e) => {
        e.preventDefault();
        sendText(inputText);
        setInputText('');
    };

    return (
        <div className="flex flex-col h-screen bg-gray-900 text-white">
            <header className="bg-gray-800 p-4 shadow-md flex items-center justify-center">
                <Bot className="w-8 h-8 mr-2 text-blue-400" />
                <h1 className="text-xl font-bold">Modern Voice Chatbot</h1>
            </header>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center text-gray-500 mt-20">
                        <p>Start a conversation by typing or recording your voice.</p>
                    </div>
                )}
                {messages.map((msg) => (
                    <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`flex items-start max-w-lg ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                            <div className={`p-2 rounded-full mx-2 ${msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-700'}`}>
                                {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                            </div>
                            <div className={`p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-200'}`}>
                                <ReactMarkdown>{msg.content}</ReactMarkdown>
                                {msg.audioUrl && (
                                    <audio controls src={msg.audioUrl} className="mt-2 w-full h-8" />
                                )}
                            </div>
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start">
                         <div className="flex items-start flex-row">
                            <div className="p-2 rounded-full mx-2 bg-gray-700">
                                <Bot size={20} />
                            </div>
                            <div className="p-3 rounded-lg bg-gray-700 text-gray-200 animate-pulse">
                                Thinking...
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="bg-gray-800 p-4 border-t border-gray-700">
                <form onSubmit={handleSendText} className="flex items-center gap-2 max-w-4xl mx-auto">
                    <button
                        type="button"
                        onClick={isRecording ? stopRecording : startRecording}
                        className={`p-3 rounded-full transition-colors ${
                            isRecording ? 'bg-red-500 hover:bg-red-600 animate-pulse' : 'bg-gray-700 hover:bg-gray-600'
                        }`}
                        title={isRecording ? "Stop Recording" : "Start Recording"}
                    >
                        {isRecording ? <StopCircle /> : <Mic />}
                    </button>

                    <input
                        type="text"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        placeholder="Type a message..."
                        className="flex-1 bg-gray-700 text-white p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />

                    <button
                        type="submit"
                        disabled={!inputText.trim() || isLoading}
                        className="p-3 bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Send />
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChatInterface;
