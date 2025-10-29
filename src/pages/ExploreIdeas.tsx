import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, Lightbulb, BookOpen, Sparkles, ArrowRight } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiService } from "@/services/api";

interface BookIdea {
  id: string;
  title: string;
  description: string;
  genre: string;
  targetAudience: string;
  uniqueAngle: string;
  marketPotential: string;
}

const ExploreIdeas = () => {
  const [topics, setTopics] = useState("");
  const [keywords, setKeywords] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedIdeas, setGeneratedIdeas] = useState<BookIdea[]>([]);
  const [selectedIdea, setSelectedIdea] = useState<BookIdea | null>(null);
  const { toast } = useToast();

  const generateIdeas = async () => {
    if (!topics.trim() && !keywords.trim()) {
      toast({
        title: "Input Required",
        description: "Please provide at least topics or keywords to generate book ideas.",
        variant: "destructive",
      });
      return;
    }

    setIsGenerating(true);
    try {
      const response = await apiService.generateIdeas({
        topics: topics.trim(),
        keywords: keywords.trim(),
      });

      if (response.success) {
        setGeneratedIdeas(response.ideas);
        toast({
          title: "Ideas Generated!",
          description: `Successfully generated ${response.ideas.length} book ideas.`,
        });
      } else {
        throw new Error(response.message || "Failed to generate ideas");
      }
    } catch (error) {
      console.error("Error generating ideas:", error);
      toast({
        title: "Generation Failed",
        description: "Failed to generate book ideas. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const selectIdea = (idea: BookIdea) => {
    setSelectedIdea(idea);
    // Store the selected idea in localStorage for the configure page
    localStorage.setItem("selectedBookIdea", JSON.stringify(idea));
    toast({
      title: "Idea Selected!",
      description: "You can now proceed to configure and generate your book.",
    });
  };

  const startBookGeneration = () => {
    if (selectedIdea) {
      // Navigate to configure page with pre-filled data
      window.location.href = "/dashboard/configure";
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-2">
          <Lightbulb className="h-8 w-8 text-yellow-500" />
          <h1 className="text-3xl font-bold bg-gradient-to-r from-yellow-500 to-orange-500 bg-clip-text text-transparent">
            Explore Book Ideas
          </h1>
        </div>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Let our AI ideation agent help you discover compelling book concepts based on your interests, 
          topics, and keywords. Get personalized suggestions tailored to your expertise.
        </p>
      </div>

      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5" />
            Tell Us About Your Interests
          </CardTitle>
          <CardDescription>
            Provide topics, themes, or keywords that interest you. Our AI will generate unique book ideas.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label htmlFor="topics" className="text-sm font-medium mb-2 block">
              Topics & Themes
            </label>
            <Textarea
              id="topics"
              placeholder="e.g., productivity, entrepreneurship, health, technology, personal development..."
              value={topics}
              onChange={(e) => setTopics(e.target.value)}
              className="min-h-[100px]"
            />
          </div>
          
          <div>
            <label htmlFor="keywords" className="text-sm font-medium mb-2 block">
              Keywords & Interests
            </label>
            <Input
              id="keywords"
              placeholder="e.g., AI, mindfulness, business strategy, cooking, fitness..."
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
            />
          </div>

          <Button 
            onClick={generateIdeas} 
            disabled={isGenerating}
            className="w-full"
            size="lg"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating Ideas...
              </>
            ) : (
              <>
                <Lightbulb className="mr-2 h-4 w-4" />
                Generate Book Ideas
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Generated Ideas */}
      {generatedIdeas.length > 0 && (
        <div className="space-y-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-2">Generated Book Ideas</h2>
            <p className="text-muted-foreground">
              Choose an idea that resonates with you to start creating your book.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {generatedIdeas.map((idea, index) => (
              <Card 
                key={idea.id} 
                className={`cursor-pointer transition-all duration-200 hover:shadow-lg ${
                  selectedIdea?.id === idea.id 
                    ? 'ring-2 ring-primary shadow-lg' 
                    : 'hover:shadow-md'
                }`}
                onClick={() => selectIdea(idea)}
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg leading-tight">{idea.title}</CardTitle>
                    <Badge variant="secondary">{idea.genre}</Badge>
                  </div>
                  <CardDescription className="text-sm">
                    Target: {idea.targetAudience}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-muted-foreground line-clamp-3">
                    {idea.description}
                  </p>
                  
                  <div className="space-y-2">
                    <div>
                      <span className="text-xs font-medium text-primary">Unique Angle:</span>
                      <p className="text-xs text-muted-foreground">{idea.uniqueAngle}</p>
                    </div>
                    
                    <div>
                      <span className="text-xs font-medium text-green-600">Market Potential:</span>
                      <p className="text-xs text-muted-foreground">{idea.marketPotential}</p>
                    </div>
                  </div>

                  <Button 
                    variant={selectedIdea?.id === idea.id ? "default" : "outline"}
                    size="sm"
                    className="w-full"
                    onClick={(e) => {
                      e.stopPropagation();
                      selectIdea(idea);
                    }}
                  >
                    {selectedIdea?.id === idea.id ? (
                      <>
                        <BookOpen className="mr-2 h-3 w-3" />
                        Selected
                      </>
                    ) : (
                      <>
                        <ArrowRight className="mr-2 h-3 w-3" />
                        Select This Idea
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Action Button */}
          {selectedIdea && (
            <div className="text-center">
              <Button 
                onClick={startBookGeneration}
                size="lg"
                className="px-8"
              >
                <BookOpen className="mr-2 h-4 w-4" />
                Start Creating "{selectedIdea.title}"
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Tips Section */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-800">💡 Tips for Better Ideas</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-blue-700">
            <li>• Be specific about your areas of expertise or interest</li>
            <li>• Include both broad topics and niche keywords</li>
            <li>• Consider your target audience when describing interests</li>
            <li>• Mix personal experience with market trends for unique angles</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};

export default ExploreIdeas;
