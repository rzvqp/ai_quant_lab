"""
PHASE B — Infrastructure Validation engine (GCQ6 iid=42011464, legacy normalization).
Single dual-compatible parser:
  - event boundary = record with F_LAST (bit 128).
  - N (None) action = no-op boundary (new normalization); if absent -> legacy (F_LAST rides on last book update).
Book mutated ONLY by A/C/M/R. T and F are trade/lifecycle annotations (do NOT mutate book size).
Implied orders: none present (0 Add with oid==0) -> pure direct L3 book.
"""
import numpy as np, sys
from sortedcontainers import SortedDict

OUT = r"C:\Users\MEDION~1\AppData\Local\Temp\claude\C--Users-MEDION-GAMING-tradingview-mcp\344b31d3-785f-43a4-b73b-d80a24bc18df\scratchpad\phaseb\npy"
INT64MAX = 9223372036854775807
F_LAST=128; F_SNAPSHOT=32

LEVEL_COLS=[]
for lv in range(10):
    LEVEL_COLS += [f"bid_px_{lv:02d}",f"bid_sz_{lv:02d}",f"bid_ct_{lv:02d}",
                   f"ask_px_{lv:02d}",f"ask_sz_{lv:02d}",f"ask_ct_{lv:02d}"]

class Book:
    def __init__(self):
        self.orders={}                 # oid -> [side(bytes), price, size]
        self.bids=SortedDict()         # price -> [size,count]
        self.asks=SortedDict()
        # invariant counters
        self.orphan_c=0; self.orphan_m=0; self.orphan_f=0
        self.neg_level=0; self.neg_order=0
    def side_book(self,side): return self.bids if side==b'B' else self.asks
    def add(self,oid,side,px,sz):
        self.orders[oid]=[side,px,sz]
        bk=self.side_book(side)
        if px in bk:
            bk[px][0]+=sz; bk[px][1]+=1
        else:
            bk[px]=[sz,1]
    def cancel(self,oid,dec_sz):
        o=self.orders.get(oid)
        if o is None:
            self.orphan_c+=1; return
        side,px,sz=o
        bk=self.side_book(side)
        lvl=bk.get(px)
        newsz=sz-dec_sz
        if lvl is not None:
            lvl[0]-=dec_sz
            if newsz<=0:
                lvl[1]-=1
            if lvl[0]<=0 or lvl[1]<=0:
                if lvl[0]<0: self.neg_level+=1
                del bk[px]
        if newsz<=0:
            del self.orders[oid]
        else:
            o[2]=newsz
    def modify(self,oid,side,npx,nsz):
        o=self.orders.get(oid)
        if o is None:
            self.orphan_m+=1
            # treat as add (order we never saw); keeps book closer to truth
            self.add(oid,side,npx,nsz); return
        oside,opx,osz=o
        bk=self.side_book(oside)
        if npx==opx and side==oside:
            bk[opx][0]+= (nsz-osz)
            o[2]=nsz
        else:
            # remove from old level
            lvl=bk.get(opx)
            if lvl is not None:
                lvl[0]-=osz; lvl[1]-=1
                if lvl[1]<=0 or lvl[0]<=0: del bk[opx]
            nb=self.side_book(side)
            if npx in nb: nb[npx][0]+=nsz; nb[npx][1]+=1
            else: nb[npx]=[nsz,1]
            o[0]=side; o[1]=npx; o[2]=nsz
    def clear(self):
        self.orders.clear(); self.bids.clear(); self.asks.clear()
    def top10_tuple(self):
        out=[]
        # bids: highest first -> last keys of SortedDict
        bkeys=self.bids.keys()
        n=len(bkeys)
        for k in range(10):
            if k<n:
                px=bkeys[n-1-k]; sz,ct=self.bids[px]
                out += [px,sz,ct]
            else:
                out += [INT64MAX,0,0]
        # asks: lowest first
        akeys=self.asks.keys(); na=len(akeys)
        # interleave to match LEVEL_COLS order (bid then ask per level)
        res=[]
        bk=self.bids; ak=self.asks
        for k in range(10):
            if k<n:
                px=bkeys[n-1-k]; sz,ct=bk[px]; res+=[px,sz,ct]
            else: res+=[INT64MAX,0,0]
            if k<na:
                px=akeys[k]; sz,ct=ak[px]; res+=[px,sz,ct]
            else: res+=[INT64MAX,0,0]
        return tuple(res)

def load_mbo(day):
    a=np.load(OUT+rf"\mbo_{day}.npy")
    return dict(
        action=a['action'], side=a['side'], price=a['price'].astype(np.int64),
        size=a['size'].astype(np.int64), oid=a['order_id'].astype(np.uint64),
        seq=a['sequence'].astype(np.int64), flags=a['flags'].astype(np.int64),
        ts_event=a['ts_event'].astype(np.int64), ts_recv=a['ts_recv'].astype(np.int64),
        ts_in_delta=a['ts_in_delta'].astype(np.int64), n=len(a))

def load_mbp(day):
    a=np.load(OUT+rf"\mbp10_{day}.npy")
    # build official top10 matrix in LEVEL_COLS order (bid_px,bid_sz,bid_ct,ask_px,ask_sz,ask_ct)*10
    cols=[]
    for lv in range(10):
        cols += [a[f'bid_px_{lv:02d}'].astype(np.int64), a[f'bid_sz_{lv:02d}'].astype(np.int64),
                 a[f'bid_ct_{lv:02d}'].astype(np.int64), a[f'ask_px_{lv:02d}'].astype(np.int64),
                 a[f'ask_sz_{lv:02d}'].astype(np.int64), a[f'ask_ct_{lv:02d}'].astype(np.int64)]
    mat=np.stack(cols,axis=1)  # (m,60)
    return dict(seq=a['sequence'].astype(np.int64), flags=a['flags'].astype(np.int64),
                action=a['action'], mat=mat, n=len(a), ts_event=a['ts_event'].astype(np.int64))

def run_day(day):
    print(f"\n{'='*60}\nDAY {day}\n{'='*60}")
    M=load_mbo(day); P=load_mbp(day)
    act=M['action']; side=M['side']; price=M['price']; size=M['size']; oid=M['oid']
    seq=M['seq']; flags=M['flags']; n=M['n']
    tse=M['ts_event']; tsr=M['ts_recv']; tsd=M['ts_in_delta']

    # regime detection
    n_none=int((act==b'N').sum())
    regime = "new (standalone N+F_LAST)" if n_none>0 else "legacy (F_LAST on last update)"
    print(f"[REGIME] N-records={n_none} -> {regime}")

    # snapshot mask
    snap_mask = (flags & F_SNAPSHOT)>0
    live = ~snap_mask
    n_snap=int(snap_mask.sum())
    print(f"[SNAPSHOT] {n_snap} snapshot records; live={int(live.sum())}")

    # ---- GATE 3: sequence monotonic on LIVE records ----
    lseq=seq[live]
    d=np.diff(lseq)
    seq_ok = bool((d>=0).all())
    n_dec=int((d<0).sum())
    print(f"[GATE3 sequence] live monotonic non-decreasing: {seq_ok} (violations={n_dec})")

    # ---- GATE 4: timestamps on LIVE records ----
    lte=tse[live]; ltr=tsr[live]; ltd=tsd[live]
    te_ok=bool((np.diff(lte)>=0).all()); n_te=int((np.diff(lte)<0).sum())
    # ts_recv should be >= ts_event (capture after exchange send) on live
    recv_ge_event=bool((ltr>=lte).all()); n_re=int((ltr<lte).sum())
    tr_ok=bool((np.diff(ltr)>=0).all()); n_tr=int((np.diff(ltr)<0).sum())
    d_ok=bool((ltd>=0).all()); n_d=int((ltd<0).sum())
    print(f"[GATE4 ts_event] non-decreasing: {te_ok} (viol={n_te})")
    print(f"[GATE4 ts_recv ] non-decreasing: {tr_ok} (viol={n_tr}); ts_recv>=ts_event: {recv_ge_event} (viol={n_re})")
    print(f"[GATE4 ts_in_delta>=0] {d_ok} (viol={n_d})")

    # ---- book reconstruction + MBP-10 compare ----
    bk=Book()
    i=0
    # snapshot phase: apply contiguous snapshot block
    while i<n and snap_mask[i]:
        a=act[i]
        if a==b'R': bk.clear()
        elif a==b'A': bk.add(int(oid[i]),side[i],int(price[i]),int(size[i]))
        elif a==b'C': bk.cancel(int(oid[i]),int(size[i]))
        elif a==b'M': bk.modify(int(oid[i]),side[i],int(price[i]),int(size[i]))
        i+=1
    snap_end=i
    # mbp snapshot record: advance to last mbp with F_SNAPSHOT
    Pseq=P['seq']; Pflags=P['flags']; Pmat=P['mat']; Pn=P['n']; Pact=P['action']
    j=0; snap_cmp=None
    while j<Pn and (Pflags[j]&F_SNAPSHOT)>0:
        snap_cmp=j; j+=1
    snap_match=None
    if snap_cmp is not None:
        snap_match = (bk.top10_tuple()==tuple(int(x) for x in Pmat[snap_cmp]))
    print(f"[SNAPSHOT compare] book-after-snapshot == official mbp snapshot top10: {snap_match}")

    # live merge by sequence group
    cmp_total=0; cmp_ok=0
    first_mismatch=None
    lifecycle_adds=0; lifecycle_removes=0
    trades=0; fills=0
    while i<n:
        S=seq[i]
        while i<n and seq[i]==S:
            a=act[i]
            if a==b'A':
                bk.add(int(oid[i]),side[i],int(price[i]),int(size[i])); lifecycle_adds+=1
            elif a==b'C':
                pre = int(oid[i]) in bk.orders
                bk.cancel(int(oid[i]),int(size[i]))
                if pre: lifecycle_removes+=1
            elif a==b'M':
                bk.modify(int(oid[i]),side[i],int(price[i]),int(size[i]))
            elif a==b'R':
                bk.clear()
            elif a==b'T':
                trades+=1
            elif a==b'F':
                fills+=1
            i+=1
        # book == state after packet S; compare to last mbp record with seq==S
        if j<Pn and Pseq[j]==S:
            last=j
            while j<Pn and Pseq[j]==S:
                last=j; j+=1
            cmp_total+=1
            mine=bk.top10_tuple()
            offi=tuple(int(x) for x in Pmat[last])
            if mine==offi: cmp_ok+=1
            elif first_mismatch is None:
                first_mismatch=(int(S),mine,offi)
        elif j<Pn and Pseq[j]<S:
            # mbp seq not aligned (skip forward) - should not happen; record
            while j<Pn and Pseq[j]<S: j+=1

    # ---- GATE 7 invariants ----
    # rebuild levels from orders and compare to maintained levels
    reb_bid={}; reb_ask={}
    neg_order=0
    for o_side,o_px,o_sz in bk.orders.values():
        if o_sz<0: neg_order+=1
        d=reb_bid if o_side==b'B' else reb_ask
        if o_px in d: d[o_px][0]+=o_sz; d[o_px][1]+=1
        else: d[o_px]=[o_sz,1]
    def cmp_levels(reb,bkside):
        bad=0
        if set(reb.keys())!=set(bkside.keys()): bad+= len(set(reb.keys())^set(bkside.keys()))
        for px,(sz,ct) in reb.items():
            if px in bkside and (bkside[px][0]!=sz or bkside[px][1]!=ct): bad+=1
        return bad
    consist_bad = cmp_levels(reb_bid,bk.bids)+cmp_levels(reb_ask,bk.asks)

    print(f"[RECON] live adds={lifecycle_adds:,} removes={lifecycle_removes:,} trades={trades:,} fills={fills:,}")
    print(f"[GATE6/7 lifecycle] orphan_cancel={bk.orphan_c} orphan_modify={bk.orphan_m} orphan_fill(n/a book)={bk.orphan_f}")
    print(f"[GATE7 invariants] neg_level_events={bk.neg_level} neg_order_sizes={neg_order} "
          f"internal_consistency_bad_levels={consist_bad}")
    print(f"[RESIDUAL book EOD] live_orders={len(bk.orders):,} bid_levels={len(bk.bids)} ask_levels={len(bk.asks)}")

    # ---- GATE 8/9 MBP-10 compare result ----
    rate = (cmp_ok/cmp_total*100) if cmp_total else 0
    print(f"[GATE8/9 MBP-10 bit-exact] compared={cmp_total:,} exact={cmp_ok:,} rate={rate:.4f}%  mismatches={cmp_total-cmp_ok:,}")
    if first_mismatch:
        S,mine,offi=first_mismatch
        print(f"  first mismatch seq={S}")
        print(f"    mine[:12]={mine[:12]}")
        print(f"    offi[:12]={offi[:12]}")
    return dict(day=day, regime=regime, seq_ok=seq_ok, te_ok=te_ok, tr_ok=tr_ok, recv_ge_event=recv_ge_event,
                d_ok=d_ok, snap_match=snap_match, cmp_total=cmp_total, cmp_ok=cmp_ok,
                orphan=bk.orphan_c+bk.orphan_m, neg=bk.neg_level+neg_order, consist_bad=consist_bad,
                n_dec=n_dec)

if __name__=="__main__":
    days=sys.argv[1:] or ["20260707","20260708"]
    results=[r for r in (run_day(d) for d in days)]
    print("\n"+"="*60+"\nSUMMARY\n"+"="*60)
    for r in results:
        print(r)
