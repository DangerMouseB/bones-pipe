## Wishlist

BStructType('entityCore', 'tEntityCore', dict(id=tID, x=tNum, y=tNum))\
BStructType('ship', 'tShip', dict(entity=tEntity, lives=tU8))\
BSumType('collidable', 'tCollideable', [tEntityCore, tShip])\
BSimpleTaggedType(tEntityCore, "tAsteroid", "tAsteroid")\
BSimpleTaggedType(tEvent, "collision", "tCollision")


what about tPyStr**(tEvent+tNull) for discrete maps?\
(tPyStr*tPyStr) ^ tInt   for functions (without named arguments)\
tagging must use call syntax as [] can't handle names or we could provide a dict thus:\
* (tPyStr**(tEvent+tNull))[tHashMap]
* (tPyStr**(tEvent+tNull))[tHashMap,tFred]
* tNum[dict(dom=tUSD, for=tGBP)]
    



<br>

## Next stage [MoSCoW]

#### MustDo / TODO


#### ShouldDo



#### CouldDo



#### WontDo

* allow collide to return an imlist / array / tensor of events, i.e. add BArrayType so can do N**(tEvent+tNull). For example this
could a allow lives to be decremented and if run out can return
```
[
    f'{a.v} damaged {b.v} (collide<:asteroid,ship:>)' >> to(tEvent),
    f'{a.v} destroyed {b.v} (collide<:asteroid,ship:>)' >> to(tEvent),
    'game over' >> to(tEvent)
]
```

* add registerRule so can do *(ccy(T1), fx(T1,T2))->ccy(T2) and +(ccy(T1),ccy(T1))->ccy(T1)
* add registrations so can see all the potential bindings for a name


<br>

## Completed

#### to Sun 2021.02.07
* check return type of actual value matches function signature
* dispatch by matching for compatible signatures if hash doesn't match so collide and return a null event,  e.g. SV(tNull, None)
* basic spaceships (can't return array of events and can't handle null events)
