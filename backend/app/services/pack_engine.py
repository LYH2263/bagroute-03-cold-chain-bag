"""Route-order bag packing with weight + volume caps; reject when exceed.

冷链订户点（is_cold_chain=True）只能进入冷链袋，非冷链订户点只能进入
普通袋，二者绝不混袋。冷链袋对照更严的冷链体积上限 max_cold_volume；
重量上限两条链共用同一路线上限。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StopItem:
    stop_id: int
    seq: int
    weight_kg: float
    volume_l: float
    label: str = ""
    is_cold_chain: bool = False


@dataclass
class Bag:
    bag_index: int
    items: list[StopItem] = field(default_factory=list)
    weight_kg: float = 0.0
    volume_l: float = 0.0
    is_cold_chain: bool = False


@dataclass(frozen=True)
class PackResult:
    bags: list[Bag]
    rejects: list[tuple[StopItem, str]]


def can_fit(bag: Bag, item: StopItem, max_weight: float, max_volume: float) -> bool:
    return (
        bag.weight_kg + item.weight_kg <= max_weight + 1e-9
        and bag.volume_l + item.volume_l <= max_volume + 1e-9
    )


def pack_route(
    stops: list[StopItem],
    max_weight: float,
    max_volume: float,
    max_cold_volume: float | None = None,
) -> PackResult:
    """按路线顺序装袋。

    max_cold_volume 为冷链袋体积上限；冷链站只对照该上限与共用的重量上限，
    非冷链站仍对照普通双上限。冷链袋与普通袋互不混装。
    """
    if max_cold_volume is None:
        max_cold_volume = max_volume
    ordered = sorted(stops, key=lambda s: s.seq)
    bags: list[Bag] = []
    rejects: list[tuple[StopItem, str]] = []
    # 两条链各自维护“当前袋”，使交错出现的同链站点仍能续袋。
    current: dict[bool, Bag | None] = {False: None, True: None}

    for item in ordered:
        cold = item.is_cold_chain
        vol_cap = max_cold_volume if cold else max_volume

        if item.weight_kg > max_weight or item.volume_l > vol_cap:
            reason = []
            if item.weight_kg > max_weight:
                reason.append(f"超重 {item.weight_kg}>{max_weight}")
            if item.volume_l > vol_cap:
                tag = "冷链超体积" if cold else "超体积"
                reason.append(f"{tag} {item.volume_l}>{vol_cap}")
            rejects.append((item, "；".join(reason)))
            continue

        bag = current[cold]
        if bag is None or not can_fit(bag, item, max_weight, vol_cap):
            bag = Bag(bag_index=len(bags) + 1, is_cold_chain=cold)
            bags.append(bag)
            current[cold] = bag

        if not can_fit(bag, item, max_weight, vol_cap):
            # should not happen after single-item check, but keep safe
            rejects.append((item, "无法装入新袋"))
            continue

        bag.items.append(item)
        bag.weight_kg += item.weight_kg
        bag.volume_l += item.volume_l

    return PackResult(bags=bags, rejects=rejects)
