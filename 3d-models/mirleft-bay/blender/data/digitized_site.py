"""
Digitised site data for Mirleft Bay. Pure data, no Blender.

PLAN PX = pixel coordinates on F01 (plan de masse A000-023, 1/500), page image rotated
+90 deg so that the ocean is on the left ("masse_rot.png", 7348 x 3596 px).
1 px = 1866 mm / 7348 px x 500 = 0.12697 m. The scale was checked against the plot area
(digitised 82 350 m2 vs title 82 070 m2, +0.3 %).

GE PX = pixel coordinates on the client's Google Earth screenshot (IMG_17, north-up,
400 m scale bar = 176.6 px).

Status of every value: INFERRED (read off the scanned plan, +/- 10 px = +/- 1.3 m)
unless a comment says otherwise.
"""

M_PER_PX = 1866.0 / 7348.0 * 500.0 / 1000.0
GE_M_PER_PX = 400.0 / 176.6
GE_SITE_CENTROID_PX = (711.5, 495.9)        # centroid of the client's traced polygon
AXIS_BEARING_DEG = 122.5                     # plan +X (towards road R104), true bearing; IoU fit to the client GE polygon (registration.json)

# ---------------------------------------------------------------------------
# Villa lot grids: (tranche, type, x-columns, y-rows). Pool sits on the west side
# of each lot, house to the east of the pool (as drawn on F01).
# ---------------------------------------------------------------------------
LOT_GRIDS = [
    # T5 villa B: 2 x 3 = 6   (permit: 6 B)
    ("T5", "B", [(3082, 3268), (3268, 3455)], [(1986, 2120), (2120, 2255), (2255, 2390)]),
    # T5 villa C: 3 x 2 = 6   (permit: 6 C)
    ("T5", "C", [(2900, 3060), (3060, 3220), (3220, 3382)], [(2450, 2632), (2672, 2860)]),
    # T4 villa B: 2 x 3 = 6   (permit: 6 B)
    ("T4", "B", [(3491, 3663), (3663, 3836)], [(1963, 2104), (2104, 2245), (2245, 2386)]),
    # T4 villa C: 3 x 2 = 6, + 1 below = 7   (permit: 7 C)
    ("T4", "C", [(3382, 3540), (3540, 3698), (3698, 3855)], [(2450, 2615), (2655, 2820)]),
    ("T4", "C", [(3698, 3855)], [(2830, 2990)]),
    # T3 villa B north: 3 x 3 = 9, south: 4 x 3 = 12 -> 21   (permit: 21 B)
    ("T3", "B", [(3900, 4060), (4105, 4280), (4330, 4520)], [(1985, 2140), (2140, 2290), (2290, 2425)]),
    ("T3", "B", [(3907, 4053), (4053, 4216), (4216, 4380), (4380, 4525)], [(2460, 2650), (2715, 2850), (2850, 2990)]),
]

# Villa A (T6): 4 lots in one column, long pool on the west side (permit: 4 A, RDC, 220 m2)
VILLA_A_LOTS = [((2105, 2345), (2018, 2163)), ((2105, 2345), (2200, 2382)),
                ((2105, 2345), (2545, 2690)), ((2105, 2345), (2727, 2910))]

# Duplex pair buildings (two mirrored units, split along plan-y). (x0, x1, y0, y1)
DUPLEX_PAIRS = {
    "T1": [  # 12 pairs = 24 units (permit: 24 duplex)
        (4792, 4897, 2153, 2274), (4792, 4897, 2379, 2500), (4792, 4897, 2605, 2732),
        (4992, 5092, 2037, 2158), (4992, 5092, 2258, 2384), (4992, 5092, 2489, 2616),
        (5160, 5266, 2010, 2131), (5160, 5266, 2189, 2310), (5160, 5266, 2389, 2510), (5160, 5266, 2532, 2658),
        (5329, 5445, 1989, 2121), (5329, 5445, 2179, 2300),
    ],
    "T2": [  # 5 pairs = 10 units (permit: 10 duplex); hidden under the red tint, evenly spaced
        (4615, 4725, 1992, 2112), (4615, 4725, 2176, 2296), (4615, 4725, 2360, 2480),
        (4615, 4725, 2544, 2664), (4615, 4725, 2728, 2848),
    ],
}

# Public buildings (catalogue 2026 names, positions from F01). levels = storeys.
PUBLIC_BUILDINGS = [
    # name, (x0, x1, y0, y1), levels, style
    ("PAVILLON_RESTAURANT_CLUBHOUSE", (5590, 5780, 2280, 2410), 2, "kasbah"),   # permit: club house RDC+1 353 m2
    ("MARKET_SUPERETTE", (5560, 5740, 1960, 2050), 1, "kasbah"),              # permit: superette + cafeteria 275 m2
    ("RECEPTION_ADMINISTRATION", (5480, 5600, 2060, 2160), 2, "kasbah_towers"),  # permit: admin 200 m2; F04 style
    ("SPA", (2930, 3040, 2050, 2330), 1, "kasbah"),                            # catalogue: SPA (T5 north-west); east side trimmed for street 5
    ("HOTEL_WING_NORTH", (2668, 2760, 2027, 2400), 2, "kasbah"),              # permit: hotel RDC+1 1520 m2
    ("HOTEL_WING_SOUTH", (2668, 2760, 2464, 2964), 2, "kasbah"),
    ("BEACH_CLUB", (1385, 1470, 1880, 1960), 1, "light"),                     # catalogue: beach club at the corniche
]

SPORTS_COURT = (5712, 5828, 1850, 2010)       # catalogue: terrain de sport
HOTEL_POOL_STRIP = (2423, 2452, 2040, 2950)   # long water channel in the hotel garden
VILLA_A_POOL_W = 27                           # px (3.4 m)

# Lake basins (T6), hand-digitised ellipse boxes (x0, x1, y0, y1) + the round feature
LAKE_BASINS = [(1703, 2050, 2033, 2267), (1803, 1997, 2273, 2447), (1703, 1983, 2487, 2640)]
LAKE_ROUND = ((1703, 2373), 80)
LAKE_ALLEE = (1900, 2780, 2427, 2463)         # pedestrian axis from the lake to the hotel

# Club pools in T1 (auto-traced from F01)
T1_POOLS = [
    [[5384, 2492], [5384, 2503], [5395, 2518], [5403, 2541], [5404, 2565], [5430, 2587], [5449, 2577], [5461, 2577], [5474, 2586], [5482, 2586], [5512, 2564], [5563, 2566], [5569, 2562], [5568, 2539], [5556, 2529], [5553, 2515], [5527, 2511], [5501, 2496], [5488, 2476], [5483, 2475], [5479, 2462], [5481, 2442], [5466, 2430], [5438, 2431], [5433, 2435], [5424, 2466], [5404, 2484], [5392, 2484]],
    [[5828, 2423], [5781, 2421], [5776, 2429], [5762, 2432], [5761, 2438], [5743, 2431], [5720, 2435], [5710, 2444], [5711, 2466], [5718, 2467], [5714, 2483], [5725, 2483], [5730, 2492], [5749, 2492], [5766, 2480], [5775, 2467], [5820, 2461], [5820, 2453], [5827, 2448]],
]

# Green / garden blocks (raised kerbed plots). Everything else inside the site = road / paving.
GREEN_BLOCKS = [
    ("T6_LAKE_PARK", None),                       # computed: site west of x=2100
    ("T6_VILLA_A", (2100, 2350, 1995, 2985)),
    ("T6_HOTEL", (2405, 2768, 1990, 2990)),
    ("T5_NORTH", (2900, 3460, 1985, 2390)),
    ("T5_SOUTH", (2900, 3382, 2450, 2860)),
    ("T4_NORTH", (3491, 3836, 1963, 2386)),
    ("T4_SOUTH", (3382, 3860, 2450, 3010)),
    ("T3_NORTH", (3900, 4522, 1985, 2425)),
    ("T3_SOUTH", (3907, 4525, 2460, 3000)),
    ("T2", (4592, 4745, 1960, 2900)),
    ("T1_COL_A", (4770, 4910, 1990, 2900)),
    ("T1_COL_B", (4975, 5110, 1990, 2760)),
    ("T1_COL_C", (5140, 5290, 1985, 2760)),
    ("T1_COL_D", (5310, 5465, 1960, 2340)),
    ("T1_CLUB", (5340, 5880, 2260, 2620)),
    ("T1_NORTH_PLAZA", (5465, 5770, 1940, 2170)),
]

# Spot heights read off F01 (plan px, metres). Mostly outside the plot (ravines and
# plateau edges). +/- 2 m positional accuracy.
SPOT_HEIGHTS = [
    (1350, 1927, 8.14), (1214, 1773, 18.36), (1595, 1991, 28.92), (1777, 1709, 26.36), (1850, 1736, 27.81),
    (2241, 1736, 33.15), (2350, 1796, 40.00), (2423, 1736, 43.06), (2677, 1755, 45.21), (3036, 1695, 50.00),
    (3918, 1723, 55.90), (4173, 1686, 57.45), (4391, 1777, 58.45), (4627, 1786, 59.39), (5014, 1705, 60.00),
    (5114, 1723, 60.97), (5341, 1705, 61.70), (5595, 1677, 62.60), (5832, 1668, 63.28),
    (1295, 2882, 15.00), (1395, 2945, 19.09), (1614, 2851, 12.93), (1668, 2855, 15.24), (1750, 2909, 14.73),
    (1868, 2918, 16.27), (1841, 2982, 11.76), (1914, 3040, 12.43), (2077, 3055, 13.45), (2386, 3091, 15.67),
    (1777, 3145, 21.83), (2005, 3173, 20.00), (2505, 3209, 16.89), (2732, 3245, 18.07), (2905, 3055, 28.49),
    (2914, 3145, 23.71), (3173, 3000, 29.66), (3355, 2986, 27.00), (3173, 3095, 24.37), (3300, 3105, 21.78),
    (3369, 3032, 22.90), (3491, 3068, 24.87), (3845, 3159, 32.69), (3882, 3214, 35.02), (3627, 3268, 39.21),
    (4500, 3268, 45.35), (5086, 2986, 55.00), (5341, 2623, 55.13), (5577, 2595, 56.45), (5741, 2577, 58.14),
    (5923, 2559, 58.96), (5777, 2932, 60.00), (5905, 3005, 61.64), (6141, 2850, 63.34),
]
# Google Earth elevation over the client's polygon: min 18.72, median 51.28, max 64.99 m (CONFIRMED F08).

# Google Earth hand-traced context (GE px). Shoreline = wet-sand / surf edge, N -> S.
GE_SHORELINE = [(585, 126), (588, 180), (575, 240), (560, 282), (540, 318), (522, 345), (505, 366),
                (482, 390), (455, 410), (420, 432), (380, 462), (340, 500), (300, 545), (268, 590),
                (240, 640), (214, 690), (190, 740), (168, 788)]
GE_BEACH_BACK = [(640, 126), (643, 200), (640, 260), (630, 315), (612, 360), (598, 392), (585, 405),
                 (560, 412), (530, 418)]        # back edge of the sand (foot of the slope)
GE_ROAD_R104 = [(912, 126), (895, 250), (882, 360), (868, 470), (845, 580), (820, 660), (790, 730), (758, 788)]


# ---------------------------------------------------------------------------
# Added 2026-10-02 after client review (catalogue p6 + plan F01): water features and parking
# ---------------------------------------------------------------------------
# Central avenue canal (blue strip on the plan): (x0, x1, y0, y1)
CANALS = [(2860, 3862, 2412, 2424), (3912, 4560, 2428, 2440)]
CANAL_STRIP = 12                 # px of stone coping on each side
# Hotel garden: T-shaped water (cross branch at the "HOTEL" label) + wide basin
HOTEL_WATER = [(2423, 2452, 2040, 2950), (2440, 2720, 2366, 2396), (2452, 2510, 2232, 2366), (2452, 2510, 2396, 2530)]
# Entrance plaza (T1): long reflecting pool + half-moon basin
PLAZA_POOL = (5848, 6130, 2204, 2236)         # entrance mall channel (masterplan: from the roundabout to R104)
PLAZA_HALFMOON = ((5752, 2292), 22)
# Parking rows: (start px, end px, bay depth m, side +1 = left of the direction, -1 = right)
PARKING_ROWS = [   # (start px, end px, bay length m, side hint, angle deg); the side with asphalt wins
    ((2790, 2090), (2790, 2340), 5.0, -1, 45),     # hotel public parking (north), angled as on the masterplan
    ((2790, 2560), (2790, 2910), 5.0, -1, 45),     # hotel public parking (south)
    ((4735, 1985), (5320, 1945), 5.0, +1, 45),     # north ring road above the duplexes
    ((5470, 1940), (5700, 1940), 5.0, +1, 45),     # north ring road, in front of the market
    ((3960, 3055), (4500, 3062), 5.0, +1, 45),     # south ring road, T3
    ((5440, 2600), (5660, 2585), 5.0, -1, 45),     # south ring road, club
    ((5887, 1790), (5887, 2140), 5.0, +1, 45),     # entrance north street, east kerb (faces the lot aisle)
    ((5960, 2292), (6220, 2292), 5.0, +1, 45),     # mall south carriageway, south kerb
    ((5944, 2420), (5944, 2590), 5.0, +1, 45),     # entrance south street, east kerb
]


# ---------------------------------------------------------------------------
# Added 2026-10-02 (client review of the catalogue masterplan, p6): street network and
# entrance parking. Grey asphalt carriageways with white markings, as on the masterplan
# (the as-built photo F04 shows beige pavers on one access: CONFLICTING, client asked for
# the masterplan streets). Positions follow the gaps of the permit plan F01.
# ---------------------------------------------------------------------------
ROAD_PERIMETER_SIDEWALK = 4.5          # m of beige pavers along the plot edge (street palms)
ROAD_ASPHALT_X_MIN = 2090              # west of this the plot is park / beach club paths
# streets cut through the villa blocks (x0, x1, y0, y1)
ROAD_CUTS = [
    (2900, 3382, 2632, 2672),          # road 7 (villa C rows, T5)
    (3382, 3860, 2615, 2655),          # road 7 (villa C rows, T4)
    (3860, 3907, 2615, 2715),          # road 7 crossing the boulevard
    (3907, 4525, 2650, 2715),          # road 7 (villa B rows, T3)
    (3046, 3082, 1985, 2392),          # street 5 between the SPA and the villa B lots
    (4060, 4105, 1985, 2425),          # street 6.2 west (T3 north)
    (4280, 4330, 1985, 2425),          # street 6.2 east (T3 north)
]
# pedestrian zones inside the street grid (stay beige pavers)
ROAD_PEDESTRIAN = [
    (2880, 3836, 2380, 2455),          # canal promenade, west of the boulevard
    (3907, 4592, 2418, 2465),          # canal promenade, east of the boulevard
    (4745, 5465, 1990, 2905),          # duplex quarter: beige paths (catalogue)
]
# dashed centre lines (plan px polylines)
ROAD_CENTRELINES = [
    [(3868, 1990), (3868, 2390), (3872, 2450), (3883, 3000)],     # boulevard 6
    [(2900, 2652), (3382, 2652), (3382, 2635), (3860, 2635), (3883, 2665), (3907, 2682), (4525, 2682)],   # road 7
    [(4557, 1990), (4557, 2990)],                                   # street 7 (T3 / T2)
    [(2834, 2000), (2834, 2990)],                                   # hotel street 10 / 14
    [(5858, 1770), (5858, 2180)],                                   # entrance north street
    [(5912, 2262), (5912, 2580)],                                   # entrance south street
]
ROUNDABOUT = ((5800, 2220), 40, 16)    # centre px, outer radius px (5 m), planted island px (2 m): west end of the mall
ENTRANCE_ACCESS = ((5800, 2220), (6320, 2220), 150)   # mall carriageways to R104: from, to, width px (19 m incl. median)
MALL_ISLAND = (5848, 6130, 2192, 2248)                  # planted median around the channel (trees both sides)
# streets of the entrance quarter (kept free of parking): (x0, x1, y0, y1)
ENTRANCE_STREETS = [
    (5832, 5885, 1760, 2190),          # north street: ring road -> roundabout (east of the sports court)
    (5885, 5940, 2250, 2590),          # south street: roundabout -> south ring road
    (5770, 6320, 2150, 2192),          # mall north carriageway
    (5770, 6320, 2248, 2290),          # mall south carriageway
]
# entrance parking lots: 45 deg bay rows along the plot-edge kerb inside these boxes, facing the
# rows along the street kerbs across a shared aisle (PARKING_ROWS). The permit plot leaves ~0.2 ha
# here, less than the catalogue drawing suggests, so the lots are single aisles. (x0, x1, y0, y1)
PARKING_LOTS = [
    (5888, 6260, 1700, 2148),          # north-east lot, beside the sports court
    (5944, 6280, 2292, 2600),          # south-east lot
]
DROP_OFF = (5948, 6022, 2298, 2410)    # hatched drop-off / coach bay (masterplan grey hatched zone)
# zebra crossings: centre px, road direction ("x" / "y" in plan), road width m
ZEBRAS = [((3870, 2378), "y", 8.0), ((3880, 2468), "y", 7.0), ((3883, 2700), "y", 7.0), ((3830, 2635), "x", 5.0),
          ((4557, 2440), "y", 8.5), ((2834, 2381), "y", 9.0), ((5858, 2140), "y", 6.5), ((5912, 2300), "y", 6.5)]

