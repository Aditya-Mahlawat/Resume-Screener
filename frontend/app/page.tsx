'use client'; // <-- This line is required for App Router

import { useState, ChangeEvent, FormEvent } from 'react';
import axios from 'axios';

// --- Types ---
// These types match the response structure from our FastAPI backend
interface SkillCoverage {
  matched_skills: string[];
  missing_skills: string[];
  coverage_percentage: number;
}

interface RankResult {
  filename: string;
  resume_skills: string[];
  experience_years: number;
  jd_skills: string[];
  semantic_similarity: number;
  skill_coverage: SkillCoverage;
  final_score: number;
  explanation: string;
}

// --- Helper Components ---
// A simple component to display a list of skills
const SkillTag = ({ skill }: { skill: string }) => (
  <span className="inline-block bg-blue-100 text-blue-800 text-xs font-medium mr-2 mb-2 px-2.5 py-0.5 rounded-full">
    {skill}
  </span>
);

// A component to display the final score as a "progress" circle
const ScoreCircle = ({ score }: { score: number }) => {
  const percentage = Math.round(score * 100);
  let colorClass = 'text-gray-400';
  if (percentage >= 80) colorClass = 'text-green-500';
  else if (percentage >= 60) colorClass = 'text-yellow-500';
  else if (percentage > 0) colorClass = 'text-orange-500';
  else colorClass = 'text-red-500';

  return (
    <div className={`relative w-32 h-32 ${colorClass}`}>
      <svg className="w-full h-full" viewBox="0 0 36 36">
        <path
          d="M18 2.0845
             a 15.9155 15.9155 0 0 1 0 31.831
             a 15.9155 15.9155 0 0 1 0 -31.831"
          className="text-gray-200"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        />
        <path
          d="M18 2.0845
             a 15.9155 15.9155 0 0 1 0 31.831
             a 15.9155 15.9155 0 0 1 0 -31.831"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeDasharray={`${percentage}, 100`}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-3xl font-bold">
        {percentage}
        <span className="text-base font-medium">%</span>
      </div>
    </div>
  );
};

// --- Main Page Component ---
export default function HomePage() {
  // --- State Variables ---
  const [jobDescription, setJobDescription] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [result, setResult] = useState<RankResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // --- Handlers ---
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setResumeFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!jobDescription || !resumeFile) {
      setError('Please provide both a job description and a resume file.');
      return;
    }

    // Reset state
    setIsLoading(true);
    setError(null);
    setResult(null);

    // Use FormData to send both text and file
    const formData = new FormData();
    formData.append('job_description', jobDescription);
    formData.append('resume_file', resumeFile);

    try {
      // Make the API call to our FastAPI backend
      const response = await axios.post<RankResult>(
        'http://127.0.0.1:8000/rank',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      setResult(response.data);
    } catch (err: any) {
      // Handle errors
      if (err.response) {
        // Error from the API
        setError(`Error: ${err.response.data.detail || err.message}`);
      } else {
        // Network error or other issues
        setError(`An error occurred: ${err.message}. Is the backend server running?`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // --- Render ---
  return (
    <div className="flex flex-col min-h-screen bg-gray-50 font-sans">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Automated Resume Screener
          </h1>
        </div>
      </header>

      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* --- Column 1: Input Form --- */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Input Details</h2>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Job Description */}
              <div>
                <label
                  htmlFor="jobDescription"
                  className="block text-sm font-medium text-blue-600"
                >
                  Job Description
                </label>
                <textarea
                  id="jobDescription"
                  rows={10}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 text-blue-700"
                  placeholder="Paste the job description here..."
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                />
              </div>

              {/* Resume File */}
              <div>
                <label
                  htmlFor="resumeFile"
                  className="block text-sm font-medium text-blue-600"
                >
                  Candidate Resume (.pdf, .docx)
                </label>
                <input
                  type="file"
                  id="resumeFile"
                  accept=".pdf,.docx"
                  onChange={handleFileChange}
                  className="mt-1 block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-md file:border-0
                    file:text-sm file:font-semibold
                    file:bg-blue-50 file:text-blue-700
                    hover:file:bg-blue-100"
                />
              </div>

              {/* Submit Button */}
              <div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
                >
                  {isLoading ? 'Ranking Candidate...' : 'Rank Candidate'}
                </button>
              </div>
            </form>
          </div>

          {/* --- Column 2: Results --- */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-900">Ranking Result</h2>
            <div className="flex flex-col items-center justify-center min-h-[300px]">
              {/* Loading State */}
              {isLoading && (
                <div className="flex flex-col items-center text-gray-500">
                  <svg className="animate-spin h-8 w-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="mt-2">Analyzing...</span>
                </div>
              )}

              {/* Error State */}
              {error && (
                <div className="text-center text-red-600 bg-red-50 p-4 rounded-md">
                  <h3 className="font-semibold">Analysis Failed</h3>
                  <p className="text-sm">{error}</p>
                </div>
              )}

              {/* Result State */}
              {result && (
                <div className="w-full animate-fade-in">
                  <div className="flex flex-col items-center mb-6">
                    <ScoreCircle score={result.final_score} />
                    <p className="mt-4 text-sm text-gray-600 text-center max-w-xs">{result.explanation}</p>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold text-gray-700">Skill Match ({result.skill_coverage.matched_skills.length}/{result.jd_skills.length})</h4>
                      <p className="text-sm text-gray-500">Skills from the JD found in the resume:</p>
                      <div className="mt-2">
                        {result.skill_coverage.matched_skills.length > 0 ? (
                          result.skill_coverage.matched_skills.map(skill => <SkillTag key={skill} skill={skill} />)
                        ) : (
                          <p className="text-sm text-gray-400 italic">No required skills matched.</p>
                        )}
                      </div>
                    </div>
                    
                    {result.skill_coverage.missing_skills.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-gray-700">Missing Skills</h4>
                        <div className="mt-2">
                          {result.skill_coverage.missing_skills.map(skill => (
                            <span key={skill} className="inline-block bg-red-100 text-red-800 text-xs font-medium mr-2 mb-2 px-2.5 py-0.5 rounded-full">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div>
                      <h4 className="font-semibold text-gray-700">Resume Details</h4>
                      <ul className="text-sm text-gray-600 mt-2 space-y-1">
                        <li><strong>File:</strong> {result.filename}</li>
                        <li><strong>Experience Found:</strong> {result.experience_years} years</li>
                        <li><strong>Semantic Similarity:</strong> {(result.semantic_similarity * 100).toFixed(1)}%</li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Initial State */}
              {!isLoading && !error && !result && (
                <p className="text-gray-500">Results will appear here once you rank a candidate.</p>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}