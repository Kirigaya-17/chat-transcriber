import React, { useState, useRef } from "react";
import axios from "axios";

const AudioRecorder: React.FC = () => {
  const [recording, setRecording] = useState(false);
  const [audioURL, setAudioURL] = useState<string | null>(null);
  const [transcript, setTranscript] = useState("");
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const options = { mimeType: "audio/webm;codecs=opus" };

      mediaRecorderRef.current = new MediaRecorder(stream, options);
      audioChunks.current = [];

      mediaRecorderRef.current.ondataavailable = (e: BlobEvent) => {
        if (e.data.size > 0) audioChunks.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        // Concatena os pedaços em um único blob
        const blob = new Blob(audioChunks.current, { type: "audio/webm" });

        // Converte para WAV usando um Worker ou ffmpeg.wasm seria o ideal,
        // mas o backend já faz a conversão — então só enviamos o arquivo original.
        const file = new File([blob], "audio.webm", { type: "audio/webm" });
        setAudioURL(URL.createObjectURL(blob));

        const formData = new FormData();
        formData.append("file", file);
        formData.append("format_text", "true");

        try {
          const res = await axios.post(
            "http://localhost:8000/transcribe/",
            formData,
            {
              headers: { "Content-Type": "multipart/form-data" },
            }
          );

          if (res.data.error) {
            setTranscript(`❌ Erro: ${res.data.error}`);
          } else {
            setTranscript(res.data.formatted_text || res.data.raw_text);
          }
        } catch (error) {
          console.error("Erro ao enviar o áudio:", error);
          setTranscript("Erro ao processar o áudio.");
        }
      };

      mediaRecorderRef.current.start();
      setRecording(true);
    } catch (err) {
      console.error("Erro ao acessar o microfone:", err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recording) {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };


  return (
    <div style={{ padding: "1rem", fontFamily: "sans-serif" }}>

      <button onClick={recording ? stopRecording : startRecording}>
        {recording ? "⏹️ Parar Gravação" : "▶️ Iniciar Gravação"}
      </button>

      {audioURL && (
        <div style={{ marginTop: "1rem" }}>
          <audio controls src={audioURL}></audio>
        </div>
      )}

      {transcript && (
        <div style={{ marginTop: "1rem" }}>
          <h3>📝 Transcrição formatada:</h3>
          <p>{transcript}</p>
        </div>
      )}
    </div>

  );
};

export default AudioRecorder;
