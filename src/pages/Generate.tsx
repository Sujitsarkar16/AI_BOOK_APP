import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, BookMarked, CheckCircle2, Circle, Eye } from "lucide-react";
import { toast } from "sonner";
import { apiService, TOCItem, BookResponse, ChapterResponse } from "@/services/api";
import { useBookWebSocket } from "@/hooks/useBookWebSocket";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface TOCItem {
  chapter: number;
  title: string;
  status: "pending" | "generating" | "complete";
  outline?: string;
}

const Generate = () => {
  const [bookId, setBookId] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [toc, setToc] = useState<TOCItem[]>([]);
  const [bookDetails, setBookDetails] = useState<BookResponse | null>(null);
  const [selectedChapter, setSelectedChapter] = useState<ChapterResponse | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  
  // Export options
  const [exportOptions, setExportOptions] = useState({
    includeCover: true,
    includeTOC: true,
    includeCitations: true,
    customBranding: false,
  });

  // Get book ID from localStorage
  const currentBookId = localStorage.getItem("bookId");
  
  // Initialize WebSocket
  const { agentStatuses, chapterProgress, isConnected } = useBookWebSocket(
    currentBookId ? parseInt(currentBookId) : null
  );

  useEffect(() => {
    const loadBook = async () => {
      const savedBookId = localStorage.getItem("bookId");
      if (!savedBookId) {
        toast.error("No book found. Please configure a book first.");
        return;
      }
      
      setBookId(parseInt(savedBookId));
      
      try {
        // Fetch tips details and chapters
        const [bookData, chapters] = await Promise.all([
          apiService.getBook(parseInt(savedBookId)),
          apiService.getChapters(parseInt(savedBookId))
        ]);
        
        setBookDetails(bookData);
        setToc(chapters);
        
        setMessages([
          {
            role: "assistant",
            content: `I've loaded your book "${bookData.book_idea}". The AI has analyzed your concept and generated ${chapters.length} chapters with detailed outlines. You can now start generating content or make adjustments.`,
          },
        ]);
      } catch (error) {
        console.error("Error loading book:", error);
        toast.error("Failed to load book.");
      }
    };
    
    loadBook();
  }, []);

  const handleSendMessage = async () => {
    if (!message.trim() || !bookId) return;

    setMessages([...messages, { role: "user", content: message }]);
    const userMessage = message;
    setMessage("");

    try {
      const response = await apiService.sendChatMessage(bookId, userMessage);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.response,
        },
      ]);
    } catch (error) {
      console.error("Error sending message:", error);
      toast.error("Failed to send message. Please try again.");
    }
  };

  const handleGenerateChapter = async (chapterIndex: number) => {
    if (!bookId) return;
    
    const updatedToc = [...toc];
    updatedToc[chapterIndex].status = "generating";
    setToc(updatedToc);

    toast.info(`Generating Chapter ${chapterIndex + 1}...`);

    try {
      // Find chapter ID
      const chapter = toc[chapterIndex];
      await apiService.generateChapter(bookId, chapter.chapter);
      
      // Status will be updated via WebSocket
    } catch (error) {
      console.error("Error generating chapter:", error);
      toast.error("Failed to generate chapter. Please try again.");
      updatedToc[chapterIndex].status = "pending";
      setToc(updatedToc);
    }
  };

  const handleSelectChapter = async (chapterIndex: number) => {
    if (!bookId) return;
    
    const chapter = toc[chapterIndex];
    if (chapter.status === "complete") {
      try {
        const chapterData = await apiService.getChapter(bookId, chapter.chapter);
        setSelectedChapter(chapterData);
        setShowPreview(true);
        toast.success("Chapter loaded for editing!");
      } catch (error) {
        console.error("Error loading chapter:", error);
        toast.error("Failed to load chapter.");
      }
    }
  };

  const handleExport = async () => {
    if (!bookId) return;
    
    toast.info("Preparing export...");
    
    try {
      // You can implement export logic here based on options
      const blob = await apiService.exportMarkdown(bookId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${bookDetails?.title || 'book'}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      toast.success("Book exported successfully!");
    } catch (error) {
      console.error("Error exporting:", error);
      toast.error("Failed to export book.");
    }
  };

  const handleGenerateAll = async () => {
    if (!bookId) return;
    
    toast.info("Generating all chapters...");
    
    try {
      await apiService.generateAllChapters(bookId);
      toast.success("Started generating all chapters!");
    } catch (error) {
      console.error("Error generating all chapters:", error);
      toast.error("Failed to start generation. Please try again.");
    }
  };

  // Update TOC when WebSocket receives updates
  useEffect(() => {
    chapterProgress.forEach((progress, chapterId) => {
      const chapterIndex = toc.findIndex((c) => c.chapter === progress.chapter_id);
      if (chapterIndex >= 0) {
        const updatedToc = [...toc];
        updatedToc[chapterIndex].status = progress.status;
        setToc(updatedToc);
        
        if (progress.status === "complete") {
          toast.success(`Chapter ${progress.chapter_id} complete!`);
        }
      }
    });
  }, [chapterProgress, toc]);

  if (!bookId) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Card className="max-w-md text-center">
          <CardHeader>
            <CardTitle>No Configuration Found</CardTitle>
            <CardDescription>Please configure your book first</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => (window.location.href = "/dashboard/configure")}>
            Go to Configure
          </Button>
        </CardContent>
      </Card>
    </div>
  );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-8rem)]">
      {/* TOC Panel */}
      <Card className="bg-white border-border shadow-card hover:shadow-lg transition-shadow lg:col-span-1">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookMarked className="h-5 w-5 text-primary" />
            Table of Contents
          </CardTitle>
          <CardDescription>Your book blueprint</CardDescription>
          <div className="mt-2">
            <Button
              size="sm"
              onClick={handleGenerateAll}
              className="w-full bg-gradient-primary hover:opacity-90"
            >
              Generate All Chapters
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[calc(100vh-16rem)]">
            <div className="space-y-2">
              {toc.map((item, index) => (
                <div
                  key={index}
                  className="p-3 rounded-lg bg-gray-50 border border-border hover:border-primary transition-colors"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        {item.status === "complete" ? (
                          <CheckCircle2 className="h-4 w-4 text-success" />
                        ) : item.status === "generating" ? (
                          <div className="h-4 w-4 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                        ) : (
                          <Circle className="h-4 w-4 text-muted-foreground" />
                        )}
                        <span className="text-xs font-semibold text-foreground">
                          Chapter {item.chapter}
                        </span>
                      </div>
                      <p className="text-sm font-medium text-gray-900 mb-1">{item.title}</p>
                      {item.outline && (
                        <p className="text-xs text-gray-600 line-clamp-2">{item.outline}</p>
                      )}
                    </div>
                    <div className="flex gap-1">
                      {item.status === "pending" && (
                        <Button
                          size="sm"
                          onClick={() => handleGenerateChapter(index)}
                          className="bg-gradient-primary hover:opacity-90"
                        >
                          Generate
                        </Button>
                      )}
                      {item.status === "complete" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleSelectChapter(index)}
                          className="flex items-center gap-1"
                        >
                          <Eye className="h-3 w-3" />
                          View
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Export moved to Preview page top nav */}

      {/* Chat Panel with Preview */}
      <Card className="bg-white border-border shadow-card hover:shadow-lg transition-shadow lg:col-span-2 flex flex-col">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Generation Playground</CardTitle>
              <CardDescription>
                Request improvements, changes, or generate specific sections
              </CardDescription>
            </div>
            {selectedChapter && (
              <Button
                variant="outline"
                onClick={() => setShowPreview(!showPreview)}
              >
                <Eye className="h-4 w-4 mr-2" />
                {showPreview ? 'Hide' : 'Show'} Preview
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col">
          {showPreview && selectedChapter ? (
            <div className="grid grid-cols-2 gap-4 h-full">
              {/* Chat Section */}
              <div className="flex flex-col">
                <ScrollArea className="flex-1 pr-4 mb-4">
                  <div className="space-y-4">
                    {messages.map((msg, index) => (
                      <div
                        key={index}
                        className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                      >
                        <div
                          className={`max-w-[90%] p-4 rounded-lg ${
                            msg.role === "user"
                              ? "bg-gradient-primary text-primary-foreground"
                              : "bg-gray-100 text-gray-900"
                          }`}
                        >
                          <p className="text-sm">{msg.content}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
                <div className="flex gap-2">
                  <Input
                    placeholder="Type your request or improvement..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                    className="bg-white border-border"
                  />
                  <Button
                    onClick={handleSendMessage}
                    className="bg-gradient-primary hover:opacity-90"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Preview Section */}
              <div className="border-l border-border pl-4">
                <ScrollArea className="h-[calc(100vh-20rem)]">
                  <div className="prose max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {selectedChapter.content_markdown || "No content yet"}
                    </ReactMarkdown>
                  </div>
                </ScrollArea>
              </div>
            </div>
          ) : (
            <>
              <ScrollArea className="flex-1 pr-4 mb-4">
                <div className="space-y-4">
                  {messages.map((msg, index) => (
                    <div
                      key={index}
                      className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[80%] p-4 rounded-lg ${
                          msg.role === "user"
                            ? "bg-gradient-primary text-primary-foreground"
                            : "bg-gray-100 text-gray-900"
                        }`}
                      >
                        <p className="text-sm">{msg.content}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>

              <div className="flex gap-2">
                <Input
                  placeholder="Type your request or improvement..."
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                  className="bg-white border-border"
                />
                <Button
                  onClick={handleSendMessage}
                  className="bg-gradient-primary hover:opacity-90"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Generate;
