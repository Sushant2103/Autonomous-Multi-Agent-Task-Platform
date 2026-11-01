
import { useMemo, useState } from 'react';
import axios from 'axios';
import {
  Activity, Bot, CheckCircle2, Circle, Clock3, FileText,
  GitBranch, LayoutDashboard, Menu, Play, Search,
  Settings, ShieldCheck, Sparkles, Terminal, Workflow,
  Zap, AlertCircle, ArrowRight, Cpu, X, RefreshCw
} from 'lucide-react';
import {
  Background, Controls, MiniMap, ReactFlow, Handle,
  Position, type Node, type Edge
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

type Task = {
  task_id: number;
  description: string;
  assigned_agent: string;
  depends_on: number[];
};

type Result = {
  status?: string;
  final_response?: string;
  plan?: {
    goal: string;
    tasks: Task[];
  };
  results?: Array<{
    task_id: number;
    agent: string;
    status?: string;
    result: unknown;
  }>;
};

const agents = [
  { name: 'Planner Agent', role: 'Task decomposition', icon: GitBranch, color: '#8b9cff' },
  { name: 'Research Agent', role: 'Information discovery', icon: Search, color: '#54c8ef' },
  { name: 'Analysis Agent', role: 'Reasoning and insights', icon: Activity, color: '#b69aff' },
  { name: 'Execution Agent', role: 'Tool execution', icon: Zap, color: '#f4b65f' },
  { name: 'Verification Agent', role: 'Quality assurance', icon: ShieldCheck, color: '#65d6a0' },
];

function WorkflowNode({
  data
}: {
  data: { label: string; subtitle: string; color: string };
}) {
  return (
    <div className="workflow-node" style={{ borderColor: data.color }}>
      <Handle type="target" position={Position.Top} />
      <span className="node-dot" style={{ background: data.color }} />
      <strong>{data.label}</strong>
      <small>{data.subtitle}</small>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

const nodeTypes = { workflow: WorkflowNode };

export default function App() {
  const [request, setRequest] = useState('');
  const [busy, setBusy] = useState(false);
  const [data, setData] = useState<Result | null>(null);
  const [error, setError] = useState('');
  const [active, setActive] = useState('Overview');
  const [mobileMenu, setMobileMenu] = useState(false);

  const tasks = data?.plan?.tasks || [];

  const graph = useMemo(() => {
    const nodes: Node[] = [
      {
        id: 'start',
        type: 'workflow',
        position: { x: 230, y: 0 },
        data: {
          label: 'User Request',
          subtitle: 'Input received',
          color: '#65a9ff'
        }
      },
      {
        id: 'planner',
        type: 'workflow',
        position: { x: 230, y: 125 },
        data: {
          label: 'Planner Agent',
          subtitle: 'Break into subtasks',
          color: '#a99aff'
        }
      },
      ...tasks.map((task, i) => ({
        id: String(task.task_id),
        type: 'workflow',
        position: {
          x: (i % 2) * 300 + 80,
          y: 270 + Math.floor(i / 2) * 130
        },
        data: {
          label: `Task ${task.task_id}`,
          subtitle: task.assigned_agent.replace('_agent', ''),
          color: '#54c8ef'
        }
      })),
      {
        id: 'final',
        type: 'workflow',
        position: {
          x: 230,
          y: 480 + Math.ceil(tasks.length / 2) * 130
        },
        data: {
          label: 'Final Result',
          subtitle: 'Workflow output',
          color: '#65d6a0'
        }
      }
    ];

    const edges: Edge[] = [
      {
        id: 'e-start',
        source: 'start',
        target: 'planner',
        animated: true
      }
    ];

    tasks.forEach(task => {
      const target = String(task.task_id);

      edges.push({
        id: `e-planner-${target}`,
        source: 'planner',
        target,
        animated: true,
        style: { stroke: '#526d91' }
      });

      (task.depends_on || []).forEach(dep => {
        edges.push({
          id: `e-${dep}-${target}`,
          source: String(dep),
          target,
          animated: true,
          style: { stroke: '#a99aff' }
        });
      });
    });

    if (tasks.length) {
      tasks.forEach(task => {
        edges.push({
          id: `e-${task.task_id}-final`,
          source: String(task.task_id),
          target: 'final',
          style: { stroke: '#65d6a0' }
        });
      });
    } else {
      edges.push({
        id: 'e-final',
        source: 'planner',
        target: 'final'
      });
    }

    return { nodes, edges };
  }, [tasks]);

  async function submit() {
    if (!request.trim() || busy) return;

    setBusy(true);
    setError('');
    setData(null);

    try {
      // Correct backend endpoint: POST /api/execute
      const response = await axios.post<Result>(
        `${API}/execute`,
        {
          user_id: 1,
          user_request: request.trim()
        },
        {
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 300000
        }
      );

      setData(response.data);
      setActive('Workflow');
    } catch (e: unknown) {
      console.error('Workflow execution error:', e);

      if (axios.isAxiosError(e)) {
        const detail = e.response?.data?.detail;

        if (Array.isArray(detail)) {
          setError(
            detail.map((item: { msg?: string }) => item.msg || 'Validation error').join(', ')
          );
        } else if (typeof detail === 'string') {
          setError(detail);
        } else if (e.code === 'ECONNABORTED') {
          setError('The workflow took too long. Check the backend terminal for its status.');
        } else if (!e.response) {
          setError('Cannot connect to the backend. Check that FastAPI is running at http://127.0.0.1:8000.');
        } else {
          setError(`Backend error (${e.response.status}): ${e.message}`);
        }
      } else {
        setError('Something went wrong while executing the workflow.');
      }
    } finally {
      setBusy(false);
    }
  }

  function clearWorkflow() {
    if (busy) return;
    setRequest('');
    setData(null);
    setError('');
    setActive('Overview');
  }

  const navigation = [
    { label: 'Overview', icon: LayoutDashboard },
    { label: 'Workflow', icon: Workflow },
    { label: 'AI Agents', icon: Bot },
    { label: 'Execution Logs', icon: Terminal },
    { label: 'Reports', icon: FileText },
  ];

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileMenu ? 'sidebar-open' : ''}`}>
        <div className="brand">
          <div className="brand-icon">
            <Bot size={23} />
          </div>
          <div>
            <strong>AgentFlow</strong>
            <span>INTELLIGENT AUTOMATION</span>
          </div>
          <button
            className="mobile-close"
            onClick={() => setMobileMenu(false)}
            aria-label="Close menu"
          >
            <X size={18} />
          </button>
        </div>

        <div className="workspace-label">WORKSPACE</div>

        <div className="workspace">
          <div className="workspace-avatar">M</div>
          <div>
            <strong>Mega Project</strong>
            <span>Development workspace</span>
          </div>
        </div>

        <div className="nav-label">PLATFORM</div>

        <nav>
          {navigation.map(item => (
            <button
              key={item.label}
              className={`nav-item ${active === item.label ? 'active' : ''}`}
              onClick={() => {
                setActive(item.label);
                setMobileMenu(false);
              }}
            >
              <item.icon size={18} />
              <span>{item.label}</span>
              {item.label === 'Workflow' && data && (
                <span className="nav-count">{tasks.length}</span>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="online-dot" />
            <span>System interface ready</span>
          </div>

          <button className="nav-item">
            <Settings size={18} />
            <span>Settings</span>
          </button>

          <div className="profile">
            <div className="profile-avatar">T</div>
            <div>
              <strong>Project Team</strong>
              <span>Administrator</span>
            </div>
            <Settings size={16} />
          </div>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="menu-button"
              onClick={() => setMobileMenu(true)}
              aria-label="Open menu"
            >
              <Menu />
            </button>

            <div>
              <span className="breadcrumb">Workspace /</span>{' '}
              <strong>{active}</strong>
            </div>
          </div>

          <div className="topbar-right">
            <span className="environment">
              <span className="online-dot" />
              LOCAL ENVIRONMENT
            </span>
            <div className="top-avatar">T</div>
          </div>
        </header>

        <div className="content">
          <div className="page-heading">
            <div>
              <div className="eyebrow">
                <Sparkles size={14} />
                AUTONOMOUS MULTI-AGENT PLATFORM
              </div>

              <h1>
                {active === 'Overview' ? 'Command Center' : active}
              </h1>

              <p>
                Plan, coordinate and monitor intelligent AI agents from one workspace.
              </p>
            </div>

            <div className="version-tag">
              <span className="online-dot" />
              PLATFORM V2.0
            </div>
          </div>

          <section className="stats-grid">
            <div className="stat-card">
              <div className="stat-top">
                <span>Total Tasks</span>
                <div className="stat-icon blue"><GitBranch /></div>
              </div>
              <strong>{data ? tasks.length : '—'}</strong>
              <small>{data ? 'Tasks in latest plan' : 'Awaiting first workflow'}</small>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <span>AI Agents</span>
                <div className="stat-icon purple"><Bot /></div>
              </div>
              <strong>05</strong>
              <small>Specialist agent roles</small>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <span>Execution Results</span>
                <div className="stat-icon green"><CheckCircle2 /></div>
              </div>
              <strong>{data?.results?.length ?? '—'}</strong>
              <small>{data ? 'Returned execution results' : 'No execution yet'}</small>
            </div>

            <div className="stat-card">
              <div className="stat-top">
                <span>Platform</span>
                <div className="stat-icon orange"><Cpu /></div>
              </div>
              <strong className="status-word">Ready</strong>
              <small>Local development mode</small>
            </div>
          </section>

          <section className="section-block">
            <div className="section-heading">
              <div>
                <h2>Start a new workflow</h2>
                <p>Describe your goal and let the planner organize the work.</p>
              </div>
              <span className="section-tag">
                <Zap size={13} /> AI POWERED
              </span>
            </div>

            <div className="composer">
              <div className="composer-label">
                <span className="composer-dot" />
                TASK INSTRUCTION
              </div>

              <textarea
                value={request}
                onChange={e => setRequest(e.target.value)}
                placeholder="Example: Research electric vehicles in India, compare leading technologies, analyze market opportunities and prepare a structured report..."
                disabled={busy}
              />

              <div className="composer-footer">
                <span>
                  <ShieldCheck size={15} />
                  Review agent output before external actions.
                </span>

                <div style={{ display: 'flex', gap: '10px' }}>
                  {data && (
                    <button
                      className="run-button"
                      onClick={clearWorkflow}
                      disabled={busy}
                    >
                      <RefreshCw size={15} /> New task
                    </button>
                  )}

                  <button
                    className="run-button"
                    onClick={submit}
                    disabled={busy || !request.trim()}
                  >
                    {busy ? (
                      <>
                        <Activity size={17} className="spin" />
                        Running...
                      </>
                    ) : (
                      <>
                        <Play size={16} fill="currentColor" />
                        Run workflow
                        <ArrowRight size={16} />
                      </>
                    )}
                  </button>
                </div>
              </div>

              {busy && (
                <div className="system-status" style={{ marginTop: '14px' }}>
                  <span className="online-dot" />
                  Sending your request to the AgentFlow backend. This may take a while.
                </div>
              )}

              {error && (
                <div className="error-message">
                  <AlertCircle size={16} />
                  {error}
                </div>
              )}
            </div>
          </section>

          <section className="section-block">
            <div className="section-heading">
              <div>
                <h2>Specialist AI agents</h2>
                <p>Collaborative roles in the task execution pipeline.</p>
              </div>
              <span className="muted-tag">5 AGENT TYPES</span>
            </div>

            <div className="agents-grid">
              {agents.map(agent => (
                <div className="agent-card" key={agent.name}>
                  <div
                    className="agent-icon"
                    style={{
                      color: agent.color,
                      background: `${agent.color}18`
                    }}
                  >
                    <agent.icon size={20} />
                  </div>

                  <div className="agent-info">
                    <strong>{agent.name}</strong>
                    <span>{agent.role}</span>
                  </div>

                  <span className="agent-indicator" title="Available" />
                </div>
              ))}
            </div>
          </section>

          <section className="section-block">
            <div className="section-heading">
              <div>
                <h2>Workflow visualization</h2>
                <p>
                  {data
                    ? 'Task plan returned by the backend.'
                    : 'Illustrative pipeline — submit a task to display its generated plan.'}
                </p>
              </div>

              <span className="muted-tag">
                <GitBranch size={13} /> TASK GRAPH
              </span>
            </div>

            <div className="graph-panel">
              {data && tasks.length ? (
                <div className="flow-container">
                  <ReactFlow
                    nodes={graph.nodes}
                    edges={graph.edges}
                    nodeTypes={nodeTypes}
                    fitView
                    fitViewOptions={{ padding: 0.2 }}
                    minZoom={0.3}
                    maxZoom={1.5}
                  >
                    <Background color="#27364a" gap={22} />
                    <Controls />
                    <MiniMap
                      nodeColor={node => String(node.data.color || '#526d91')}
                      maskColor="#0b1220bb"
                    />
                  </ReactFlow>
                </div>
              ) : (
                <div className="pipeline-preview">
                  <div className="pipeline-node">
                    <div className="pipeline-icon blue"><Circle size={18} /></div>
                    <strong>User Request</strong>
                    <span>Task input</span>
                  </div>

                  <div className="pipeline-arrow"><ArrowRight /></div>

                  <div className="pipeline-node">
                    <div className="pipeline-icon purple"><GitBranch size={18} /></div>
                    <strong>Planner</strong>
                    <span>Task breakdown</span>
                  </div>

                  <div className="pipeline-arrow"><ArrowRight /></div>

                  <div className="pipeline-node">
                    <div className="pipeline-icon cyan"><Bot size={18} /></div>
                    <strong>Specialist Agents</strong>
                    <span>Collaborative work</span>
                  </div>

                  <div className="pipeline-arrow"><ArrowRight /></div>

                  <div className="pipeline-node">
                    <div className="pipeline-icon green"><CheckCircle2 size={18} /></div>
                    <strong>Final Result</strong>
                    <span>Workflow output</span>
                  </div>
                </div>
              )}
            </div>
          </section>

          {data && (
            <section className="section-block">
              <div className="section-heading">
                <div>
                  <h2>Execution results</h2>
                  <p>Output returned by the task execution API.</p>
                </div>

                <span className="section-tag">
                  <CheckCircle2 size={13} /> RESPONSE RECEIVED
                </span>
              </div>

              <div className="result-panel">
                <div className="result-header">
                  <div>
                    <FileText size={18} />
                    <strong>Final response</strong>
                  </div>
                  <span className="muted-tag">
                    {data.status || 'Response received'}
                  </span>
                </div>

                <div className="result-content">
                  {data.final_response ||
                    'The backend returned a response. Inspect the execution details below.'}
                </div>

                {data.plan && (
                  <details className="execution-details">
                    <summary>
                      <GitBranch size={15} /> Generated task plan ({tasks.length} tasks)
                    </summary>
                    <pre>{JSON.stringify(data.plan, null, 2)}</pre>
                  </details>
                )}

                {data.results && (
                  <details className="execution-details">
                    <summary>
                      <Terminal size={15} /> Execution details ({data.results.length} results)
                    </summary>
                    <pre>{JSON.stringify(data.results, null, 2)}</pre>
                  </details>
                )}
              </div>
            </section>
          )}

          <footer className="footer">
            <span>AgentFlow <b>·</b> Autonomous Multi-Agent Task Platform</span>
            <span><Clock3 size={13} /> Development prototype</span>
          </footer>
        </div>
      </main>
    </div>
  );
}
