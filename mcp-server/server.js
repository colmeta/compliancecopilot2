#!/usr/bin/env node

/**
 * CLARITY ENGINE MCP SERVER
 * Model Context Protocol server for AI assistant integration
 * Allows Claude Desktop, Cursor, and other AI tools to access CLARITY engine
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import fetch from "node-fetch";

// Configuration
const CLARITY_API_BASE = process.env.CLARITY_API_URL || "https://veritas-engine-zae0.onrender.com";
const API_KEY = process.env.CLARITY_API_KEY || "";

/**
 * Make API request to CLARITY engine
 */
async function callClarityAPI(endpoint, method = "GET", data = null) {
  const url = `${CLARITY_API_BASE}${endpoint}`;
  const options = {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(API_KEY && { "X-API-KEY": API_KEY }),
    },
  };

  if (data && method !== "GET") {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(url, options);
  
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`CLARITY API error (${response.status}): ${errorText}`);
  }

  return await response.json();
}

/**
 * Initialize MCP server
 */
const server = new Server(
  {
    name: "clarity-engine",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/**
 * List available tools
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      // Legal Intelligence
      {
        name: "analyze_legal",
        description: "Analyze legal documents for compliance, risks, liability clauses, and contract issues. Returns detailed legal intelligence analysis.",
        inputSchema: {
          type: "object",
          properties: {
            directive: {
              type: "string",
              description: "What to analyze (e.g., 'Find liability clauses', 'Review for compliance')",
            },
            document_content: {
              type: "string",
              description: "The legal document text to analyze",
            },
          },
          required: ["directive", "document_content"],
        },
      },
      
      // Financial Intelligence
      {
        name: "analyze_financial",
        description: "Analyze financial documents, statements, budgets for anomalies, trends, and risks. Professional financial intelligence.",
        inputSchema: {
          type: "object",
          properties: {
            directive: {
              type: "string",
              description: "What to analyze (e.g., 'Find anomalies', 'Analyze spending patterns')",
            },
            document_content: {
              type: "string",
              description: "Financial document or data to analyze",
            },
          },
          required: ["directive", "document_content"],
        },
      },
      
      // Security Intelligence
      {
        name: "analyze_security",
        description: "Audit security policies, SOC2 compliance, vulnerability assessment, and security posture analysis.",
        inputSchema: {
          type: "object",
          properties: {
            directive: {
              type: "string",
              description: "What to analyze (e.g., 'SOC2 audit', 'Security vulnerabilities')",
            },
            document_content: {
              type: "string",
              description: "Security policies or system documentation",
            },
          },
          required: ["directive", "document_content"],
        },
      },
      
      // Healthcare Intelligence
      {
        name: "analyze_healthcare",
        description: "HIPAA compliance review, patient data analysis, clinical protocol assessment for healthcare documents.",
        inputSchema: {
          type: "object",
          properties: {
            directive: {
              type: "string",
              description: "What to analyze (e.g., 'HIPAA compliance', 'Clinical protocol review')",
            },
            document_content: {
              type: "string",
              description: "Healthcare documents or records",
            },
          },
          required: ["directive", "document_content"],
        },
      },
      
      // Data Science Engine
      {
        name: "analyze_data",
        description: "Statistical analysis, predictive modeling, data insights, and trend analysis on datasets.",
        inputSchema: {
          type: "object",
          properties: {
            directive: {
              type: "string",
              description: "What to analyze (e.g., 'Find trends', 'Predictive analysis')",
            },
            document_content: {
              type: "string",
              description: "Dataset or data file content",
            },
          },
          required: ["directive", "document_content"],
        },
      },
      
      // Proposal Intelligence
      {
        name: "analyze_proposal",
        description: "RFP response optimization, bid analysis, compliance checking, and proposal strategy.",
        inputSchema: {
          type: "object",
          properties: {
            directive: {
              type: "string",
              description: "What to analyze (e.g., 'Optimize RFP response', 'Check compliance')",
            },
            document_content: {
              type: "string",
              description: "RFP or proposal document",
            },
          },
          required: ["directive", "document_content"],
        },
      },
      
      // NGO & Impact
      {
        name: "analyze_ngo",
        description: "Grant writing assistance, impact assessment, donor reporting, and NGO program analysis.",
        inputSchema: {
          type: "object",
          properties: {
            directive: {
              type: "string",
              description: "What to do (e.g., 'Write grant proposal', 'Assess program impact')",
            },
            document_content: {
              type: "string",
              description: "Program details or grant requirements",
            },
          },
          required: ["directive", "document_content"],
        },
      },
      
      // Expense Management
      {
        name: "analyze_expenses",
        description: "Analyze expenses, find savings opportunities, categorize spending, and optimize costs.",
        inputSchema: {
          type: "object",
          properties: {
            directive: {
              type: "string",
              description: "What to analyze (e.g., 'Find savings', 'Categorize expenses')",
            },
            document_content: {
              type: "string",
              description: "Expense data or financial records",
            },
          },
          required: ["directive", "document_content"],
        },
      },
      
      // Get Available Domains
      {
        name: "list_domains",
        description: "List all available CLARITY intelligence domains with descriptions and capabilities.",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      
      // Generate Funding Documents
      {
        name: "generate_funding_documents",
        description: "Generate complete funding document package (business plan, pitch deck, financial projections) for startups and NGOs.",
        inputSchema: {
          type: "object",
          properties: {
            company_name: {
              type: "string",
              description: "Company or organization name",
            },
            description: {
              type: "string",
              description: "Brief description of the business/project",
            },
            industry: {
              type: "string",
              description: "Industry or sector",
            },
            funding_goal: {
              type: "string",
              description: "Funding amount sought (e.g., '$500K seed round')",
            },
          },
          required: ["company_name", "description"],
        },
      },
      
      // Health Check
      {
        name: "check_health",
        description: "Check CLARITY engine health status and availability.",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
    ],
  };
});

/**
 * Handle tool execution
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "analyze_legal":
        return await handleAnalysis("legal", args);
      
      case "analyze_financial":
        return await handleAnalysis("financial", args);
      
      case "analyze_security":
        return await handleAnalysis("security", args);
      
      case "analyze_healthcare":
        return await handleAnalysis("healthcare", args);
      
      case "analyze_data":
        return await handleAnalysis("data-science", args);
      
      case "analyze_proposal":
        return await handleAnalysis("proposals", args);
      
      case "analyze_ngo":
        return await handleAnalysis("ngo", args);
      
      case "analyze_expenses":
        return await handleAnalysis("expenses", args);
      
      case "list_domains":
        return await handleListDomains();
      
      case "generate_funding_documents":
        return await handleFundingGeneration(args);
      
      case "check_health":
        return await handleHealthCheck();
      
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

/**
 * Handle analysis requests
 */
async function handleAnalysis(domain, args) {
  const { directive, document_content } = args;

  const result = await callClarityAPI("/real/analyze", "POST", {
    directive,
    domain,
    document_content,
  });

  // Format response for MCP
  const analysis = result.analysis || {};
  const summary = analysis.summary || result.summary || "Analysis complete";
  const findings = analysis.findings || result.findings || [];
  const recommendations = analysis.recommendations || result.recommendations || [];
  
  let responseText = `# ${domain.toUpperCase()} INTELLIGENCE ANALYSIS\n\n`;
  responseText += `**Directive:** ${directive}\n\n`;
  responseText += `## Summary\n${summary}\n\n`;
  
  if (findings.length > 0) {
    responseText += `## Key Findings\n`;
    findings.forEach((finding, idx) => {
      responseText += `${idx + 1}. ${finding}\n`;
    });
    responseText += `\n`;
  }
  
  if (recommendations.length > 0) {
    responseText += `## Recommendations\n`;
    recommendations.forEach((rec, idx) => {
      responseText += `${idx + 1}. ${rec}\n`;
    });
  }
  
  if (analysis.confidence) {
    responseText += `\n**Confidence:** ${(analysis.confidence * 100).toFixed(0)}%\n`;
  }

  return {
    content: [
      {
        type: "text",
        text: responseText,
      },
    ],
  };
}

/**
 * Handle list domains request
 */
async function handleListDomains() {
  const result = await callClarityAPI("/real/domains", "GET");
  
  let responseText = `# CLARITY ENGINE - AVAILABLE DOMAINS\n\n`;
  responseText += `**Total Domains:** ${result.total}\n`;
  responseText += `**AI Status:** ${result.ai_engine_status}\n\n`;
  
  result.domains.forEach((domain) => {
    responseText += `## ${domain.name}\n`;
    responseText += `**ID:** \`${domain.id}\`\n`;
    responseText += `**Description:** ${domain.description}\n`;
    responseText += `**Example:** "${domain.example}"\n`;
    responseText += `**AI-Powered:** ${domain.ai_powered ? "✅ Yes" : "❌ No"}\n\n`;
  });

  return {
    content: [
      {
        type: "text",
        text: responseText,
      },
    ],
  };
}

/**
 * Handle funding document generation
 */
async function handleFundingGeneration(args) {
  const { company_name, description, industry, funding_goal } = args;

  const result = await callClarityAPI("/real/funding/generate", "POST", {
    company_name,
    description,
    industry: industry || "Technology",
    funding_goal: funding_goal || "$500K seed",
  });

  let responseText = `# FUNDING DOCUMENTS GENERATED\n\n`;
  responseText += `**Company:** ${company_name}\n`;
  responseText += `**Status:** ${result.status || "Processing"}\n\n`;
  
  if (result.task_id) {
    responseText += `**Task ID:** ${result.task_id}\n`;
    responseText += `Documents are being generated. Check back in 5-10 minutes.\n\n`;
  }
  
  if (result.documents) {
    responseText += `## Generated Documents:\n`;
    result.documents.forEach((doc) => {
      responseText += `- ${doc.name} (${doc.pages} pages)\n`;
    });
  }

  return {
    content: [
      {
        type: "text",
        text: responseText,
      },
    ],
  };
}

/**
 * Handle health check
 */
async function handleHealthCheck() {
  const result = await callClarityAPI("/real/health", "GET");
  
  let responseText = `# CLARITY ENGINE STATUS\n\n`;
  responseText += `**Service:** ${result.service}\n`;
  responseText += `**Status:** ${result.status}\n`;
  responseText += `**Ready:** ${result.ready ? "✅ Yes" : "❌ No"}\n`;
  responseText += `**AI Model:** ${result.model}\n`;
  responseText += `**API Key Set:** ${result.api_key_set ? "✅ Yes" : "❌ No"}\n`;

  return {
    content: [
      {
        type: "text",
        text: responseText,
      },
    ],
  };
}

/**
 * Start the server
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("CLARITY Engine MCP server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
