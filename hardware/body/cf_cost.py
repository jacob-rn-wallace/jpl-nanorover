"""Cost of one carbon body: bonded woven plates versus pressed forged carbon in 3D-printed moulds.

Run: python3 hardware/body/cf_cost.py   (no CAD needed).
Every input is tagged SRC (a vendor page, see docs/body-redesign.md) or ASM (my assumption). Output is low / mid / high in US dollars.
NOT included: shipping, import duty, dangerous-goods surcharges on resin (Easy Composites flags its kit as such), tax, and your time.
Exchange rates are assumptions (today's were not checked): 1 GBP = 1.30 USD, 1 ZAR = 0.055 USD.
"""
import math
GBP, ZAR = 1.30, 0.055
AREA = 728.0                    # cm2, outer surface of the box (six faces); plate area is within a few percent of this
NEST = 1.5                      # ASM: sheet area needed per part area, for nesting waste

def row(name, lo, mid, hi): return (name, lo, mid, hi)

def woven(N):
    sheets = math.ceil(N * AREA * NEST / 2350)                 # a 500 x 470 mm sheet is 2350 cm2
    price_sheet = (257.78 * 0.235 * GBP,  # SRC: Easy Composites 1 mm twill, GBP 257.78 per m2 ex VAT, so GBP 60.6 for 500 x 470 (the GBP 14.50 headline is the 250 x 230 sheet)
                   110.0,                 # ASM: a US supplier at a higher price per m2
                   189.0)                 # SRC (unconfirmed, search snippet): Rock West 600 x 600 x 1 mm twill, USD 188.99
    rate = (1.72 * ZAR, 0.15, 0.25)       # per cm2 of cut part: low SRC (Flying Robot, South Africa, ZAR 1.72/cm2 for 1 mm, 100 cm2 minimum, quote by DXF); mid and high ASM
    setup = (0, 40, 100)                  # ASM: order setup fee
    glue = (25, 40, 60)                   # ASM: structural adhesive, edge-sealing epoxy, printed keys, a bonding jig
    out = []
    for i in range(3):
        c = sheets * price_sheet[i] + setup[i] + N * AREA * rate[i] + glue[i] + (N - 1) * glue[i] * 0.5
        out.append(c)
    return out

def forged(N, pressure_tool=True):
    # per part: the guide's recipe (Easy Composites): fibre 60% of the finished part mass, mixed resin 25% over the fibre weight, excess squeezed out
    wall = 1.5                                                  # mm: Easy Composites calls 1.5 mm "very much towards the lower limit"
    part_g = AREA * wall / 10 * 1.5                              # g at 1.5 g/cm3 (SRC density)
    fibre_g, resin_g = 0.6 * part_g, 0.6 * part_g * 1.25
    mat = (fibre_g * 8.65 / 150 * GBP + resin_g * 22.0 / 1000 * GBP,       # SRC: CT12 chopped tow GBP 8.65 per 150 g, IN2 fast resin GBP 22 per kg (ex VAT)
           fibre_g * 0.45 + resin_g * 0.10,                                  # ASM: US supplier; Rock West kit USD 269.99 for 1.5 lb (SRC, unconfirmed) is about USD 0.40 per g of fibre incl. resin
           269.99 / (680 / fibre_g))                                         # SRC (snippet): whole Rock West kit divided into parts by fibre weight
    waste = 1.25                                                # ASM: tow and resin lost to trimming and spills
    consum_once = (30, 40, 60)                                   # ASM: release wax, wipes, gloves, abrasives, brushes (the EC kit includes wax and gloves)
    consum_part = (5, 10, 15)                                    # ASM: sanding, clearcoat share
    mould_print = (40, 55, 80)                                   # ASM: about 2 kg PETG at USD 20-25/kg for the cavity block and the plug, plus failed prints (print time alone about 140 h, my estimate)
    mould_finish = (30, 45, 80)                                  # ASM: sealing and surface-coating the printed faces (FDM layer lines transfer to the part: SRC, Easy Composites)
    life = (10, 5, 2)                                            # ASM parts per printed mould (Easy Composites: "short runs and one-off prototypes", no count given)
    scrap = (1, 3, 5)                                            # ASM: parts lost while learning a 55 mm deep 1.5 mm tub
    press = (0, 60, 250)                                         # ASM: low = a bench vice you own; mid = clamps and plywood platens; high = a 12-ton shop press. Needed force not sourced
    out = []
    for i in range(3):
        moulds = math.ceil((N + scrap[i]) / life[i])
        c = (moulds * (mould_print[i] + mould_finish[i]) + press[i] + consum_once[i]
             + (N + scrap[i]) * (mat[i] * waste + consum_part[i]))
        out.append(c)
    return out, part_g

print(f"{'parts built':>11s} | {'bonded woven plates':^28s} | {'forged, printed moulds':^28s}")
print(f"{'':>11s} | {'low':>8s}{'mid':>9s}{'high':>9s}  | {'low':>8s}{'mid':>9s}{'high':>9s}")
for N in (1, 2, 5, 20):
    w = woven(N); f, pg = forged(N)
    print(f"{N:11d} | " + "".join(f"{v:9.0f}" for v in w) + "   | " + "".join(f"{v:9.0f}" for v in f))
print(f"\nper-part cost at N = 20 (mid): woven {woven(20)[1]/20:.0f}, forged {forged(20)[0][1]/20:.0f}")
print(f"forged shell mass at 1.5 mm: {forged(1)[1]:.0f} g; at 2.0 mm it would be {AREA*2/10*1.5:.0f} g. Woven 1.0 mm plates: {AREA*1/10*1.55:.0f} g plus about 25-30 g of keys and adhesive (my estimate).")
print("Hours (my estimates, not priced): woven plates about 8 h; forged about 140 h unattended printing, 8 h CAD, 10 h mould finishing, 4 h per trial pressing (cure time not stated by the source), 6 h per part finishing.")
