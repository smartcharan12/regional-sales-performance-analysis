"""
Generate the synthetic RetailCo sales dataset (data/raw/sales_raw.csv).

WHY SYNTHETIC?
Public datasets such as Tableau's "Sample - Superstore" have unclear
redistribution terms and are already used in thousands of portfolios.
Instead, this script builds a dataset with the SAME column layout as
Superstore, using explicit, documented business rules. Every pattern in the
data comes from a rule written below, so nothing is hidden.

HOW THE NUMBERS ARE BUILT (one order line)
    list_price   = product's catalogue price per unit
    Sales        = list_price x Quantity x (1 - Discount)
    Cost         = list_price x Quantity x (1 - base_margin)
    Profit       = Sales - Cost  (+ small random noise)
                 = list_price x Quantity x (base_margin - Discount)
So a line loses money whenever Discount > the product's base margin.

DELIBERATE DATA-QUALITY PROBLEMS
Real exports are messy, so after building clean data we inject a small,
known number of realistic errors (duplicates, typos, missing values, bad
dates ...). They are listed in `inject_quality_issues` and are what
src/data_cleaning.py has to find and fix.

The random seed is fixed, so running this script always produces the
identical file -> the whole project is reproducible.
"""

import numpy as np
import pandas as pd

from utils import DATA_RAW, RAW_FILE, STATE_TO_REGION

SEED = 42
START_DATE = "2021-01-01"
END_DATE = "2024-12-31"
N_ORDERS = 5_200
N_CUSTOMERS = 780

# ---------------------------------------------------------------------------
# Business rules (assumptions) that shape the data
# ---------------------------------------------------------------------------
CITIES = {
    "West": [("Los Angeles", "California"), ("San Francisco", "California"),
             ("San Diego", "California"), ("Seattle", "Washington"),
             ("Portland", "Oregon"), ("Phoenix", "Arizona"),
             ("Denver", "Colorado"), ("Salt Lake City", "Utah"),
             ("Las Vegas", "Nevada")],
    "East": [("New York City", "New York"), ("Buffalo", "New York"),
             ("Philadelphia", "Pennsylvania"), ("Pittsburgh", "Pennsylvania"),
             ("Columbus", "Ohio"), ("Cleveland", "Ohio"),
             ("Boston", "Massachusetts"), ("Newark", "New Jersey"),
             ("Baltimore", "Maryland"), ("Hartford", "Connecticut")],
    "Central": [("Houston", "Texas"), ("Dallas", "Texas"),
                ("San Antonio", "Texas"), ("Chicago", "Illinois"),
                ("Detroit", "Michigan"), ("Minneapolis", "Minnesota"),
                ("Milwaukee", "Wisconsin"), ("Kansas City", "Missouri"),
                ("Indianapolis", "Indiana")],
    "South": [("Jacksonville", "Florida"), ("Miami", "Florida"),
              ("Atlanta", "Georgia"), ("Charlotte", "North Carolina"),
              ("Nashville", "Tennessee"), ("Richmond", "Virginia"),
              ("Louisville", "Kentucky"), ("Birmingham", "Alabama")],
}

# Share of customers living in each region (West/East are bigger markets)
REGION_CUSTOMER_SHARE = {"West": 0.32, "East": 0.29, "Central": 0.23, "South": 0.16}

# Yearly growth in order volume per region (compound). South is shrinking.
REGION_GROWTH = {"West": 0.15, "East": 0.11, "Central": 0.02, "South": -0.07}

# Discount policy per region: probabilities over discount levels.
# Central's sales teams discount far more aggressively than the others.
DISCOUNT_LEVELS = [0.0, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
REGION_DISCOUNT_PROBS = {
    "West":    [0.52, 0.06, 0.04, 0.30, 0.03, 0.02, 0.01, 0.01, 0.005, 0.005],
    "East":    [0.50, 0.07, 0.04, 0.28, 0.04, 0.03, 0.02, 0.01, 0.005, 0.005],
    "South":   [0.48, 0.07, 0.04, 0.27, 0.05, 0.03, 0.03, 0.02, 0.005, 0.005],
    "Central": [0.42, 0.06, 0.04, 0.24, 0.07, 0.05, 0.04, 0.04, 0.02, 0.02],
}
# Certain sub-categories are discounted more (clearance-prone, bulky items)
SUBCAT_DISCOUNT_BOOST = {"Tables": 0.18, "Bookcases": 0.12, "Machines": 0.10,
                         "Binders": 0.08}

# Month-of-year demand weights: quiet Jan/Feb, back-to-school Sep, Q4 peak
MONTH_WEIGHTS = {1: 0.60, 2: 0.55, 3: 0.95, 4: 0.75, 5: 0.80, 6: 0.85,
                 7: 0.75, 8: 0.85, 9: 1.40, 10: 0.95, 11: 1.45, 12: 1.50}

SEGMENT_SHARE = {"Consumer": 0.52, "Corporate": 0.30, "Home Office": 0.18}

SHIP_MODES = {  # mode: (probability, min shipping days, max shipping days)
    "Standard Class": (0.60, 4, 7), "Second Class": (0.20, 2, 5),
    "First Class": (0.15, 1, 3), "Same Day": (0.05, 0, 0),
}

# Sub-category: (category, unit price range, base gross margin, demand weight)
SUBCATEGORIES = {
    "Chairs":      ("Furniture",       (90, 650),  0.26, 0.060),
    "Tables":      ("Furniture",       (180, 900), 0.08, 0.035),
    "Bookcases":   ("Furniture",       (90, 500),  0.12, 0.025),
    "Furnishings": ("Furniture",       (8, 120),   0.32, 0.090),
    "Binders":     ("Office Supplies", (4, 60),    0.38, 0.150),
    "Paper":       ("Office Supplies", (6, 45),    0.45, 0.135),
    "Storage":     ("Office Supplies", (20, 260),  0.22, 0.085),
    "Art":         ("Office Supplies", (3, 40),    0.30, 0.080),
    "Appliances":  ("Office Supplies", (30, 400),  0.30, 0.045),
    "Labels":      ("Office Supplies", (3, 25),    0.42, 0.035),
    "Envelopes":   ("Office Supplies", (5, 50),    0.40, 0.025),
    "Fasteners":   ("Office Supplies", (2, 20),    0.30, 0.020),
    "Supplies":    ("Office Supplies", (8, 120),   0.12, 0.020),
    "Phones":      ("Technology",      (60, 900),  0.24, 0.090),
    "Accessories": ("Technology",      (12, 250),  0.28, 0.075),
    "Machines":    ("Technology",      (250, 2500), 0.22, 0.012),
    "Copiers":     ("Technology",      (600, 2400), 0.34, 0.018),
}

# Word lists used to build fictional (non-brand) product names
NAME_PARTS = {
    "Chairs": (["ErgoFlex", "Comfort+", "Executive", "Mesh Task", "Stacking"], ["Chair", "Office Chair", "Guest Chair"]),
    "Tables": (["Conference", "Round", "Rectangular", "Folding", "Training"], ["Table", "Work Table"]),
    "Bookcases": (["Open", "5-Shelf", "3-Shelf", "Barrister", "Corner"], ["Bookcase", "Shelving Unit"]),
    "Furnishings": (["Desk", "Wall", "LED", "Frame", "Floor"], ["Lamp", "Clock", "Mat", "Organizer"]),
    "Binders": (["Ring", "Presentation", "Heavy-Duty", "Clear-View", "Poly"], ["Binder", "Binder Set"]),
    "Paper": (["Copy", "Recycled", "Premium", "Colour", "Laser"], ["Paper Ream", "Paper Pack"]),
    "Storage": (["Rolling", "Stackable", "Locking", "Archive", "Wire"], ["Storage Box", "File Cart", "Drawer Unit"]),
    "Art": (["Fine-Tip", "Highlighter", "Pencil", "Marker", "Crayon"], ["Set", "Pack"]),
    "Appliances": (["Compact", "Desktop", "Quiet", "Smart", "Heavy-Duty"], ["Shredder", "Air Purifier", "Microwave", "Heater"]),
    "Labels": (["Address", "Shipping", "Colour-Coded", "Removable"], ["Labels"]),
    "Envelopes": (["Security", "Window", "Padded", "Kraft"], ["Envelopes"]),
    "Fasteners": (["Jumbo", "Mini", "Assorted", "Coloured"], ["Paper Clips", "Push Pins", "Rubber Bands"]),
    "Supplies": (["Steel", "Precision", "Desktop", "Titanium"], ["Scissors", "Trimmer", "Letter Opener"]),
    "Phones": (["Nova", "Pulse", "Vertex", "Orbit", "Zen"], ["Smartphone", "Conference Phone", "IP Phone"]),
    "Accessories": (["Wireless", "USB-C", "Bluetooth", "Ergonomic"], ["Mouse", "Keyboard", "Headset", "Hub"]),
    "Machines": (["Office", "Wide-Format", "Industrial", "Compact"], ["Printer", "Label Maker", "Binding Machine"]),
    "Copiers": (["Colour", "Mono", "Multifunction"], ["Copier", "Copier Pro"]),
}

FIRST_NAMES = ["Aarav", "Maya", "Liam", "Sofia", "Noah", "Priya", "Ethan", "Olivia",
               "Lucas", "Ava", "Mateo", "Zara", "Owen", "Chloe", "Ravi", "Emma",
               "Daniel", "Hana", "Leo", "Grace", "Omar", "Isla", "Samuel", "Nina",
               "Jonah", "Elena", "Kai", "Lena", "Ryan", "Mei"]
LAST_NAMES = ["Patel", "Garcia", "Kim", "Nguyen", "Johnson", "Okafor", "Silva",
              "Brown", "Rossi", "Khan", "Martin", "Lopez", "Walker", "Chen",
              "Hughes", "Reddy", "Novak", "Murphy", "Sato", "Fischer", "Diaz",
              "Clark", "Ahmed", "Moreau", "Evans"]


def build_products(rng: np.random.Generator) -> pd.DataFrame:
    """Create the product catalogue: ID, name, category, price and margin."""
    rows = []
    for sub, (category, (lo, hi), margin, weight) in SUBCATEGORIES.items():
        prefixes, suffixes = NAME_PARTS[sub]
        n_products = max(6, int(weight * 160))
        names = set()
        while len(names) < n_products:
            names.add(f"{rng.choice(prefixes)} {rng.choice(suffixes)} "
                      f"{rng.choice(list('ABCDEFGHJKLMNPRSTVWXZ'))}{rng.integers(100, 999)}")
        for i, name in enumerate(sorted(names)):
            rows.append({
                "Product ID": f"{category[:3].upper()}-{sub[:2].upper()}-{1000 + i}",
                "Product Name": name,
                "Category": category,
                "Sub-Category": sub,
                # log-uniform price: many cheap items, few expensive ones
                "list_price": round(float(np.exp(rng.uniform(np.log(lo), np.log(hi)))), 2),
                # each product's margin varies a little around its sub-category's
                "base_margin": float(np.clip(margin + rng.normal(0, 0.04), -0.05, 0.6)),
                "weight": weight / n_products,
            })
    return pd.DataFrame(rows)


def build_customers(rng: np.random.Generator) -> pd.DataFrame:
    """Create customers, each with a segment and a home city/state/region."""
    regions = rng.choice(list(REGION_CUSTOMER_SHARE), size=N_CUSTOMERS,
                         p=list(REGION_CUSTOMER_SHARE.values()))
    names = set()
    rows = []
    for i, region in enumerate(regions):
        city, state = CITIES[region][rng.integers(len(CITIES[region]))]
        name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
        while name in names:  # keep names unique so they identify one person
            name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)} {rng.choice(list('ABCDEFGHJK'))}."
        names.add(name)
        initials = "".join(part[0] for part in name.split()[:2])
        rows.append({
            "Customer ID": f"{initials}-{10000 + i}",
            "Customer Name": name,
            "Segment": rng.choice(list(SEGMENT_SHARE), p=list(SEGMENT_SHARE.values())),
            "City": city, "State": state, "Region": region,
            # a few customers buy much more often than others (realistic skew)
            "activity": float(rng.lognormal(0, 0.8)),
        })
    return pd.DataFrame(rows)


def order_dates(rng: np.random.Generator, region: str, n: int) -> pd.DatetimeIndex:
    """Sample n order dates using seasonality and the region's growth trend."""
    days = pd.date_range(START_DATE, END_DATE, freq="D")
    years_since_start = (days.year - days.year.min()) + days.dayofyear / 365
    weights = (np.array([MONTH_WEIGHTS[m] for m in days.month])
               * (1 + REGION_GROWTH[region]) ** np.asarray(years_since_start)
               * np.where(days.dayofweek >= 5, 0.6, 1.0))  # fewer weekend orders
    return pd.DatetimeIndex(rng.choice(days, size=n, p=weights / weights.sum()))


def build_clean_orders(rng: np.random.Generator) -> pd.DataFrame:
    products = build_products(rng)
    customers = build_customers(rng)
    lines = []

    # Split total orders across regions in proportion to customer activity
    activity_by_region = customers.groupby("Region")["activity"].sum()
    orders_by_region = (activity_by_region / activity_by_region.sum() * N_ORDERS).round().astype(int)

    order_seq = 0
    for region, n_orders in orders_by_region.items():
        region_customers = customers[customers["Region"] == region]
        cust_p = region_customers["activity"] / region_customers["activity"].sum()
        dates = order_dates(rng, region, n_orders)
        for order_date in dates:
            order_seq += 1
            cust = region_customers.iloc[rng.choice(len(region_customers), p=cust_p)]
            ship_mode = rng.choice(list(SHIP_MODES), p=[v[0] for v in SHIP_MODES.values()])
            _, dmin, dmax = SHIP_MODES[ship_mode]
            ship_date = order_date + pd.Timedelta(days=int(rng.integers(dmin, dmax + 1)))
            order_id = f"US-{order_date.year}-{100000 + order_seq}"

            n_lines = rng.choice([1, 2, 3, 4, 5], p=[0.38, 0.27, 0.18, 0.11, 0.06])
            picked = rng.choice(len(products), size=n_lines, replace=False,
                                p=products["weight"] / products["weight"].sum())
            for idx in picked:
                prod = products.iloc[idx]
                # cheap items are bought in larger quantities, expensive ones singly
                max_qty = 3 if prod["list_price"] > 600 else 6 if prod["list_price"] > 150 else 10
                qty = int(rng.integers(1, max_qty + 1))

                probs = np.array(REGION_DISCOUNT_PROBS[region], dtype=float)
                boost = SUBCAT_DISCOUNT_BOOST.get(prod["Sub-Category"], 0)
                if boost:  # move probability mass from "no discount" to deep discounts
                    probs[0] -= boost
                    probs[5:] += boost / 5
                discount = float(rng.choice(DISCOUNT_LEVELS, p=probs / probs.sum()))

                gross = prod["list_price"] * qty
                sales = gross * (1 - discount)
                noise = rng.normal(0, 0.02) * gross   # freight, rebates etc.
                profit = gross * (prod["base_margin"] - discount) + noise

                lines.append({
                    "Order ID": order_id,
                    "Order Date": order_date.strftime("%Y-%m-%d"),
                    "Ship Date": ship_date.strftime("%Y-%m-%d"),
                    "Ship Mode": ship_mode,
                    "Customer ID": cust["Customer ID"],
                    "Customer Name": cust["Customer Name"],
                    "Segment": cust["Segment"],
                    "Country": "United States",
                    "City": cust["City"],
                    "State": cust["State"],
                    "Region": region,
                    "Product ID": prod["Product ID"],
                    "Category": prod["Category"],
                    "Sub-Category": prod["Sub-Category"],
                    "Product Name": prod["Product Name"],
                    "Sales": round(sales, 2),
                    "Quantity": qty,
                    "Discount": discount,
                    "Profit": round(profit, 2),
                })

    df = pd.DataFrame(lines).sort_values(["Order Date", "Order ID"]).reset_index(drop=True)
    assert set(df["State"].map(STATE_TO_REGION)) <= set(REGION_GROWTH)
    return df


def inject_quality_issues(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """
    Add realistic, *known* errors so the cleaning step has real work to do.
    Each issue mimics something that happens in real company exports.
    """
    df = df.copy()
    n = len(df)

    def pick(k):
        return rng.choice(n, size=k, replace=False)

    # 1. Inconsistent region spelling (manual entry / different source systems)
    #    The region is still the RIGHT one, just written differently.
    for i in pick(60):
        region = df.loc[i, "Region"]
        style = rng.choice(["lower", "upper", "padded", "typo"])
        if style == "lower":
            df.loc[i, "Region"] = region.lower()
        elif style == "upper":
            df.loc[i, "Region"] = region.upper()
        elif style == "padded":
            df.loc[i, "Region"] = f" {region} "
        else:  # a typo only exists for Central in this export
            df.loc[i, "Region"] = "Centrl" if region == "Central" else region.lower()
    # 2. Region missing (field left blank) - recoverable from State
    df.loc[pick(35), "Region"] = np.nan
    # 3. Inconsistent category spelling
    for i, bad in zip(pick(45), rng.choice(["office supplies", "Technology ",
                                             "FURNITURE", "Tech"], size=45)):
        df.loc[i, "Category"] = bad
    # 4. Missing customer / product names - recoverable via their IDs
    df.loc[pick(25), "Customer Name"] = np.nan
    df.loc[pick(20), "Product Name"] = np.nan
    # 5. Leading / trailing spaces in text fields
    for i in pick(40):
        df.loc[i, "City"] = f"  {df.loc[i, 'City']} "
    # 6. Discount typed as a percentage instead of a fraction (20 instead of 0.2)
    #    (only discounted lines: 0% typed as a percentage is still 0)
    for i in rng.choice(np.flatnonzero(df["Discount"] > 0), size=18, replace=False):
        df.loc[i, "Discount"] = df.loc[i, "Discount"] * 100
    # 7. Sales stored as text with currency symbols (e.g. "$1,234.50")
    df["Sales"] = df["Sales"].astype(object)
    for i in pick(30):
        df.loc[i, "Sales"] = f"${float(df.loc[i, 'Sales']):,.2f}"
    # 8. Impossible values: negative sales, zero/negative quantity
    for i in pick(8):
        df.loc[i, "Sales"] = -abs(float(str(df.loc[i, "Sales"]).replace("$", "").replace(",", "")))
    df.loc[pick(6), "Quantity"] = rng.choice([0, -1, -2], size=6)
    # 9. Missing sales / profit (failed export of numeric fields)
    df.loc[pick(10), "Sales"] = np.nan
    df.loc[pick(7), "Profit"] = np.nan
    # 10. Invalid / impossible dates
    df.loc[pick(5), "Order Date"] = ["2023-02-30", "not recorded", "2022-13-05",
                                     "2023-02-30", "not recorded"]
    for i in pick(6):   # ship date earlier than order date
        od = pd.to_datetime(df.loc[i, "Order Date"], errors="coerce")
        if pd.notna(od):
            df.loc[i, "Ship Date"] = (od - pd.Timedelta(days=3)).strftime("%Y-%m-%d")
    # 11. Exact duplicate rows (the same line exported twice)
    dupes = df.iloc[pick(70)]
    df = pd.concat([df, dupes], ignore_index=True)

    # shuffle so the errors are not grouped at the end
    return df.sample(frac=1, random_state=SEED).reset_index(drop=True)


def main() -> None:
    rng = np.random.default_rng(SEED)
    clean = build_clean_orders(rng)
    raw = inject_quality_issues(clean, rng)
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    raw.to_csv(RAW_FILE, index=False, lineterminator="\n")  # identical bytes on every OS
    print(f"Clean lines generated : {len(clean):,}")
    print(f"Raw rows written      : {len(raw):,} -> {RAW_FILE}")


if __name__ == "__main__":
    main()
