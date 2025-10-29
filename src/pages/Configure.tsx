import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { apiService } from "@/services/api";

const Configure = () => {
  const navigate = useNavigate();
  const [config, setConfig] = useState({
    bookIdea: "",
    description: "",
    targetAudience: "",
    genre: "",
    chapters: 10,
    wordsPerChapter: 2500,
    tone: "professional",
    includeImages: false,
    includeCitations: true,
  });

  // Load pre-filled data from selected book idea
  useEffect(() => {
    const selectedIdea = localStorage.getItem("selectedBookIdea");
    if (selectedIdea) {
      try {
        const idea = JSON.parse(selectedIdea);
        setConfig(prev => ({
          ...prev,
          bookIdea: idea.title || "",
          description: idea.description || "",
          targetAudience: idea.targetAudience || "",
          genre: idea.genre.toLowerCase() || "",
        }));
        
        // Clear the selected idea from localStorage after using it
        localStorage.removeItem("selectedBookIdea");
        
        toast.success("Book idea loaded! You can modify the details below.");
      } catch (error) {
        console.error("Error parsing selected book idea:", error);
      }
    }
  }, []);

  const handleSubmit = async () => {
    if (!config.bookIdea || !config.genre) {
      toast.error("Please fill in the required fields");
      return;
    }
    
    try {
      toast.loading("🤖 AI Ideation Agent is analyzing your book idea and drafting the outline...", {
        duration: Infinity,
        id: 'creating-book'
      });
      
      // Call API to create book - This triggers ideation agent analysis
      const bookId = await apiService.createBook(config);
      
      // Store book ID in localStorage
      localStorage.setItem("bookId", bookId.toString());
      
      toast.dismiss('creating-book');
      toast.success("✨ Book concept analyzed! Introduction and outline ready. Moving to generation...");
      navigate("/dashboard/generate");
    } catch (error) {
      console.error("Error creating book:", error);
      toast.dismiss('creating-book');
      toast.error("Failed to create book. Please try again.");
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-500">
      <div>
        <h2 className="text-3xl font-bold mb-2 bg-gradient-primary bg-clip-text text-transparent">
          Configure Your Book
        </h2>
        <p className="text-muted-foreground">
          Set up the structure and requirements for your e-book
        </p>
      </div>

      <Card className="bg-white border-border shadow-card hover:shadow-lg transition-shadow">
        <CardHeader>
          <CardTitle>Book Concept</CardTitle>
          <CardDescription>What's your book about?</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="bookIdea">Book Idea *</Label>
            <Input
              id="bookIdea"
              placeholder="e.g., A comprehensive guide to sustainable living"
              value={config.bookIdea}
              onChange={(e) => setConfig({ ...config, bookIdea: e.target.value })}
              className="bg-white border-border"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Detailed Description</Label>
            <Textarea
              id="description"
              placeholder="Provide more details about your book concept, key themes, and what makes it unique..."
              value={config.description}
              onChange={(e) => setConfig({ ...config, description: e.target.value })}
              className="bg-input border-border min-h-[120px]"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="genre">Genre *</Label>
              <Select value={config.genre} onValueChange={(value) => setConfig({ ...config, genre: value })}>
                <SelectTrigger className="bg-input border-border">
                  <SelectValue placeholder="Select a genre" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="non-fiction">Non-Fiction</SelectItem>
                  <SelectItem value="fiction">Fiction</SelectItem>
                  <SelectItem value="self-help">Self-Help</SelectItem>
                  <SelectItem value="business">Business</SelectItem>
                  <SelectItem value="technical">Technical</SelectItem>
                  <SelectItem value="educational">Educational</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="targetAudience">Target Audience</Label>
              <Input
                id="targetAudience"
                placeholder="e.g., Young professionals, Students"
                value={config.targetAudience}
                onChange={(e) => setConfig({ ...config, targetAudience: e.target.value })}
                className="bg-white border-border"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-white border-border shadow-card hover:shadow-lg transition-shadow">
        <CardHeader>
          <CardTitle>Structure & Format</CardTitle>
          <CardDescription>Define how your book will be organized</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Number of Chapters: {config.chapters}</Label>
              <Slider
                value={[config.chapters]}
                onValueChange={([value]) => setConfig({ ...config, chapters: value })}
                min={5}
                max={30}
                step={1}
                className="w-full"
              />
            </div>

            <div className="space-y-2">
              <Label>Words per Chapter: {config.wordsPerChapter.toLocaleString()}</Label>
              <Slider
                value={[config.wordsPerChapter]}
                onValueChange={([value]) => setConfig({ ...config, wordsPerChapter: value })}
                min={1000}
                max={5000}
                step={500}
                className="w-full"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="tone">Writing Tone</Label>
            <Select value={config.tone} onValueChange={(value) => setConfig({ ...config, tone: value })}>
              <SelectTrigger className="bg-input border-border">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="professional">Professional</SelectItem>
                <SelectItem value="casual">Casual</SelectItem>
                <SelectItem value="academic">Academic</SelectItem>
                <SelectItem value="conversational">Conversational</SelectItem>
                <SelectItem value="inspirational">Inspirational</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="includeImages">Include Images</Label>
                <p className="text-sm text-muted-foreground">Add AI-generated illustrations</p>
              </div>
              <Switch
                id="includeImages"
                checked={config.includeImages}
                onCheckedChange={(checked) => setConfig({ ...config, includeImages: checked })}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="includeCitations">Include Citations</Label>
                <p className="text-sm text-muted-foreground">Add references and sources</p>
              </div>
              <Switch
                id="includeCitations"
                checked={config.includeCitations}
                onCheckedChange={(checked) => setConfig({ ...config, includeCitations: checked })}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end gap-4">
        <Button variant="outline" onClick={() => navigate("/")}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          className="bg-gradient-primary hover:opacity-90 shadow-glow"
        >
          Continue to Generate
        </Button>
      </div>
    </div>
  );
};

export default Configure;
