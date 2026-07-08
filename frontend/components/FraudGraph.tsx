'use client'

import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import { GraphNode, GraphEdge } from '@/lib/api'

interface Props {
  nodes: GraphNode[]
  edges: GraphEdge[]
  width?: number
  height?: number
}

const TYPE_COLORS: Record<string, string> = {
  report: '#B23A3A',
  phone: '#C9A34E',
  device: '#1E3A5F',
  account: '#0B1F3A',
  upi: '#7A8B99',
}

export default function FraudGraph({ nodes, edges, width = 760, height = 480 }: Props) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove()

    type SimNode = GraphNode & d3.SimulationNodeDatum
    type SimLink = { source: string; target: string; relation: string }

    const simNodes: SimNode[] = nodes.map((n) => ({ ...n }))
    const simLinks: SimLink[] = edges.map((e) => ({ ...e }))

    const simulation = d3
      .forceSimulation(simNodes)
      .force(
        'link',
        d3
          .forceLink<SimNode, d3.SimulationLinkDatum<SimNode>>(simLinks as any)
          .id((d: any) => d.id)
          .distance(70)
      )
      .force('charge', d3.forceManyBody().strength(-180))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(24))

    const link = svg
      .append('g')
      .attr('stroke', '#0B1F3A')
      .attr('stroke-opacity', 0.15)
      .selectAll('line')
      .data(simLinks)
      .join('line')
      .attr('stroke-width', 1.2)

    const node = svg
      .append('g')
      .selectAll('circle')
      .data(simNodes)
      .join('circle')
      .attr('r', (d) => (d.type === 'report' ? 9 : 6))
      .attr('fill', (d) => TYPE_COLORS[d.type] ?? '#7A8B99')
      .attr('stroke', '#F7F5F0')
      .attr('stroke-width', 1.5)
      .call(
        d3
          .drag<SVGCircleElement, SimNode>()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart()
            d.fx = d.x
            d.fy = d.y
          })
          .on('drag', (event, d) => {
            d.fx = event.x
            d.fy = event.y
          })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0)
            d.fx = null
            d.fy = null
          }) as any
      )

    node.append('title').text((d) => d.label)

    const label = svg
      .append('g')
      .selectAll('text')
      .data(simNodes)
      .join('text')
      .text((d) => d.label)
      .attr('font-size', 9.5)
      .attr('font-family', 'var(--font-inter), sans-serif')
      .attr('fill', '#1A1F2B')
      .attr('dx', 10)
      .attr('dy', 3)
      .attr('opacity', 0.75)

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      node.attr('cx', (d) => d.x ?? 0).attr('cy', (d) => d.y ?? 0)
      label.attr('x', (d) => d.x ?? 0).attr('y', (d) => d.y ?? 0)
    })

    return () => {
      simulation.stop()
    }
  }, [nodes, edges, width, height])

  return (
    <svg
      ref={svgRef}
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className="w-full h-auto"
    />
  )
}
