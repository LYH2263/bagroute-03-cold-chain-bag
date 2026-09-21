import { useEffect, useState } from "react";
import { api } from "../api/client";
type R = { id: number; name: string; max_weight_kg: number; max_volume_l: number; max_cold_volume_l: number };
export default function RoutesPage() {
  const [rows, setRows] = useState<R[]>([]);
  const [draft, setDraft] = useState<Record<number, string>>({});
  const [busy, setBusy] = useState<number | null>(null);
  const [msg, setMsg] = useState(""); const [err, setErr] = useState("");
  useEffect(() => { api<R[]>("/routes").then(setRows); }, []);

  async function save(r: R) {
    const val = Number(draft[r.id]);
    if (!Number.isFinite(val) || val <= 0) { setErr("冷链体积上限必须为正数"); return; }
    setBusy(r.id); setMsg(""); setErr("");
    try {
      const updated = await api<R>(`/routes/${r.id}`, {
        method: "PATCH", body: JSON.stringify({ max_cold_volume_l: val }),
      });
      setRows(rs => rs.map(x => x.id === updated.id ? updated : x));
      setMsg(`已保存「${r.name}」冷链体积上限 ${updated.max_cold_volume_l}L`);
    } catch (e) { setErr(e instanceof Error ? e.message : String(e)); }
    finally { setBusy(null); }
  }

  return (<>
    <h2>路线</h2>
    {msg && <div className="ok">{msg}</div>}
    {err && <div className="err">{err}</div>}
    <table className="table"><thead><tr><th>名称</th><th>重量上限 kg</th><th>普通体积上限 L</th><th>冷链体积上限 L</th><th></th></tr></thead>
    <tbody>{rows.map(r => <tr key={r.id}>
      <td>{r.name}</td>
      <td className="mono">{r.max_weight_kg}</td>
      <td className="mono">{r.max_volume_l}</td>
      <td>
        <input
          className="cold-input mono"
          type="number" step="0.1" min="0"
          defaultValue={r.max_cold_volume_l}
          onChange={e => setDraft(d => ({ ...d, [r.id]: e.target.value }))}
        />
        <span className="cold-tag">冷链</span>
      </td>
      <td><button disabled={busy === r.id || !(r.id in draft)} onClick={() => save(r)}>{busy === r.id ? "保存中…" : "保存"}</button></td>
    </tr>)}</tbody></table>
    <p className="hint">冷链体积上限须严于普通体积上限，保存后再次进入仍生效。</p>
  </>);
}
