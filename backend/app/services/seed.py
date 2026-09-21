from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import DeliveryRoute, SubscriberStop


def seed_if_empty(db: Session) -> None:
    if db.scalar(select(DeliveryRoute.id).limit(1)):
        return
    # 冷链体积上限严于普通体积上限。
    r1 = DeliveryRoute(
        name="城东晨线",
        max_weight_kg=8.0,
        max_volume_l=18.0,
        max_cold_volume_l=6.0,
    )
    r2 = DeliveryRoute(
        name="园区午线",
        max_weight_kg=6.0,
        max_volume_l=14.0,
        max_cold_volume_l=8.0,
    )
    db.add_all([r1, r2])
    db.flush()
    db.add_all(
        [
            SubscriberStop(route_id=r1.id, seq=1, name="松林里 3 栋", weight_kg=2.2, volume_l=4.0),
            SubscriberStop(route_id=r1.id, seq=2, name="梧桐苑门岗", weight_kg=3.5, volume_l=5.5),
            SubscriberStop(route_id=r1.id, seq=3, name="地铁口快递柜", weight_kg=1.8, volume_l=3.0),
            SubscriberStop(route_id=r1.id, seq=4, name="超大件样例", weight_kg=9.5, volume_l=6.0),
            SubscriberStop(route_id=r1.id, seq=5, name="咖啡店后门", weight_kg=2.0, volume_l=4.5),
            # 体积 7.0：未超普通上限 18.0，但超过冷链上限 6.0 → 冷链超体积拒收。
            SubscriberStop(
                route_id=r1.id, seq=6, name="冷链鲜奶站",
                weight_kg=1.0, volume_l=7.0, is_cold_chain=True,
            ),
            # 两笔冷链，合计 2.4kg / 5.0L，可进入同一冷链袋。
            SubscriberStop(
                route_id=r1.id, seq=7, name="冷链药房 A",
                weight_kg=1.2, volume_l=2.5, is_cold_chain=True,
            ),
            SubscriberStop(
                route_id=r1.id, seq=8, name="冷链药房 B",
                weight_kg=1.2, volume_l=2.5, is_cold_chain=True,
            ),
            SubscriberStop(route_id=r2.id, seq=1, name="A 座前台", weight_kg=1.5, volume_l=3.0),
            SubscriberStop(route_id=r2.id, seq=2, name="B 座茶水间", weight_kg=2.0, volume_l=4.0),
            SubscriberStop(route_id=r2.id, seq=3, name="地下车库岗亭", weight_kg=2.8, volume_l=5.0),
        ]
    )
    db.commit()
