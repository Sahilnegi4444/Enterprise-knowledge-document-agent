export interface ToolExecutionLog {
  tool_name: string;
  inputs: Record<string, any>;
  success: boolean;
  message: string;
}

export interface Section {
  heading: string;
  subheading?: string;
  paragraphs: string[];
  bullets: string[];
  tables: Array<{
    headers: string[];
    rows: string[][];
  }>;
  references: string[];
}

export interface StructuredDocument {
  title: string;
  metadata: Record<string, any>;
  sections: Section[];
}

export interface AgentResponse {
  success: boolean;
  goal: string;
  intent: string;
  assumptions: string[];
  tools_executed: ToolExecutionLog[];
  reflection_report: {
    passed: boolean;
    score: number;
    feedback: string;
    suggestions: string[];
  };
  docx_base64: string;
  document_data?: StructuredDocument;
  message: string;
}

export interface AgentRequest {
  request: string;
  metadata?: Record<string, any>;
}

// Live fetch to FastAPI backend with fallback to high-fidelity mock data if offline/error
export async function generateDocument(req: AgentRequest, useMock: boolean = false): Promise<AgentResponse> {
  if (useMock) {
    return getMockResponse(req.request);
  }

  try {
    const response = await fetch('/agent', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(req),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData?.detail?.message || `Server error: ${response.status}`);
    }

    return await response.json();
  } catch (error: any) {
    console.error('API Error:', error);
    throw new Error(error.message || 'API request failed.');
  }
}

// Generate rich mock response mimicking the actual LLM and tool registry output
function getMockResponse(prompt: string, errorContext?: string): Promise<AgentResponse> {
  return new Promise((resolve) => {
    setTimeout(() => {
      const isSOP = prompt.toLowerCase().includes('sop') || prompt.toLowerCase().includes('procedure');
      const isDesign = prompt.toLowerCase().includes('design') || prompt.toLowerCase().includes('architecture') || prompt.toLowerCase().includes('technical');
      const isPRD = prompt.toLowerCase().includes('prd') || prompt.toLowerCase().includes('requirement');
      
      let intent = 'Project Proposal';
      if (isSOP) intent = 'SOP';
      else if (isDesign) intent = 'Technical Design';
      else if (isPRD) intent = 'PRD';

      const mockDoc: StructuredDocument = {
        title: `${intent} for ${prompt.split('for').pop()?.trim() || 'Enterprise Initiative'}`,
        metadata: {
          Author: 'Enterprise AI Agent',
          Version: '1.0.0',
          Date: new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }),
          Classification: 'Confidential'
        },
        sections: [
          {
            heading: '1. Executive Summary',
            paragraphs: [
              `This document presents a comprehensive outline for the proposed initiative. The goal is to establish a robust framework that drives efficiency, security, and scalability across the organization.`,
              `Our proposed approach utilizes state-of-the-art technologies and methodologies to address current operational bottlenecks while establishing a solid foundation for future expansion.`
            ],
            bullets: [
              'Alignment with corporate strategic objectives',
              'Minimization of operational overhead and latency',
              'Enrichment of data assets and decision governance'
            ],
            tables: [],
            references: []
          },
          {
            heading: '2. Problem Statement & Scope',
            paragraphs: [
              `The current infrastructure suffers from fragmented workflows and manual synchronization processes. This leads to higher error rates, increased latency, and a lack of real-time visibility.`,
              `The scope of this project encompasses the design, development, and deployment of a centralized enterprise orchestration system, integrating existing data lakes and reporting layers.`
            ],
            bullets: [],
            tables: [
              {
                headers: ['Metric Affected', 'Current State', 'Target State', 'Business Impact'],
                rows: [
                  ['Manual Entry Overhead', '14.5 hours / week', '< 2 hours / week', '85% productivity gain'],
                  ['Data Reconciliation Delay', '24 - 48 hours', 'Real-time (< 5s)', 'Instantaneous decision making'],
                  ['Process Audit Compliance', 'Manual sample checks', '100% automated logging', 'Zero audit compliance risk']
                ]
              }
            ],
            references: ['ISO-27001 Security Standard Reference Guidelines', 'Section 4.2: Data Retention & Compliance Protocols']
          },
          {
            heading: '3. Technical Stack & Implementation Steps',
            paragraphs: [
              `The architecture is based on a modern service model, utilizing microservices for decoupled functionality and event streaming for high throughput communication.`
            ],
            bullets: [
              'Frontend Layer: React 19, TypeScript, Tailwind CSS v4, shadcn/ui components',
              'Backend Logic: FastAPI, Python 3.12, Uvicorn asynchronous server',
              'Agent Core: Dynamic Deterministic & LLM-routed planning models',
              'Storage & Search: ChromaDB Vector Store for local RAG, Tavily Search API'
            ],
            tables: [],
            references: []
          }
        ]
      };

      resolve({
        success: true,
        goal: `Synthesize a structured ${intent} addressing: ${prompt.substring(0, 80)}...`,
        intent: intent,
        assumptions: [
          'Enterprise guidelines require modular sections, tabular metrics, and detailed stack specs.',
          'RAG context provides the standard layout structure and corporate typography rules.',
          'External web search provides the latest industry standard benchmarks for compliance.'
        ],
        tools_executed: [
          {
            tool_name: 'rag_tool',
            inputs: { query: `${intent} standard formatting guidelines template` },
            success: true,
            message: 'Retrieved 3 vector document chunks with similarity score > 0.81.'
          },
          {
            tool_name: 'search_tool',
            inputs: { query: `latest industry best practices for ${intent}` },
            success: true,
            message: 'Web search completed. Extracted 4 authoritative industry sources.'
          },
          {
            tool_name: 'document_tool',
            inputs: { title: mockDoc.title },
            success: true,
            message: 'Word document compiled successfully in memory.'
          }
        ],
        reflection_report: {
          passed: true,
          score: 8.7,
          feedback: 'The document meets all structural requirements, contains rich tabular metrics, uses formal enterprise vocabulary, and has no placeholders.',
          suggestions: []
        },
        docx_base64: 'UEsDBBQAAAAIA...', // Mock base64 docx file header
        document_data: mockDoc,
        message: `Synthesized ${intent} successfully in 4.82s.${errorContext ? ` (Offline Fallback due to: ${errorContext})` : ''}`
      });
    }, 2500); // Simulate API latency
  });
}
