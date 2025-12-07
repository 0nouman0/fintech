import { useState } from 'react';
import axios from 'axios';
import { ScanLine, FileText, Loader2, Upload, Mic, Square } from 'lucide-react';
import RiskCard from './components/RiskCard';

function App() {
  const [activeTab, setActiveTab] = useState<'text' | 'image' | 'audio'>('text');
  const [inputText, setInputText] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<any>(null); // Using any for simplicity, or import AnalysisResult
  const [error, setError] = useState<string | null>(null);

  // Audio Recording State
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks: BlobPart[] = [];

      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/mp3' });
        const file = new File([blob], "recording.mp3", { type: "audio/mp3" });
        setSelectedFile(file);
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
      setError(null);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      setError("Could not access microphone. Please check permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    if (activeTab === 'text') {
      formData.append('text', inputText);
      formData.append('type', 'unknown');
    } else {
      if (!selectedFile) {
        setError(activeTab === 'image' ? "Please select an image first." : "Please select an audio file or record something.");
        setLoading(false);
        return;
      }
      formData.append('file', selectedFile);
      formData.append('type', activeTab === 'image' ? 'upi_qr' : 'spam_check');
    }

    try {
      const response = await axios.post('http://localhost:8000/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.error) {
        setError(response.data.error);
        setResult(null);
      } else {
        setResult(response.data);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-extrabold text-blue-900 mb-2">Financial Safety Net</h1>
        <p className="text-gray-600">AI-powered protection against scams and fraud.</p>
      </header>

      <main className="w-full max-w-2xl bg-white rounded-2xl shadow-xl overflow-hidden">
        {/* Tabs */}
        <div className="flex border-b border-gray-100">
          <button
            onClick={() => setActiveTab('text')}
            className={`flex-1 py-4 flex items-center justify-center gap-2 font-medium transition-colors ${activeTab === 'text' ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:bg-gray-50'
              }`}
          >
            <FileText className="w-5 h-5" /> Text Analysis
          </button>
          <button
            onClick={() => setActiveTab('image')}
            className={`flex-1 py-4 flex items-center justify-center gap-2 font-medium transition-colors ${activeTab === 'image' ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:bg-gray-50'
              }`}
          >
            <ScanLine className="w-5 h-5" /> QR / Image Scan
          </button>
          <button
            onClick={() => setActiveTab('audio')}
            className={`flex-1 py-4 flex items-center justify-center gap-2 font-medium transition-colors ${activeTab === 'audio' ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:bg-gray-50'
              }`}
          >
            <Mic className="w-5 h-5" /> Voice Analysis
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {activeTab === 'text' ? (
            <textarea
              className="w-full h-32 p-4 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none"
              placeholder="Paste the suspicious message, loan offer, or policy text here..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
          ) : (
            <div className="flex flex-col gap-4">
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:bg-gray-50 transition-colors relative">
                <input
                  type="file"
                  accept={activeTab === 'image' ? "image/*" : "audio/*"}
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setSelectedFile(e.target.files[0]);
                    }
                  }}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                <div className="flex flex-col items-center pointer-events-none">
                  {activeTab === 'image' ? (
                    <Upload className="w-10 h-10 text-gray-400 mb-2" />
                  ) : (
                    <Mic className="w-10 h-10 text-gray-400 mb-2" />
                  )}
                  <p className="text-gray-500 font-medium">
                    {selectedFile ? selectedFile.name : (activeTab === 'image' ? "Click or Drag to Upload Image" : "Click or Drag to Upload Audio (MP3/WAV)")}
                  </p>
                </div>
              </div>

              {activeTab === 'audio' && (
                <div className="flex flex-col items-center gap-2">
                  <div className="flex items-center gap-2 w-full">
                    <div className="h-px bg-gray-200 flex-1"></div>
                    <span className="text-xs text-gray-400 font-medium uppercase">Or Record</span>
                    <div className="h-px bg-gray-200 flex-1"></div>
                  </div>

                  <button
                    onClick={isRecording ? stopRecording : startRecording}
                    className={`flex items-center gap-2 px-6 py-3 rounded-full font-bold transition-all shadow-sm ${isRecording
                      ? 'bg-red-50 text-red-600 border border-red-200 hover:bg-red-100 animate-pulse'
                      : 'bg-white text-blue-600 border border-blue-200 hover:bg-blue-50'
                      }`}
                  >
                    {isRecording ? (
                      <>
                        <Square className="w-5 h-5 fill-current" /> Stop Recording
                      </>
                    ) : (
                      <>
                        <Mic className="w-5 h-5" /> Start Recording
                      </>
                    )}
                  </button>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="mt-4 p-3 bg-red-50 text-red-600 rounded-lg text-sm">
              {error}
            </div>
          )}

          <button
            onClick={handleAnalyze}
            disabled={loading || (activeTab === 'text' && !inputText) || (activeTab !== 'text' && !selectedFile)}
            className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Analyze Risk"}
          </button>
        </div>

        {/* Results */}
        {result && (
          <div className="p-6 border-t border-gray-100 bg-gray-50">
            <RiskCard result={result} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
