## Wishlist

* register into a specified scope


<br>

## Next stage [MoSCoW]

#### MustDo / TODO
* add binary

* dispatch should throw Dynamic/ partial TypeError e.g. int+null has been bound to (int) -> ... but at run time the Val is null
* @bones throws an NonUniqueSignatureError subclass of TypeError - i.e. enforce signatures to not overlap
* add registerRule so can do *(ccy(T1), fx(T1,T2))->ccy(T2) and +(ccy(T1),ccy(T1))->ccy(T1)

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

* add registrations so can see all the potential bindings for a name


<br>

## Completed
* test cow and fow (fragment on write) for vector

#### to Sun 2021.02.07
* test_inplace
* handle signatures with python types, e.g. so [] >> to(matrix[unbound]) can call def to(t: list, v: list) -> matrix[unbound]
* check return type of actual value matches function signature
* dispatch by matching for compatible signatures if hash doesn't match so collide and return a null event,  e.g. SV(tNull, None)
* basic spaceships (can't return array of events and can't handle null events)
