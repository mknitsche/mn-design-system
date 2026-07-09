"""Pydantic-Contracts fuer die Twin-Chat-Web-Komponenten (Build-Spec cld1-S57, T-3.4).

Eigene Datei statt Erweiterung von `contracts.py` — die bestehenden Web-Contracts
bleiben unangetastet (LP-08 upstream-first: neue Bausteine kommen additiv, kein
Risiko fuer die live gerenderten Bestandsseiten /dateien etc.).

Vier Komponenten fuer `/kabinett/chat`:
- ChatStreamInput   — Nachrichten-Strom-Rahmen (Shell + leerer Zustand).
- ChatComposerInput — Eingabefeld + Senden/Unterbrechen + Hinweis-Zeile.
- StreamCursorInput — Tipp-Indikator waehrend SSE-Deltas eintreffen.
- StatusBannerInput — Sitzungsstatus (gesperrt/entsperrt/Budget-Block/Fehler).

Die eigentlichen Chat-Nachrichten (Rolle owner/twin, Markdown-Body, Tool-Badges)
werden AUSSCHLIESSLICH clientseitig durch chat.js in den `mn-chat-stream`-Rahmen
gerendert (DOM-Knoten, kein innerHTML — XSS-Schutz). Diese Contracts modellieren
deshalb bewusst nur den serverseitig gerenderten Rahmen; das CSS
(`render_chat_stream_css()`) definiert zusaetzlich den vollstaendigen Klassen-
Vertrag fuer die von chat.js erzeugten Nachrichten-Knoten (Rolle-Modifier,
Markdown-Body-Typografie, Code-Bloecke, Tool-Badge) — dokumentiert im Docstring
von `chat_stream.py`.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ChatStreamInput(BaseModel):
    """API-Contract fuer render_chat_stream_html() — der leere Nachrichten-Rahmen.

    stream_id: DOM-id des Containers, den chat.js befuellt (Default "chat-stream").
    empty_hint: Text im Leer-Zustand, bevor die erste Nachricht eintrifft.
    aria_label: Landmark-Label fuer die Live-Region (Screenreader).
    """

    model_config = {"extra": "forbid", "frozen": True}

    stream_id: str = Field(default="chat-stream", min_length=1)
    empty_hint: str = Field(default="Noch keine Nachrichten.", min_length=1)
    aria_label: str = Field(default="Chat-Verlauf", min_length=1)


class ChatComposerInput(BaseModel):
    """API-Contract fuer render_chat_composer_html() — Eingabe-Leiste.

    textarea_id / send_id / interrupt_id / hint_id: DOM-ids, die chat.js verdrahtet.
    placeholder: Platzhaltertext im leeren Eingabefeld.
    send_label / interrupt_label: Beschriftung der beiden Aktions-Buttons.
    hint: initialer Text der Hinweis-Zeile (Zeichen-/Kosten-Anzeige); chat.js
          aktualisiert den Inhalt laufend.
    """

    model_config = {"extra": "forbid", "frozen": True}

    textarea_id: str = Field(default="chat-input", min_length=1)
    send_id: str = Field(default="chat-send", min_length=1)
    interrupt_id: str = Field(default="chat-interrupt", min_length=1)
    hint_id: str = Field(default="chat-hint", min_length=1)
    placeholder: str = Field(default="Nachricht schreiben …", min_length=1)
    send_label: str = Field(default="Senden", min_length=1)
    interrupt_label: str = Field(default="Stopp", min_length=1)
    hint: str = Field(default="0 Zeichen", min_length=1)


class StreamCursorInput(BaseModel):
    """API-Contract fuer render_stream_cursor_html() — Tipp-Indikator.

    cursor_id: DOM-id; chat.js schaltet `hidden` waehrend eines laufenden Turns.
    label: begleitender Text neben den drei pulsierenden Punkten.
    """

    model_config = {"extra": "forbid", "frozen": True}

    cursor_id: str = Field(default="stream-cursor", min_length=1)
    label: str = Field(default="denkt …", min_length=1)


class StatusBannerState(str, Enum):
    """Die vier Sitzungs-Zustaende der Twin-Chat-Seite."""

    LOCKED = "locked"
    UNLOCKED = "unlocked"
    BUDGET_BLOCK = "budget-block"
    ERROR = "error"


class StatusBannerInput(BaseModel):
    """API-Contract fuer render_status_banner_html() — Sitzungsstatus-Zeile.

    banner_id: DOM-id; chat.js aktualisiert state-Klasse + message-Text laufend.
    state: Server-seitiger Startzustand — IMMER LOCKED (fail-safe: der Server
           kennt den Entsperrt-Status erst nach dem clientseitigen /api/me-Call;
           bis dahin gilt die restriktivste Annahme).
    message: begleitender Text.
    """

    model_config = {"extra": "forbid", "frozen": True}

    banner_id: str = Field(default="status-banner", min_length=1)
    state: StatusBannerState = StatusBannerState.LOCKED
    message: str = Field(min_length=1)
