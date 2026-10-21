ARCHITECTURE_ANIMATION_JS = r'''
    function architectureClamp(value, minimum, maximum) {
        return Math.max(minimum, Math.min(maximum, value));
    }

    function architectureEase(value) {
        const t = architectureClamp(value, 0, 1);
        return t * t * (3 - 2 * t);
    }

    function architectureActionProgress(graph, targetId, action, time) {
        const events = (graph.actions || []).filter(item => item.target_id === targetId && item.action === action);
        if (!events.length) return action === "reveal_node" || action === "draw_edge" ? 1 : 0;
        return Math.max(...events.map(item => {
            const duration = Math.max(0.001, Number(item.duration) || 0.001);
            return architectureClamp((time - Number(item.start || 0)) / duration, 0, 1);
        }));
    }

    function architectureActionIsActive(graph, targetId, action, time) {
        return (graph.actions || []).some(item => item.target_id === targetId && item.action === action
            && time >= Number(item.start || 0) && time <= Number(item.end || item.start || 0));
    }

    function architectureNodeSize(node, width, height, count) {
        const columns = Math.max(1, Number(node.column_count) || 1);
        const boxWidth = Math.min(width * 0.88, width * 0.88 / columns);
        const rowCount = Math.max(1, Math.ceil(count / columns));
        const boxHeight = Math.min(150, Math.max(104, height * 0.62 / rowCount * 0.56));
        return { width: boxWidth, height: boxHeight };
    }

    function architecturePoint(node, width, height, nodes) {
        const size = architectureNodeSize(node, width, height, nodes.length);
        return { x: Number(node.x || 0.5) * width, y: Number(node.y || 0.5) * height, ...size };
    }

    function architectureConnectorPoints(edge, source, target) {
        const vertical = Math.abs(target.y - source.y) >= Math.abs(target.x - source.x);
        let start, end;
        if (vertical) {
            start = { x: source.x, y: source.y + (target.y >= source.y ? source.height / 2 : -source.height / 2) };
            end = { x: target.x, y: target.y - (target.y >= source.y ? target.height / 2 : -target.height / 2) };
        } else {
            start = { x: source.x + (target.x >= source.x ? source.width / 2 : -source.width / 2), y: source.y };
            end = { x: target.x - (target.x >= source.x ? target.width / 2 : -target.width / 2), y: target.y };
        }
        const style = edge.style || "bezier";
        if (style === "straight") return [start, end];
        if (style === "elbow") {
            if (vertical) {
                const bendY = (start.y + end.y) / 2;
                return [start, { x: start.x, y: bendY }, { x: end.x, y: bendY }, end];
            }
            const bendX = (start.x + end.x) / 2;
            return [start, { x: bendX, y: start.y }, { x: bendX, y: end.y }, end];
        }
        const samples = [];
        const dx = end.x - start.x;
        const dy = end.y - start.y;
        if (style === "curved") {
            const control = vertical
                ? { x: (start.x + end.x) / 2 + Math.min(90, Math.abs(dx) * 0.25), y: (start.y + end.y) / 2 }
                : { x: (start.x + end.x) / 2, y: (start.y + end.y) / 2 + Math.min(90, Math.abs(dy) * 0.25) };
            for (let i = 0; i <= 24; i++) {
                const t = i / 24, u = 1 - t;
                samples.push({ x: u * u * start.x + 2 * u * t * control.x + t * t * end.x, y: u * u * start.y + 2 * u * t * control.y + t * t * end.y });
            }
            return samples;
        }
        const c1 = vertical ? { x: start.x, y: start.y + dy * 0.48 } : { x: start.x + dx * 0.48, y: start.y };
        const c2 = vertical ? { x: end.x, y: end.y - dy * 0.48 } : { x: end.x - dx * 0.48, y: end.y };
        for (let i = 0; i <= 28; i++) {
            const t = i / 28, u = 1 - t;
            samples.push({
                x: u * u * u * start.x + 3 * u * u * t * c1.x + 3 * u * t * t * c2.x + t * t * t * end.x,
                y: u * u * u * start.y + 3 * u * u * t * c1.y + 3 * u * t * t * c2.y + t * t * t * end.y,
            });
        }
        return samples;
    }

    function architecturePointAt(points, progress) {
        const lengths = [];
        let total = 0;
        for (let i = 1; i < points.length; i++) {
            const length = Math.hypot(points[i].x - points[i - 1].x, points[i].y - points[i - 1].y);
            lengths.push(length);
            total += length;
        }
        let remaining = total * architectureClamp(progress, 0, 1);
        for (let i = 0; i < lengths.length; i++) {
            if (remaining <= lengths[i] || i === lengths.length - 1) {
                const ratio = lengths[i] ? remaining / lengths[i] : 0;
                const start = points[i], end = points[i + 1];
                return { x: start.x + (end.x - start.x) * ratio, y: start.y + (end.y - start.y) * ratio, dx: end.x - start.x, dy: end.y - start.y, distance: total * architectureClamp(progress, 0, 1) };
            }
            remaining -= lengths[i];
        }
        return { ...points[0], dx: 0, dy: 0, distance: 0 };
    }

    function architectureStrokeProgress(ctx, points, progress) {
        if (progress <= 0 || points.length < 2) return null;
        const tip = architecturePointAt(points, progress);
        const distance = Math.hypot(tip.dx, tip.dy) || 1;
        const ux = tip.dx / distance, uy = tip.dy / distance;
        const end = { x: tip.x, y: tip.y };
        ctx.beginPath();
        ctx.moveTo(points[0].x, points[0].y);
        let total = 0;
        for (let i = 1; i < points.length; i++) {
            const segment = Math.hypot(points[i].x - points[i - 1].x, points[i].y - points[i - 1].y);
            if (total + segment >= tip.distance || i === points.length - 1) {
                const ratio = segment ? architectureClamp((tip.distance - total) / segment, 0, 1) : 0;
                ctx.lineTo(points[i - 1].x + (points[i].x - points[i - 1].x) * ratio, points[i - 1].y + (points[i].y - points[i - 1].y) * ratio);
                break;
            }
            ctx.lineTo(points[i].x, points[i].y);
            total += segment;
        }
        ctx.stroke();
        return { ...end, ux, uy };
    }

    function architectureDrawArrow(ctx, tip, color, size = 13) {
        if (!tip) return;
        const angle = Math.atan2(tip.uy, tip.ux);
        ctx.save();
        ctx.translate(tip.x, tip.y);
        ctx.rotate(angle);
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(-size, -size * 0.62);
        ctx.lineTo(-size, size * 0.62);
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();
        ctx.restore();
    }

    function architectureShapePath(ctx, shape, x, y, width, height) {
        const cx = x + width / 2, cy = y + height / 2;
        ctx.beginPath();
        if (shape === "database") {
            const cap = Math.min(22, height * 0.19);
            ctx.moveTo(x, y + cap);
            ctx.ellipse(cx, y + cap, width / 2, cap, 0, Math.PI, 0, true);
            ctx.lineTo(x + width, y + height - cap);
            ctx.ellipse(cx, y + height - cap, width / 2, cap, 0, 0, Math.PI, true);
            ctx.closePath();
        } else if (shape === "circle") {
            ctx.ellipse(cx, cy, width * 0.45, height * 0.47, 0, 0, Math.PI * 2);
        } else if (shape === "diamond") {
            ctx.moveTo(cx, y); ctx.lineTo(x + width, cy); ctx.lineTo(cx, y + height); ctx.lineTo(x, cy); ctx.closePath();
        } else if (shape === "hexagon") {
            const inset = width * 0.17;
            ctx.moveTo(x + inset, y); ctx.lineTo(x + width - inset, y); ctx.lineTo(x + width, cy);
            ctx.lineTo(x + width - inset, y + height); ctx.lineTo(x + inset, y + height); ctx.lineTo(x, cy); ctx.closePath();
        } else if (shape === "cloud") {
            ctx.moveTo(x + width * 0.18, y + height * 0.78);
            ctx.bezierCurveTo(x - width * 0.02, y + height * 0.72, x + width * 0.02, y + height * 0.42, x + width * 0.22, y + height * 0.38);
            ctx.bezierCurveTo(x + width * 0.24, y + height * 0.06, x + width * 0.58, y + height * 0.02, x + width * 0.68, y + height * 0.31);
            ctx.bezierCurveTo(x + width * 0.98, y + height * 0.23, x + width * 1.02, y + height * 0.66, x + width * 0.82, y + height * 0.76);
            ctx.closePath();
        } else if (shape === "document") {
            const fold = Math.min(22, width * 0.12);
            ctx.moveTo(x + 12, y); ctx.lineTo(x + width - fold, y); ctx.lineTo(x + width, y + fold);
            ctx.lineTo(x + width, y + height); ctx.lineTo(x + 12, y + height); ctx.closePath();
        } else if (shape === "rounded_rectangle" || shape === "terminal" || shape === "dashboard") {
            ctx.roundRect(x, y, width, height, Math.min(22, height * 0.2));
        } else {
            ctx.rect(x, y, width, height);
        }
        return { x, y, width, height, cx, cy };
    }

    function architectureDrawGroup(ctx, group, positions, width, height, time) {
        const members = (group.node_ids || []).map(id => positions.get(id)).filter(Boolean);
        if (!members.length) return;
        const minX = Math.min(...members.map(item => item.x - item.width / 2)) - 28;
        const maxX = Math.max(...members.map(item => item.x + item.width / 2)) + 28;
        const minY = Math.min(...members.map(item => item.y - item.height / 2)) - 42;
        const maxY = Math.max(...members.map(item => item.y + item.height / 2)) + 30;
        const box = architectureShapePath(ctx, group.shape === "cloud" ? "cloud" : "rounded_rectangle", minX, minY, maxX - minX, maxY - minY);
        ctx.save();
        ctx.fillStyle = "rgba(30, 64, 175, 0.07)";
        ctx.strokeStyle = "rgba(125, 211, 252, 0.42)";
        ctx.lineWidth = 2;
        ctx.setLineDash([10, 9]);
        ctx.fill();
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle = "rgba(191, 219, 254, 0.9)";
        ctx.font = "600 19px 'Segoe UI', sans-serif";
        ctx.textAlign = "left";
        ctx.fillText(group.label || "Group", box.x + 18, box.y + 26);
        ctx.restore();
    }

    function architectureDrawEdge(ctx, edge, source, target, graph, width, height, time) {
        const progress = architectureActionProgress(graph, edge.id, "draw_edge", time);
        if (progress <= 0) return;
        const points = architectureConnectorPoints(edge, source, target);
        const sourcePort = points[0], targetPort = points[points.length - 1];
        ctx.save();
        ctx.strokeStyle = edge.color || "#38BDF8";
        ctx.lineWidth = 4;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.shadowColor = edge.color || "#38BDF8";
        ctx.shadowBlur = 12;
        const tip = architectureStrokeProgress(ctx, points, progress);
        ctx.shadowBlur = 0;
        architectureDrawArrow(ctx, tip, edge.color || "#38BDF8", 13);
        [sourcePort, targetPort].forEach(port => {
            ctx.beginPath(); ctx.arc(port.x, port.y, 6, 0, Math.PI * 2);
            ctx.fillStyle = "#E0F2FE"; ctx.fill();
            ctx.strokeStyle = edge.color || "#38BDF8"; ctx.lineWidth = 2; ctx.stroke();
        });
        if (edge.label && progress > 0.65) {
            const midpoint = points[Math.floor(points.length / 2)];
            ctx.font = "600 18px 'Segoe UI', sans-serif";
            const labelWidth = Math.min(width * 0.55, ctx.measureText(edge.label).width + 28);
            ctx.fillStyle = "rgba(8, 16, 34, 0.94)";
            ctx.beginPath(); ctx.roundRect(midpoint.x - labelWidth / 2, midpoint.y - 15, labelWidth, 30, 12); ctx.fill();
            ctx.strokeStyle = "rgba(56,189,248,0.4)"; ctx.lineWidth = 1; ctx.stroke();
            ctx.fillStyle = "#DBEAFE"; ctx.textAlign = "center"; ctx.fillText(edge.label, midpoint.x, midpoint.y + 6, labelWidth - 16);
        }
        if (edge.data_flow && architectureActionIsActive(graph, edge.id, "packets", time)) {
            for (let packet = 0; packet < 3; packet++) {
                const phase = (time * 0.72 + packet / 3) % 1;
                const point = architecturePointAt(points, phase);
                ctx.beginPath(); ctx.arc(point.x, point.y, 7, 0, Math.PI * 2);
                ctx.fillStyle = "#F8FAFC"; ctx.shadowColor = edge.color || "#38BDF8"; ctx.shadowBlur = 16; ctx.fill();
            }
        }
        ctx.restore();
    }

    function architectureDrawNode(ctx, node, position, graph, width, height, time) {
        const reveal = architectureActionProgress(graph, node.id, "reveal_node", time);
        if (reveal <= 0) return;
        const highlighted = architectureActionIsActive(graph, node.id, "highlight_node", time);
        const pulsing = architectureActionIsActive(graph, node.id, "pulse_node", time);
        const expanding = architectureActionIsActive(graph, node.id, "expand_node", time);
        const morphing = architectureActionIsActive(graph, node.id, "morph_node", time);
        const entrance = architectureEase(reveal);
        const pulse = pulsing || highlighted ? 1 + 0.08 * Math.sin(time * 7) : 1;
        const scale = (0.72 + 0.28 * entrance) * pulse * (morphing ? 1 + 0.05 * Math.sin(time * 5) : 1);
        const boxWidth = position.width * scale, boxHeight = position.height * scale;
        const x = position.x - boxWidth / 2, y = position.y - boxHeight / 2;
        const color = node.color || "#38BDF8";
        ctx.save();
        ctx.globalAlpha = entrance;
        ctx.shadowColor = highlighted || pulsing || morphing ? color : "rgba(56,189,248,0.35)";
        ctx.shadowBlur = highlighted || pulsing ? 28 : 12;
        const box = architectureShapePath(ctx, node.shape || "rounded_rectangle", x, y, boxWidth, boxHeight);
        const fill = ctx.createLinearGradient(x, y, x + boxWidth, y + boxHeight);
        fill.addColorStop(0, highlighted ? "rgba(14,116,144,0.94)" : "rgba(12,25,49,0.96)");
        fill.addColorStop(1, "rgba(8,14,30,0.96)");
        ctx.fillStyle = fill; ctx.fill();
        ctx.strokeStyle = highlighted ? color : "rgba(125,211,252,0.86)";
        ctx.lineWidth = highlighted ? 4 : 2.5; ctx.stroke(); ctx.shadowBlur = 0;
        if (node.shape === "database") {
            ctx.beginPath(); ctx.ellipse(box.cx, box.y + Math.min(22, box.height * 0.19), box.width / 2, Math.min(22, box.height * 0.19), 0, 0, Math.PI * 2);
            ctx.strokeStyle = "rgba(186,230,253,0.82)"; ctx.lineWidth = 2; ctx.stroke();
        } else if (node.shape === "table") {
            for (let row = 1; row <= 2; row++) { ctx.beginPath(); ctx.moveTo(x + boxWidth * 0.12, y + boxHeight * row / 3); ctx.lineTo(x + boxWidth * 0.88, y + boxHeight * row / 3); ctx.stroke(); }
            for (let col = 1; col <= 2; col++) { ctx.beginPath(); ctx.moveTo(x + boxWidth * col / 3, y + boxHeight * 0.14); ctx.lineTo(x + boxWidth * col / 3, y + boxHeight * 0.86); ctx.stroke(); }
        } else if (node.shape === "terminal") {
            ctx.font = "700 19px Consolas, monospace"; ctx.textAlign = "left"; ctx.fillStyle = "#86EFAC"; ctx.fillText(">_", x + 16, y + 25);
        } else if (node.shape === "dashboard") {
            ctx.fillStyle = "rgba(56,189,248,0.5)";
            const chartBase = y + boxHeight * 0.78;
            [0.34, 0.58, 0.44, 0.74].forEach((value, index) => ctx.fillRect(x + boxWidth * (0.12 + index * 0.12), chartBase - boxHeight * value * 0.28, boxWidth * 0.07, boxHeight * value * 0.28));
        } else if (node.shape === "document") {
            ctx.beginPath(); ctx.moveTo(x + boxWidth * 0.7, y + 2); ctx.lineTo(x + boxWidth * 0.7, y + boxHeight * 0.22); ctx.lineTo(x + boxWidth * 0.98, y + boxHeight * 0.22); ctx.stroke();
        }
        const fontSize = architectureClamp(Math.min(boxWidth / Math.max(8, String(node.label || "").length * 0.58), boxHeight * 0.28), 16, 27);
        ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillStyle = "#F8FAFC";
        ctx.font = `700 ${fontSize}px 'Segoe UI', sans-serif`;
        const titleLines = wrapCanvasText(ctx, node.label || "Component", boxWidth * 0.84, 2);
        const titleHeight = titleLines.length * (fontSize + 3);
        const descriptionLines = node.description ? wrapCanvasText(ctx, node.description, boxWidth * 0.82, 1) : [];
        const lineHeight = Math.min(18, boxHeight * 0.15);
        const descriptionHeight = descriptionLines.length * lineHeight;
        const contentHeight = titleHeight + descriptionHeight + (descriptionLines.length ? 4 : 0);
        let textY = box.cy - contentHeight / 2 + fontSize / 2;
        ctx.save(); ctx.beginPath(); ctx.rect(x + 12, y + 8, boxWidth - 24, boxHeight - 16); ctx.clip();
        titleLines.forEach(line => { ctx.globalAlpha = entrance * architectureClamp((reveal - 0.08) * 5, 0, 1); ctx.fillText(line, box.cx, textY); textY += fontSize + 3; });
        ctx.font = `500 ${lineHeight}px 'Segoe UI', sans-serif`; ctx.fillStyle = "#CBD5E1";
        descriptionLines.forEach(line => { ctx.globalAlpha = entrance * architectureClamp((reveal - 0.28) * 4, 0, 1); ctx.fillText(line, box.cx, textY); textY += lineHeight; });
        ctx.restore();
        ctx.beginPath(); ctx.arc(x + boxWidth - 16, y + 15, 5, 0, Math.PI * 2);
        ctx.fillStyle = node.status === "warning" ? "#FBBF24" : node.status === "error" ? "#F87171" : "#34D399"; ctx.fill();
        if (expanding) {
            ctx.strokeStyle = color; ctx.globalAlpha = 0.55 + 0.35 * Math.sin(time * 6); ctx.lineWidth = 2;
            ctx.beginPath(); ctx.roundRect(x - 8, y - 8, boxWidth + 16, boxHeight + 16, 24); ctx.stroke();
        }
        ctx.restore();
    }

    function architectureGraphForScene(graph, stage, time) {
        const stageActions = stage && Array.isArray(stage.diagram_actions) ? stage.diagram_actions : null;
        if (!stageActions) return graph;
        const validActions = stageActions.filter(action => action && typeof action === "object");
        if (!validActions.length) return null;

        const nodes = Array.isArray(graph.nodes) ? graph.nodes : [];
        const edges = Array.isArray(graph.edges) ? graph.edges : [];
        const targets = new Set(validActions.map(action => String(action.target_id || "")));
        const nodeIds = new Set(nodes.filter(node => targets.has(String(node.id))).map(node => String(node.id)));
        const edgeIds = new Set();
        edges.forEach(edge => {
            if (targets.has(String(edge.id))) {
                edgeIds.add(String(edge.id));
                nodeIds.add(String(edge.from));
                nodeIds.add(String(edge.to));
            }
        });
        if (!nodeIds.size) return null;

        edges.forEach(edge => {
            if (nodeIds.has(String(edge.from)) && nodeIds.has(String(edge.to))) edgeIds.add(String(edge.id));
        });
        const stageStart = Number(stage.start || 0);
        const stageEnd = Number(stage.end || stageStart);
        const stageDuration = Math.max(0.1, stageEnd - stageStart);
        const actions = validActions
            .filter(action => nodeIds.has(String(action.target_id)) || edgeIds.has(String(action.target_id)))
            .map(action => {
                const cue = Math.max(0, Math.min(1, Number(action.cue_progress) || 0));
                const start = stageStart + cue * stageDuration;
                return {
                    target_id: String(action.target_id),
                    action: String(action.action || "highlight_node"),
                    start,
                    end: stageEnd,
                    duration: Math.min(0.7, Math.max(0.12, stageEnd - start)),
                };
            });
        return {
            ...graph,
            nodes: nodes.filter(node => nodeIds.has(String(node.id))),
            edges: edges.filter(edge => edgeIds.has(String(edge.id))),
            groups: (graph.groups || []).filter(group =>
                (group.node_ids || []).some(id => nodeIds.has(String(id)))
            ),
            actions,
        };
    }

    function drawTechnicalArchitectureGraph(ctx, width, height, graph, time, stageIndex, totalDuration, stage) {
        if (!graph || !Array.isArray(graph.nodes) || !graph.nodes.length) return false;
        graph = architectureGraphForScene(graph, stage, time);
        if (!graph || !graph.nodes.length) return false;
        const nodes = graph.nodes;
        const positions = new Map(nodes.map(node => [node.id, architecturePoint(node, width, height, nodes)]));
        const activeFocus = (graph.actions || []).filter(action => action.action === "highlight_node"
            && time >= Number(action.start || 0) && time <= Number(action.end || action.start || 0))
            .sort((left, right) => Number(right.start || 0) - Number(left.start || 0))[0];
        const focusNode = activeFocus ? nodes.find(node => node.id === activeFocus.target_id) : null;
        const priorFocus = activeFocus ? (graph.actions || []).filter(action => action.action === "highlight_node"
            && action.start < activeFocus.start).sort((left, right) => Number(right.start || 0) - Number(left.start || 0))[0] : null;
        const priorNode = priorFocus ? nodes.find(node => node.id === priorFocus.target_id) : null;
        const focusProgress = activeFocus ? architectureEase((time - Number(activeFocus.start || 0)) / 0.7) : 0;
        const focusX = focusNode ? (priorNode ? priorNode.x * (1 - focusProgress) + focusNode.x * focusProgress : focusNode.x) : 0.5;
        const focusY = focusNode ? (priorNode ? priorNode.y * (1 - focusProgress) + focusNode.y * focusProgress : focusNode.y) : 0.5;
        const normalizedTime = architectureClamp(time / Math.max(0.1, totalDuration || 0.1), 0, 1);
        const zoom = 1.045 - 0.095 * architectureEase(normalizedTime);
        const panX = architectureClamp((0.5 - focusX) * width * 0.12, -width * 0.045, width * 0.045);
        const panY = architectureClamp((0.52 - focusY) * height * 0.1, -height * 0.045, height * 0.045);
        ctx.save();
        ctx.translate(width / 2 + panX, height / 2 + panY); ctx.scale(zoom, zoom); ctx.translate(-width / 2, -height / 2);
        (graph.groups || []).forEach(group => architectureDrawGroup(ctx, group, positions, width, height, time));
        for (const edge of graph.edges || []) {
            const source = positions.get(edge.from), target = positions.get(edge.to);
            if (source && target) architectureDrawEdge(ctx, edge, source, target, graph, width, height, time);
        }
        for (const node of nodes) architectureDrawNode(ctx, node, positions.get(node.id), graph, width, height, time);
        ctx.restore();
        return true;
    }
'''
