import React, { useState, useEffect } from 'react';
import { Toaster, toast } from 'sonner';
import { Trees, Waves, Mountain, Loader2, BookHeart, Sparkles, History, BarChart2, X, PanelLeft, PanelRight } from 'lucide-react';
import { Button } from './components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Textarea } from './components/ui/textarea';
import { Badge } from './components/ui/badge';
import { api, JournalEntry, AnalysisResult, Insights } from './lib/api';

export default function App() {
  const initialUserName = typeof window !== 'undefined' ? localStorage.getItem('journalUserName') || '' : '';

  // State
  const [userName, setUserName] = useState(initialUserName);
  const [userInput, setUserInput] = useState(initialUserName);
  const [isUserReady, setIsUserReady] = useState(Boolean(initialUserName.trim()));

  const [ambience, setAmbience] = useState<'forest' | 'ocean' | 'mountain'>('forest');
  const [text, setText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  
  const [history, setHistory] = useState<JournalEntry[]>([]);
  const [insights, setInsights] = useState<Insights | null>(null);
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [openedEntry, setOpenedEntry] = useState<JournalEntry | null>(null);

  // Sidebar State
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isInsightsOpen, setIsInsightsOpen] = useState(false);

  const activeUserId = userName.trim();

  // Fetch initial data
  const fetchData = async (currentUserId: string) => {
    try {
      setIsLoadingData(true);
      const [historyData, insightsData] = await Promise.all([
        api.getHistory(currentUserId),
        api.getInsights(currentUserId)
      ]);
      setHistory(historyData);
      setInsights(insightsData);
    } catch (error) {
      toast.error("Failed to load dashboard data");
    } finally {
      setIsLoadingData(false);
    }
  };

  const handleUserSubmit = () => {
    const normalized = userInput.trim();
    if (!normalized) {
      toast.error('Please enter your name to continue.');
      return;
    }
    setUserName(normalized);
    setIsUserReady(true);
    localStorage.setItem('journalUserName', normalized);
    toast.success(`Welcome, ${normalized}!`);
  };

  const handleSwitchUser = () => {
    setIsUserReady(false);
    setUserInput(userName);
    setHistory([]);
    setInsights(null);
    setOpenedEntry(null);
    setAnalysisResult(null);
    setText('');
  };

  useEffect(() => {
    if (!isUserReady || !activeUserId) {
      setHistory([]);
      setInsights(null);
      setIsLoadingData(false);
      return;
    }
    fetchData(activeUserId);
  }, [isUserReady, activeUserId]);

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
    if (!activeUserId) {
      toast.error('Please set your user name first.');
      return;
    }
    if (!text.trim()) {
      toast.error("Cannot save an empty journal entry.");
      return;
    }
    try {
      setIsSaving(true);
      await api.saveEntry({
        userId: activeUserId,
        ambience,
        text
      });
      toast.success("Journal entry saved!");
      setText('');
      setAnalysisResult(null);
      fetchData(activeUserId); // Refresh history and insights
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
    <div className="relative h-screen w-full bg-zinc-50 text-zinc-900 font-sans overflow-hidden flex">
      <Toaster position="top-right" />

      {!isUserReady && (
        <div className="absolute inset-0 z-[60] bg-zinc-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <Card className="w-full max-w-md border-zinc-200 shadow-xl">
            <CardHeader>
              <CardTitle className="text-lg">Start With Your Name</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-zinc-600">Your name is used as your journal user id for history and insights.</p>
              <input
                type="text"
                className="h-10 w-full rounded-md border border-zinc-300 bg-white px-3 text-sm outline-none focus:ring-2 focus:ring-zinc-900"
                placeholder="Enter your name"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleUserSubmit();
                }}
              />
              <Button className="w-full" onClick={handleUserSubmit}>Continue</Button>
            </CardContent>
          </Card>
        </div>
      )}
      
      {/* TOP NAVIGATION / FLOATING BUTTONS */}
      <div className="absolute top-0 left-0 right-0 p-4 flex justify-between items-start z-40 pointer-events-none">
        <Button 
          variant="outline" 
          size="sm"
          className="pointer-events-auto bg-white/80 backdrop-blur-md shadow-sm border-zinc-200 hover:bg-zinc-100 text-zinc-700"
          onClick={() => setIsHistoryOpen(true)}
        >
          <PanelLeft className="w-4 h-4 mr-2" />
          Recent History
        </Button>
        
        <Button 
          variant="outline" 
          size="sm"
          className="pointer-events-auto bg-white/80 backdrop-blur-md shadow-sm border-zinc-200 hover:bg-zinc-100 text-zinc-700"
          onClick={() => setIsInsightsOpen(true)}
        >
          Insights
          <PanelRight className="w-4 h-4 ml-2" />
        </Button>
      </div>

      {/* LEFT SIDEBAR: HISTORY */}
      <div 
        className={`fixed inset-y-0 left-0 w-80 bg-white border-r border-zinc-200 shadow-2xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col ${
          isHistoryOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="p-4 border-b border-zinc-100 flex justify-between items-center bg-zinc-50/50">
          <h2 className="font-semibold flex items-center gap-2 text-zinc-800">
            <History className="w-4 h-4 text-zinc-500" />
            Recent History
          </h2>
          <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-500 hover:text-zinc-900" onClick={() => setIsHistoryOpen(false)}>
            <X className="w-4 h-4" />
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-2 custom-scrollbar">
          {isLoadingData ? (
            <div className="space-y-2">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-24 bg-zinc-100 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : history.length > 0 ? (
            history.map((entry) => (
              <button
                key={entry.id}
                type="button"
                onClick={() => setOpenedEntry(entry)}
                className="w-full text-left p-3 rounded-xl border border-zinc-100 bg-zinc-50/50 hover:bg-zinc-50 transition-colors group"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="p-1 bg-white rounded-md shadow-sm">
                      {getAmbienceIcon(entry.ambience)}
                    </div>
                    <span className="text-[11px] font-medium text-zinc-500">
                      {new Date(entry.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                  {entry.emotion && (
                    <Badge variant="secondary" className="text-[9px] px-1.5 py-0 h-4 bg-white border-zinc-200">
                      {entry.emotion}
                    </Badge>
                  )}
                </div>
                <p className="text-xs text-zinc-600 line-clamp-3 leading-relaxed">
                  {entry.text}
                </p>
              </button>
            ))
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-zinc-400 space-y-2">
              <BookHeart className="w-6 h-6 opacity-20" />
              <p className="text-xs">No entries yet.</p>
            </div>
          )}
        </div>
      </div>

      {/* RIGHT SIDEBAR: INSIGHTS */}
      <div 
        className={`fixed inset-y-0 right-0 w-80 bg-white border-l border-zinc-200 shadow-2xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col ${
          isInsightsOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="p-4 border-b border-zinc-100 flex justify-between items-center bg-zinc-50/50">
          <h2 className="font-semibold flex items-center gap-2 text-zinc-800">
            <BarChart2 className="w-4 h-4 text-zinc-500" />
            Insights
          </h2>
          <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-500 hover:text-zinc-900" onClick={() => setIsInsightsOpen(false)}>
            <X className="w-4 h-4" />
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          {isLoadingData ? (
            <div className="grid grid-cols-2 gap-3">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-20 bg-zinc-100 rounded-xl animate-pulse" />
              ))}
            </div>
          ) : insights ? (
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-xl bg-zinc-50 border border-zinc-100 flex flex-col justify-center">
                <p className="text-[10px] text-zinc-500 font-medium mb-1 uppercase tracking-wider">Total Entries</p>
                <p className="text-xl font-bold text-zinc-900">{insights.totalEntries}</p>
              </div>
              <div className="p-3 rounded-xl bg-zinc-50 border border-zinc-100 flex flex-col justify-center">
                <p className="text-[10px] text-zinc-500 font-medium mb-1 uppercase tracking-wider">Top Emotion</p>
                <p className="text-sm font-semibold text-zinc-900 truncate">{insights.topEmotion}</p>
              </div>
              <div className="p-3 rounded-xl bg-zinc-50 border border-zinc-100 flex flex-col justify-center col-span-2">
                <p className="text-[10px] text-zinc-500 font-medium mb-1 uppercase tracking-wider">Top Ambience</p>
                <div className="flex items-center gap-2">
                  {getAmbienceIcon(insights.mostUsedAmbience)}
                  <p className="text-sm font-semibold text-zinc-900 capitalize">{insights.mostUsedAmbience}</p>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-zinc-50 border border-zinc-100 flex flex-col justify-center col-span-2">
                <p className="text-[10px] text-zinc-500 font-medium mb-2 uppercase tracking-wider">Recent Topics</p>
                <div className="flex flex-wrap gap-1.5">
                  {insights.recentKeywords.slice(0, 5).map((kw, i) => (
                    <span key={i} className="text-[10px] px-2 py-0.5 bg-white border border-zinc-200 text-zinc-700 rounded-md">
                      {kw}
                    </span>
                  ))}
                  {insights.recentKeywords.length === 0 && <span className="text-xs text-zinc-400">None yet</span>}
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </div>

      {/* BACKDROP FOR MOBILE */}
      {(isHistoryOpen || isInsightsOpen) && (
        <div 
          className="fixed inset-0 bg-zinc-900/20 backdrop-blur-sm z-40 md:hidden transition-opacity"
          onClick={() => { setIsHistoryOpen(false); setIsInsightsOpen(false); }}
        />
      )}

      {openedEntry && (
        <div className="fixed inset-0 z-[70] bg-zinc-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <Card className="w-full max-w-2xl max-h-[85vh] overflow-hidden border-zinc-200 shadow-2xl">
            <CardHeader className="pb-3 border-b border-zinc-100 flex flex-row items-center justify-between">
              <div className="space-y-1">
                <CardTitle className="text-base flex items-center gap-2">
                  {getAmbienceIcon(openedEntry.ambience)}
                  Previous Entry
                </CardTitle>
                <p className="text-xs text-zinc-500">
                  {new Date(openedEntry.date).toLocaleString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </div>
              <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setOpenedEntry(null)}>
                <X className="w-4 h-4" />
              </Button>
            </CardHeader>
            <CardContent className="p-5 space-y-4 overflow-y-auto max-h-[calc(85vh-5.5rem)]">
              <div className="flex flex-wrap gap-2 items-center">
                <Badge variant="secondary" className="bg-zinc-100 text-zinc-700 border-zinc-200">
                  {openedEntry.ambience}
                </Badge>
                {openedEntry.emotion && (
                  <Badge variant="secondary" className="bg-indigo-100 text-indigo-800 border-indigo-200">
                    {openedEntry.emotion}
                  </Badge>
                )}
              </div>

              <div className="rounded-lg border border-zinc-200 bg-zinc-50 p-4">
                <p className="text-sm text-zinc-700 leading-relaxed whitespace-pre-wrap">
                  {openedEntry.text}
                </p>
              </div>

              {openedEntry.summary && (
                <div className="space-y-1">
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500">Summary</p>
                  <p className="text-sm text-zinc-700 leading-relaxed">{openedEntry.summary}</p>
                </div>
              )}

              {openedEntry.keywords && openedEntry.keywords.length > 0 && (
                <div className="space-y-1">
                  <p className="text-[11px] font-semibold uppercase tracking-wider text-zinc-500">Keywords</p>
                  <div className="flex flex-wrap gap-1.5">
                    {openedEntry.keywords.map((kw, i) => (
                      <Badge key={i} variant="secondary" className="bg-white border-zinc-200 text-zinc-700">
                        {kw}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* MAIN CENTER AREA */}
      <main className="flex-1 h-full flex flex-col items-center justify-center p-4 sm:p-8 overflow-y-auto">
        <div className="w-full max-w-2xl flex flex-col items-center space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
          
          {/* Header / Logo */}
          <div className="text-center space-y-3">
            <div className="inline-flex p-3 bg-zinc-900 text-white rounded-2xl shadow-lg shadow-zinc-900/20">
              <BookHeart className="w-8 h-8" />
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-zinc-900">AI-Assisted Journal</h1>
            <p className="text-zinc-500 text-sm">Reflect on your day. Let AI uncover your patterns.</p>
            {isUserReady && (
              <div className="flex items-center justify-center gap-2 pt-1">
                <span className="text-xs text-zinc-500">User: <strong className="text-zinc-800">{userName}</strong></span>
                <Button variant="outline" size="sm" onClick={handleSwitchUser}>Switch</Button>
              </div>
            )}
          </div>

          {/* New Entry Bounding Box */}
          <Card className="w-full border-zinc-200 shadow-xl shadow-zinc-200/50 bg-white/80 backdrop-blur-xl">
            <CardHeader className="pb-4 border-b border-zinc-100/50">
              <CardTitle className="text-sm font-medium text-zinc-500 uppercase tracking-wider text-center">
                New Entry
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              
              {/* Ambience Selector */}
              <div className="space-y-3">
                <div className="flex justify-center gap-3">
                  {(['forest', 'ocean', 'mountain'] as const).map((type) => (
                    <button
                      key={type}
                      onClick={() => setAmbience(type)}
                      className={`flex items-center gap-2 px-4 py-2 rounded-full border text-sm transition-all ${
                        ambience === type 
                          ? 'border-zinc-900 bg-zinc-900 text-white shadow-md' 
                          : 'border-zinc-200 bg-white text-zinc-600 hover:bg-zinc-50'
                      }`}
                    >
                      {getAmbienceIcon(type)}
                      <span className="font-medium capitalize">{type}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Textarea */}
              <div className="space-y-3">
                <Textarea 
                  placeholder="What's on your mind today?"
                  className="min-h-[180px] resize-y text-base p-4 leading-relaxed border-zinc-200 shadow-inner bg-zinc-50/50 focus:bg-white transition-colors"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                />
              </div>

              {/* Analysis Results Card */}
              {analysisResult && (
                <Card className="bg-indigo-50/80 border-indigo-100 shadow-sm animate-in fade-in zoom-in-95 duration-300">
                  <CardHeader className="pb-2 pt-4 px-4">
                    <CardTitle className="text-sm flex items-center gap-2 text-indigo-900">
                      <Sparkles className="w-4 h-4 text-indigo-600" />
                      AI Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3 px-4 pb-4">
                    <div className="flex items-center gap-4">
                      <div>
                        <p className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider mb-1.5">Emotion</p>
                        <Badge className="bg-indigo-100 text-indigo-800 hover:bg-indigo-200 border-none px-2.5 py-0.5 text-xs">
                          {analysisResult.emotion}
                        </Badge>
                      </div>
                      <div className="flex-1">
                        <p className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider mb-1.5">Themes</p>
                        <div className="flex flex-wrap gap-1.5">
                          {analysisResult.keywords.map((kw, i) => (
                            <Badge key={i} variant="secondary" className="bg-white text-indigo-700 border-indigo-100 text-xs">
                              {kw}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="pt-2 border-t border-indigo-100/50">
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
                  className="flex-1 gap-2 h-11 text-zinc-700"
                  onClick={handleAnalyze}
                  disabled={isAnalyzing || !text.trim()}
                >
                  {isAnalyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4 text-indigo-500" />}
                  Analyze Emotion
                </Button>
                <Button 
                  className="flex-1 gap-2 h-11 bg-zinc-900 hover:bg-zinc-800 text-white shadow-md"
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
      </main>
    </div>
  );
}
