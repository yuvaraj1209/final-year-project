import { useEffect, useState } from 'react';

interface CameraStreamProps {
  onFaceDetection?: (result: any) => void;
  connected?: boolean;
}

const CameraStream = ({ onFaceDetection, connected }: CameraStreamProps) => {
  const [faceDetected, setFaceDetected] = useState(false);

  // 🔴 IMPORTANT: Your ngrok HTTPS URL
  const PI_STREAM_URL =
    "https://louvenia-cetological-doreatha.ngrok-free.dev/video_feed";

  // Listen for face detection messages from backend
  useEffect(() => {
    const handleCustomMessage = (event: CustomEvent) => {
      const message = event.detail;

      if (message.type === "face_detection_result") {
        const detected = message.payload?.active || false;
        setFaceDetected(detected);
        onFaceDetection?.(message.payload);
      }
    };

    window.addEventListener(
      "websocket-message",
      handleCustomMessage as EventListener
    );

    return () => {
      window.removeEventListener(
        "websocket-message",
        handleCustomMessage as EventListener
      );
    };
  }, [onFaceDetection]);

  return (
    <div className="camera-stream relative">
      <div className="relative rounded-lg overflow-hidden bg-gray-900 h-48">

        {/* 🔴 Raspberry Pi USB Camera Stream */}
        {connected ? (
          <img
            src={PI_STREAM_URL}
            className="w-full h-48 object-cover"
            alt="Raspberry Pi USB Camera"
          />
        ) : (
          <div className="flex items-center justify-center h-full text-white">
            🔴 Backend Disconnected
          </div>
        )}

        {/* 👁 Face Detection Indicator */}
        <div
          className={`absolute top-2 left-2 px-2 py-1 rounded text-xs font-bold ${
            faceDetected
              ? "bg-green-500 text-white"
              : "bg-red-500 text-white"
          }`}
        >
          {faceDetected
            ? "👁️ Face Detected"
            : "🔍 Looking for face..."}
        </div>

        {/* 🔗 Connection Indicator */}
        <div
          className={`absolute top-2 right-2 px-2 py-1 rounded text-xs font-bold ${
            connected
              ? "bg-green-500 text-white"
              : "bg-gray-500 text-white"
          }`}
        >
          {connected ? "🔴 LIVE (Pi USB)" : "⭕ Offline"}
        </div>

      </div>

      <div className="mt-2 text-center">
        <p className="text-sm text-gray-600">
          📡 Raspberry Pi USB Camera (via ngrok)
        </p>
      </div>
    </div>
  );
};

export default CameraStream;