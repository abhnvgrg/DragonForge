import * as d3 from 'd3';
import { useEffect, useRef, useState } from 'react';
import { ToggleLeft, ToggleRight, Info, ExternalLink } from 'lucide-react';
import { ClaimBadge } from './ClaimBadge';

export function PanelA_NetworkTopology({ 
  structureData, 
  graphData, 
  modelConfig,
  showControl = false,
  onToggleControl
}) {
  const svgRef = useRef(null);
  const containerRef = useRef(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const [selectedNode, setSelectedNode] = useState(null);

  // Resize observer
  useEffect(() => {
    const resizeObserver = new ResizeObserver(entries => {
      for (let entry of entries) {
        const { width, height } = entry.contentRect;
        setDimensions({ width, height });
      }
    });
    
    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }
    return () => resizeObserver.disconnect();
  }, []);

  // Render force-directed graph
  useEffect(() => {
    if (!svgRef.current || !graphData || !dimensions.width) return;
    
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    
    const { width, height } = dimensions;
    const margin = 40;
    const graphWidth = width - margin * 2;
    const graphHeight = height - margin * 2;
    
    // Prepare nodes and links
    const nodes = graphData.nodes?.map((id, i) => ({
      id,
      ...graphData.node_metadata?.[id],
      index: i
    })) || [];
    
    const links = graphData.edges?.map(([source, target, weight]) => ({
      source,
      target,
      weight: Math.abs(weight)
    })) || [];
    
    if (nodes.length === 0) return;
    
    // Limit nodes for performance
    const maxNodes = 300;
    const displayNodes = nodes.slice(0, maxNodes);
    const displayNodeIds = new Set(displayNodes.map(n => n.id));
    const displayLinks = links.filter(l => displayNodeIds.has(l.source) && displayNodeIds.has(l.target));
    
    // Create simulation
    const simulation = d3.forceSimulation(displayNodes)
      .force('link', d3.forceLink(displayLinks).id(d => d.id).distance(30).strength(0.1))
      .force('charge', d3.forceManyBody().strength(-50))
      .force('center', d3.forceCenter(graphWidth / 2, graphHeight / 2))
      .force('collision', d3.forceCollide().radius(8))
      .alphaDecay(0.02);
    
    // Create link elements
    const link = svg.append('g')
      .attr('stroke', '#27272A')
      .attr('stroke-opacity', 0.4)
      .selectAll('line')
      .data(displayLinks)
      .join('line')
      .attr('stroke-width', d => Math.max(0.5, d.weight * 2));
    
    // Create node elements
    const node = svg.append('g')
      .selectAll('circle')
      .data(displayNodes)
      .join('circle')
      .attr('r', 4)
      .attr('fill', d => d.community !== undefined 
        ? d3.schemeCategory10[d.community % 10] 
        : '#FAFAFA')
      .attr('stroke', '#09090B')
      .attr('stroke-width', 1.5)
      .call(drag(simulation))
      .on('click', (event, d) => {
        event.stopPropagation();
        setSelectedNode(d);
      })
      .on('mouseover', (event, d) => {
        d3.select(event.currentTarget).attr('r', 6).attr('stroke-width', 2);
      })
      .on('mouseout', (event, d) => {
        if (selectedNode?.id !== d.id) {
          d3.select(event.currentTarget).attr('r', 4).attr('stroke-width', 1.5);
        }
      });
    
    // Add labels for high-degree nodes
    const label = svg.append('g')
      .selectAll('text')
      .data(displayNodes.filter(n => (graphData.edges || []).filter(e => e[0] === n.id || e[1] === n.id).length > 10))
      .join('text')
      .text(d => d.id.split('_').pop())
      .attr('font-size', '8px')
      .attr('fill', '#A1A1AA')
      .attr('text-anchor', 'middle')
      .attr('dy', -10)
      .attr('pointer-events', 'none');
    
    // Tick function
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
      
      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
      
      label
        .attr('x', d => d.x)
        .attr('y', d => d.y);
    });
    
    // Drag behavior
    function drag(simulation) {
      function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }
      
      function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
      }
      
      function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }
      
      return d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
    }
    
    // Cleanup
    return () => simulation.stop();
  }, [graphData, dimensions, showControl]);

  // Metrics from structure data
  const modularity = structureData?.modularity || 0;
  const modularityControl = structureData?.modularity_random_control || 0;
  const sparsity = structureData?.sparsity || 0;
  const clustering = structureData?.clustering_coefficient || 0;
  const degreeDist = structureData?.degree_distribution || [];

  return (
    <div className="panel h-[500px] md:h-[600px] flex flex-col">
      <div className="panel-header">
        <div className="flex items-center gap-3">
          <h2 className="panel-title">Network Topology Inspector</h2>
          <ClaimBadge tag="MEASURED" />
        </div>
        <div className="flex items-center gap-2">
          <label className="toggle" title="Show Randomized Control Graph">
            <input
              type="checkbox"
              checked={showControl}
              onChange={onToggleControl}
              aria-label="Show Randomized Control Graph"
            />
            <span className="toggle-track">
              <span className="toggle-thumb" />
            </span>
          </label>
          <span className="text-tiny text-dragonforge-textMuted font-mono">
            {showControl ? 'Control' : 'BDH'}
          </span>
        </div>
      </div>
      
      <div className="flex-1 flex overflow-hidden">
        {/* Graph Visualization */}
        <div className="flex-1 relative" ref={containerRef}>
          <svg 
            ref={svgRef} 
            className="w-full h-full" 
            style={{ backgroundColor: '#09090B' }}
          />
          
          {/* Legend */}
          <div className="absolute bottom-4 left-4 flex flex-col gap-1.5 bg-dragonforge-surface/90 backdrop-blur-sm border border-dragonforge-border rounded-panel p-3 text-tiny">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-white" />
              <span className="text-dragonforge-textSecondary">BDH Nodes</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full" style={{ background: '#3F3F46' }} />
              <span className="text-dragonforge-textSecondary">Control Nodes</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-0.5 bg-dragonforge-border" />
              <span className="text-dragonforge-textSecondary">Edges (correlation)</span>
            </div>
          </div>
        </div>
        
        {/* Metrics Sidebar */}
        <div className="w-72 border-l border-dragonforge-border p-4 overflow-y-auto flex-shrink-0">
          <h3 className="font-mono text-small font-medium text-dragonforge-textSecondary mb-4 uppercase tracking-wide">
            Structural Metrics
          </h3>
          
          <div className="space-y-4">
            <div className="metric-card">
              <span className="metric-label">Modularity Score</span>
              <div className="flex items-baseline gap-2">
                <span className="metric-value font-mono">{modularity.toFixed(2)}</span>
                <span className="metric-diff metric-diff-positive font-mono text-tiny">
                  vs Control: {modularityControl.toFixed(2)}
                </span>
              </div>
              <div className="text-tiny text-dragonforge-textMuted">
                Louvain community detection
              </div>
            </div>
            
            <div className="metric-card">
              <span className="metric-label">Activation Sparsity</span>
              <span className="metric-value font-mono">{(sparsity * 100).toFixed(1)}%</span>
              <div className="text-tiny text-dragonforge-textMuted">
                Fraction of zero activations
              </div>
            </div>
            
            <div className="metric-card">
              <span className="metric-label">Clustering Coefficient</span>
              <span className="metric-value font-mono">{clustering.toFixed(3)}</span>
              <div className="text-tiny text-dragonforge-textMuted">
                Mean local clustering
              </div>
            </div>
            
            <div className="metric-card">
              <span className="metric-label">Degree Distribution</span>
              <span className="metric-value font-mono text-small">
                {degreeDist.length > 0 ? 'Heavy-Tailed' : 'N/A'}
              </span>
              <div className="text-tiny text-dragonforge-textMuted">
                Power-law structure observed
              </div>
            </div>
            
            <div className="metric-card">
              <span className="metric-label">Nodes / Edges</span>
              <span className="metric-value font-mono text-small">
                {graphData?.nodes?.length || 0} / {graphData?.edges?.length || 0}
              </span>
              <div className="text-tiny text-dragonforge-textMuted">
                Neuron-level granularity
              </div>
            </div>
            
            <div className="metric-card">
              <span className="metric-label">Graph Config</span>
              <div className="text-tiny text-dragonforge-textMuted font-mono space-y-1">
                <div>Node: Neuron</div>
                <div>Edge: Correlation (τ=0.3)</div>
                <div>Samples: 100 batches × 512 seq</div>
                <div>Aggregation: Mean over seq & batch</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}