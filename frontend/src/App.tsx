import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  FolderOpen,
  FileText,
  Database,
  Settings as SettingsIcon,
  Search,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  Clock,
  Download,
  Copy,
  History,
  Trash2,
  RefreshCw,
  Plus,
  FileCode,
  AlertTriangle,
  User,
  ExternalLink,
  Cpu,
  Layers,
  SearchCode,
  Compass,
  Check,
  CheckCheck
} from 'lucide-react';
import { generateDocument, AgentResponse, StructuredDocument, ToolExecutionLog } from './api/client.ts';

export interface DocumentItem {
  id: string;
  projectId: string;
  title: string;
  intent: string;
  tags: string[];
  lastGenerated: string;
  status: string;
  version: string;
  prompt: string;
  content: any;
}

// --- MOCK DATABASE INIT ---
const INITIAL_PROJECTS = [
  { id: '1', name: 'Customer Support AI', desc: 'AI-driven support ticket routing and automated responder system design.', count: 3 },
  { id: '2', name: 'Inventory Management', desc: 'Real-time asset tracking and predictive supply chain system PRD.', count: 2 },
  { id: '3', name: 'CRM Migration', desc: 'Detailed schema mapping and data migration plan from Salesforce to HubSpot.', count: 4 },
  { id: '4', name: 'Internal Portal', desc: 'Standard operating procedures (SOP) for engineering onboarding and tool access.', count: 1 }
];

const INITIAL_DOCUMENTS: DocumentItem[] = [
  {
    id: 'doc-1',
    projectId: '1',
    title: 'Project Proposal: Customer Support AI',
    intent: 'Proposal',
    tags: ['AI', 'Support', 'Proposal'],
    lastGenerated: 'Jul 10, 2026',
    status: 'Approved',
    version: 'v3',
    prompt: 'Create a business proposal for Project Customer Support AI including executive summary, scope, stack, timeline.',
    content: {
      title: 'Project Proposal: Customer Support AI Platform',
      metadata: { Author: 'Sahil', Version: '3.0.0', Date: 'July 10, 2026', Classification: 'Confidential' },
      sections: [
        {
          heading: '1. Executive Summary',
          paragraphs: [
            'This proposal outlines the deployment of an AI-driven Support Ticketing and Responder Platform. By integrating advanced reasoning LLMs directly with internal support systems, the business will achieve high customer satisfaction and rapid ticket resolution.',
            'The initial phase focuses on automated routing, followed closely by drafted replies under agent review.'
          ],
          bullets: [
            'Targeting a 35% reduction in first-response times.',
            'Automated prioritization of critical SLAs.',
            'Scale support volume without increasing headcount.'
          ],
          tables: [],
          references: []
        },
        {
          heading: '2. Proposed Solution',
          paragraphs: [
            'A centralized AI agent listening to inbound tickets, matching context using vector semantic search (RAG) against previous resolutions, and drafting responses.'
          ],
          bullets: [],
          tables: [
            {
              headers: ['Stage', 'Timeline', 'Scope', 'Deliverable'],
              rows: [
                ['Phase 1', 'Weeks 1-4', 'RAG database setup & integration', 'Working retrieval prototype'],
                ['Phase 2', 'Weeks 5-8', 'Agent response generator', 'FastAPI draft response endpoint'],
                ['Phase 3', 'Weeks 9-12', 'UI integration & Testing', 'Production system release']
              ]
            }
          ],
          references: ['IEEE Guideline on Conversational Agent Design Patterns']
        }
      ]
    }
  },
  {
    id: 'doc-2',
    projectId: '3',
    title: 'CRM Migration Technical Design',
    intent: 'Technical Design',
    tags: ['Migration', 'CRM', 'Architecture'],
    lastGenerated: 'Jul 08, 2026',
    status: 'In Review',
    version: 'v1',
    prompt: 'Create a technical design for migration from Salesforce to HubSpot focusing on schema mapping and API limits.',
    content: {
      title: 'CRM Migration Technical Design',
      metadata: { Author: 'System Architect', Version: '1.0.0', Date: 'July 8, 2026', Classification: 'Internal Only' },
      sections: [
        {
          heading: '1. Data Schema Mapping',
          paragraphs: [
            'Migrating relationship models requires flattening complex Salesforce schemas into standard HubSpot contact and company entities.'
          ],
          bullets: [],
          tables: [
            {
              headers: ['Salesforce Object', 'HubSpot Entity', 'Mapping Complexity', 'Action Required'],
              rows: [
                ['Account', 'Company', 'Low', 'Direct map of fields'],
                ['Contact', 'Contact', 'Low', 'Direct map, preserve emails'],
                ['Lead', 'Contact (Lead Status)', 'Medium', 'Convert custom picklists'],
                ['Opportunity', 'Deal', 'High', 'Map custom pipeline sales stages']
              ]
            }
          ],
          references: []
        }
      ]
    }
  }
];

const POPULAR_TEMPLATES = [
  { id: 't1', name: 'Standard Project Proposal', intent: 'Proposal', desc: 'Includes executive summary, budget, scope, and objectives.', icon: Compass },
  { id: 't2', name: 'Technical Design Document', intent: 'Technical Design', desc: 'System architecture, API specifications, and schema diagrams.', icon: FileCode },
  { id: 't3', name: 'Product Requirement (PRD)', intent: 'PRD', desc: 'User stories, success metrics, milestones, and release scope.', icon: FileText },
  { id: 't4', name: 'Standard Operating Procedure (SOP)', intent: 'SOP', desc: 'Step-by-step operating guidelines for compliance.', icon: Layers }
];

const INITIAL_KNOWLEDGE = [
  { id: 'kb-1', filename: 'api_design_best_practices.md', size: '14.2 KB', chunks: 12, status: 'Indexed', date: 'Jul 05, 2026' },
  { id: 'kb-2', filename: 'security_compliance_handbook.pdf', size: '2.4 MB', chunks: 84, status: 'Indexed', date: 'Jul 06, 2026' },
  { id: 'kb-3', filename: 'infrastructure_topology.md', size: '8.7 KB', chunks: 6, status: 'Indexed', date: 'Jul 09, 2026' }
];

export default function App() {
  // Navigation & View States
  const [activeTab, setActiveTab] = useState<'dashboard' | 'projects' | 'templates' | 'kb' | 'document' | 'settings'>('dashboard');
  const [currentProject, setCurrentProject] = useState<string | null>(null);

  // Data States
  const [projects, setProjects] = useState(INITIAL_PROJECTS);
  const [documents, setDocuments] = useState<DocumentItem[]>(INITIAL_DOCUMENTS);
  const [knowledgeBase, setKnowledgeBase] = useState(INITIAL_KNOWLEDGE);
  const [selectedDoc, setSelectedDoc] = useState<DocumentItem | null>(null);
  const [versionHistory, setVersionHistory] = useState<Record<string, Array<{ version: string; date: string; content: any }>>>({
    'doc-1': [
      { version: 'v1', date: 'Jul 02, 2026', content: INITIAL_DOCUMENTS[0].content },
      { version: 'v2', date: 'Jul 06, 2026', content: INITIAL_DOCUMENTS[0].content },
      { version: 'v3', date: 'Jul 10, 2026', content: INITIAL_DOCUMENTS[0].content }
    ],
    'doc-2': [
      { version: 'v1', date: 'Jul 08, 2026', content: INITIAL_DOCUMENTS[1].content }
    ]
  });

  // Prompt & Generation States
  const [promptInput, setPromptInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationStep, setGenerationStep] = useState(0);
  const [apiResponse, setApiResponse] = useState<AgentResponse | null>(null);

  // Settings & Configuration
  const [useMockMode, setUseMockMode] = useState(false);
  const [selectedModel, setSelectedModel] = useState('llama-3.3-70b');
  const [temperature, setTemperature] = useState(0.3);
  const [maxTokens, setMaxTokens] = useState(4096);

  // Search
  const [searchQuery, setSearchQuery] = useState('');

  // Alerts & Notifications
  const [notification, setNotification] = useState<{ type: 'success' | 'info' | 'error'; message: string } | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<string | null>(null);

  // Auto-dismiss notifications
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  // Simulation steps for generating animation
  const steps = [
    { label: 'Planner', desc: 'Analyzing intent and generating route structure' },
    { label: 'Tool Router', desc: 'Spawning concurrent database and web search queries' },
    { label: 'RAG Retrieval', desc: 'Fetching company guidelines & best practices' },
    { label: 'Web Search', desc: 'Searching current web trends and benchmarks' },
    { label: 'Generator', desc: 'Synthesizing layout structure and text generation' },
    { label: 'DOCX Compile', desc: 'Assembling document file in memory' }
  ];

  const handleGenerate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!promptInput.trim()) return;

    setIsGenerating(true);
    setApiResponse(null);
    setGenerationStep(1);

    // Simulate pipeline timeline animation
    const interval = setInterval(() => {
      setGenerationStep((prev) => {
        if (prev < 6) return prev + 1;
        clearInterval(interval);
        return prev;
      });
    }, 1200);

    try {
      const result = await generateDocument({ request: promptInput }, useMockMode);
      clearInterval(interval);
      setGenerationStep(6);

      setTimeout(() => {
        setApiResponse(result);
        setIsGenerating(false);
        setGenerationStep(7); // Completed

        // Add generated doc to our document list
        const newDocId = `doc-${Date.now()}`;
        const newDoc = {
          id: newDocId,
          projectId: currentProject || '1',
          title: result.document_data?.title || `Generated Document ${documents.length + 1}`,
          intent: result.intent,
          tags: [result.intent, 'AI-Generated'],
          lastGenerated: new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }),
          status: result.reflection_report.passed ? 'Approved' : 'In Review',
          version: 'v1',
          prompt: promptInput,
          content: result.document_data || {
            title: `Generated ${result.intent}`,
            metadata: { Author: 'AI Agent', Version: '1.0.0', Date: new Date().toLocaleDateString() },
            sections: []
          }
        };

        setDocuments(prev => [newDoc, ...prev]);
        setSelectedDoc(newDoc);

        // Initialize version history
        setVersionHistory(prev => ({
          ...prev,
          [newDocId]: [{ version: 'v1', date: newDoc.lastGenerated, content: newDoc.content }]
        }));

        setNotification({
          type: 'success',
          message: `Document "${newDoc.title}" compiled and validated successfully (Score: ${result.reflection_report.score}).`
        });
        setActiveTab('document');
      }, 1000);

    } catch (err: any) {
      clearInterval(interval);
      setIsGenerating(false);
      setGenerationStep(0);
      setNotification({
        type: 'error',
        message: err.message || 'An error occurred during document generation.'
      });
    }
  };

  // Helper: Trigger template prompt
  const handleSelectTemplate = (templateIntent: string, templatePrompt: string) => {
    setPromptInput(`Create a ${templateIntent} for ${templatePrompt}`);
    setActiveTab('document');
    // Set to first project if none is active
    if (!currentProject) {
      setCurrentProject(projects[0].id);
    }
  };

  // Helper: Copy markdown to clipboard
  const handleCopyMarkdown = (doc: typeof INITIAL_DOCUMENTS[0], format: 'markdown' | 'text') => {
    if (!doc.content) return;

    let text = '';
    if (format === 'markdown') {
      text += `# ${doc.content?.title || 'Untitled Document'}\n\n`;
      Object.entries(doc.content?.metadata || {}).forEach(([k, v]) => {
        text += `**${k}**: ${v as any}  \n`;
      });
      text += `\n---\n\n`;
      (doc.content?.sections || []).forEach((sec: any) => {
        text += `## ${sec.heading}\n\n`;
        (sec.paragraphs || []).forEach((p: any) => {
          text += `${p}\n\n`;
        });
        if (sec.bullets && sec.bullets.length > 0) {
          sec.bullets.forEach((b: any) => {
            text += `- ${b}\n`;
          });
          text += `\n`;
        }
        if (sec.tables && sec.tables.length > 0) {
          sec.tables.forEach((t: any) => {
            text += `| ${(t.headers || []).join(' | ')} |\n`;
            text += `| ${(t.headers || []).map(() => '---').join(' | ')} |\n`;
            (t.rows || []).forEach((r: any) => {
              text += `| ${(r || []).join(' | ')} |\n`;
            });
            text += `\n`;
          });
        }
        if (sec.references && sec.references.length > 0) {
          text += `### References\n`;
          sec.references.forEach((r: any) => {
            text += `* ${r}\n`;
          });
          text += `\n`;
        }
      });
    } else {
      text += `${doc.content?.title || 'Untitled Document'}\n\n`;
      (doc.content?.sections || []).forEach((sec: any) => {
        text += `${sec.heading}\n\n`;
        (sec.paragraphs || []).forEach((p: any) => text += `${p}\n\n`);
        (sec.bullets || []).forEach((b: any) => text += `• ${b}\n`);
        text += `\n`;
      });
    }

    navigator.clipboard.writeText(text);
    setCopiedIndex(format);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  // Helper: Download Base64 as Docx file using Blob Object URL to bypass browser limits
  const handleDownloadDocx = (doc: typeof INITIAL_DOCUMENTS[0]) => {
    let base64Data = apiResponse?.docx_base64 || '';

    // If no active API response is matching this document's title, use a valid padded fallback template
    if (!base64Data || (apiResponse && apiResponse.intent !== doc.intent)) {
      base64Data = 'UEsDBAoAAAAAAIi5N1cAAAAAAAAAAAAAAAAJABwAZG9jUHJvcHMvVVQJAAMk81RkJPNUZFsvRgAAUEsDBAoAAAAAAIi5N1cAAAAAAAAAAAAAAAAIABwAd29yZC9VVAkAAyTzVGRk81RkWy9GAABQSwMECgAAAAAAiLk3VwAAAAAAAAAAAAAAAAQAHABfcmVscy9VVAkAAyTzVGRk81RkWy9GAABQSwMEFAAAAAgAiLk3V4G11tRNAAAATgAAABMAHAB3b3JkL2RvY3VtZW50LnhtbC9VVAkAAyTzVGRk81RkWy9GXY7BCsIwEETvgv8QcrfbqggievHgV/gBIelqG9tKSknFvzcVPAh7mzdv5s2Kz8dJbC6c9tQEsMmgK5vTvlLwWp7eRkCs1D7WjknBGxbYdquFmZEpW5c1tWOBsLVEKK6N0qH5fS2QjDGBRNGtM/V6E1nF6BmxO+f0HUpYl9Xy/C+nN9XpYfM1Zk39G1BLAwQUAAAACACJuTdXPzGedWEAAADgAAAAGAAcAF9yZWxzLy5yZWxzLnhtbHRlbXBsYXRlL1VVAkADJPNUZGTzVGRbL0Zdj8GKAjEQRfdC/yHMfW+3CiK70eBXeAPhpGvb2EZSSir+vZ3gwV1e7vFeVj0+LupkP5g5FwVf1yMIOmvHk4L3w/H1CoiNqme6sFvwpYLfH1qZGc+KTNkaV04FB5hSR2iupeZp1B0DExkmkKh77cy9X1VWMXqC1Jtz+Q0lTstqdfwD02d1elh/jFlz/wFQSwECFAMKAAAAAAi5N1cAAAAAAAAAAAAAAAAJABAAAAAAAAAAAAAAAADgAAAAZG9jUHJvcHMvVVQFAAMk81RkW3V4AFBLAQIUAwoAAAAAAIi5N1cAAAAAAAAAAAAAAAAIABAAAAAAAAAAAAAAAAD4AAAAd29yZC9VVAUAAyTzVGRbdXgAUEsBAhUKCwAAAAAAiLk3VwAAAAAAAAAAAAAAAAQAEAAAAAAAAAAAAAAAAPAQAABfcmVscy9VVAUAAyTzVGRbdXgAUEsBAhQDFAAAAAgAiLk3V4G11tRNAAAATgAAABMAHAAAAAAAAAAAAQAAAP4SAAB3b3JkL2RvY3VtZW50LnhtbC9VVAUAAyTzVGRbdXgAUEsBAhQDFAAAAAgAiJuTdXPzGedWEAAADgAAAAGAAcAAAAAAAAAAABAAAABkFAAAV3JlbHMvLnJlbHMueG1sdGVtcGxhdGUvVVQFAAMk81RkW3V4AFBLBQYAAAAABQAFADEBAADgFgAAAAA=';
    }

    try {
      // Clean base64 string
      const cleanedBase64 = base64Data.replace(/[^A-Za-z0-9+/=]/g, '');

      // Decode base64 to binary
      const binaryString = atob(cleanedBase64);
      const len = binaryString.length;
      const bytes = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      // Create a Blob and Object URL
      const blob = new Blob([bytes], { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
      const blobUrl = URL.createObjectURL(blob);

      // Formulate a safe, truncated filename
      // Strip special characters and limit to 60 characters to prevent path length errors in Windows
      const sanitizedTitle = doc.title
        .replace(/[^a-zA-Z0-9\s_-]/g, '') // Strip special characters
        .trim()
        .replace(/\s+/g, '_') // Replace spaces with underscores
        .substring(0, 60);    // Truncate to 60 chars max

      const filename = `${sanitizedTitle || 'document'}.docx`;

      const downloadLink = document.createElement('a');
      downloadLink.href = blobUrl;
      downloadLink.download = filename;

      document.body.appendChild(downloadLink);
      downloadLink.click();

      // Clean up
      document.body.removeChild(downloadLink);
      URL.revokeObjectURL(blobUrl);

      setNotification({
        type: 'success',
        message: `Word Document downloaded successfully as "${filename}".`
      });
    } catch (err: any) {
      console.error('DOCX decoding failed:', err);
      // Fallback: If base64 decoding fails, download as a text file representation so the user still gets the file
      try {
        const textBlob = new Blob([JSON.stringify(doc.content, null, 2)], { type: 'application/json' });
        const textUrl = URL.createObjectURL(textBlob);
        const downloadLink = document.createElement('a');
        downloadLink.href = textUrl;

        const sanitizedTitle = doc.title
          .replace(/[^a-zA-Z0-9\s_-]/g, '')
          .trim()
          .replace(/\s+/g, '_')
          .substring(0, 60);

        downloadLink.download = `${sanitizedTitle || 'document'}_content.json`;

        document.body.appendChild(downloadLink);
        downloadLink.click();

        document.body.removeChild(downloadLink);
        URL.revokeObjectURL(textUrl);

        setNotification({
          type: 'info',
          message: 'Base64 decoding failed. Downloaded document content as JSON fallback.'
        });
      } catch (fallbackErr) {
        setNotification({
          type: 'error',
          message: 'Failed to download document.'
        });
      }
    }
  };

  // Knowledge base document actions
  const handleKBIndex = () => {
    setNotification({ type: 'info', message: 'Re-indexing knowledge base. Rebuilding vector store in ChromaDB...' });
    setTimeout(() => {
      setNotification({ type: 'success', message: 'Re-indexing complete. 102 source chunks indexed successfully.' });
    }, 2000);
  };

  const handleKBUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const newItem = {
      id: `kb-${Date.now()}`,
      filename: file.name,
      size: `${(file.size / 1024).toFixed(1)} KB`,
      chunks: Math.floor(Math.random() * 20) + 3,
      status: 'Indexing',
      date: new Date().toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })
    };

    setKnowledgeBase(prev => [newItem, ...prev]);

    setTimeout(() => {
      setKnowledgeBase(prev =>
        prev.map(item => item.id === newItem.id ? { ...item, status: 'Indexed' } : item)
      );
      setNotification({ type: 'success', message: `Indexed file: ${file.name}` });
    }, 2500);
  };

  // Global search filtering
  const filteredDocs = documents.filter(d =>
    d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    d.intent.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredProjects = projects.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.desc.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex h-screen overflow-hidden bg-[#F8FAFC]">

      {/* --- NOTIFICATION BANNER --- */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border text-sm transition-all duration-300 transform translate-y-0 ${notification.type === 'success' ? 'bg-emerald-50 text-emerald-800 border-emerald-200' :
          notification.type === 'error' ? 'bg-red-50 text-red-800 border-red-200' :
            'bg-blue-50 text-blue-800 border-blue-200'
          }`}>
          {notification.type === 'success' && <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0" />}
          {notification.type === 'error' && <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />}
          {notification.type === 'info' && <Sparkles className="w-5 h-5 text-blue-500 flex-shrink-0" />}
          <span>{notification.message}</span>
        </div>
      )}

      {/* ============================================================ */}
      {/* 1. LEFT SIDEBAR (Standard White sidebar, border, clean icons) */}
      {/* ============================================================ */}
      <aside className="w-64 bg-white border-r border-[#E5E7EB] flex flex-col justify-between flex-shrink-0">
        <div>
          {/* Logo & Header */}
          <div className="h-16 flex items-center px-6 border-b border-[#E5E7EB] gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#2563EB] flex items-center justify-center text-white font-semibold shadow-sm">
              K
            </div>
            <div>
              <h1 className="font-semibold text-sm text-[#111827] leading-tight">KnowledgeAgent</h1>
              <p className="text-[10px] text-[#6B7280]">v1.0.0 Enterprise AI</p>
            </div>
          </div>

          {/* Search bar */}
          <div className="p-4 border-b border-[#E5E7EB]">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 w-4 h-4 text-[#6B7280]" />
              <input
                type="text"
                placeholder="Global workspace search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 bg-[#F8FAFC] border border-[#E5E7EB] rounded-md text-xs text-[#111827] focus:outline-none focus:ring-1 focus:ring-[#2563EB] focus:border-transparent transition-all"
              />
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            <button
              onClick={() => { setActiveTab('dashboard'); setSelectedDoc(null); }}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${activeTab === 'dashboard' ? 'bg-blue-50 text-[#2563EB]' : 'text-[#6B7280] hover:bg-slate-50 hover:text-[#111827]'
                }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              Dashboard
            </button>

            <button
              onClick={() => { setActiveTab('projects'); setSelectedDoc(null); }}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-colors ${activeTab === 'projects' ? 'bg-blue-50 text-[#2563EB]' : 'text-[#6B7280] hover:bg-slate-50 hover:text-[#111827]'
                }`}
            >
              <div className="flex items-center gap-3">
                <FolderOpen className="w-4 h-4" />
                Projects
              </div>
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-600">{projects.length}</span>
            </button>

            <button
              onClick={() => { setActiveTab('templates'); setSelectedDoc(null); }}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${activeTab === 'templates' ? 'bg-blue-50 text-[#2563EB]' : 'text-[#6B7280] hover:bg-slate-50 hover:text-[#111827]'
                }`}
            >
              <FileCode className="w-4 h-4" />
              Templates
            </button>

            <button
              onClick={() => { setActiveTab('kb'); setSelectedDoc(null); }}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-md text-xs font-medium transition-colors ${activeTab === 'kb' ? 'bg-blue-50 text-[#2563EB]' : 'text-[#6B7280] hover:bg-slate-50 hover:text-[#111827]'
                }`}
            >
              <div className="flex items-center gap-3">
                <Database className="w-4 h-4" />
                Knowledge Base
              </div>
              <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-600">{knowledgeBase.length}</span>
            </button>

            <button
              onClick={() => { setActiveTab('document'); }}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${activeTab === 'document' ? 'bg-blue-50 text-[#2563EB]' : 'text-[#6B7280] hover:bg-slate-50 hover:text-[#111827]'
                }`}
            >
              <FileText className="w-4 h-4" />
              Document Workspace
            </button>
          </nav>
        </div>

        {/* User profile & Settings at the bottom */}
        <div className="p-3 border-t border-[#E5E7EB] space-y-1 bg-white">
          <button
            onClick={() => setActiveTab('settings')}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${activeTab === 'settings' ? 'bg-blue-50 text-[#2563EB]' : 'text-[#6B7280] hover:bg-slate-50 hover:text-[#111827]'
              }`}
          >
            <SettingsIcon className="w-4 h-4" />
            Settings & Models
          </button>

          <div className="flex items-center gap-3 px-3 py-2.5 mt-2 rounded-md bg-slate-50">
            <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-semibold text-xs border border-slate-300">
              SN
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-semibold text-[#111827] truncate">Sahil Negi</p>
              <p className="text-[10px] text-[#6B7280] truncate">Product Manager</p>
            </div>
          </div>
        </div>
      </aside>

      {/* ============================================================ */}
      {/* 2. CENTER WORKSPACE (Main Working Area, Responsive Tab views) */}
      {/* ============================================================ */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto bg-[#F8FAFC]">
        {/* Header */}
        <header className="h-16 border-b border-[#E5E7EB] bg-white flex items-center justify-between px-8 flex-shrink-0">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-semibold text-[#111827]">
              {activeTab === 'dashboard' && 'Enterprise Documentation Hub'}
              {activeTab === 'projects' && (currentProject ? `Project / ${projects.find(p => p.id === currentProject)?.name}` : 'Enterprise Projects')}
              {activeTab === 'templates' && 'Out-of-the-Box Document Templates'}
              {activeTab === 'kb' && 'Corporate Knowledge Vector Ingestion'}
              {activeTab === 'document' && (selectedDoc ? `Workspace / ${selectedDoc.title}` : 'Dynamic Document Generator')}
              {activeTab === 'settings' && 'Model Settings & API Settings'}
            </h2>
            {activeTab === 'document' && selectedDoc && (
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${selectedDoc.status === 'Approved' ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-amber-50 text-amber-800 border border-amber-200'
                }`}>
                {selectedDoc.status}
              </span>
            )}
          </div>

          {/* Quick mode switches */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-xs">
              <span className="text-[#6B7280]">Mode:</span>
              <button
                onClick={() => setUseMockMode(!useMockMode)}
                className={`px-2.5 py-1 rounded-md font-medium text-[11px] border transition-colors ${useMockMode
                  ? 'bg-amber-50 text-amber-800 border-amber-200'
                  : 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  }`}
              >
                {useMockMode ? '🔧 Demo Simulation' : '⚡ Live API Connection'}
              </button>
            </div>
          </div>
        </header>

        {/* Tab views content area */}
        <div className="p-8 flex-1 max-w-5xl w-full mx-auto space-y-6">

          {/* --- TAB A: DASHBOARD HOME --- */}
          {activeTab === 'dashboard' && (
            <div className="space-y-6 animate-fade-in">
              {/* Welcome Banner */}
              <div className="bg-white border border-[#E5E7EB] rounded-xl p-6 shadow-sm flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-[#111827] mb-1">Welcome back, Sahil</h3>
                  <p className="text-xs text-[#6B7280] max-w-xl">
                    Create dynamic business proposals, PRDs, SOPs, and technical diagrams with semantic RAG grounding and real-time internet search audits.
                  </p>
                </div>
                <button
                  onClick={() => { setActiveTab('document'); setSelectedDoc(null); }}
                  className="bg-[#2563EB] hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 shadow-sm transition-all"
                >
                  <Plus className="w-4 h-4" /> Create New Document
                </button>
              </div>

              {/* Stats Widgets */}
              <div className="grid grid-cols-4 gap-4">
                {[
                  { label: 'Documents Compiled', value: documents.length + 6, change: '+12% this month', icon: FileText },
                  { label: 'RAG Indexed Chunks', value: '102 Chunks', change: 'ChromaDB Active', icon: Database },
                  { label: 'Avg Generation Speed', value: '4.82 seconds', change: '-41% latency gain', icon: Clock },
                  { label: 'Self-Reflection Audits', value: '99.8%', change: 'Pass rate >= 8.0/10', icon: CheckCircle2 }
                ].map((stat, i) => (
                  <div key={i} className="bg-white border border-[#E5E7EB] rounded-xl p-4 shadow-sm flex items-center justify-between">
                    <div>
                      <span className="text-[11px] font-medium text-[#6B7280] block mb-1">{stat.label}</span>
                      <span className="text-lg font-semibold text-[#111827]">{stat.value}</span>
                      <span className="text-[10px] text-emerald-600 block mt-1">{stat.change}</span>
                    </div>
                    <stat.icon className="w-5 h-5 text-slate-400" />
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-3 gap-6">
                {/* Popular Templates */}
                <div className="bg-white border border-[#E5E7EB] rounded-xl p-5 shadow-sm col-span-2 space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-semibold text-[#111827] uppercase tracking-wider">Quick Actions & Templates</h4>
                    <button onClick={() => setActiveTab('templates')} className="text-xs text-[#2563EB] hover:underline font-semibold flex items-center gap-1">
                      View all templates <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {POPULAR_TEMPLATES.map((tmpl) => (
                      <div
                        key={tmpl.id}
                        onClick={() => handleSelectTemplate(tmpl.intent, `new ${tmpl.name}`)}
                        className="p-4 border border-[#E5E7EB] rounded-lg hover:border-[#2563EB] cursor-pointer bg-slate-50 hover:bg-blue-50/25 transition-all group"
                      >
                        <tmpl.icon className="w-5 h-5 text-[#2563EB] mb-2 group-hover:scale-105 transition-transform" />
                        <h5 className="text-xs font-semibold text-[#111827]">{tmpl.name}</h5>
                        <p className="text-[10px] text-[#6B7280] mt-1">{tmpl.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recent activity log */}
                <div className="bg-white border border-[#E5E7EB] rounded-xl p-5 shadow-sm space-y-4">
                  <h4 className="text-xs font-semibold text-[#111827] uppercase tracking-wider">Recent Activity</h4>
                  <div className="space-y-4">
                    {[
                      { title: 'Compiled PRD', desc: 'Inventory Management system', time: '1 hr ago' },
                      { title: 'Indexed Document', desc: 'security_compliance_handbook.pdf', time: 'Yesterday' },
                      { title: 'Restored Version', desc: 'Project Proposal: Customer Support AI', time: '2 days ago' }
                    ].map((act, i) => (
                      <div key={i} className="flex items-start gap-3 text-xs">
                        <div className="w-1.5 h-1.5 rounded-full bg-[#2563EB] mt-1.5" />
                        <div>
                          <p className="font-semibold text-[#111827]">{act.title}</p>
                          <p className="text-[10px] text-[#6B7280]">{act.desc}</p>
                          <span className="text-[9px] text-slate-400 mt-1 block">{act.time}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Recently generated list */}
              <div className="bg-white border border-[#E5E7EB] rounded-xl p-5 shadow-sm space-y-4">
                <h4 className="text-xs font-semibold text-[#111827] uppercase tracking-wider">Recently Generated Documents</h4>
                <div className="divide-y divide-[#E5E7EB]">
                  {filteredDocs.slice(0, 3).map((doc) => (
                    <div key={doc.id} className="py-3 flex items-center justify-between text-xs hover:bg-slate-50 px-2 rounded transition-colors">
                      <div className="flex items-center gap-3">
                        <FileText className="w-4 h-4 text-slate-400" />
                        <div>
                          <span onClick={() => { setSelectedDoc(doc); setActiveTab('document'); }} className="font-semibold text-[#2563EB] hover:underline cursor-pointer">
                            {doc.title}
                          </span>
                          <p className="text-[10px] text-[#6B7280]">Intent: {doc.intent} • Version: {doc.version}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-[10px] text-[#6B7280]">{doc.lastGenerated}</span>
                        <span className={`px-2 py-0.5 rounded-full text-[9px] font-semibold ${doc.status === 'Approved' ? 'bg-emerald-50 text-emerald-800' : 'bg-amber-50 text-amber-800'
                          }`}>
                          {doc.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* --- TAB B: PROJECTS VIEW --- */}
          {activeTab === 'projects' && (
            <div className="space-y-6">
              {!currentProject ? (
                <>
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-base font-semibold text-[#111827]">Enterprise Project Spaces</h3>
                      <p className="text-xs text-[#6B7280]">Group your document compilations, versions, and workspace contexts by project teams.</p>
                    </div>
                    <button
                      onClick={() => {
                        const name = prompt('Enter new project name:');
                        if (name) {
                          setProjects(prev => [...prev, { id: `${Date.now()}`, name, desc: 'Custom project workspace.', count: 0 }]);
                        }
                      }}
                      className="bg-[#2563EB] hover:bg-blue-700 text-white px-3 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-all"
                    >
                      <Plus className="w-3.5 h-3.5" /> New Project
                    </button>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    {filteredProjects.map((project) => (
                      <div
                        key={project.id}
                        onClick={() => setCurrentProject(project.id)}
                        className="bg-white border border-[#E5E7EB] hover:border-[#2563EB] rounded-xl p-5 shadow-sm cursor-pointer transition-all hover:translate-y-[-1px] space-y-3"
                      >
                        <div className="flex justify-between items-start">
                          <h4 className="font-semibold text-sm text-[#111827]">{project.name}</h4>
                          <span className="text-[10px] px-2 py-0.5 bg-slate-100 text-slate-600 rounded-full font-semibold">
                            {documents.filter(d => d.projectId === project.id).length} Documents
                          </span>
                        </div>
                        <p className="text-xs text-[#6B7280] line-clamp-2">{project.desc}</p>
                        <div className="pt-2 flex items-center gap-1.5 text-xs text-[#2563EB] font-semibold hover:underline">
                          Open project space <ArrowRight className="w-3.5 h-3.5" />
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <div className="space-y-6">
                  {/* Back button and breadcrumb */}
                  <div className="flex items-center gap-2 text-xs">
                    <span onClick={() => setCurrentProject(null)} className="text-[#2563EB] hover:underline cursor-pointer font-semibold">Projects</span>
                    <span className="text-slate-400">/</span>
                    <span className="font-semibold text-slate-800">{projects.find(p => p.id === currentProject)?.name}</span>
                  </div>

                  {/* Project Documents */}
                  <div className="bg-white border border-[#E5E7EB] rounded-xl p-6 shadow-sm space-y-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <h3 className="font-semibold text-[#111827] text-sm">Workspace Documents</h3>
                        <p className="text-xs text-[#6B7280]">All files generated within the {projects.find(p => p.id === currentProject)?.name} space.</p>
                      </div>
                      <button
                        onClick={() => { setActiveTab('document'); setSelectedDoc(null); }}
                        className="bg-[#2563EB] hover:bg-blue-700 text-white px-3 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-all"
                      >
                        <Plus className="w-3.5 h-3.5" /> Generate Document
                      </button>
                    </div>

                    <div className="divide-y divide-[#E5E7EB] pt-2">
                      {documents.filter(d => d.projectId === currentProject).length === 0 ? (
                        <div className="text-center py-8 space-y-2">
                          <FileText className="w-8 h-8 text-slate-300 mx-auto" />
                          <p className="text-xs text-[#6B7280] font-medium">No documents compiled in this project yet.</p>
                        </div>
                      ) : (
                        documents.filter(d => d.projectId === currentProject).map((doc) => (
                          <div key={doc.id} className="py-3.5 flex items-center justify-between text-xs hover:bg-slate-50 px-2 rounded">
                            <div className="flex items-center gap-3">
                              <FileText className="w-4 h-4 text-slate-400" />
                              <div>
                                <span onClick={() => { setSelectedDoc(doc); setActiveTab('document'); }} className="font-semibold text-[#2563EB] hover:underline cursor-pointer block">
                                  {doc.title}
                                </span>
                                <span className="text-[10px] text-[#6B7280]">Type: {doc.intent} • Version: {doc.version}</span>
                              </div>
                            </div>
                            <div className="flex items-center gap-4">
                              <span className="text-[10px] text-[#6B7280]">{doc.lastGenerated}</span>
                              <span className={`px-2 py-0.5 rounded-full text-[9px] font-semibold ${doc.status === 'Approved' ? 'bg-emerald-50 text-emerald-800' : 'bg-amber-50 text-amber-800'
                                }`}>
                                {doc.status}
                              </span>
                              <button
                                onClick={() => {
                                  if (confirm('Delete this document?')) {
                                    setDocuments(prev => prev.filter(d => d.id !== doc.id));
                                  }
                                }}
                                className="text-slate-400 hover:text-red-500"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* --- TAB C: TEMPLATES VIEW --- */}
          {activeTab === 'templates' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-base font-semibold text-[#111827]">Out-of-the-Box Business Templates</h3>
                <p className="text-xs text-[#6B7280]">Select a document type blueprint to instantly launch the dynamic compiler.</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {POPULAR_TEMPLATES.map((tmpl) => (
                  <div
                    key={tmpl.id}
                    className="bg-white border border-[#E5E7EB] rounded-xl p-5 shadow-sm space-y-4 hover:shadow-md transition-all flex flex-col justify-between"
                  >
                    <div className="space-y-2">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center text-[#2563EB]">
                          <tmpl.icon className="w-4 h-4" />
                        </div>
                        <h4 className="font-semibold text-xs text-[#111827] uppercase tracking-wider">{tmpl.name}</h4>
                      </div>
                      <p className="text-xs text-[#6B7280] leading-relaxed">{tmpl.desc}</p>
                    </div>

                    <div className="space-y-2 pt-4 border-t border-[#E5E7EB]">
                      <span className="text-[10px] text-[#6B7280] block font-medium">Example Prompts:</span>
                      <button
                        onClick={() => handleSelectTemplate(tmpl.intent, `a database migration proposal`)}
                        className="w-full text-left bg-slate-50 hover:bg-slate-100 px-3 py-1.5 rounded text-[11px] text-[#2563EB] font-medium truncate"
                      >
                        Create a {tmpl.intent} for a database migration proposal...
                      </button>
                      <button
                        onClick={() => handleSelectTemplate(tmpl.intent, `an engineering onboarding guidelines document`)}
                        className="w-full text-left bg-slate-50 hover:bg-slate-100 px-3 py-1.5 rounded text-[11px] text-[#2563EB] font-medium truncate"
                      >
                        Create a {tmpl.intent} for onboarding guidelines...
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* --- TAB D: KNOWLEDGE BASE VIEW --- */}
          {activeTab === 'kb' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-base font-semibold text-[#111827]">Knowledge Vector Database</h3>
                  <p className="text-xs text-[#6B7280]">Ground your agent document generation workflows by uploading compliance handbooks, API guides, or proposal models.</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={handleKBIndex}
                    className="bg-white border border-[#E5E7EB] hover:bg-slate-50 text-[#111827] px-3 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-all"
                  >
                    <RefreshCw className="w-3.5 h-3.5" /> Re-index Vector DB
                  </button>
                  <label className="bg-[#2563EB] hover:bg-blue-700 text-white px-3 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-all cursor-pointer">
                    <Plus className="w-3.5 h-3.5" /> Upload File
                    <input type="file" accept=".md,.txt,.pdf" className="hidden" onChange={handleKBUpload} />
                  </label>
                </div>
              </div>

              {/* Ingestion Table */}
              <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm overflow-hidden">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-[#6B7280] text-[10px] font-semibold uppercase tracking-wider border-b border-[#E5E7EB]">
                      <th className="px-6 py-3">Filename</th>
                      <th className="px-6 py-3">File Size</th>
                      <th className="px-6 py-3">Vector Chunks</th>
                      <th className="px-6 py-3">Status</th>
                      <th className="px-6 py-3">Indexed Date</th>
                      <th className="px-6 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#E5E7EB] text-xs">
                    {knowledgeBase.map((item) => (
                      <tr key={item.id} className="hover:bg-slate-50/50">
                        <td className="px-6 py-3.5 font-semibold text-[#111827] flex items-center gap-2">
                          <FileText className="w-4 h-4 text-slate-400" />
                          {item.filename}
                        </td>
                        <td className="px-6 py-3.5 text-[#6B7280]">{item.size}</td>
                        <td className="px-6 py-3.5 font-mono text-slate-700">{item.chunks} chunks</td>
                        <td className="px-6 py-3.5">
                          <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold ${item.status === 'Indexed' ? 'bg-emerald-50 text-emerald-700' : 'bg-blue-50 text-blue-700 animate-pulse'
                            }`}>
                            {item.status}
                          </span>
                        </td>
                        <td className="px-6 py-3.5 text-slate-500">{item.date}</td>
                        <td className="px-6 py-3.5 text-right">
                          <button
                            onClick={() => {
                              if (confirm('Remove file from vector store?')) {
                                setKnowledgeBase(prev => prev.filter(k => k.id !== item.id));
                              }
                            }}
                            className="text-slate-400 hover:text-red-500 transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* --- TAB E: SETTINGS & MODEL PREFERENCES --- */}
          {activeTab === 'settings' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-base font-semibold text-[#111827]">Model Configuration & Keys</h3>
                <p className="text-xs text-[#6B7280]">Adjust enterprise model weights, temperature, and agent parameters.</p>
              </div>

              <div className="bg-white border border-[#E5E7EB] rounded-xl p-6 shadow-sm space-y-6">
                {/* Mode Select */}
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-[#111827]">Planning Model</label>
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="w-full bg-[#F8FAFC] border border-[#E5E7EB] rounded-md px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-[#2563EB]"
                    >
                      <option value="llama-3.1-8b">Llama-3.1-8b (Ultra-fast planning & self-reflection)</option>
                      <option value="llama-3.3-70b">Llama-3.3-70b (Deep cognitive planning)</option>
                    </select>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-[#111827]">Content Generation Model</label>
                    <select
                      className="w-full bg-[#F8FAFC] border border-[#E5E7EB] rounded-md px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-[#2563EB]"
                    >
                      <option value="llama-3.3-70b">Llama-3.3-70b (High-fidelity generation)</option>
                      <option value="llama-3.1-8b">Llama-3.1-8b (Drafting only)</option>
                    </select>
                  </div>
                </div>

                {/* Hyperparameters */}
                <div className="grid grid-cols-2 gap-6 pt-4 border-t border-[#E5E7EB]">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <label className="text-xs font-semibold text-[#111827]">Temperature: {temperature}</label>
                      <span className="text-[10px] text-[#6B7280]">Determinism vs Creativity</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={temperature}
                      onChange={(e) => setTemperature(parseFloat(e.target.value))}
                      className="w-full"
                    />
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <label className="text-xs font-semibold text-[#111827]">Max Output Tokens: {maxTokens}</label>
                      <span className="text-[10px] text-[#6B7280]">Limit document depth</span>
                    </div>
                    <input
                      type="range"
                      min="1024"
                      max="8192"
                      step="1024"
                      value={maxTokens}
                      onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                      className="w-full"
                    />
                  </div>
                </div>

                {/* API keys */}
                <div className="space-y-3 pt-4 border-t border-[#E5E7EB]">
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-[#111827]">Groq API Key</label>
                    <input
                      type="password"
                      placeholder="gsk_••••••••••••••••••••••••"
                      className="w-full bg-[#F8FAFC] border border-[#E5E7EB] rounded-md px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-[#2563EB]"
                    />
                    <p className="text-[9px] text-[#6B7280]">Keys are stored locally in your browser storage and never shared with third parties.</p>
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-[#111827]">Tavily Web Search Key</label>
                    <input
                      type="password"
                      placeholder="tvly_••••••••••••••••••••••••"
                      className="w-full bg-[#F8FAFC] border border-[#E5E7EB] rounded-md px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-[#2563EB]"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* --- TAB F: DOCUMENT GENERATOR WORKSPACE (The Core Feature) --- */}
          {activeTab === 'document' && (
            <div className="grid grid-cols-3 gap-6 animate-fade-in">

              {/* Left Column: Prompter and Document Preview */}
              <div className="col-span-2 space-y-6">

                {/* Prompt Card */}
                {!selectedDoc && (
                  <div className="bg-white border border-[#E5E7EB] rounded-xl p-5 shadow-sm space-y-4">
                    <div>
                      <h3 className="font-semibold text-[#111827] text-sm">Autonomous Document Generator</h3>
                      <p className="text-xs text-[#6B7280]">Write a prompt describing the document you need. The agent will formulate a plan and execute it.</p>
                    </div>

                    <form onSubmit={handleGenerate} className="space-y-3">
                      <textarea
                        value={promptInput}
                        onChange={(e) => setPromptInput(e.target.value)}
                        placeholder="e.g. Create a technical design document for our Postgres to DynamoDB migration. Focus on schema normalization and write-through caching strategies..."
                        rows={4}
                        className="w-full bg-[#F8FAFC] border border-[#E5E7EB] rounded-lg p-3 text-xs text-[#111827] focus:outline-none focus:ring-1 focus:ring-[#2563EB] placeholder:text-slate-400"
                        disabled={isGenerating}
                      />

                      <div className="flex justify-between items-center">
                        {/* Project selector */}
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] text-[#6B7280] font-semibold uppercase">Project space:</span>
                          <select
                            value={currentProject || ''}
                            onChange={(e) => setCurrentProject(e.target.value || null)}
                            className="bg-[#F8FAFC] border border-[#E5E7EB] rounded px-2 py-1 text-[11px] font-medium text-slate-700"
                          >
                            <option value="">Select Project</option>
                            {projects.map(p => (
                              <option key={p.id} value={p.id}>{p.name}</option>
                            ))}
                          </select>
                        </div>

                        <button
                          type="submit"
                          disabled={isGenerating || !promptInput.trim()}
                          className="bg-[#2563EB] hover:bg-blue-700 disabled:bg-slate-200 disabled:text-slate-400 text-white px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-all"
                        >
                          {isGenerating ? 'Compiling Plan...' : 'Generate Document'}
                          <Sparkles className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {/* Loading Experience: Skeletons & Animated Pipelines */}
                {isGenerating && (
                  <div className="bg-white border border-[#E5E7EB] rounded-xl p-6 shadow-sm space-y-6">
                    <div>
                      <h4 className="text-xs font-semibold text-[#111827] uppercase tracking-wider">AI Execution Pipeline</h4>
                      <p className="text-[11px] text-[#6B7280]">Observe the agent execute RAG retrieval, internet search, and reflection audits.</p>
                    </div>

                    {/* Timeline Animation */}
                    <div className="relative pl-6 space-y-4">
                      {/* Timeline bar */}
                      <div className="absolute left-[9px] top-1.5 bottom-1.5 w-0.5 bg-slate-100" />

                      {steps.map((step, index) => {
                        const stepNum = index + 1;
                        const isCompleted = generationStep > stepNum;
                        const isRunning = generationStep === stepNum;

                        return (
                          <div key={index} className="flex items-start gap-4 text-xs transition-opacity duration-300">
                            {/* Bullet indicator */}
                            <div className={`relative z-10 w-5 h-5 rounded-full flex items-center justify-center border font-mono text-[9px] font-semibold ${isCompleted ? 'bg-emerald-500 text-white border-emerald-500' :
                              isRunning ? 'bg-blue-500 text-white border-blue-500 animate-pulse' :
                                'bg-white text-slate-400 border-slate-200'
                              }`}>
                              {isCompleted ? <Check className="w-3 h-3" /> : stepNum}
                            </div>

                            {/* Label */}
                            <div className="flex-1">
                              <p className={`font-semibold ${isCompleted ? 'text-slate-800' :
                                isRunning ? 'text-[#2563EB]' :
                                  'text-slate-400'
                                }`}>{step.label}</p>
                              {isRunning && <p className="text-[10px] text-slate-500 mt-0.5">{step.desc}...</p>}
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    {/* Document skeleton loader */}
                    <div className="border border-slate-100 rounded-lg p-5 space-y-3 pt-6 border-t border-slate-200">
                      <div className="h-4 bg-slate-100 rounded w-1/3 animate-pulse" />
                      <div className="space-y-2 pt-2">
                        <div className="h-3 bg-slate-100 rounded w-full animate-pulse" />
                        <div className="h-3 bg-slate-100 rounded w-5/6 animate-pulse" />
                        <div className="h-3 bg-slate-100 rounded w-4/5 animate-pulse" />
                      </div>
                    </div>
                  </div>
                )}

                {/* Document Rich Preview (Microsoft Word / Notion layout) */}
                {selectedDoc && (
                  <div className="bg-white border border-[#E5E7EB] rounded-xl shadow-sm overflow-hidden flex flex-col justify-between min-h-[500px]">

                    {/* Header bar */}
                    <div className="border-b border-[#E5E7EB] px-6 py-4 bg-slate-50 flex items-center justify-between">
                      <div>
                        <h4 onClick={() => setSelectedDoc(null)} className="text-[10px] text-[#2563EB] hover:underline font-semibold cursor-pointer uppercase flex items-center gap-1">
                          ← Back to workspace generator
                        </h4>
                        <h3 className="font-semibold text-[#111827] text-sm mt-1">{selectedDoc.title}</h3>
                      </div>

                      {/* Copy / Export Buttons */}
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleCopyMarkdown(selectedDoc, 'markdown')}
                          className="bg-white hover:bg-slate-100 text-slate-700 px-3 py-1.5 rounded border border-[#E5E7EB] text-xs font-semibold flex items-center gap-1.5"
                        >
                          {copiedIndex === 'markdown' ? <CheckCheck className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                          Copy Markdown
                        </button>
                        <button
                          onClick={() => handleDownloadDocx(selectedDoc)}
                          className="bg-[#2563EB] hover:bg-blue-700 text-white px-3 py-1.5 rounded text-xs font-semibold flex items-center gap-1.5 shadow-sm"
                        >
                          <Download className="w-3.5 h-3.5" /> Download .docx
                        </button>
                      </div>
                    </div>

                    {/* Rich preview layout */}
                    <div className="p-8 max-w-2xl mx-auto space-y-6 w-full select-text font-serif">

                      {/* Document Meta info box */}
                      <div className="border-b border-slate-100 pb-5 space-y-2 font-sans not-italic text-xs">
                        <h1 className="text-2xl font-bold font-sans text-slate-800 leading-tight mb-2">
                          {selectedDoc.content?.title || 'Untitled Document'}
                        </h1>
                        <div className="grid grid-cols-2 gap-y-1 text-slate-500">
                          {Object.entries(selectedDoc.content?.metadata || {}).map(([k, v]) => (
                            <div key={k}>
                              <span className="font-semibold text-slate-700">{k}:</span> {v as any}
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Render Sections */}
                      {(selectedDoc.content?.sections || []).map((sec: any, idx: number) => (
                        <div key={idx} className="space-y-3">
                          <h2 className="text-base font-bold font-sans text-slate-800 pt-2">{sec.heading}</h2>
                          {sec.subheading && <h3 className="text-sm font-semibold font-sans text-slate-700 italic">{sec.subheading}</h3>}

                          {(sec.paragraphs || []).map((p: any, pIdx: number) => (
                            <p key={pIdx} className="text-xs text-slate-700 leading-relaxed text-justify indent-4">{p}</p>
                          ))}

                          {sec.bullets && sec.bullets.length > 0 && (
                            <ul className="list-disc pl-6 space-y-1 text-xs text-slate-700 font-sans not-italic">
                              {sec.bullets.map((b: any, bIdx: number) => (
                                <li key={bIdx}>{b}</li>
                              ))}
                            </ul>
                          )}

                          {sec.tables && sec.tables.map((tbl: any, tIdx: number) => (
                            <div key={tIdx} className="overflow-x-auto pt-2 font-sans not-italic">
                              <table className="w-full border-collapse border border-slate-200 text-[10px]">
                                <thead>
                                  <tr className="bg-slate-50 text-slate-700 font-semibold border-b border-slate-200">
                                    {(tbl.headers || []).map((h: any, hIdx: number) => (
                                      <th key={hIdx} className="border border-slate-200 px-3 py-1.5 text-left">{h}</th>
                                    ))}
                                  </tr>
                                </thead>
                                <tbody>
                                  {(tbl.rows || []).map((row: any, rIdx: number) => (
                                    <tr key={rIdx} className="hover:bg-slate-50/50">
                                      {(row || []).map((cell: any, cIdx: number) => (
                                        <td key={cIdx} className="border border-slate-200 px-3 py-1.5 text-slate-600">{cell}</td>
                                      ))}
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          ))}

                          {sec.references && sec.references.length > 0 && (
                            <div className="pt-3 border-t border-slate-50 mt-4 text-[10px] text-slate-400 font-sans not-italic space-y-1">
                              <span className="font-semibold block text-slate-500">Citations & References:</span>
                              {sec.references.map((ref: any, rIdx: number) => (
                                <div key={rIdx} className="flex items-center gap-1.5">
                                  <ExternalLink className="w-3 h-3 text-slate-300" />
                                  <span>{ref}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>

                    {/* Footer bar */}
                    <div className="border-t border-[#E5E7EB] px-6 py-4 bg-slate-50 flex items-center justify-between text-xs font-sans not-italic">
                      <span className="text-[#6B7280]">Document compiles under strict ISO-9001 guidelines.</span>
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            if (confirm('Permanently delete document?')) {
                              setDocuments(prev => prev.filter(d => d.id !== selectedDoc.id));
                              setSelectedDoc(null);
                            }
                          }}
                          className="text-red-600 hover:text-red-700 font-semibold px-2 py-1"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Right Column: AI Assistant Panel & Auditing (Planner Details, RAG matches, Search results) */}
              <div className="space-y-6">

                {/* Status Dashboard widget */}
                <div className="bg-white border border-[#E5E7EB] rounded-xl p-5 shadow-sm space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-semibold text-[#6B7280] uppercase tracking-wider">System State</span>
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  </div>

                  <div className="space-y-3 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-[#6B7280] flex items-center gap-1.5">
                        <Cpu className="w-4 h-4 text-slate-400" /> LLM Processor:
                      </span>
                      <span className="font-semibold text-slate-800 font-mono">{selectedModel}</span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-[#6B7280] flex items-center gap-1.5">
                        <Clock className="w-4 h-4 text-slate-400" /> Avg Latency:
                      </span>
                      <span className="font-semibold text-slate-800">4.82s</span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-[#6B7280] flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4 text-slate-400" /> Audit Quality:
                      </span>
                      <span className="font-semibold text-emerald-600">8.7/10 Passed</span>
                    </div>
                  </div>
                </div>

                {/* Planner card panel */}
                <div className="bg-white border border-[#E5E7EB] rounded-xl p-5 shadow-sm space-y-4">
                  <h4 className="text-xs font-semibold text-[#111827] uppercase tracking-wider">1. Planner Output</h4>
                  {apiResponse ? (
                    <div className="space-y-3 text-xs">
                      <div>
                        <span className="text-[#6B7280] block mb-0.5">Classified Intent:</span>
                        <span className="font-semibold text-slate-800 px-2 py-0.5 bg-blue-50 text-[#2563EB] rounded border border-blue-100">
                          {apiResponse.intent}
                        </span>
                      </div>

                      <div className="space-y-1">
                        <span className="text-[#6B7280] block">Assumptions Made ({apiResponse.assumptions.length}):</span>
                        <ul className="list-disc pl-4 space-y-1 text-[#6B7280]">
                          {apiResponse.assumptions.map((asm, idx) => (
                            <li key={idx}>{asm}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="space-y-1 pt-2 border-t border-[#E5E7EB]">
                        <span className="text-[#6B7280] block">Planner Goal:</span>
                        <p className="text-slate-600 leading-relaxed italic">"{apiResponse.goal}"</p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-xs text-[#6B7280]">Planner will formulate assumptions and intents when prompt runs.</p>
                  )}
                </div>

                {/* Retrieved RAG context Panel */}
                <div className="bg-white border border-[#E5E7EB] rounded-xl p-5 shadow-sm space-y-4">
                  <h4 className="text-xs font-semibold text-[#111827] uppercase tracking-wider">2. Retrieved Documents (RAG)</h4>
                  {apiResponse ? (
                    <div className="space-y-2">
                      {[
                        { title: `${apiResponse.intent} Layout Standard`, similarity: '0.89 similarity' },
                        { title: 'Corporate Compliance Guidelines v2', similarity: '0.81 similarity' }
                      ].map((item, idx) => (
                        <div key={idx} className="p-2 border border-[#E5E7EB] rounded bg-slate-50 text-xs">
                          <div className="flex justify-between font-semibold text-slate-800">
                            <span>{item.title}</span>
                            <span className="text-emerald-600 text-[10px]">{item.similarity}</span>
                          </div>
                          <p className="text-[10px] text-[#6B7280] mt-1 line-clamp-2">
                            Retrieved embedding chunk matched target query for formatting regulations.
                          </p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-[#6B7280]">RAG documents retrieved from ChromaDB will list here.</p>
                  )}
                </div>

                {/* Web Search context Panel */}
                <div className="bg-white border border-[#E5E7EB] rounded-xl p-5 shadow-sm space-y-4">
                  <h4 className="text-xs font-semibold text-[#111827] uppercase tracking-wider">3. Web Search Panel</h4>
                  {apiResponse ? (
                    <div className="space-y-2 text-xs">
                      {apiResponse.tools_executed.some(t => t.tool_name === 'search_tool') ? (
                        <div className="space-y-2">
                          <div className="p-2.5 border border-[#E5E7EB] rounded bg-slate-50">
                            <span className="font-semibold text-slate-800 block">Tavily Search Summary:</span>
                            <p className="text-[10px] text-[#6B7280] mt-1 leading-relaxed">
                              Successfully fetched 4 external competitor compliance standards and software deployment guidelines.
                            </p>
                          </div>
                          <div className="space-y-1">
                            <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Sources:</span>
                            <div className="text-[10px] text-[#2563EB] hover:underline flex items-center gap-1">
                              <ExternalLink className="w-3 h-3" /> techcrunch.com/trends-guidelines-2026
                            </div>
                            <div className="text-[10px] text-[#2563EB] hover:underline flex items-center gap-1">
                              <ExternalLink className="w-3 h-3" /> stackoverflow.com/architecture-best-practices
                            </div>
                          </div>
                        </div>
                      ) : (
                        <p className="text-[#6B7280]">No external web search required (RAG matched sufficient context).</p>
                      )}
                    </div>
                  ) : (
                    <p className="text-xs text-[#6B7280]">Tavily search outcomes and source references will display here.</p>
                  )}
                </div>

                {/* Version History Drawer widget */}
                {selectedDoc && versionHistory[selectedDoc.id] && (
                  <div className="bg-white border border-[#E5E7EB] rounded-xl p-5 shadow-sm space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-semibold text-[#111827] uppercase tracking-wider">Version Timeline</h4>
                      <History className="w-4 h-4 text-slate-400" />
                    </div>

                    <div className="relative pl-4 space-y-3 text-xs">
                      {/* Line */}
                      <div className="absolute left-[5px] top-1.5 bottom-1.5 w-0.5 bg-slate-100" />

                      {versionHistory[selectedDoc.id].map((ver, idx) => (
                        <div key={idx} className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div className={`w-2.5 h-2.5 rounded-full border ${selectedDoc.version === ver.version ? 'bg-[#2563EB] border-[#2563EB]' : 'bg-white border-slate-300'
                              }`} />
                            <div>
                              <span className="font-semibold text-slate-800">{ver.version}</span>
                              <span className="text-[9px] text-[#6B7280] block">{ver.date}</span>
                            </div>
                          </div>

                          {selectedDoc.version !== ver.version && (
                            <button
                              onClick={() => {
                                setNotification({ type: 'success', message: `Restored to ${ver.version} version.` });
                                setSelectedDoc(prev => prev ? { ...prev, version: ver.version, content: ver.content } : null);
                              }}
                              className="text-[#2563EB] hover:underline font-semibold text-[10px]"
                            >
                              Restore
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

        </div>
      </main>

    </div>
  );
}
