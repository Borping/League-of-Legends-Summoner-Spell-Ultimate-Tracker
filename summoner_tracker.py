import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QGridLayout, QSpinBox, QLineEdit, QHBoxLayout, QMessageBox,
    QComboBox, QStackedLayout, QGraphicsOpacityEffect, QGraphicsDropShadowEffect,
    QSlider, QCheckBox
)
from PyQt5.QtCore import QTimer, Qt, QSize, QRect
from PyQt5.QtGui import QPixmap, QIcon, QIntValidator, QFont, QColor

# ----------------------------
# UI Tuning – central controls
# ----------------------------
ICON_SIZE = 36           # Champion, summoner spell, and ultimate icons
TOGGLE_ICON_SIZE = 24    # Lucidity Boots & Cosmic Insight toggle buttons
AH_MAX_CHARS = 3         # Ability Haste max digits (0–999)
TOPBTN_SIZE = 30         # Size of the top-right toolbar buttons (min 30 to avoid emoji clipping)
TOPBTN_ICON = 26         # <-- Inner icon size for toolbar buttons so styled borders remain visible
BG_SCALE = 1.0           # Crest target scale (keep at 1.0 for crispness)

# ----------------------------
# Themes catalog
# ----------------------------
THEMES = {
    "Default": {"bg": "#1f1f1f", "fg": "#eaeaea", "accent": "#4d90fe", "crest_url": None},
    "Dark":    {"bg": "#141414", "fg": "#e0e0e0", "accent": "#7aa2f7", "crest_url": None},
    "Light":   {"bg": "#f2f2f2", "fg": "#111111", "accent": "#3b82f6", "crest_url": None},
    "Master": {
        "bg": "#2a1f2f", "fg": "#f0eaff", "accent": "#b85cff",
        "crest_url": "https://wiki.leagueoflegends.com/en-us/images/Season_2023_-_Master.png?470b8"
    },
    "Grandmaster": {
        "bg": "#2d1a1a", "fg": "#ffecec", "accent": "#ff6b6b",
        "crest_url": "https://wiki.leagueoflegends.com/en-us/images/Season_2023_-_Grandmaster.png?87870"
    },
    "Challenger": {
        "bg": "#0f1f2f", "fg": "#eaf6ff", "accent": "#4fd1ff",
        "crest_url": "https://wiki.leagueoflegends.com/en-us/images/Season_2023_-_Challenger.png?40b78"
    },
}

# ----------------------------
# DataDragon helpers (JSON only pre-QApplication)
# ----------------------------
def get_latest_version():
    try:
        return requests.get('https://ddragon.leagueoflegends.com/api/versions.json', timeout=5).json()[0]
    except Exception:
        return "15.11.1"  # fallback

def get_champion_data():
    version = get_latest_version()
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/championFull.json"
    try:
        return requests.get(url, timeout=8).json()
    except Exception as e:
        print("Error fetching champion data:", e)
        return {}

# NOTE: Pixmap creation must be called AFTER QApplication exists.
def _fetch_pixmap(url):
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            pm = QPixmap()
            pm.loadFromData(resp.content)
            return pm
    except Exception as e:
        print(f"Error fetching image at {url}: {e}")
    return None

def get_champion_icon(champ_name, version):
    if champ_name in champion_data.get("data", {}):
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champ_name}.png"
        return _fetch_pixmap(url)
    return None

# Summoner spell icon names on DDragon
SUMMONER_SPELLS = {
    "Flash": "SummonerFlash.png",
    "Teleport": "SummonerTeleport.png",
    "Ignite": "SummonerDot.png",
    "Cleanse": "SummonerBoost.png",
    "Exhaust": "SummonerExhaust.png",
    "Heal": "SummonerHeal.png",
    "Barrier": "SummonerBarrier.png",
    "Ghost": "SummonerHaste.png",
    "Clarity": "SummonerMana.png",
    "Smite": "SummonerSmite.png",
}

# Hard-coded Unleashed Teleport icon (not reliably on DDragon)
UNLEASHED_TP_WIKI_URL = "https://wiki.leagueoflegends.com/en-us/images/Unleashed_Teleport.png?f93be"

def get_summoner_icon(spell_name, version):
    if spell_name in ("U. Teleport", "Unleashed Teleport"):
        return _fetch_pixmap(UNLEASHED_TP_WIKI_URL)
    filename = SUMMONER_SPELLS.get(spell_name)
    if not filename:
        return None
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/spell/{filename}"
    return _fetch_pixmap(url)

# Lucidity Boots (item 3158) + Cosmic Insight rune (wiki URL)
def get_lucidity_icon(version):
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/item/3158.png"
    return _fetch_pixmap(url)

def get_cosmic_icon():
    wiki_url = "https://wiki.leagueoflegends.com/en-us/images/Cosmic_Insight_rune.png?004b5"
    return _fetch_pixmap(wiki_url)

# Known ultimate icon overrides (when {ChampionName}R.png doesn't exist)
ULTIMATE_ICON_OVERRIDES = {
    "Alistar": "FerociousHowl.png",
    "Amumu": "CurseoftheSadMummy.png",
    "Anivia": "GlacialStorm.png",
    "Ashe": "EnchantedCrystalArrow.png",
    "Blitzcrank": "StaticField.png",
    "Braum": "BraumRWrapper.png",
    "Chogath": "Feast.png",
    "Corki": "MissileBarrage.png",
    "Darius": "DariusExecute.png",
    "Draven": "DravenRCast.png",
    "Fiddlesticks": "FiddleSticksR.png",
    "Graves": "GravesChargeShot.png",
    "Hecarim": "HecarimUlt.png",
    "Janna": "ReapTheWhirlwind.png",
    "JarvanIV": "JarvanIVCataclysm.png",
    "Jayce": "JayceStanceHtG.png",
    "Kalista": "KalistaRx.png",
    "Karma": "KarmaMantra.png",
    "Karthus": "KarthusFallenOne.png",
    "Kassadin": "RiftWalk.png",
    "Kennen": "KennenShurikenStorm.png",
    "KogMaw": "KogMawLivingArtillery.png",
    "Leona": "LeonaSolarFlare.png",
    "Malphite": "UFSlash.png",
    "MasterYi": "Highlander.png",
    "MissFortune": "MissFortuneBulletTime.png",
    "MonkeyKing": "MonkeyKingSpinToWin.png",
    "Nautilus": "NautilusGrandLine.png",
    "Nidalee": "AspectOfTheCougar.png",
    "Nocturne": "NocturneParanoia.png",
    "Olaf": "OlafRagnarok.png",
    "Orianna": "OrianaDetonateCommand.png",
    "Rammus": "Tremors2.png",
    "Renekton": "RenektonReignOfTheTyrant.png",
    "Riven": "RivenFengShuiEngine.png",
    "Rumble": "RumbleCarpetBomb.png",
    "Shaco": "HallucinateFull.png",
    "Shyvana": "ShyvanaTransformCast.png",
    "Singed": "InsanityPotion.png",
    "TahmKench": "TahmKenchRWrapper.png",
    "Thresh": "ThreshRPenta.png",
    "Trundle": "TrundlePain.png",
    "Tryndamere": "UndyingRage.png",
    "TwistedFate": "Destiny.png",
    "Twitch": "TwitchFullAutomatic.png",
    "Vayne": "VayneInquisition.png",
    "Vladimir": "VladimirHemoplague.png",
    "Xerath": "XerathLocusOfPower2.png",
    "Zilean": "ChronoShift.png",
}

def get_ultimate_icon(champ_name, version):
    base = f"https://ddragon.leagueoflegends.com/cdn/{version}/img/spell/"
    pm = _fetch_pixmap(f"{base}{champ_name}R.png")
    if pm:
        return pm
    override = ULTIMATE_ICON_OVERRIDES.get(champ_name)
    if override:
        pm = _fetch_pixmap(f"{base}{override}")
        if pm:
            return pm
    return None

# JSON data safe to fetch pre-QApplication
champion_data = get_champion_data()
dd_version = get_latest_version()

# ----------------------------
# Name mapping helpers (Wukong <-> MonkeyKing)
# ----------------------------
def to_display_champ(name: str) -> str:
    return "Wukong" if name == "MonkeyKing" else name

def to_internal_champ(name: str) -> str:
    return "MonkeyKing" if name == "Wukong" else name

def get_display_champion_list():
    internal = sorted(list(champion_data.get("data", {}).keys()))
    # Replace MonkeyKing with Wukong for player-facing list
    display = [to_display_champ(n) for n in internal]
    return display

# ----------------------------
# Cooldown helpers
# ----------------------------
def ability_haste_to_cdr_percent(haste):
    return haste / (haste + 100)

def get_ultimate_cooldowns(champion_name):
    if champion_name not in champion_data.get("data", {}):
        return [100, 80, 60]  # fallback
    return champion_data["data"][champion_name]["spells"][-1]["cooldown"]

# ----------------------------
# Small style helper for top-right tool buttons
# ----------------------------
def style_tool_button(btn: QPushButton, accent: str, fg: str):
    btn.setFlat(True)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setFixedSize(TOPBTN_SIZE, TOPBTN_SIZE)
    btn.setStyleSheet(f"""
        QPushButton {{
            border: 1px solid {accent};
            background-color: rgba(255,255,255,0.06);
            color: {fg};
            border-radius: 6px;
        }}
        QPushButton:hover {{
            background-color: rgba(255,255,255,0.12);
        }}
        QPushButton:pressed {{
            background-color: rgba(255,255,255,0.18);
        }}
    """)

# ----------------------------
# GUI
# ----------------------------
class CooldownTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("League Cooldown Tracker")
        self.resize(600, 200)  # launch size

        # Initialize theme / crest state early
        self.current_theme = "Default"
        self.current_crest = None  # QPixmap or None
        self.crest_opacity = 0.18  # default opacity (0..1)
        self.crest_opacity_effect = None  # QGraphicsOpacityEffect set in _build_main_page

        # Root layout holds a stacked layout for pages
        root_vbox = QVBoxLayout(self)
        self.pages = QStackedLayout()
        root_vbox.addLayout(self.pages)

        # Build pages
        self.main_page = self._build_main_page()
        self.themes_page = self._build_themes_page()
        self.settings_page = self._build_settings_page()
        self.config_page = self._build_game_config_page()  # Game Configuration

        self.pages.addWidget(self.main_page)
        self.pages.addWidget(self.themes_page)
        self.pages.addWidget(self.settings_page)
        self.pages.addWidget(self.config_page)
        self.pages.setCurrentWidget(self.main_page)

        # Apply default theme now that pages exist
        self.apply_theme(self.current_theme)

        # Set the window icon to Summoner Flash
        flash_icon = get_summoner_icon("Flash", dd_version)
        if flash_icon:
            icon = QIcon(flash_icon.scaled(ICON_SIZE, ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.setWindowIcon(icon)

    # --------- Page builders ---------
    def _build_main_page(self) -> QWidget:
        page = QWidget()

        # Background crest label behind content
        self.bg_label = QLabel(parent=page)
        self.bg_label.setScaledContents(False)
        self.bg_label.setAlignment(Qt.AlignCenter)
        self.bg_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.crest_opacity_effect = QGraphicsOpacityEffect(self.bg_label)
        self.crest_opacity_effect.setOpacity(self.crest_opacity)
        self.bg_label.setGraphicsEffect(self.crest_opacity_effect)
        self.bg_label.hide()

        # Foreground content
        vbox = QVBoxLayout(page)

        # Top bar: Game timer (left) + start + toolbar (right)
        top_bar = QHBoxLayout()
        self.timer_label = QLabel("Game Time: 0:00")
        self._style_glassy_label(self.timer_label, underline=True)
        top_bar.addWidget(self.timer_label)

        # ▶️ Start button (timer begins only when clicked)
        self.start_btn = QPushButton("▶️")
        self.start_btn.setToolTip("Start timer")
        self.start_btn.clicked.connect(self.start_timer)
        top_bar.addWidget(self.start_btn)

        top_bar.addStretch()

        # Game Config button with icon fallback — NOW using TOPBTN_ICON so the styled border is visible
        self.config_btn = QPushButton()
        cfg_pm = _fetch_pixmap("https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/-1.png")
        if cfg_pm:
            self.config_btn.setIcon(QIcon(cfg_pm))
            self.config_btn.setIconSize(QSize(TOPBTN_ICON, TOPBTN_ICON))
        else:
            self.config_btn.setText("📝")
        self.config_btn.setToolTip("Game Configuration")
        self.config_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.config_page))
        top_bar.addWidget(self.config_btn)

        self.themes_btn = QPushButton("🎨")
        self.themes_btn.setToolTip("Themes")
        self.themes_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.themes_page))
        top_bar.addWidget(self.themes_btn)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.settings_page))
        top_bar.addWidget(self.settings_btn)

        vbox.addLayout(top_bar)

        # Single-line cooldown log (latest press)
        self.cd_log_label = QLabel("Cooldown Log: None")
        self._style_glassy_label(self.cd_log_label, underline=False)
        vbox.addWidget(self.cd_log_label)
        self.cd_log_token = None  # which timer "owns" the log line

        # Game timer (do NOT start yet)
        self.game_time = 0  # seconds
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.update_game_time)

        # Enemy grid
        self.enemy_layout = QGridLayout()
        vbox.addLayout(self.enemy_layout)

        headers = ["Champ", "Lvl", "AH", "Spell 1", "CD", "Spell 2", "CD", "Ult", "CD", "", ""]
        header_font = QFont()
        header_font.setBold(True)
        for col, header in enumerate(headers):
            lbl = QLabel(header)
            lbl.setFont(header_font)
            self._style_header_label(lbl)  # transparent bg + shadow
            self.enemy_layout.addWidget(lbl, 0, col)

        # Load lucidity/cosmic icons (post-QApplication)
        self.lucidity_pm = get_lucidity_icon(dd_version)
        self.cosmic_pm = get_cosmic_icon()

        self.enemies = []
        # initial loadout
        default_rows = [
            {"champ": "Aatrox", "s1": "Flash", "s2": "Teleport"},
            {"champ": "Ahri",   "s1": "Flash", "s2": "Teleport"},
            {"champ": "Akali",  "s1": "Flash", "s2": "Teleport"},
            {"champ": "Akshan", "s1": "Flash", "s2": "Teleport"},
            {"champ": "Alistar","s1": "Flash", "s2": "Teleport"},
        ]
        self.setup_enemy_rows(default_rows)

        # Crest ordering
        self.bg_label.lower()
        self._position_background_label(page)
        return page

    def _build_themes_page(self) -> QWidget:
        page = QWidget()
        vbox = QVBoxLayout(page)

        # Top bar: Back
        top = QHBoxLayout()
        self.back_btn = QPushButton("◀ Back")
        self.back_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.main_page))
        top.addWidget(self.back_btn)
        top.addStretch()
        vbox.addLayout(top)

        # Instruction + dropdown
        theme_lbl = QLabel("Select a Theme:")
        self._style_header_label(theme_lbl)
        vbox.addWidget(theme_lbl)

        self.theme_dropdown = QComboBox()
        self.theme_dropdown.addItems(list(THEMES.keys()))
        self.theme_dropdown.setCurrentText(self.current_theme)
        self.theme_dropdown.currentTextChanged.connect(self.apply_theme)
        vbox.addWidget(self.theme_dropdown)

        # Crest opacity controls
        opacity_row = QHBoxLayout()
        self.opacity_label_prefix = QLabel("Crest Opacity:")
        self._style_header_label(self.opacity_label_prefix)
        self.opacity_value_label = QLabel(f"{self.crest_opacity:.2f}")
        self._style_header_label(self.opacity_value_label)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)  # map 0..100 -> 0.00..1.00
        self.opacity_slider.setSingleStep(1)
        self.opacity_slider.setPageStep(5)
        self.opacity_slider.setValue(int(self.crest_opacity * 100))
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)

        opacity_row.addWidget(self.opacity_label_prefix)
        opacity_row.addWidget(self.opacity_slider, 1)
        opacity_row.addWidget(self.opacity_value_label)
        vbox.addLayout(opacity_row)

        hint = QLabel("Rank themes add a watermark crest and adjust the color palette.")
        hint.setWordWrap(True)
        self._style_header_label(hint)
        vbox.addWidget(hint)
        vbox.addStretch(1)
        return page

    def _build_settings_page(self) -> QWidget:
        page = QWidget()
        vbox = QVBoxLayout(page)

        # Top bar: Back
        top = QHBoxLayout()
        back = QPushButton("◀ Back")
        back.clicked.connect(lambda: self.pages.setCurrentWidget(self.main_page))
        top.addWidget(back)
        top.addStretch()
        vbox.addLayout(top)

        # Window opacity slider (10% to 100%)
        row1 = QHBoxLayout()
        lbl1 = QLabel("Window Opacity:")
        self._style_header_label(lbl1)
        self.window_opacity_value = QLabel("1.00")
        self._style_header_label(self.window_opacity_value)

        self.window_opacity_slider = QSlider(Qt.Horizontal)
        self.window_opacity_slider.setRange(10, 100)  # 0.10 .. 1.00
        self.window_opacity_slider.setValue(100)
        self.window_opacity_slider.setSingleStep(1)
        self.window_opacity_slider.setPageStep(5)
        self.window_opacity_slider.valueChanged.connect(self._on_window_opacity_changed)

        row1.addWidget(lbl1)
        row1.addWidget(self.window_opacity_slider, 1)
        row1.addWidget(self.window_opacity_value)
        vbox.addLayout(row1)

        # Keep on top toggle
        row2 = QHBoxLayout()
        self.keep_on_top_cb = QCheckBox("Keep on top (always on top)")
        self.keep_on_top_cb.stateChanged.connect(self._on_keep_on_top_toggled)
        row2.addWidget(self.keep_on_top_cb)
        row2.addStretch()
        vbox.addLayout(row2)

        vbox.addStretch(1)
        return page

    def _build_game_config_page(self) -> QWidget:
        """Game Configuration page with header, 5 rows × 3 columns of dropdowns, and Apply (bottom-right)."""
        page = QWidget()
        vbox = QVBoxLayout(page)

        # Top bar: Back
        top = QHBoxLayout()
        back = QPushButton("◀ Back")
        back.clicked.connect(lambda: self.pages.setCurrentWidget(self.main_page))
        top.addWidget(back)
        top.addStretch()
        vbox.addLayout(top)

        # Header
        cfg_hdr = QLabel("Game Configuration")
        hdr_font = QFont()
        hdr_font.setBold(True)
        hdr_font.setPointSize(14)
        cfg_hdr.setFont(hdr_font)
        self._style_header_label(cfg_hdr)
        vbox.addWidget(cfg_hdr)

        # Grid with headers
        grid = QGridLayout()
        headers = ["Champion", "Summoner 1", "Summoner 2"]
        header_font = QFont()
        header_font.setBold(True)
        for col, header in enumerate(headers):
            lbl = QLabel(header)
            lbl.setFont(header_font)
            self._style_header_label(lbl)
            grid.addWidget(lbl, 0, col)

        # Data sources
        self.all_champions_display = get_display_champion_list()
        self.all_summoners = list(SUMMONER_SPELLS.keys())

        # Keep references to dropdowns so we can read them on Apply
        self.config_rows = []

        # 5 rows of selectors
        for r in range(1, 6):
            champ_cb = QComboBox()
            champ_cb.addItems(self.all_champions_display)  # player-facing names
            grid.addWidget(champ_cb, r, 0)

            s1_cb = QComboBox()
            s1_cb.addItems(self.all_summoners)
            grid.addWidget(s1_cb, r, 1)

            s2_cb = QComboBox()
            s2_cb.addItems(self.all_summoners)
            grid.addWidget(s2_cb, r, 2)

            self.config_rows.append({"champ": champ_cb, "s1": s1_cb, "s2": s2_cb})

        vbox.addLayout(grid)

        # Apply button bottom-right; also re-applies current theme
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        apply_btn = QPushButton("Apply")
        apply_btn.setToolTip("Apply choices to the main page and re-apply theme")
        apply_btn.clicked.connect(self.apply_configuration)
        btn_row.addWidget(apply_btn)
        vbox.addLayout(btn_row)

        vbox.addStretch(1)
        return page

    # --------- Enemy rows (builder/reset) ---------
    def _clear_enemy_rows(self):
        """Remove all current enemy rows (keep header row). Also stop timers."""
        for row in getattr(self, "enemies", []):
            for t in row.get("timers", {}).values():
                try:
                    t.stop()
                except Exception:
                    pass
        current_rows = len(getattr(self, "enemies", []))
        cols = self.enemy_layout.columnCount()
        for i in range(1, current_rows + 1):
            for c in range(cols):
                item = self.enemy_layout.itemAtPosition(i, c)
                if item:
                    w = item.widget()
                    if w:
                        w.deleteLater()
        self.enemies = []

    def setup_enemy_rows(self, rows_data):
        """
        rows_data: list of dicts like:
          {"champ": "Aatrox", "s1": "Flash", "s2": "Teleport"}
        champ name must be internal (e.g., 'MonkeyKing' not 'Wukong')
        """
        for i, rowinfo in enumerate(rows_data, start=1):
            champ = rowinfo.get("champ", "Aatrox")  # internal name
            s1_name = rowinfo.get("s1", "Flash")
            s2_name = rowinfo.get("s2", "Teleport")

            row = {}

            # Champion icon + caution if unknown
            icon = get_champion_icon(champ, dd_version)
            if icon:
                champ_icon = QLabel()
                champ_icon.setPixmap(icon.scaled(ICON_SIZE, ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                caution = QLabel("")
                container = QWidget()
                hl = QHBoxLayout(container)
                hl.setContentsMargins(0, 0, 0, 0)
                hl.addWidget(champ_icon)
                hl.addWidget(caution)
            else:
                name_lbl = QLabel(to_display_champ(champ))
                self._style_header_label(name_lbl)  # readable over crest
                caution = QLabel("⚠")
                self._style_header_label(caution)
                caution.setToolTip("Champion data missing — using fallback ultimate cooldowns")
                container = QWidget()
                hl = QHBoxLayout(container)
                hl.setContentsMargins(0, 0, 0, 0)
                hl.addWidget(name_lbl)
                hl.addWidget(caution)
            self.enemy_layout.addWidget(container, i, 0)

            row["champion"] = champ
            row["caution_label"] = caution
            row["timers"] = {}

            # Level & ability haste
            lvl = QSpinBox()
            lvl.setRange(1, 18)
            lvl.setValue(6)
            self.enemy_layout.addWidget(lvl, i, 1)
            row["level_spinner"] = lvl

            haste = QLineEdit()
            haste.setPlaceholderText("AH")
            haste.setValidator(QIntValidator(0, 999, self))
            haste.setMaxLength(AH_MAX_CHARS)
            fm = haste.fontMetrics()
            fudge = 26  # ensure 3 digits visible
            haste.setFixedWidth(fm.horizontalAdvance("9" * AH_MAX_CHARS) + fudge)
            haste.setAlignment(Qt.AlignCenter)
            self.enemy_layout.addWidget(haste, i, 2)
            row["haste_input"] = haste

            # Summoner spell 1
            s1_btn = QPushButton()
            s1_icon_pm = get_summoner_icon(s1_name, dd_version)
            if s1_icon_pm:
                s1_btn.setIcon(QIcon(s1_icon_pm.scaled(ICON_SIZE, ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
                s1_btn.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
            else:
                s1_btn.setText(s1_name)
            s1_lbl = QLabel("")
            self._style_cd_label(s1_lbl)
            self.enemy_layout.addWidget(s1_btn, i, 3)
            self.enemy_layout.addWidget(s1_lbl, i, 4)
            row["spell1_btn"] = s1_btn
            row["spell1_label"] = s1_lbl
            row["summ1_name"] = s1_name
            row["teleport_upgraded_s1"] = False

            # Summoner spell 2
            s2_btn = QPushButton()
            s2_icon_pm = get_summoner_icon(s2_name, dd_version)
            if s2_icon_pm:
                s2_btn.setIcon(QIcon(s2_icon_pm.scaled(ICON_SIZE, ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
                s2_btn.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
            else:
                s2_btn.setText(s2_name)
            s2_lbl = QLabel("")
            self._style_cd_label(s2_lbl)
            self.enemy_layout.addWidget(s2_btn, i, 5)
            self.enemy_layout.addWidget(s2_lbl, i, 6)
            row["spell2_btn"] = s2_btn
            row["spell2_label"] = s2_lbl
            row["summ2_name"] = s2_name
            row["teleport_upgraded_s2"] = False

            # Ultimate button (icon if available; else "R")
            ult_btn = QPushButton()
            ult_icon = get_ultimate_icon(champ, dd_version)
            if ult_icon:
                ult_btn.setIcon(QIcon(ult_icon.scaled(ICON_SIZE, ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
                ult_btn.setIconSize(QSize(ICON_SIZE, ICON_SIZE))
            else:
                ult_btn.setText("R")
            ult_lbl = QLabel("")
            self._style_cd_label(ult_lbl)
            self.enemy_layout.addWidget(ult_btn, i, 7)
            self.enemy_layout.addWidget(ult_lbl, i, 8)
            row["ult_btn"] = ult_btn
            row["ult_label"] = ult_lbl

            # Lucidity + Cosmic toggle buttons
            lucidity_pm = getattr(self, "lucidity_pm", None)
            cosmic_pm = getattr(self, "cosmic_pm", None)

            if lucidity_pm:
                l_btn = QPushButton()
                l_btn.setCheckable(True)
                l_btn.setIcon(QIcon(lucidity_pm.scaled(TOGGLE_ICON_SIZE, TOGGLE_ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
                l_btn.setIconSize(QSize(TOGGLE_ICON_SIZE, TOGGLE_ICON_SIZE))
                l_btn.setToolTip("Ionian Boots of Lucidity (toggle)")
            else:
                l_btn = QPushButton("L")
                l_btn.setCheckable(True)
                l_btn.setToolTip("Lucidity (toggle)")

            if cosmic_pm:
                c_btn = QPushButton()
                c_btn.setCheckable(True)
                c_btn.setIcon(QIcon(cosmic_pm.scaled(TOGGLE_ICON_SIZE, TOGGLE_ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
                c_btn.setIconSize(QSize(TOGGLE_ICON_SIZE, TOGGLE_ICON_SIZE))
                c_btn.setToolTip("Cosmic Insight (toggle)")
            else:
                c_btn = QPushButton("C")
                c_btn.setCheckable(True)
                c_btn.setToolTip("Cosmic Insight (toggle)")

            self._style_toggle_button(l_btn)
            self._style_toggle_button(c_btn)

            self.enemy_layout.addWidget(l_btn, i, 9)
            self.enemy_layout.addWidget(c_btn, i, 10)
            row["lucidity_btn"] = l_btn
            row["cosmic_btn"] = c_btn

            # Connect buttons via a method that reads current names (works after upgrades)
            s1_btn.clicked.connect(lambda _, rw=row: self._on_summoner_click(rw, slot=1))
            s2_btn.clicked.connect(lambda _, rw=row: self._on_summoner_click(rw, slot=2))
            ult_btn.clicked.connect(lambda _, rw=row: self.start_ultimate_timer(rw))

            self.enemies.append(row)

    # ---------- game config apply ----------
    def apply_configuration(self):
        """Read the 5×3 dropdowns and rebuild the main page rows accordingly. Also re-applies theme."""
        rows_data = []
        for r in self.config_rows:
            champ_display = r["champ"].currentText()
            champ_internal = to_internal_champ(champ_display)  # map Wukong -> MonkeyKing
            s1 = r["s1"].currentText()
            s2 = r["s2"].currentText()
            rows_data.append({"champ": champ_internal, "s1": s1, "s2": s2})

        # Clear and rebuild rows
        self._clear_enemy_rows()
        self.setup_enemy_rows(rows_data)
        # Re-apply theme styling to ensure new widgets match theme (also satisfies "apply themes")
        self.apply_theme(self.current_theme)
        # Return to main page
        self.pages.setCurrentWidget(self.main_page)

    # ---------- game clock ----------
    def start_timer(self):
        """Start the game timer (if not already running)."""
        if not self.game_timer.isActive():
            self.game_timer.start(1000)

    def update_game_time(self):
        self.game_time += 1
        m = self.game_time // 60
        s = self.game_time % 60
        self.timer_label.setText(f"Game Time: {m}:{s:02d}")

        # At 10:00, upgrade Teleport -> Unleashed Teleport (icon swap only; running CDs keep counting)
        if self.game_time == 600:
            ut_icon = get_summoner_icon("U. Teleport", dd_version)
            for row in self.enemies:
                # slot 1
                if not row.get("teleport_upgraded_s1") and row.get("summ1_name") == "Teleport":
                    row["teleport_upgraded_s1"] = True
                    row["summ1_name"] = "U. Teleport"
                    if ut_icon:
                        row["spell1_btn"].setIcon(QIcon(ut_icon.scaled(ICON_SIZE, ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
                        row["spell1_btn"].setIconSize(QSize(ICON_SIZE, ICON_SIZE))
                    else:
                        row["spell1_btn"].setText("U. Teleport")
                # slot 2
                if not row.get("teleport_upgraded_s2") and row.get("summ2_name") == "Teleport":
                    row["teleport_upgraded_s2"] = True
                    row["summ2_name"] = "U. Teleport"
                    if ut_icon:
                        row["spell2_btn"].setIcon(QIcon(ut_icon.scaled(ICON_SIZE, ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
                        row["spell2_btn"].setIconSize(QSize(ICON_SIZE, ICON_SIZE))
                    else:
                        row["spell2_btn"].setText("U. Teleport")

    # ---------- helpers ----------
    def _on_opacity_changed(self, value: int):
        """Themes page crest opacity slider: value 0..100 -> 0.00..1.00"""
        self.crest_opacity = max(0.0, min(1.0, value / 100.0))
        self.opacity_value_label.setText(f"{self.crest_opacity:.2f}")
        if self.crest_opacity_effect:
            self.crest_opacity_effect.setOpacity(self.crest_opacity)

    def _on_window_opacity_changed(self, value: int):
        """Settings page window opacity: 10..100 -> 0.10..1.00"""
        op = value / 100.0
        self.setWindowOpacity(op)
        self.window_opacity_value.setText(f"{op:.2f}")

    def _on_keep_on_top_toggled(self, state: int):
        enabled = state == Qt.Checked
        flags = self.windowFlags()
        if enabled:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
        # Re-show to apply new flags
        self.show()

    def _set_cd_log(self, text, token):
        self.cd_log_token = token
        self.cd_log_label.setText(f"Cooldown Log: {text}")

    def _clear_cd_log_if_owned(self, token):
        if self.cd_log_token == token:
            self.cd_log_token = None
            self.cd_log_label.setText("Cooldown Log: None")

    def _position_background_label(self, page: QWidget):
        self.bg_label.setGeometry(QRect(0, 0, page.width(), page.height()))

    def _style_toggle_button(self, btn: QPushButton):
        spec = THEMES.get(self.current_theme, THEMES["Default"])
        accent = spec["accent"]
        fg = spec["fg"]
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                border: 1px solid rgba(255,255,255,0.25);
                background-color: rgba(255,255,255,0.06);
                color: {fg};
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: rgba(255,255,255,0.12);
            }}
            QPushButton:checked {{
                border: 2px solid {accent};
                background-color: rgba(77,144,254,0.18);
            }}
        """)

    def _style_cd_label(self, lbl: QLabel):
        """Transparent CD label with soft text shadow so it stays legible over the crest."""
        spec = THEMES.get(self.current_theme, THEMES["Default"])
        fg = spec["fg"]
        lbl.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {fg};
                border: 1px solid rgba(255,255,255,0.18);
                border-radius: 4px;
                padding: 1px 4px;
                min-width: 34px;
            }}
        """)
        lbl.setAlignment(Qt.AlignCenter)
        shadow = QGraphicsDropShadowEffect(lbl)
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 170))
        lbl.setGraphicsEffect(shadow)

    def _style_header_label(self, lbl: QLabel):
        """Transparent header label with drop shadow."""
        spec = THEMES.get(self.current_theme, THEMES["Default"])
        fg = spec["fg"]
        lbl.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {fg};
                padding: 1px 2px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(lbl)
        shadow.setBlurRadius(7)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 150))
        lbl.setGraphicsEffect(shadow)

    def _style_glassy_label(self, lbl: QLabel, underline: bool = False):
        """Transparent label for timer/log with optional accent underline and shadow."""
        spec = THEMES.get(self.current_theme, THEMES["Default"])
        fg = spec["fg"]
        accent = spec["accent"]
        underline_css = f"border-bottom: 2px solid {accent};" if underline else "border-bottom: none;"
        lbl.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: {fg};
                {underline_css}
                padding: 1px 2px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(lbl)
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 170))
        lbl.setGraphicsEffect(shadow)

    # ---------- summoner spells ----------
    def _on_summoner_click(self, row, slot: int):
        """Reads current summoner name for the slot and starts that timer."""
        label = row["spell1_label"] if slot == 1 else row["spell2_label"]
        name_key = "summ1_name" if slot == 1 else "summ2_name"
        spell_name = row.get(name_key, "Flash")
        self.start_summoner_timer(row, spell_name, label)

    def start_summoner_timer(self, row, spell_name, label):
        # Base CDs (seconds)
        base_cds = {
            "Flash": 300, "Teleport": 300,
            "Clarity": 240, "Cleanse": 240, "Exhaust": 240,
            "Ghost": 240, "Heal": 240, "Barrier": 180,
            "Ignite": 180, "Smite": 90, "U. Teleport": 0  # placeholder; handled below
        }

        # Unleashed Teleport scales 330 (lvl1) → 240 (lvl10+), step -10 per level
        if spell_name == "U. Teleport":
            level = row["level_spinner"].value()
            base_cd = max(330 - (level - 1) * 10, 240)
        else:
            base_cd = base_cds.get(spell_name, 300)

        # Apply per-row Lucidity / Cosmic
        lucidity = row["lucidity_btn"].isChecked()
        cosmic = row["cosmic_btn"].isChecked()
        if lucidity and cosmic:
            cd = base_cd * 0.78125
        elif lucidity:
            cd = base_cd * 0.9091
        elif cosmic:
            cd = base_cd * 0.8475
        else:
            cd = base_cd

        # Stop existing timer for this specific spell, if any
        key = f"summoner:{spell_name}"
        if key in row["timers"]:
            row["timers"][key].stop()

        # Show initial CD
        remaining = int(cd)
        label.setText(f"{remaining}s")

        # Log ready time (single line)
        ready_time = self.game_time + remaining
        rm, rs = divmod(ready_time, 60)
        log_text = f"{to_display_champ(row['champion'])} {spell_name} – {rm}:{rs:02d}"

        # Make a token tied to this timer instance
        timer = QTimer(self)
        token = (id(timer), key)
        self._set_cd_log(log_text, token)

        timer.setInterval(1000)

        def tick():
            nonlocal remaining
            remaining -= 1
            if remaining > 0:
                label.setText(f"{remaining}s")
            else:
                label.setText("R")  # compact 'ready' indicator
                timer.stop()
                self._clear_cd_log_if_owned(token)

        timer.timeout.connect(tick)
        timer.start()
        row["timers"][key] = timer

    # ---------- ultimates ----------
    def start_ultimate_timer(self, row):
        champ = row["champion"]
        level = row["level_spinner"].value()
        try:
            haste = int(row["haste_input"].text())
        except ValueError:
            haste = 0

        ult_cds = get_ultimate_cooldowns(champ)
        # Determine ult rank by level (6/11/16)
        if level >= 16:
            rank = 3
        elif level >= 11:
            rank = 2
        else:
            rank = 1

        base_cd = ult_cds[rank - 1]
        cdr = ability_haste_to_cdr_percent(haste)
        final_cd = base_cd * (1 - cdr)

        # Stop existing ult timer for this row
        key = "ult"
        if key in row["timers"]:
            row["timers"][key].stop()

        remaining = int(final_cd)
        label = row["ult_label"]
        label.setText(f"{remaining}s")

        # Log ready time (single line)
        ready_time = self.game_time + remaining
        rm, rs = divmod(ready_time, 60)
        log_text = f"{to_display_champ(champ)} R – {rm}:{rs:02d}"

        timer = QTimer(self)
        token = (id(timer), key)
        self._set_cd_log(log_text, token)

        timer.setInterval(1000)

        def tick():
            nonlocal remaining
            remaining -= 1
            if remaining > 0:
                label.setText(f"{remaining}s")
            else:
                label.setText("R")  # compact 'ready' indicator
                timer.stop()
                self._clear_cd_log_if_owned(token)

        timer.timeout.connect(tick)
        timer.start()
        row["timers"][key] = timer

    # ---------- theming ----------
    def apply_theme(self, theme_name: str):
        spec = THEMES.get(theme_name, THEMES["Default"])
        self.current_theme = theme_name

        bg = spec["bg"]
        fg = spec["fg"]
        accent = spec["accent"]

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg};
                color: {fg};
                font-size: 12pt;
            }}
            QLabel {{ color: {fg}; }}
            QLineEdit {{
                background-color: rgba(255,255,255,0.06);
                color: {fg};
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 4px;
                padding: 2px 4px;
            }}
            QPushButton {{
                background-color: rgba(255,255,255,0.06);
                color: {fg};
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 6px;
                padding: 4px 6px;
            }}
            QPushButton:hover {{
                background-color: rgba(255,255,255,0.12);
            }}
            QSpinBox {{
                background-color: rgba(255,255,255,0.06);
                color: {fg};
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 4px;
            }}
            QComboBox {{
                background-color: rgba(255,255,255,0.06);
                color: {fg};
                border: 1px solid rgba(255,255,255,0.15);
                border-radius: 4px;
                padding: 2px 4px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {bg};
                color: {fg};
                selection-background-color: {accent};
            }}
        """)

        # Keep timer/log transparent with shadow; add accent underline only to timer
        self._style_glassy_label(self.timer_label, underline=True)
        self._style_glassy_label(self.cd_log_label, underline=False)

        # Style toolbar buttons (start, config, themes, settings)
        style_tool_button(self.start_btn, accent, fg)
        style_tool_button(self.config_btn, accent, fg)
        style_tool_button(self.themes_btn, accent, fg)
        style_tool_button(self.settings_btn, accent, fg)

        # Restyle toggle buttons & cooldown labels & headers for current theme
        for row in getattr(self, "enemies", []):
            if "lucidity_btn" in row:
                self._style_toggle_button(row["lucidity_btn"])
            if "cosmic_btn" in row:
                self._style_toggle_button(row["cosmic_btn"])
            if "spell1_label" in row:
                self._style_cd_label(row["spell1_label"])
            if "spell2_label" in row:
                self._style_cd_label(row["spell2_label"])
            if "ult_label" in row:
                self._style_cd_label(row["ult_label"])

        # Restyle header cells on main grid
        for col in range(self.enemy_layout.columnCount()):
            item = self.enemy_layout.itemAtPosition(0, col)
            if item:
                w = item.widget()
                if isinstance(w, QLabel):
                    self._style_header_label(w)

        # Crest handling
        crest_pm = None
        if spec.get("crest_url"):
            crest_pm = _fetch_pixmap(spec["crest_url"])
        self.current_crest = crest_pm
        self._update_crest_background()

    def _update_crest_background(self):
        if not hasattr(self, "bg_label"):
            return
        page = self.main_page
        self._position_background_label(page)

        if self.current_crest:
            native_w = self.current_crest.width()
            native_h = self.current_crest.height()
            if native_w <= 0 or native_h <= 0:
                self.bg_label.hide()
                return

            target_side = int(min(page.width(), page.height()) * BG_SCALE)
            target_side = min(target_side, min(native_w, native_h))

            pm = self.current_crest.scaled(
                target_side, target_side, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.bg_label.setPixmap(pm)
            x = (page.width() - pm.width()) // 2
            y = (page.height() - pm.height()) // 2
            self.bg_label.setGeometry(x, y, pm.width(), pm.height())
            # Keep current opacity from slider
            if self.crest_opacity_effect:
                self.crest_opacity_effect.setOpacity(self.crest_opacity)
            self.bg_label.show()
            self.bg_label.lower()
        else:
            self.bg_label.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_crest_background()

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CooldownTracker()
    window.show()
    sys.exit(app.exec_())
