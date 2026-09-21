import { useEffect, useState } from "react";
import { api } from "../api/client";
type R = { id: number; name: string };
type Bag = { id: number; bag_index: number; weight_kg: number; volume_l: number; is_cold_chain: boolean; items: { stop_name: string }[] };
export default function PackPage() {
  const [routes, setRoutes] = useState<R[]>([]);
  const [rid, setRid] = useState<number | "">("");
  const [bags, setBags] = useState<Bag[]>([]);
  const [msg, setMsg] = useState(""); const [err, setErr] = useState("");
  useEffect(() => { api<R[]>("/routes").then(r => { setRoutes(r); if (r[0]) setRid(r[0].id); }); }, []);
  async function run() {
    setMsg(""); setErr("");
    try {
      const out = await api<Bag[]>("/pack", { method: "POST", body: JSON.stringify({ route_id: rid }) });
      setBags(out);
      const cold = out.filter(b => b.is_cold_chain).length;
      setMsg(`完成装袋：${out.length} 袋${cold ? `（含冷链袋 ${cold} 袋）` : ""}`);
    } catch (e) { setErr(e instanceof Error ? e.message : String(e)); }
  }
  return (<>
    <h2>装袋</h2>
    <div className="toolbar">
      <select value={rid} onChange={e => setRid(Number(e.target.value))}>{routes.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}</select>
      <button onClick={run}>按路线顺序双约束装袋</button>
    </div>
    {msg && <div className="ok">{msg}</div>}
    {err && <div className="err">{err}</div>}
    {bags.map(b => (
      <div key={b.id}>
        <div className="mono bag-summary">
          {b.is_cold_chain ? <span className="cold-tag">冷链袋</span> : <span className="normal-tag">普通袋</span>}
          <span>袋 {b.bag_index} · {b.weight_kg}kg / {b.volume_l}L</span>
        </div>
        <div className="bag-row">{b.items.map((it, i) => <div className={`bag-block${b.is_cold_chain ? " bag-block--cold" : ""}`} key={i}>{it.stop_name}</div>)}</div>
      </div>
    ))}
  </>);
}
