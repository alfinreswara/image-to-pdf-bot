#!/usr/bin/env python3
"""Telegram bot for converting images into a single PDF."""

from __future__ import annotations

import logging
import os
import shutil
import uuid
from pathlib import Path

from telegram import Document, Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from image_to_pdf import SUPPORTED_EXTENSIONS, convert_images_to_pdf


BASE_DIR = Path(__file__).resolve().parent
SESSION_DIR = BASE_DIR / "telegram_sessions"
MAX_IMAGES_PER_SESSION = 50

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def get_user_dir(user_id: int) -> Path:
    path = SESSION_DIR / str(user_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_image_paths(user_id: int) -> list[Path]:
    user_dir = get_user_dir(user_id)
    return sorted(
        path
        for path in user_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def clear_user_session(user_id: int) -> None:
    user_dir = SESSION_DIR / str(user_id)
    if user_dir.exists():
        shutil.rmtree(user_dir)


def document_is_supported_image(document: Document) -> bool:
    file_name = document.file_name or ""
    mime_type = document.mime_type or ""

    return (
        Path(file_name).suffix.lower() in SUPPORTED_EXTENSIONS
        or mime_type.startswith("image/")
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Kirim satu atau beberapa gambar, lalu ketik /done untuk dibuat PDF.\n\n"
        "Perintah:\n"
        "/done - buat PDF dari gambar yang sudah dikirim\n"
        "/status - cek jumlah gambar\n"
        "/cancel - hapus gambar yang sedang antre"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    count = len(get_image_paths(user_id))

    if count == 0:
        await update.message.reply_text("Belum ada gambar. Kirim gambar dulu ya.")
        return

    await update.message.reply_text(f"Saat ini ada {count} gambar dalam antrean.")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    clear_user_session(user_id)
    await update.message.reply_text("Antrean gambar sudah dihapus.")


async def save_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    image_paths = get_image_paths(user_id)

    if len(image_paths) >= MAX_IMAGES_PER_SESSION:
        await update.message.reply_text(
            f"Batas maksimal {MAX_IMAGES_PER_SESSION} gambar per PDF. "
            "Ketik /done untuk membuat PDF atau /cancel untuk mulai ulang."
        )
        return

    message = update.message
    user_dir = get_user_dir(user_id)

    if message.photo:
        telegram_file = await message.photo[-1].get_file()
        suffix = ".jpg"
    elif message.document and document_is_supported_image(message.document):
        telegram_file = await message.document.get_file()
        suffix = Path(message.document.file_name or "").suffix.lower() or ".jpg"
        if suffix not in SUPPORTED_EXTENSIONS:
            suffix = ".jpg"
    else:
        await message.reply_text("File itu belum didukung. Kirim gambar JPG, PNG, WEBP, BMP, GIF, atau TIFF.")
        return

    next_number = len(image_paths) + 1
    output_path = user_dir / f"{next_number:03d}-{uuid.uuid4().hex}{suffix}"

    await telegram_file.download_to_drive(output_path)
    await message.reply_text(
        f"Gambar {next_number} diterima. Kirim gambar lagi atau ketik /done."
    )


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    image_paths = get_image_paths(user_id)

    if not image_paths:
        await update.message.reply_text("Belum ada gambar untuk dibuat PDF.")
        return

    output_path = get_user_dir(user_id) / "hasil.pdf"

    await update.message.chat.send_action(ChatAction.UPLOAD_DOCUMENT)

    try:
        convert_images_to_pdf(image_paths, output_path)
        with output_path.open("rb") as pdf_file:
            await update.message.reply_document(
                document=pdf_file,
                filename="hasil.pdf",
                caption=f"PDF selesai dibuat dari {len(image_paths)} gambar.",
            )
    except Exception:
        logger.exception("Failed to convert images for user %s", user_id)
        await update.message.reply_text(
            "Maaf, PDF gagal dibuat. Coba kirim gambar lain atau mulai ulang dengan /cancel."
        )
        return
    finally:
        clear_user_session(user_id)


async def unsupported(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Kirim gambar sebagai foto atau dokumen, lalu ketik /done."
    )


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN belum diatur. Contoh: "
            "set TELEGRAM_BOT_TOKEN=123456:ABCDEF"
        )

    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("done", done))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, save_image))
    app.add_handler(MessageHandler(filters.ALL, unsupported))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
