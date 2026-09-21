from app.services.pack_engine import StopItem, pack_route


def test_packs_in_route_order_splitting_bags():
    stops = [
        StopItem(1, 1, 2.0, 3.0),
        StopItem(2, 2, 2.5, 3.0),
        StopItem(3, 3, 1.0, 1.0),
    ]
    result = pack_route(stops, max_weight=4.0, max_volume=10.0)
    assert len(result.bags) == 2
    assert [i.stop_id for i in result.bags[0].items] == [1]
    assert [i.stop_id for i in result.bags[1].items] == [2, 3]
    assert not result.rejects


def test_reject_oversized_stop():
    stops = [StopItem(1, 1, 9.0, 1.0, "大件"), StopItem(2, 2, 1.0, 1.0)]
    result = pack_route(stops, max_weight=5.0, max_volume=5.0)
    assert len(result.rejects) == 1
    assert result.rejects[0][0].stop_id == 1
    assert len(result.bags) == 1
    assert result.bags[0].items[0].stop_id == 2


def test_volume_cap_triggers_new_bag():
    stops = [StopItem(1, 1, 1.0, 4.0), StopItem(2, 2, 1.0, 4.0)]
    result = pack_route(stops, max_weight=10.0, max_volume=5.0)
    assert len(result.bags) == 2


def test_cold_and_normal_never_share_bag():
    # 体积上任意两笔都能同袋，但冷链与非冷链必须分开。
    stops = [
        StopItem(1, 1, 1.0, 2.0, "普通甲", is_cold_chain=False),
        StopItem(2, 2, 1.0, 2.0, "冷链甲", is_cold_chain=True),
        StopItem(3, 3, 1.0, 2.0, "普通乙", is_cold_chain=False),
        StopItem(4, 4, 1.0, 2.0, "冷链乙", is_cold_chain=True),
    ]
    result = pack_route(stops, max_weight=10.0, max_volume=10.0, max_cold_volume=10.0)
    assert not result.rejects
    assert len(result.bags) == 2
    normal_bag = next(b for b in result.bags if not b.is_cold_chain)
    cold_bag = next(b for b in result.bags if b.is_cold_chain)
    assert [i.stop_id for i in normal_bag.items] == [1, 3]
    assert [i.stop_id for i in cold_bag.items] == [2, 4]
    # 每一袋必须是纯链：袋内冷链标记一致。
    for bag in result.bags:
        assert all(it.is_cold_chain == bag.is_cold_chain for it in bag.items)


def test_cold_volume_cap_rejects_alone():
    # 体积 7.0：未超普通上限 18.0，但超过冷链上限 6.0 → 拒收。
    cold = StopItem(1, 1, 1.0, 7.0, "冷链鲜奶站", is_cold_chain=True)
    normal = StopItem(2, 2, 1.0, 7.0, "普通站", is_cold_chain=False)
    result = pack_route(
        [cold, normal], max_weight=8.0, max_volume=18.0, max_cold_volume=6.0
    )
    assert len(result.rejects) == 1
    rejected, reason = result.rejects[0]
    assert rejected.stop_id == cold.stop_id
    assert "冷链超体积" in reason
    # 同样体积的非冷链站不受冷链上限影响，正常入袋。
    assert len(result.bags) == 1
    assert not result.bags[0].is_cold_chain
    assert [i.stop_id for i in result.bags[0].items] == [2]


def test_two_cold_stops_share_cold_bag():
    stops = [
        StopItem(1, 1, 1.2, 2.5, "冷链药房 A", is_cold_chain=True),
        StopItem(2, 2, 1.2, 2.5, "冷链药房 B", is_cold_chain=True),
    ]
    result = pack_route(stops, max_weight=8.0, max_volume=18.0, max_cold_volume=6.0)
    assert not result.rejects
    assert len(result.bags) == 1
    bag = result.bags[0]
    assert bag.is_cold_chain
    assert [i.stop_id for i in bag.items] == [1, 2]
    assert abs(bag.volume_l - 5.0) < 1e-9


def test_normal_oversize_reason_is_not_cold():
    normal = StopItem(1, 1, 1.0, 20.0, "普通大件", is_cold_chain=False)
    result = pack_route(
        [normal], max_weight=8.0, max_volume=18.0, max_cold_volume=6.0
    )
    assert len(result.rejects) == 1
    _, reason = result.rejects[0]
    assert "超体积" in reason
    assert "冷链超体积" not in reason
