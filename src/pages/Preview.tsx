import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { BookOpen, Download } from "lucide-react";
import { apiService, BookResponse, ChapterResponse } from "@/services/api";
import { useBookWebSocket } from "@/hooks/useBookWebSocket";

const Preview = () => {
  const [book, setBook] = useState<BookResponse | null>(null);
  const [chapters, setChapters] = useState<ChapterResponse[]>([]);
  const [bookId, setBookId] = useState<number | null>(null);
  const [exporting, setExporting] = useState(false);
  const [options, setOptions] = useState({
    includeCover: true,
    includeTOC: true,
    includeCitations: true,
    customBranding: false,
  });

  // Initialize WebSocket for updates
  const { chapterProgress } = useBookWebSocket(bookId);

  useEffect(() => {
    const loadBook = async () => {
      const savedBookId = localStorage.getItem("bookId");
      if (!savedBookId) return;

      setBookId(parseInt(savedBookId));

      try {
        const bookData = await apiService.getBook(parseInt(savedBookId));
        setBook(bookData);

        // Fetch all completed chapters
        const allChapters = await apiService.getChapters(parseInt(savedBookId));
        const completedChapters = allChapters.filter((c) => c.status === "complete");

        // Fetch full content for each completed chapter
        const chapterDetails: ChapterResponse[] = [];
        for (const chapter of completedChapters) {
          try {
            const detail = await apiService.getChapter(parseInt(savedBookId), chapter.chapter);
            chapterDetails.push(detail);
          } catch (error) {
            console.error(`Error loading chapter ${chapter.chapter}:`, error);
          }
        }
        setChapters(chapterDetails);
      } catch (error) {
        console.error("Error loading book:", error);
      }
    };

    loadBook();
  }, []);

  useEffect(() => {
    // Refresh when new chapters are completed
    const loadNewChapters = async () => {
      if (!bookId) return;

      const allChapters = await apiService.getChapters(bookId);
      const completedChapters = allChapters.filter((c) => c.status === "complete");

      const chapterDetails: ChapterResponse[] = [];
      for (const chapter of completedChapters) {
        try {
          const detail = await apiService.getChapter(bookId, chapter.chapter);
          chapterDetails.push(detail);
        } catch (error) {
          console.error(`Error loading chapter ${chapter.chapter}:`, error);
        }
      }
      setChapters(chapterDetails);
    };

    loadNewChapters();
  }, [chapterProgress, bookId]);

  if (!book) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <Card className="max-w-md text-center">
          <CardHeader>
            <CardTitle>No Book Found</CardTitle>
            <CardDescription>Please configure and generate a book first</CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto animate-in fade-in duration-500">
      {/* Top Navigation with Export Options */}
      <div className="sticky top-0 z-10 bg-white/80 backdrop-blur border-b border-border mb-6">
        <div className="flex items-center justify-between py-3 gap-4">
          <div>
            <h2 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">Live Preview</h2>
            <p className="text-xs text-muted-foreground">Configure export and download your book</p>
          </div>
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2">
              <Label htmlFor="opt-cover" className="text-xs">Cover</Label>
              <Switch id="opt-cover" checked={options.includeCover} onCheckedChange={(v) => setOptions({ ...options, includeCover: v })} />
            </div>
            <div className="flex items-center gap-2">
              <Label htmlFor="opt-toc" className="text-xs">TOC</Label>
              <Switch id="opt-toc" checked={options.includeTOC} onCheckedChange={(v) => setOptions({ ...options, includeTOC: v })} />
            </div>
            <div className="flex items-center gap-2">
              <Label htmlFor="opt-cite" className="text-xs">Citations</Label>
              <Switch id="opt-cite" checked={options.includeCitations} onCheckedChange={(v) => setOptions({ ...options, includeCitations: v })} />
            </div>
            <div className="flex items-center gap-2">
              <Label htmlFor="opt-brand" className="text-xs">Branding</Label>
              <Switch id="opt-brand" checked={options.customBranding} onCheckedChange={(v) => setOptions({ ...options, customBranding: v })} />
            </div>
            <div className="flex items-center gap-2">
              <Button size="sm" variant="outline" disabled={exporting} onClick={async () => {
                if (!bookId) return;
                setExporting(true);
                try {
                  const blob = await apiService.exportMarkdown(bookId);
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `${book?.title || book?.book_idea || 'book'}.md`;
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                  window.URL.revokeObjectURL(url);
                } finally {
                  setExporting(false);
                }
              }}>
                <Download className="h-4 w-4 mr-2" /> Markdown
              </Button>
              <Button size="sm" className="bg-gradient-primary" disabled={exporting} onClick={async () => {
                if (!bookId) return;
                setExporting(true);
                try {
                  const blob = await apiService.exportHTML(bookId);
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `${book?.title || book?.book_idea || 'book'}.html`;
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                  window.URL.revokeObjectURL(url);
                } finally {
                  setExporting(false);
                }
              }}>
                <Download className="h-4 w-4 mr-2" /> HTML
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-3xl font-bold mb-2 bg-gradient-primary bg-clip-text text-transparent">
          Live Preview
        </h2>
        <p className="text-muted-foreground">
          See your book as it's being generated
        </p>
      </div>

      <Card className="bg-white border-border shadow-card hover:shadow-lg transition-shadow">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-primary" />
            Your E-Book Preview
          </CardTitle>
          <CardDescription>
            This preview updates as chapters are generated
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[calc(100vh-16rem)]">
            <div className="prose max-w-none">
              <div className="text-center mb-12 pb-8 border-b border-border">
                <h1 className="text-4xl font-bold mb-4 bg-gradient-primary bg-clip-text text-transparent">
                  {book.book_idea}
                </h1>
                <p className="text-xl text-muted-foreground">
                  Genre: {book.genre} | {book.chapters_count} Chapters
                </p>
                {book.description && (
                  <p className="text-lg text-muted-foreground mt-4">{book.description}</p>
                )}
              </div>

              {chapters.length === 0 ? (
                <div className="p-6 bg-gray-50 rounded-lg border border-border">
                  <p className="text-sm text-muted-foreground text-center">
                    No chapters generated yet. Use the Generate page to start creating content...
                  </p>
                </div>
              ) : (
                <div className="space-y-8">
                  {chapters.map((chapter, index) => (
                    <div key={chapter.id}>
                      <h2 className="text-2xl font-bold mb-4 text-primary">{chapter.title}</h2>
                      {chapter.content_markdown ? (
                        <div
                          className="text-foreground leading-relaxed"
                          dangerouslySetInnerHTML={{
                            __html: chapter.content_markdown
                              .replace(/\n\n/g, "</p><p>")
                              .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                              .replace(/\*(.*?)\*/g, "<em>$1</em>")
                              .replace(/^### (.*?)$/gm, "<h3>$1</h3>")
                              .replace(/^## (.*?)$/gm, "<h2>$1</h2>")
                          }}
                        />
                      ) : (
                        <p className="text-muted-foreground">Content loading...</p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};

export default Preview;
