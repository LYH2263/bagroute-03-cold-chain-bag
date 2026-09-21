import { useEffect, useState } from "react";
import { api } from "../api/client";
type Bag = { id: number; route_id: number; bag_index: number; weight_kg: number; volume_l: number; is_cold_chain: boolean; items: { stop_name: string; weight_kg: number; volume_l: number }[] };
export default function BagsPage() {
  const [rows, setRows] = useState<Bag[]>([]);
  useEffect(() => { api<Bag[]>("/bags").then(setRows); }, []);
  return (<>
    <h2>袋明细</h2>
    <table className="table"><thead><tr><th>路线</th><th>袋号</th><th>类型</th><th>重量</th><th>体积</th><th>订户</th></tr></thead>
    <tbody>{rows.map(b => <tr key={b.id} className={b.is_cold_chain ? "row-cold" : ""}>
      <td>{b.route_id}</td>
      <td>{b.bag_index}</td>
      <td>{b.is_cold_chain ? <span className="cold-tag">冷链袋</span> : <span className="normal-tag">普通袋</span>}</td>
      <td className="mono">{b.weight_kg}</td>
      <td className="mono">{b.volume_l}</td>
      <td className="bag-names">{b.items.map((i, idx) => (
        <span className="bag-name-seq" key={idx}>
          {idx > 0 && <span className="bag-arrow"> → </span>}
          <span className={b.is_cold_chain ? "bag-item-name--cold" : ""}>{i.stop_name}</span>
        </span>
      ))}</td></tr>)}
      {!rows.length && <tr><td colSpan={6}>尚无装袋结果，请先执行装袋</td></tr>}
    </tbody></table>
  </>);
}
