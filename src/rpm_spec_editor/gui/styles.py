def build_style(colors):

    return f"""
    QMainWindow {{
        background-color: {colors["background"]};
    }}
    
    QPlainTextEdit {{
        background-color: {colors["background"]};
        color: {colors["text"]};
        border: none;
        selection-background-color: {colors["selection"]};
    }}
    
    QTreeView {{
        background-color: {colors["sidebar"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
    }}
    
    QTreeWidget {{
        background-color: {colors["secondary_background"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        alternate-background-color: {colors["secondary_background"]};
        outline: none;
    }}
    
    QTreeWidget::item:selected {{
        background-color: {colors["selection"]};
        color: {colors["text"]};
    }}
    
    
    QTreeWidget::item:hover {{
        background-color: {colors["button_hover"]};
    }}
    
    QHeaderView::section {{
        background-color: {colors["sidebar"]};
        color: {colors["text"]};
        padding: 4px;
        border: none;
    }}
    
    QMenuBar {{
        background-color: {colors["secondary_background"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
    }}
    
    QMenu::item:selected {{
        background-color: {colors["selection"]};
    }}
    
    QSplitter::handle {{
        background-color: {colors["border"]};
    }}
    
    QStatusBar {{
        background-color: {colors["secondary_background"]};
        color: {colors["text"]};
    }}
    
    QLineEdit {{
        background-color: {colors["secondary_background"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        padding: 4px;
    }}
    
    QPushButton {{
        background-color: {colors["sidebar"]};
        color: {colors["text"]};
        border: 1px solid {colors["border"]};
        padding: 4px 8px;
    }}
    
    QPushButton:hover {{
        background-color: {colors["button_hover"]};
    }}
    
    QTabWidget::pane {{
        border: 1px solid {colors["border"]};
        background: {colors["secondary_background"]};
    }}
    
    
    QTabBar {{
        qproperty-expanding: false;
    }}
    
    
    QTabBar::tab {{
        background: {colors["sidebar"]};
        color: {colors["text"]};
        padding: 6px 12px;
        margin-right: 2px;
        border: 1px solid {colors["border"]};
    }}
    
    
    QTabBar::tab:selected {{
        background: {colors["selection"]};
    }}
    
    """