"""
Generate Power BI-style dashboard mockup images for the pharma repo.
These look like real Power BI screenshots for the GitHub README.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "docs" / "screenshots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Color palette matching Power BI default theme
BLUE = '#2563EB'
DARK_BLUE = '#1E40AF'
LIGHT_BLUE = '#DBEAFE'
GREEN = '#16A34A'
RED = '#DC2626'
AMBER = '#D97706'
TEAL = '#0D9488'
GRAY = '#94A3B8'
LIGHT_GRAY = '#F1F5F9'
BG = '#F8FAFC'
CARD_BG = '#FFFFFF'
TEXT = '#1E293B'
MUTED = '#64748B'

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
plt.rcParams['font.size'] = 10


def add_card_bg(ax, facecolor=CARD_BG):
    ax.set_facecolor(facecolor)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color('#E2E8F0')
        spine.set_linewidth(0.8)


# ============================================================
# PAGE 1: Executive Summary
# ============================================================
fig = plt.figure(figsize=(16, 10), facecolor=BG)
fig.suptitle('Executive Summary', fontsize=16, fontweight='bold', color=TEXT, x=0.08, ha='left', y=0.97)
fig.text(0.08, 0.945, 'Wound Care, Burn Care, Hyperbaric & Infusion Therapy  |  Jan 2024 - Dec 2025  |  All Divisions', 
         fontsize=9, color=MUTED)

# KPI Cards
kpis = [
    ('Total Rx Fills', '3,000', '+8.2% YoY', GREEN),
    ('New Patient Starts', '1,749', '58.3% of fills', BLUE),
    ('PA Approval Rate', '79.6%', 'Across all payers', AMBER),
    ('Avg Time to Fill', '4.8 days', 'Prescription to fill', TEAL),
]
for i, (label, value, sub, color) in enumerate(kpis):
    ax = fig.add_axes([0.05 + i*0.235, 0.78, 0.22, 0.12])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis('off')
    add_card_bg(ax)
    ax.text(0.08, 0.72, label, fontsize=9, color=MUTED, transform=ax.transAxes)
    ax.text(0.08, 0.28, value, fontsize=26, fontweight='bold', color=color, transform=ax.transAxes)
    ax.text(0.08, 0.08, sub, fontsize=8, color=MUTED, transform=ax.transAxes)

# Monthly volume chart
ax1 = fig.add_axes([0.05, 0.38, 0.55, 0.35])
add_card_bg(ax1)
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec',
          'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
fills = [101,118,158,126,138,102,138,143,118,151,116,120,119,94,117,115,120,121,120,142,112,132,121,158]
x = np.arange(len(months))
bars = ax1.bar(x, fills, color=BLUE, alpha=0.7, width=0.7, zorder=3)
# Rolling avg
window = 3
rolling = [np.mean(fills[max(0,i-window+1):i+1]) for i in range(len(fills))]
ax1.plot(x, rolling, color=RED, linewidth=2, zorder=4)
ax1.set_title('Monthly Rx Fills with 3-Month Rolling Average', fontsize=11, fontweight='bold', color=TEXT, loc='left', pad=10)
ax1.set_xticks(x)
ax1.set_xticklabels(months, fontsize=7, rotation=45)
ax1.set_ylabel('Fills', fontsize=9, color=MUTED)
ax1.tick_params(colors=MUTED, labelsize=8)
ax1.grid(axis='y', alpha=0.3, zorder=0)
ax1.legend(['3-Mo Avg', 'Monthly Fills'], fontsize=8, loc='upper right')
# Year labels
ax1.text(5.5, -22, '2024', fontsize=9, color=MUTED, ha='center', fontweight='bold')
ax1.text(17.5, -22, '2025', fontsize=9, color=MUTED, ha='center', fontweight='bold')

# Revenue by product
ax2 = fig.add_axes([0.65, 0.38, 0.32, 0.35])
add_card_bg(ax2)
drugs = ['Solu-Medrol', 'Santyl', 'Remicade', 'Regranex', 'Silvadene']
rev = [1607, 1574, 1539, 1510, 1488]
colors_drugs = [TEAL, BLUE, DARK_BLUE, GREEN, AMBER]
y_pos = np.arange(len(drugs))
ax2.barh(y_pos, rev, color=colors_drugs, height=0.6, zorder=3)
ax2.set_yticks(y_pos)
ax2.set_yticklabels(drugs, fontsize=9)
ax2.set_xlabel('Revenue ($K)', fontsize=9, color=MUTED)
ax2.set_title('Revenue by Product', fontsize=11, fontweight='bold', color=TEXT, loc='left', pad=10)
ax2.tick_params(colors=MUTED, labelsize=8)
ax2.grid(axis='x', alpha=0.3, zorder=0)
ax2.invert_yaxis()
for i, v in enumerate(rev):
    ax2.text(v + 15, i, f'${v}K', fontsize=8, color=MUTED, va='center')

# Payer approval table area
ax3 = fig.add_axes([0.05, 0.04, 0.92, 0.28])
add_card_bg(ax3)
ax3.axis('off')
ax3.set_title('Payer Performance Summary', fontsize=11, fontweight='bold', color=TEXT, loc='left', pad=10)
table_data = [
    ['Commercial', '375', '285', '76.0%', '4.7 days'],
    ['Medicaid', '383', '309', '80.7%', '4.7 days'],
    ['Medicare', '343', '280', '81.6%', '4.9 days'],
    ['Self-Pay', '374', '294', '78.6%', '5.1 days'],
    ['VA', '361', '294', '81.4%', '4.7 days'],
]
col_labels = ['Payer', 'PA Requests', 'Approved', 'Approval Rate', 'Avg Days to Fill']
table = ax3.table(cellText=table_data, colLabels=col_labels, loc='center',
                  cellLoc='center', colColours=[LIGHT_BLUE]*5)
table.auto_set_font_size(False)
table.set_fontsize(9)
table.scale(1, 1.6)
for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor('#E2E8F0')
    if row == 0:
        cell.set_text_props(fontweight='bold', color=DARK_BLUE)
        cell.set_facecolor(LIGHT_BLUE)
    else:
        cell.set_facecolor(CARD_BG)
    # Color the approval rate cells
    if row > 0 and col == 3:
        rate = float(cell.get_text().get_text().replace('%', ''))
        if rate >= 80:
            cell.set_facecolor('#DCFCE7')
            cell.set_text_props(color='#166534', fontweight='bold')
        elif rate >= 75:
            cell.set_facecolor('#FEF3C7')
            cell.set_text_props(color='#92400E', fontweight='bold')

fig.savefig(OUTPUT_DIR / 'page1_executive_summary.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("Page 1 saved")


# ============================================================
# PAGE 2: Patient Journey and Channel Mix
# ============================================================
fig = plt.figure(figsize=(16, 10), facecolor=BG)
fig.suptitle('Patient Journey & Channel Analysis', fontsize=16, fontweight='bold', color=TEXT, x=0.08, ha='left', y=0.97)
fig.text(0.08, 0.945, 'Wound Care, Burn Care, Hyperbaric & Infusion Therapy  |  All Products', fontsize=9, color=MUTED)

# Patient funnel
ax1 = fig.add_axes([0.05, 0.52, 0.42, 0.38])
add_card_bg(ax1)
stages = ['Diagnosis', 'PA Approved', 'First Fill', 'Ongoing Therapy']
counts = [499, 435, 499, 495]
max_c = max(counts)
colors_funnel = [BLUE, '#7C3AED', TEAL, GREEN]
y_pos = np.arange(len(stages))
widths = [c/max_c * 100 for c in counts]
for i, (stage, count, w, c) in enumerate(zip(stages, counts, widths, colors_funnel)):
    bar = ax1.barh(i, w, color=c, height=0.6, zorder=3, left=(100-w)/2)
    ax1.text(50, i, f'{stage}: {count}', ha='center', va='center', fontsize=10, color='white', fontweight='bold', zorder=5)
ax1.set_xlim(0, 100)
ax1.set_yticks([])
ax1.set_xticks([])
ax1.set_title('Patient Journey Funnel', fontsize=11, fontweight='bold', color=TEXT, loc='left', pad=10)
ax1.text(50, -0.8, f'Conversion: {counts[-1]}/{counts[0]} = {counts[-1]/counts[0]*100:.0f}% reach ongoing therapy', 
         ha='center', fontsize=9, color=MUTED)

# Channel mix donut
ax2 = fig.add_axes([0.55, 0.52, 0.40, 0.38])
add_card_bg(ax2)
channel_data = [1773, 1227]
channel_labels = ['Retail (59.1%)', 'Specialty (40.9%)']
wedges, texts = ax2.pie(channel_data, labels=channel_labels, colors=[BLUE, TEAL],
                         startangle=90, wedgeprops=dict(width=0.4, edgecolor=CARD_BG, linewidth=2))
for t in texts:
    t.set_fontsize(10)
ax2.set_title('Channel Mix', fontsize=11, fontweight='bold', color=TEXT, y=1.05)

# New starts by month
ax3 = fig.add_axes([0.05, 0.06, 0.55, 0.38])
add_card_bg(ax3)
new_starts = [99,106,135,110,107,76,101,94,75,81,64,71,63,53,59,53,58,52,43,62,41,52,46,48]
ax3.fill_between(x, new_starts, alpha=0.15, color=GREEN, zorder=3)
ax3.plot(x, new_starts, color=GREEN, linewidth=2, marker='o', markersize=3, zorder=4)
ax3.set_title('Monthly New Patient Starts', fontsize=11, fontweight='bold', color=TEXT, loc='left', pad=10)
ax3.set_xticks(x)
ax3.set_xticklabels(months, fontsize=7, rotation=45)
ax3.set_ylabel('New Starts', fontsize=9, color=MUTED)
ax3.tick_params(colors=MUTED, labelsize=8)
ax3.grid(axis='y', alpha=0.3, zorder=0)

# Time to fill by payer
ax4 = fig.add_axes([0.65, 0.06, 0.32, 0.38])
add_card_bg(ax4)
payers = ['Commercial', 'Medicaid', 'Medicare', 'Self-Pay', 'VA']
ttf = [4.7, 4.7, 4.9, 5.1, 4.7]
colors_ttf = [BLUE if t <= 4.8 else AMBER for t in ttf]
y_pos = np.arange(len(payers))
ax4.barh(y_pos, ttf, color=colors_ttf, height=0.5, zorder=3)
ax4.set_yticks(y_pos)
ax4.set_yticklabels(payers, fontsize=9)
ax4.set_xlabel('Days', fontsize=9, color=MUTED)
ax4.set_title('Avg Time to Fill by Payer', fontsize=11, fontweight='bold', color=TEXT, loc='left', pad=10)
ax4.tick_params(colors=MUTED, labelsize=8)
ax4.grid(axis='x', alpha=0.3, zorder=0)
ax4.invert_yaxis()
ax4.set_xlim(0, 6)
for i, v in enumerate(ttf):
    ax4.text(v + 0.1, i, f'{v}d', fontsize=8, color=MUTED, va='center')

fig.savefig(OUTPUT_DIR / 'page2_patient_journey.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("Page 2 saved")


# ============================================================
# PAGE 3: Product & Therapeutic Detail
# ============================================================
fig = plt.figure(figsize=(16, 10), facecolor=BG)
fig.suptitle('Product & Therapeutic Class Analysis', fontsize=16, fontweight='bold', color=TEXT, x=0.08, ha='left', y=0.97)
fig.text(0.08, 0.945, 'Wound Care, Burn Care, Hyperbaric & Infusion Therapy  |  All Payers', fontsize=9, color=MUTED)

# Fills by product (bar)
ax1 = fig.add_axes([0.05, 0.52, 0.42, 0.38])
add_card_bg(ax1)
drug_names = ['Solu-Medrol', 'Regranex', 'Santyl', 'Remicade', 'Silvadene']
drug_fills = [637, 606, 604, 585, 568]
drug_colors = [TEAL, GREEN, BLUE, DARK_BLUE, AMBER]
bars = ax1.bar(drug_names, drug_fills, color=drug_colors, width=0.6, zorder=3)
ax1.set_title('Rx Fills by Product', fontsize=11, fontweight='bold', color=TEXT, loc='left', pad=10)
ax1.tick_params(colors=MUTED, labelsize=8)
ax1.set_ylabel('Fills', fontsize=9, color=MUTED)
ax1.grid(axis='y', alpha=0.3, zorder=0)
for bar, v in zip(bars, drug_fills):
    ax1.text(bar.get_x() + bar.get_width()/2, v + 8, str(v), ha='center', fontsize=9, color=MUTED)

# Revenue by therapeutic class (stacked)
ax2 = fig.add_axes([0.55, 0.52, 0.40, 0.38])
add_card_bg(ax2)
classes = ['Wound Care', 'Infusion\nTherapy', 'Hyperbaric/\nInfusion', 'Burn Care']
class_rev = [3084, 1539, 1607, 1488]
class_colors = [BLUE, DARK_BLUE, TEAL, AMBER]
ax2.barh(classes, class_rev, color=class_colors, height=0.5, zorder=3)
ax2.set_title('Revenue by Therapeutic Class ($K)', fontsize=11, fontweight='bold', color=TEXT, loc='left', pad=10)
ax2.tick_params(colors=MUTED, labelsize=9)
ax2.grid(axis='x', alpha=0.3, zorder=0)
ax2.invert_yaxis()
for i, v in enumerate(class_rev):
    ax2.text(v + 30, i, f'${v}K', fontsize=9, color=MUTED, va='center')

# Avg cost per fill by product
ax3 = fig.add_axes([0.05, 0.06, 0.42, 0.38])
add_card_bg(ax3)
avg_costs = [2522, 2492, 2606, 2630, 2620]
ax3.bar(drug_names, avg_costs, color=[TEAL, GREEN, BLUE, DARK_BLUE, AMBER], width=0.6, zorder=3)
ax3.set_title('Avg Cost per Fill by Product', fontsize=11, fontweight='bold', color=TEXT, loc='left', pad=10)
ax3.set_ylabel('Cost ($)', fontsize=9, color=MUTED)
ax3.tick_params(colors=MUTED, labelsize=8)
ax3.grid(axis='y', alpha=0.3, zorder=0)
ax3.set_ylim(2300, 2750)
for i, v in enumerate(avg_costs):
    ax3.text(i, v + 15, f'${v}', ha='center', fontsize=8, color=MUTED)

# PA rate by product
ax4 = fig.add_axes([0.55, 0.06, 0.40, 0.38])
add_card_bg(ax4)
# Simulated PA rates per drug
pa_rates = [81.2, 78.5, 80.1, 77.8, 79.9]
colors_pa = [GREEN if r >= 80 else AMBER for r in pa_rates]
y_pos = np.arange(len(drug_names))
ax4.barh(y_pos, pa_rates, color=colors_pa, height=0.5, zorder=3)
ax4.set_yticks(y_pos)
ax4.set_yticklabels(drug_names, fontsize=9)
ax4.set_title('PA Approval Rate by Product', fontsize=11, fontweight='bold', color=TEXT, loc='left', pad=10)
ax4.tick_params(colors=MUTED, labelsize=8)
ax4.grid(axis='x', alpha=0.3, zorder=0)
ax4.set_xlim(70, 90)
ax4.invert_yaxis()
for i, v in enumerate(pa_rates):
    ax4.text(v + 0.3, i, f'{v}%', fontsize=8, color=MUTED, va='center')

fig.savefig(OUTPUT_DIR / 'page3_product_detail.png', dpi=150, bbox_inches='tight', facecolor=BG)
plt.close()
print("Page 3 saved")

print("\nAll screenshots saved to", OUTPUT_DIR)
