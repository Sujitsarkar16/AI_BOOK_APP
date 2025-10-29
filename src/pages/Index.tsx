import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import { BookOpen, Sparkles, Zap, Brain, Lightbulb } from "lucide-react";

const Index = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-hero relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/10 rounded-full blur-3xl animate-float" style={{ animationDelay: "1s" }} />
      </div>

      <div className="container mx-auto px-4 py-20 relative z-10">
        {/* Hero Section */}
        <div className="text-center mb-16 animate-in fade-in slide-in-from-bottom duration-700">
          <div className="flex items-center justify-center gap-3 mb-6">
            <BookOpen className="h-12 w-12 text-primary" />
            <h1 className="text-6xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              BookForge AI
            </h1>
          </div>
          <p className="text-2xl text-gray-700 mb-4 max-w-3xl mx-auto">
            Transform Your Ideas into Complete E-Books
          </p>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-8">
            Powered by 7 specialized AI agents working together to write, edit, and format your book from start to finish
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              onClick={() => navigate("/dashboard/explore")}
              className="bg-gradient-to-r from-yellow-500 to-orange-500 hover:opacity-90 shadow-glow text-lg px-8 py-6 h-auto"
            >
              <Lightbulb className="mr-2 h-5 w-5" />
              Explore Book Ideas
            </Button>
            <Button
              size="lg"
              onClick={() => navigate("/dashboard/configure")}
              className="bg-gradient-primary hover:opacity-90 shadow-glow text-lg px-8 py-6 h-auto"
            >
              <Sparkles className="mr-2 h-5 w-5" />
              Start Writing
            </Button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto mt-20">
          <div className="p-6 rounded-xl bg-white border border-border hover:border-primary transition-all shadow-card hover:shadow-lg">
            <div className="h-12 w-12 rounded-lg bg-gradient-primary flex items-center justify-center mb-4">
              <Brain className="h-6 w-6 text-primary-foreground" />
            </div>
            <h3 className="text-xl font-bold mb-2 text-gray-900">AI-Powered Writing</h3>
            <p className="text-gray-600">
              7 specialized AI agents collaborate to research, write, and polish your content
            </p>
          </div>

          <div className="p-6 rounded-xl bg-white border border-border hover:border-primary transition-all shadow-card hover:shadow-lg">
            <div className="h-12 w-12 rounded-lg bg-gradient-secondary flex items-center justify-center mb-4">
              <Zap className="h-6 w-6 text-secondary-foreground" />
            </div>
            <h3 className="text-xl font-bold mb-2 text-gray-900">Fast & Efficient</h3>
            <p className="text-gray-600">
              Generate complete chapters in minutes with our optimized AI pipeline
            </p>
          </div>

          <div className="p-6 rounded-xl bg-white border border-border hover:border-primary transition-all shadow-card hover:shadow-lg">
            <div className="h-12 w-12 rounded-lg bg-gradient-accent flex items-center justify-center mb-4">
              <BookOpen className="h-6 w-6 text-accent-foreground" />
            </div>
            <h3 className="text-xl font-bold mb-2 text-gray-900">Publication Ready</h3>
            <p className="text-gray-600">
              Professional formatting and structure ready for immediate publishing
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
