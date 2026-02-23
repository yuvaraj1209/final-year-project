import { useEffect, useRef, useState } from 'react';

interface CameraStreamProps {
  onFaceDetection?: (result: any) => void;
  connected?: boolean;
}

const CameraStream = ({ onFaceDetection, connected }: CameraStreamProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [faceDetected, setFaceDetected] = useState(false);

  // Listen for face detection messages from backend
  useEffect(() => {
    const handleCustomMessage = (event: CustomEvent) => {
      const message = event.detail;

      if (message.type === 'face_detection_result') {
        const detected = message.payload?.active || false;
        setFaceDetected(detected);
        onFaceDetection?.(message.payload);
      }
    };

    window.addEventListener(
      'websocket-message',
      handleCustomMessage as EventListener
    );

    return () => {
      window.removeEventListener(
        'websocket-message',
        handleCustomMessage as EventListener
      );
    };
  }, [onFaceDetection]);

  // Start browser camera
  useEffect(() => {
    let stream: MediaStream;

    const startCamera = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false
        });

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.muted = true;
          videoRef.current.playsInline = true;
          await videoRef.current.play();
        }

        console.log("✅ Browser camera started");

      } catch (err) {
        console.error("❌ Camera error:", err);
      }
    };

    startCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className="relative rounded-lg overflow-hidden bg-gray-900 h-48">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full h-48 object-cover"
      />

      <div
        className={`absolute top-2 left-2 px-2 py-1 rounded text-xs font-bold ${
          faceDetected
            ? 'bg-green-500 text-white'
            : 'bg-red-500 text-white'
        }`}
      >
        {faceDetected
          ? '👁️ Face Detected'
          : '🔍 Looking for face...'}
      </div>

      <div
        className={`absolute top-2 right-2 px-2 py-1 rounded text-xs font-bold ${
          connected
            ? 'bg-green-500 text-white'
            : 'bg-gray-500 text-white'
        }`}
      >
        {connected ? '🔴 LIVE (Browser)' : '⭕ Offline'}
      </div>
    </div>
  );
};

export default CameraStream;