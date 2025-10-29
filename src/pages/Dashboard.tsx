import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { BookOpen, Settings, Sparkles, Eye, Lightbulb } from "lucide-react";
import { AIAgentPanel } from "@/components/AIAgentPanel";
import { useBookWebSocket } from "@/hooks/useBookWebSocket";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
  SidebarInset,
} from "@/components/ui/sidebar";

const Dashboard = () => {
  const location = useLocation();
  const navigate = useNavigate();

  // Get book ID from localStorage
  const bookId = localStorage.getItem("bookId");
  
  // Initialize WebSocket for real-time agent updates
  const { agentStatuses, isConnected } = useBookWebSocket(
    bookId ? parseInt(bookId) : null
  );

  const navItems = [
    { id: "explore", label: "Explore Ideas", icon: Lightbulb, path: "/dashboard/explore" },
    { id: "configure", label: "Configure", icon: Settings, path: "/dashboard/configure" },
    { id: "generate", label: "Generate", icon: Sparkles, path: "/dashboard/generate" },
    { id: "preview", label: "Live Preview", icon: Eye, path: "/dashboard/preview" },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <Sidebar collapsible="icon">
          <SidebarHeader className="border-b border-sidebar-border">
            <div className="flex items-center gap-2 px-2 py-4">
              <BookOpen className="h-6 w-6 text-primary" />
              <span className="font-bold text-lg">BookForge AI</span>
            </div>
          </SidebarHeader>

          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupContent>
                <SidebarMenu>
                  {navItems.map((item) => {
                    const Icon = item.icon;
                    const active = isActive(item.path);
                    return (
                      <SidebarMenuItem key={item.id}>
                        <SidebarMenuButton
                          onClick={() => navigate(item.path)}
                          isActive={active}
                          tooltip={item.label}
                          className={active ? "bg-gradient-primary shadow-glow" : ""}
                        >
                          <Icon className="h-4 w-4" />
                          <span>{item.label}</span>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    );
                  })}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>

            <AIAgentPanel agentStatuses={agentStatuses} />
          </SidebarContent>
        </Sidebar>

        <SidebarInset>
          <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-lg border-b border-border shadow-sm">
            <div className="flex items-center justify-between p-4">
              <SidebarTrigger />
              <h1 className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                E-Book Writer Studio
              </h1>
              <div className="w-10" />
            </div>
          </header>

          <main className="p-6">
            <Outlet />
          </main>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
};

export default Dashboard;
