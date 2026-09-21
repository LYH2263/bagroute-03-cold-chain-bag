import { useEffect, useState } from "react";
import { api } from "../api/client";
type Rj = { id: number; route_id: number; stop_name: string; reason: string; created_at: string };

function rejectKind(reason: string): "cold-volume" | "normal" {
  return reason.includes("冷链超体积") ? "cold-volume" : "normal";
}

export default function RejectsPage() {
  const [rows, setRows] = useState<Rj[]>([]);
  useEffect(() => { api<Rj[]>("/rejects").then(setRows); }, []);
  return (<>
    <h2>拒收</h2>
    <table className="table"><thead><tr><th>时间</th><th>路线</th><th>订户</th><th>类型</th><th>原因</th></tr></thead>
    <tbody>{rows.map(r => {
      const cold = rejectKind(r.reason) === "cold-volume";
      return <tr key={r.id} className={cold ? "row-cold" : ""}>
        <td className="mono">{new Date(r.created_at).toLocaleString()}</td>
        <td>{r.route_id}</td>
        <td>{r.stop_name}</td>
        <td>{cold
          ? <span className="cold-tag">冷链超体积</span>
          : <span className="normal-tag">普通超限</span>}</td>
        <td className={cold ? "reason-cold" : ""}>{r.reason}</td>
      </tr>;
    })}
      {!rows.length && <tr><td colSpan={5}>暂无拒收</td></tr>}
    </tbody></table>
  </>);
}
