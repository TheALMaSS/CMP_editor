"""
Timing checks for a crop management plan, run by VALIDATE CMP.

ALMaSS runs a plan step by step: a step with fixed dates waits for its window, a step given as
"+N days" runs N days after the step before, a probability or condition node passes on at once,
"Sleep / Wait" holds until the last day of its window, and "Do nothing" completes at once. Some plan
mistakes only show when the steps are followed in time -- a harvest given as "+10 days" after a
probability node that is decided right after sowing is harvested in April. These checks follow
every route through the plan from START with the earliest day each step can run, the way ALMaSS
places it (GenericCrop::ScheduleFor / PlaceAfter / PlaceWindow, including the 240-day rule for a
window that is still to come this season), and report:

  A  a skipped step that moves what follows weeks or months earlier (a harvest in spring);
  B  a dated step reached when its window has long passed, which ALMaSS then runs at once;
  C  a rare step (10 % or less) that an arrow from an operation makes certain;
  D  a harvest window that ends well after the plan's own last date.

Days are counted from 1 January of the year START falls in (0 = 1 January). Weather can only make a
step later, so these earliest days are what matters for "too early" and "already passed".

The checks work on plain dictionaries, so they run on the editor's drawing (nodes_from_editor) and on
an exported plan (nodes_from_json) alike.
"""
import re

DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
HARVEST_OPS = {"Harvest", "Harvest (Long Duration)", "Swathing", "Fruit Harvest", "Manual Harvest",
               "Harvest Bush Fruit", "Harvest Bush Fruit (Hand)"}
SOW_WORDS = ("Sow", "Plant")
MAX_SEASON_WAIT = 240          # as in GenericCrop.cpp
SKIP_SHIFT_DAYS = 30           # check A
PASSED_DAYS = 30               # check B
LATE_END_DAYS = 14             # check D
RARE_PCT = 10                  # check C


def is_dm(s):
    return bool(s) and bool(re.fullmatch(r"\d\d/\d\d", s.strip()))


def doy(s):                    # 0-based day of year, as ALMaSS DayInYear
    d, m = map(int, s.strip().split("/"))
    return sum(DAYS[:m - 1]) + d - 1


def offset(s):
    m = re.fullmatch(r"\+(\d+)d", (s or "").strip())
    return int(m.group(1)) if m else None


def mod(x):
    return x % 365


def ddmm(t):
    d = mod(t)
    for i, n in enumerate(DAYS):
        if d < n:
            return f"{d + 1:02d}/{i + 1:02d}"
        d -= n
    return "31/12"


def place_window(e, l, re_, rl, ref_start):
    span, ref_span, after = mod(l - e), mod(rl - re_), mod(e - re_)
    overlapping = after - 365
    return ref_start + overlapping if overlapping + span >= ref_span else ref_start + after


# ------------------------------------------------------------------------------------------------
# plan as dictionaries
# ------------------------------------------------------------------------------------------------
def nodes_from_editor(op_nodes, prob_nodes, cond_nodes, catch_crop_nodes):
    """{id: {...}} from the editor's drawing."""
    out = {}
    for kind, lst in (("op", op_nodes), ("prob", prob_nodes), ("cond", cond_nodes), ("catch", catch_crop_nodes or [])):
        for n in lst:
            nid = n.id_text.toPlainText()
            dates = n.dates_text.toPlainText().strip() if hasattr(n, "dates_text") else ""
            parts = [p.strip() for p in dates.split(" - ")] if " - " in dates else [dates, ""]
            name = n.name_text.toPlainText() if hasattr(n, "name_text") else ""
            out[nid] = {"id": nid, "kind": kind, "name": " ".join(name.split()), "earliest": parts[0], "latest": parts[1],
                        "cond_type": getattr(n, "cond_type", None), "cond_value": getattr(n, "cond_value", None),
                        "out": [(a.end_node.id_text.toPlainText(),
                                 a.text_item.toPlainText().strip() if getattr(a, "text_item", None) else "")
                                for a in n.outgoing_arrows if getattr(a, "end_node", None) is not None]}
    return out


def nodes_from_json(plan):
    """{id: {...}} from an exported plan (ids without the crop-name prefix)."""
    pre = plan["crop_name"] + "_"
    short = lambda i: i[len(pre):] if i.startswith(pre) else i
    code = {n["code"]: short(n["id"]) for n in plan["nodes"]}
    kind = {"OpNode": "op", "ProbNode": "prob", "CondNode": "cond", "CatchCropNode": "catch"}
    out = {}
    for n in plan["nodes"]:
        out[short(n["id"])] = {"id": short(n["id"]), "kind": kind.get(n["type"], "op"), "name": " ".join(n["name"].split()),
                               "earliest": n.get("earliest", ""), "latest": n.get("latest", ""),
                               "cond_type": n.get("cond_type"), "cond_value": n.get("cond_value"),
                               "out": [(code[o["destination_code"]], o.get("branching_condition", "")) for o in n["outgoing"]]}
    return out


# ------------------------------------------------------------------------------------------------
# following the plan in time
# ------------------------------------------------------------------------------------------------
class Tracer:
    def __init__(self, nodes, crop_name):
        self.N = nodes
        self.crop = crop_name
        self.start = next((n for n in nodes.values() if n["kind"] == "op" and n["name"] == "START"), None)
        self.ref = {}
        if self.start:
            self._refs()
        self.history_ids = {self._short(n["cond_value"]) for n in nodes.values()
                            if n["kind"] == "cond" and n.get("cond_type") == "field_history" and n.get("cond_value")}
        self.runs = []         # (node id, day, how, route)

    def _short(self, v):
        pre = self.crop + "_"
        return v[len(pre):] if v and v.startswith(pre) else v

    def _refs(self):           # the reference window each node inherits (GenericCrop constructor)
        s = self.start
        self.ref[s["id"]] = (s["earliest"], s["earliest"])
        todo = [s]
        while todo:
            n = todo.pop(0)
            for cid, _ in n["out"]:
                c = self.N.get(cid)
                if c is None or cid in self.ref:
                    continue
                own = is_dm(c["earliest"]) and is_dm(c["latest"])
                self.ref[cid] = (c["earliest"], c["latest"]) if own else self.ref[n["id"]]
                todo.append(c)

    def _place_after(self, frm, t, e_s, l_s, rt=None):
        td = mod(t)
        o = offset(e_s)
        if not is_dm(e_s):
            return t + max(1, o or 0), False
        e = doy(e_s)
        l = doy(l_s) if is_dm(l_s) else e
        if (td >= e or td <= l) if e > l else (e <= td <= l):
            return t + 1, False
        if not is_dm(frm["earliest"]) and is_dm(frm["latest"]):
            end = doy(frm["latest"])
            if mod(end - td) <= mod(td - end):
                st = place_window(e, l, td, end, t)
            else:
                st = place_window(e, l, end, end, t - mod(td - end))
            return (st, False) if st > t else (t + 1, True)
        if rt:
            re_, rl, rs = rt
            while t - rs >= 365:
                rs += 365
            st = place_window(e, l, re_, rl, rs)
            return (st, False) if st > t else (t + 1, True)
        r = self.ref.get(frm["id"])
        if not r or not is_dm(r[0]):
            return t + mod(e - td), False
        re_ = doy(r[0]); rl = doy(r[1]) if is_dm(r[1]) else re_
        st = place_window(e, l, re_, rl, t - mod(td - re_))
        return (st, False) if st > t else (t + 1, True)

    def schedule(self, frm, t, child, rt):
        """ScheduleFor: the day a successor runs, and whether it was placed as already missed."""
        e_s, l_s = child["earliest"], child["latest"]
        td = mod(t)
        fixed = is_dm(e_s) and (is_dm(l_s) or not l_s)
        if fixed:
            e = doy(e_s); l = doy(l_s) if is_dm(l_s) else e
            if (td >= e or td <= l) if e > l else (e <= td <= l):
                return t + 1, False
        o = offset(e_s)
        if not fixed or not (self.ref.get(frm["id"]) and is_dm(self.ref[frm["id"]][0])):
            if o is not None:
                return t + o, False
            if is_dm(e_s):
                e = doy(e_s)
                return (t - td + e if td <= e else t - td + 365 + e), False
            return t, False
        placed, missed = self._place_after(frm, t, e_s, l_s)
        if placed <= t + 1 and rt:
            ahead, _ = self._place_after(frm, t, e_s, l_s, rt)
            if t + 1 < ahead <= t + MAX_SEASON_WAIT:
                return ahead, False
        return placed, missed

    def run(self, max_states=20000):
        if not self.start or not is_dm(self.start["earliest"]):
            return
        s0 = doy(self.start["earliest"])
        seen = set()
        stack = []
        for cid, lab in self.start["out"]:
            c = self.N.get(cid)
            if c is None:
                continue
            if is_dm(c["earliest"]):
                e = doy(c["earliest"]); l = doy(c["latest"]) if is_dm(c["latest"]) else e
                t = max(s0, place_window(e, l, s0, s0, s0))
                missed = False
            else:
                t, missed = s0 + (offset(c["earliest"]) or 0), False
            stack.append((cid, t, None, frozenset(), ("START",), None, missed, self.start["id"]))
        while stack and len(seen) < max_states:
            nid, t, rt, hist, route, sown, missed, prev = stack.pop()
            key = (nid, t, rt, hist)
            if key in seen:
                continue
            seen.add(key)
            n = self.N.get(nid)
            if n is None or (n["kind"] == "op" and n["name"] == "END") or n["kind"] == "catch":
                continue
            t_run = t
            if n["kind"] == "op":
                if n["name"] == "Sleep / Wait" and is_dm(n["latest"]):
                    end = doy(n["latest"]); t_run = t + mod(end - mod(t))
                self.runs.append((nid, t_run, missed, route, sown, prev))
                if is_dm(n["earliest"]) and is_dm(n["latest"]):
                    e = doy(n["earliest"]); rt = (e, doy(n["latest"]), t_run - mod(mod(t_run) - e))
                elif is_dm(n["latest"]):
                    end = doy(n["latest"]); td = mod(t_run)
                    rt = (td, end, t_run) if mod(end - td) <= mod(td - end) else (end, end, t_run - mod(td - end))
                if nid in self.history_ids:
                    hist = hist | {nid}
                if any(w in n["name"] for w in SOW_WORDS):
                    sown = t_run
            outs = n["out"]
            if n["kind"] == "cond":
                ct, cv = n.get("cond_type"), n.get("cond_value")
                ans = None
                if ct == "calendar_date" and cv not in (None, ""):
                    ans = mod(t_run) <= int(cv)
                elif ct == "field_history" and cv:
                    ans = self._short(cv) in hist
                if ans is not None:
                    outs = [(c, lab) for c, lab in outs if lab.upper() == ("YES" if ans else "NO")]
            if n["kind"] != "op":
                self.runs.append((nid, t_run, False, route, sown, prev))
            # a "Do nothing" passes straight on, so the step after it counts as coming from the node before it
            via = prev if (n["kind"] == "op" and n["name"] == "Do nothing") else nid
            for cid, lab in outs:
                c = self.N.get(cid)
                if c is None:
                    continue
                tc, m = self.schedule(n, t_run, c, rt)
                if tc - t_run > 800:
                    continue
                stack.append((cid, tc, rt, hist, route + (nid + (f" {lab}" if lab else ""),), sown, m, via))


# ------------------------------------------------------------------------------------------------
# the checks
# ------------------------------------------------------------------------------------------------
def check_timing(nodes, crop_name, rotation=None):
    """Warnings (plain text) from checks A-D."""
    W = []
    tr = Tracer(nodes, crop_name)
    tr.run()
    perm = crop_name.endswith("_Perm") or "Orch" in crop_name or bool((rotation or {}).get("cycle_years"))
    done = set()
    # earliest day each node is reached from each node before it
    via = {}
    for nid, t, missed, route, sown, prev in tr.runs:
        k = (nid, prev)
        if k not in via or t < via[k][0]:
            via[k] = (t, route)
    harvests = {}
    for nid, t, missed, route, sown, prev in tr.runs:
        n = nodes[nid]
        if n["kind"] == "op" and n["name"] in HARVEST_OPS and offset(n["earliest"]) is not None:
            harvests.setdefault(nid, []).append((t, route))
    # A: a probability node either does a step or skips it, and both branches meet again at X. On the skip
    # branch X counts from the probability node's day instead of the step's, so it can run weeks or months
    # early -- a harvest after a skipped pre-harvest herbicide or swathing, harvested in spring.
    for p in nodes.values():
        if p["kind"] != "prob":
            continue
        for s_id in [c for c, _ in p["out"] if c in nodes]:
            S = nodes[s_id]
            if S["kind"] != "op" or S["name"] in ("END", "Sleep / Wait", "Do nothing"):
                continue
            for x_id in [c for c, _ in S["out"] if c in nodes]:
                skip = [v[0] for (xx, pv), v in via.items() if xx == x_id and pv == p["id"]]
                did = [v[0] for (xx, pv), v in via.items() if xx == x_id and pv == s_id]
                if not skip or not did:
                    continue
                t_skip, t_do = min(skip), min(did)
                if t_do - t_skip < SKIP_SHIFT_DAYS or ("A", p["id"], x_id) in done:
                    continue
                # does the shift reach a harvest? Compare the harvest's earliest day on routes that took the skip
                # with routes that did the step -- conditions answered on the day, so a dated step (or a date
                # condition sending the route through one) absorbs the shift.
                lab = next((l for c, l in p["out"] if c == x_id), "")
                skip_el = f"{p['id']} {lab}" if lab else p["id"]
                for h_id, hh in harvests.items():
                    th_skip = [t for t, r in hh if skip_el in r]
                    th_do = [t for t, r in hh if s_id in r]
                    if th_skip and th_do and min(th_do) - min(th_skip) >= SKIP_SHIFT_DAYS:
                        done.add(("A", p["id"], x_id))
                        H = nodes[h_id]
                        W.append(f"When '{s_id}' is skipped (probability node '{p['id']}'), what follows counts from the "
                                 f"probability node's day, around {ddmm(t_skip)}, instead of from '{s_id}', around "
                                 f"{ddmm(t_do)}. '{h_id}' ({H['name']}, {H['earliest']} - {H['latest']}) can then run "
                                 f"around {ddmm(min(th_skip))} instead of {ddmm(min(th_do))}, {min(th_do) - min(th_skip)} "
                                 f"days earlier. Put a Sleep / Wait until the date '{s_id}' would run on the skip branch.")
                        break
    for nid, t, missed, route, sown, prev in tr.runs:
        n = nodes[nid]
        # B: a dated step reached long after its window, so ALMaSS runs it at once
        if missed and n["kind"] == "op" and is_dm(n["earliest"]) and is_dm(n["latest"]) and ("B", nid) not in done:
            end = doy(n["latest"]); since = mod(mod(t) - 1 - end)
            harvest_after_sowing = n["name"] in HARVEST_OPS and sown is not None and t - sown < 120
            if since >= PASSED_DAYS or harvest_after_sowing:
                done.add(("B", nid))
                why = (f"right after sowing ({ddmm(sown)})" if harvest_after_sowing and since < PASSED_DAYS
                       else f"{since} days after its window closed")
                W.append(f"'{nid}' ({n['name']}, {n['earliest']} - {n['latest']}) is reached around {ddmm(t - 1)}, "
                         f"{why}, on the route {' > '.join(route[-4:])}. ALMaSS runs it at once. If it belongs to the "
                         f"next season, put a dated step (or a Sleep / Wait) before it on that route.")
    # C: a probability node whose chance an operation's arrow bypasses (a condition routing around it is design)
    for p in nodes.values():
        if p["kind"] != "prob":
            continue
        for cid, lab in p["out"]:
            m = re.match(r"(\d+(?:\.\d+)?)\s*%", lab or "")
            # only a step meant to be rare: a larger share is usually a choice between alternatives, and an
            # alternative route reaching the step directly is then design (direct sowing after a burndown herbicide)
            if not m or float(m.group(1)) > RARE_PCT or cid not in nodes:
                continue
            c = nodes[cid]
            if c["kind"] != "op" or c["name"] in ("END", "Sleep / Wait", "Do nothing"):
                continue
            others = set()
            for oid, _ in p["out"]:
                if oid != cid:
                    others |= reach_from(nodes, oid)
            if cid in others:
                continue                          # the other branches lead there too: not a gate
            without = reach_without(nodes, tr.start["id"], p["id"]) if tr.start else set()
            bypass = [q["id"] for q in nodes.values() if q["kind"] == "op" and q["name"] != "Do nothing"
                      and q["id"] in without and any(x == cid for x, _ in q["out"])]
            if bypass:
                one = len(bypass) == 1
                W.append(f"'{cid}' ({c['name']}) is meant to happen with {lab} (probability node '{p['id']}'), but "
                         f"{', '.join(repr(b) for b in bypass)} also lead{'s' if one else ''} into it directly, so after "
                         f"{'that step' if one else 'those steps'} it always happens. Send {'that arrow' if one else 'those arrows'} "
                         f"to '{p['id']}' instead.")
    # D: a harvest window that ends well after the plan's own last date
    r = rotation or {}
    if not perm and is_dm(r.get("last_date") or ""):
        last = doy(r["last_date"])
        for n in nodes.values():
            if n["kind"] == "op" and n["name"] in HARVEST_OPS and is_dm(n["latest"]):
                late = mod(doy(n["latest"]) - last)
                if LATE_END_DAYS < late < 200:
                    W.append(f"'{n['id']}' ({n['name']}) may run until {n['latest']}, {late} days after the crop's "
                             f"last date in Rotation Timing ({r['last_date']}). Harvest needs dry weather, so it often "
                             f"waits for the last day. End the window by the last date, or change the last date.")
    return W


def reach_from(nodes, nid):
    seen, todo = set(), [nid]
    while todo:
        x = todo.pop()
        if x in seen or x not in nodes:
            continue
        seen.add(x)
        todo += [c for c, _ in nodes[x]["out"]]
    return seen


def reach_without(nodes, start, skip):
    """Nodes reachable from start without passing through skip."""
    seen, todo = set(), [start]
    while todo:
        x = todo.pop()
        if x in seen or x == skip or x not in nodes:
            continue
        seen.add(x)
        todo += [c for c, _ in nodes[x]["out"]]
    return seen


def harvest_downstream(nodes, nid):
    """A harvest-type step with an offset start reachable from nid through steps without dates of their own
    (probability and condition nodes, "+N days" steps, "Do nothing"); None if there is none."""
    seen, todo = set(), [nid]
    while todo:
        x = todo.pop()
        if x in seen or x not in nodes:
            continue
        seen.add(x)
        n = nodes[x]
        if n["kind"] == "op" and n["name"] in HARVEST_OPS and offset(n["earliest"]) is not None:
            return x
        if n["kind"] == "op" and n["name"] not in ("Do nothing",) and is_dm(n["earliest"]) and x != nid:
            continue                                  # a dated step absorbs the shift
        if n["kind"] == "op" and n["name"] == "END":
            continue
        todo += [c for c, _ in n["out"]]
    return None
