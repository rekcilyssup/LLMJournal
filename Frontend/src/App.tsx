import React, { useState, useEffect } from 'react';
import { Toaster, toast } from 'sonner';
import { Trees, Waves, Mountain, Loader2, BookHeart, Sparkles, History, BarChart2 } from 'lucide-react';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Textarea } from './components/ui/textarea';
import { Badge } from './components/ui/badge';
import { api, JournalEntry, AnalysisResult, Insights } from './lib/api';

const USER_ID = "123";

export default function App() {
  // State
  const [ambience, setAmbience] = useState<'forest' | 'ocean' | 'mountain'>('forest');
  const [text, setText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  
  const [history, setHistory] = useState<JournalEntry[]>([]);
  const [insights, setInsights] = useState<Insights | null>(null);
  const [isLoadingData, setIsLoadingData] = useState(true);

  // Fetch initial data
  const fetchData = async () => {
    try {
      setIsLoadingData(true);
      const [historyData, insightsData] = await Promise.all([
        api.getHistory(USER_ID),
        api.getInsights(USER_ID)
      ]);
      setHistory(historyData);
      setInsights(insightsData);
    } catch (error) {
      toast.error("Failed to load dashboard data");
    } finally {
      setIsLoadingData(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAnalyze = async () => {
    if (!text.trim()) {
      toast.error("Please write something to analyze.");
      return;
    }
    try {
      setIsAnalyzing(true);
      const result = await api.analyzeText(text);
      setAnalysisResult(result);
      toast.success("Analysis complete!");
    } catch (error) {
      toast.error("Failed to analyze text.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSave = async () => {
    if (!text.trim()) {
      toast.error("Cannot save an empty journal entry.");
      return;
    }
    try {
      setIsSaving(true);
      await api.saveEntry({
        userId: USER_ID,
        ambience,
        text
      });
      toast.success("Journal entry saved!");
      setText('');
      setAnalysisResult(null);
      fetchData(); // Refresh history and insights
    } catch (error) {
      toast.error("Failed to save entry.");
    } finally {
      setIsSaving(false);
    }
  };

  const getAmbienceIcon = (type: string) => {
    switch (type) {
      case 'forest': return <Trees className="w-5 h-5 text-emerald-600" />;
      case 'ocean': return <Waves className="w-5 h-5 text-blue-600" />;
      case 'mountain': return <Mountain className="w-5 h-5 text-slate-600" />;
      default: return <BookHeart className="w-5 h-5 text-zinc-600" />;
    }
  };

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900 font-sans p-4 md:p-8">
      <Toaster position="top-right" />
      
      <header className="max-w-6xl mx-auto mb-8 flex items-center gap-3">
        <div className="p-2 bg-zinc-900 text-white rounded-xl shadow-sm">
          <BookHeart className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">AI-Assisted Journal</h1>
          <p className="text-sm text-zinc-500">Reflect, analyze, and grow.</p>
        </div>
      </header>

      <main className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* LEFT COLUMN: Input & Analysis */}
        <div className="lg:col-span-7 space-y-6">
          <Card className="border-zinc-200 shadow-sm">
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                New Entry
              </CardTitle>
              <CardDescription>Choose your ambience and write your thoughts.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              
              {/* Ambience Selector */}
              <div className="space-y-3">
                <label className="text-sm font-medium text-zinc-700">Ambience</label>
                <div className="flex gap-3">
                  {(['forest', 'ocean', 'mountain'] as const).map((type) => (
                    <button
                      key={type}
                      onClick={() => setAmbience(type)}
                      className={`flex-1 flex flex-col items-center justify-center gap-2 p-4 rounded-xl border transition-all ${
                        ambience === type 
                          ? 'border-zinc-900 bg-zinc-900/5 ring-1 ring-zinc-900' 
                          : 'border-zinc-200 bg-white hover:bg-zinc-50'
                      }`}
                    >
                      {getAmbienceIcon(type)}
                      <span className="text-xs font-medium capitalize">{type}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Textarea */}
              <div className="space-y-3">
                <label className="text-sm font-medium text-zinc-700">Your Thoughts</label>
                <Textarea 
                  placeholder="What's on your mind today?"
                  className="min-h-[200px] resize-y text-base p-4 leading-relaxed"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                />
              </div>

              {/* Analysis Results Card */}
              {analysisResult && (
                <Card className="bg-indigo-50/50 border-indigo-100 shadow-sm animate-in fade-in slide-in-from-bottom-2 duration-300">
                  <CardHeader className="pb-2 pt-4 px-4">
                    <CardTitle className="text-sm flex items-center gap-2 text-indigo-900">
                      <Sparkles className="w-4 h-4 text-indigo-600" />
                      AI Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3 px-4 pb-4">
                    <div>
                      <p className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider mb-1.5">Detected Emotion</p>
                      <Badge className="bg-indigo-100 text-indigo-800 hover:bg-indigo-200 border-none px-2.5 py-0.5 text-xs">
                        {analysisResult.emotion}
                      </Badge>
                    </div>
                    <div>
                      <p className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider mb-1.5">Key Themes</p>
                      <div className="flex flex-wrap gap-1.5">
                        {analysisResult.keywords.map((kw, i) => (
                          <Badge key={i} variant="secondary" className="bg-white text-indigo-700 border-indigo-100 text-xs">
                            {kw}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider mb-1">Summary</p>
                      <p className="text-sm text-indigo-900 leading-relaxed">{analysisResult.summary}</p>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-3 pt-2">
                <Button 
                  variant="outline" 
                  className="flex-1 gap-2"
                  onClick={handleAnalyze}
                  disabled={isAnalyzing || !text.trim()}
                >
                  {isAnalyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                  Analyze Emotion
                </Button>
                <Button 
                  className="flex-1 gap-2"
                  onClick={handleSave}
                  disabled={isSaving || !text.trim()}
                >
                  {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <BookHeart className="w-4 h-4" />}
                  Save Journal Entry
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* RIGHT COLUMN: Insights & History */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Insights Dashboard */}
          <Card className="border-zinc-200 shadow-sm">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg flex items-center gap-2">
                <BarChart2 className="w-5 h-5 text-zinc-500" />
                Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoadingData ? (
                <div className="grid grid-cols-2 gap-4">
                  {[1, 2, 3, 4].map(i => (
                    <div key={i} className="h-24 bg-zinc-100 rounded-xl animate-pulse" />
                  ))}
                </div>
              ) : insights ? (
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-zinc-50 border border-zinc-100 flex flex-col justify-center">
                    <p className="text-xs text-zinc-500 font-medium mb-1">Total Entries</p>
                    <p className="text-2xl font-bold text-zinc-900">{insights.totalEntries}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-zinc-50 border border-zinc-100 flex flex-col justify-center">
                    <p className="text-xs text-zinc-500 font-medium mb-1">Top Emotion</p>
                    <p className="text-lg font-semibold text-zinc-900 truncate">{insights.topEmotion}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-zinc-50 border border-zinc-100 flex flex-col justify-center">
                    <p className="text-xs text-zinc-500 font-medium mb-1">Top Ambience</p>
                    <div className="flex items-center gap-2">
                      {getAmbienceIcon(insights.mostUsedAmbience)}
                      <p className="text-sm font-semibold text-zinc-900 capitalize">{insights.mostUsedAmbience}</p>
                    </div>
                  </div>
                  <div className="p-4 rounded-xl bg-zinc-50 border border-zinc-100 flex flex-col justify-center">
                    <p className="text-xs text-zinc-500 font-medium mb-2">Recent Topics</p>
                    <div className="flex flex-wrap gap-1">
                      {insights.recentKeywords.slice(0, 3).map((kw, i) => (
                        <span key={i} className="text-[10px] px-1.5 py-0.5 bg-zinc-200 text-zinc-700 rounded-md truncate max-w-full">
                          {kw}
                        </span>
                      ))}
                      {insights.recentKeywords.length === 0 && <span className="text-xs text-zinc-400">None yet</span>}
                    </div>
                  </div>
                </div>
              ) : null}
            </CardContent>
          </Card>

          {/* History Feed */}
          <Card className="border-zinc-200 shadow-sm flex flex-col h-[calc(100vh-24rem)] min-h-[400px]">
            <CardHeader className="pb-4 shrink-0">
              <CardTitle className="text-lg flex items-center gap-2">
                <History className="w-5 h-5 text-zinc-500" />
                Recent History
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto pr-2 space-y-4 custom-scrollbar">
              {isLoadingData ? (
                <div className="space-y-4">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="h-32 bg-zinc-100 rounded-xl animate-pulse" />
                  ))}
                </div>
              ) : history.length > 0 ? (
                history.map((entry) => (
                  <div key={entry.id} className="p-4 rounded-xl border border-zinc-100 bg-white hover:border-zinc-200 transition-colors shadow-sm group">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div className="p-1.5 bg-zinc-50 rounded-lg group-hover:bg-zinc-100 transition-colors">
                          {getAmbienceIcon(entry.ambience)}
                        </div>
                        <span className="text-xs font-medium text-zinc-500">
                          {new Date(entry.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                        </span>
                      </div>
                      {entry.emotion && (
                        <Badge variant="secondary" className="text-[10px] px-2 py-0 h-5">
                          {entry.emotion}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-zinc-700 line-clamp-3 leading-relaxed">
                      {entry.text}
                    </p>
                  </div>
                ))
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-zinc-400 space-y-3">
                  <BookHeart className="w-8 h-8 opacity-20" />
                  <p className="text-sm">No journal entries yet.</p>
                </div>
              )}
            </CardContent>
          </Card>

        </div>
      </main>
    </div>
  );
}
