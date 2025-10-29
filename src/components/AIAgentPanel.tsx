import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, FileText, Lightbulb, Book, CheckCircle2, Search, Pencil } from "lucide-react";

interface AgentStatus {
  agent_name: string;
  status: "idle" | "active" | "error";
  current_task?: string;
}

interface AIAgentPanelProps {
  agentStatuses?: AgentStatus[];
}

const agentIcons: Record<string, any> = {
  "ideation_agent": Lightbulb,
  "research_agent": Search,
  "outline_agent": FileText,
  "writing_agent": Pencil,
  "content_agent": Brain,
  "editor_agent": CheckCircle2,
  "format_agent": Book,
};

const agentNames: Record<string, string> = {
  "ideation_agent": "Ideation Agent",
  "research_agent": "Research Agent",
  "outline_agent": "Outline Agent",
  "writing_agent": "Writing Agent",
  "content_agent": "Content Agent",
  "editor_agent": "Editor Agent",
  "format_agent": "Format Agent",
};

export const AIAgentPanel = ({ agentStatuses = [] }: AIAgentPanelProps) => {
  // Default agents if no statuses provided
  const defaultAgents = [
    { agent_name: "ideation_agent", status: "idle" },
    { agent_name: "research_agent", status: "idle" },
    { agent_name: "outline_agent", status: "idle" },
    { agent_name: "writing_agent", status: "idle" },
    { agent_name: "content_agent", status: "idle" },
    { agent_name: "editor_agent", status: "idle" },
    { agent_name: "format_agent", status: "idle" },
  ];

  const agents = agentStatuses.length > 0 ? agentStatuses : defaultAgents;

  return (
    <div className="p-4 border-t border-border">
      <h3 className="text-sm font-semibold mb-3 text-gray-900">AI Agents</h3>
      <div className="space-y-2">
        {agents.map((agent, index) => {
          const Icon = agentIcons[agent.agent_name] || Brain;
          const isActive = agent.status === "active";
          const agentDisplayName = agentNames[agent.agent_name] || agent.agent_name;
          const colorClass = isActive ? "text-accent" : "text-muted-foreground";
          
          return (
            <Card
              key={index}
              className={`p-3 bg-gray-50 border-border transition-all ${
                isActive ? "animate-pulse-glow" : ""
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Icon className={`h-4 w-4 ${colorClass}`} />
                  <span className="text-xs font-medium text-gray-900">
                    {agentDisplayName}
                  </span>
                </div>
                <Badge
                  variant={isActive ? "default" : "secondary"}
                  className={`text-xs ${isActive ? "bg-success" : ""}`}
                >
                  {agent.status}
                </Badge>
              </div>
              {isActive && agent.current_task && (
                <p className="text-xs text-muted-foreground mt-2">{agent.current_task}</p>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
};
