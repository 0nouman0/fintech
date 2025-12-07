import React from 'react';
import { ShieldAlert, ShieldCheck, ShieldQuestion, AlertTriangle, FileText } from 'lucide-react';

interface ExtractedDetails {
    interest_rate?: string | null;
    fees?: string | null;
    tenure?: string | null;
    exclusions?: string | null;
    other_key_points?: string[];
}

interface AnalysisResult {
    risk_level: "SAFE" | "SCAM" | "SUSPICIOUS" | "CONFUSING";
    score: number;
    reasons: string[];
    advice: string;
    transcript?: string | null;
    audio_advice_url?: string | null;
    extracted_details: ExtractedDetails;
}

interface RiskCardProps {
    result: AnalysisResult | null;
}

const RiskCard: React.FC<RiskCardProps> = ({ result }) => {
    if (!result) return null;

    const { risk_level, score, reasons, advice, extracted_details, transcript, audio_advice_url } = result;

    let colorClass = "bg-gray-100 border-gray-300 text-gray-800";
    let Icon = ShieldQuestion;

    if (risk_level === "SAFE") {
        colorClass = "bg-green-50 border-green-200 text-green-800";
        Icon = ShieldCheck;
    } else if (risk_level === "SCAM") {
        colorClass = "bg-red-50 border-red-200 text-red-800";
        Icon = ShieldAlert;
    } else if (risk_level === "SUSPICIOUS") {
        colorClass = "bg-orange-50 border-orange-200 text-orange-800";
        Icon = AlertTriangle;
    }

    return (
        <div className={`p-6 rounded-xl border-2 ${colorClass} shadow-sm transition-all duration-300`}>
            <div className="flex items-center gap-4 mb-4">
                <Icon className="w-10 h-10" />
                <div>
                    <h2 className="text-2xl font-bold">{risk_level}</h2>
                    <p className="text-sm opacity-80">Risk Score: {score}/100</p>
                </div>
            </div>

            <div className="mb-4">
                <h3 className="font-semibold mb-2">Why?</h3>
                <ul className="list-disc list-inside space-y-1">
                    {(reasons || []).map((reason, idx) => (
                        <li key={idx}>{reason}</li>
                    ))}
                </ul>
            </div>

            <div className="mb-4 bg-white bg-opacity-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2 flex items-center gap-2">
                    Advice
                    {audio_advice_url && (
                        <span className="text-xs font-normal bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full flex items-center gap-1">
                            Audio Available
                        </span>
                    )}
                </h3>
                <p className="mb-3">{advice}</p>

                {audio_advice_url && (
                    <audio controls className="w-full h-8 mt-2">
                        <source src={`http://localhost:8000${audio_advice_url}`} type="audio/mpeg" />
                        Your browser does not support the audio element.
                    </audio>
                )}
            </div>

            {transcript && (
                <div className="mb-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <h3 className="font-semibold mb-2 flex items-center gap-2">
                        <FileText className="w-4 h-4" /> Call Transcript
                    </h3>
                    <p className="text-sm text-gray-600 italic whitespace-pre-wrap">"{transcript}"</p>
                </div>
            )}

            {extracted_details && (
                <div className="text-sm mt-4 pt-4 border-t border-gray-200 border-opacity-50">
                    <h4 className="font-semibold mb-2">Extracted Details</h4>
                    <div className="grid grid-cols-2 gap-2">
                        {extracted_details.interest_rate && <p>Interest: {extracted_details.interest_rate}</p>}
                        {extracted_details.fees && <p>Fees: {extracted_details.fees}</p>}
                        {extracted_details.tenure && <p>Tenure: {extracted_details.tenure}</p>}
                    </div>
                </div>
            )}
        </div>
    );
};

export default RiskCard;
