import streamlit as st
import re
import base64
from io import BytesIO
from PIL import Image
import requests

def display_llm_response(response_text):
    segments = split_text_and_images(response_text)

    for segment in segments:
        if segment["type"] == "text":
            if segment["content"].strip():
                st.markdown(segment["content"])
        elif segment["type"] == "image":
            try:
                display_image(segment)
            except Exception as e:
                st.error(f"Ошибка при отображении изображения: {e}")
                st.text(f"Ссылка на изображение: {segment['src'][:100]}...")

def split_text_and_images(text):
    segments = []
    placeholders = {}

    def replace_markdown_image(match):
        placeholder = f"__IMAGE_PLACEHOLDER_{len(placeholders)}__"
        placeholders[placeholder] = {
            "type": "image",
            "format": "markdown",
            "alt": match.group(1),
            "src": match.group(2)
        }
        return placeholder

    text = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_markdown_image, text)

    def replace_html_image(match):
        placeholder = f"__IMAGE_PLACEHOLDER_{len(placeholders)}__"
        src = re.search(r'src=["\'](.*?)["\']', match.group(0))
        alt = re.search(r'alt=["\'](.*?)["\']', match.group(0))
        placeholders[placeholder] = {
            "type": "image",
            "format": "html",
            "src": src.group(1) if src else "",
            "alt": alt.group(1) if alt else ""
        }
        return placeholder

    text = re.sub(r'<img\s+[^>]*?>', replace_html_image, text)

    def replace_data_url(match):
        placeholder = f"__IMAGE_PLACEHOLDER_{len(placeholders)}__"
        placeholders[placeholder] = {
            "type": "image",
            "format": "data_url",
            "src": match.group(0),
            "alt": "Base64 изображение"
        }
        return placeholder

    text = re.sub(r'data:image\/[a-zA-Z]+;base64,[a-zA-Z0-9+/=]+', replace_data_url, text)

    parts = re.split(r'(__IMAGE_PLACEHOLDER_\d+__)', text)

    for part in parts:
        if part.startswith("__IMAGE_PLACEHOLDER_"):
            segments.append(placeholders[part])
        else:
            segments.append({"type": "text", "content": part})

    return segments

def display_image(image_segment):
    caption = image_segment.get("alt", "")

    if image_segment["format"] in ["markdown", "html"]:
        src = image_segment["src"]

        if src.startswith("data:image"):
            b64_data = src.split(",")[1]
            image_data = base64.b64decode(b64_data)
            image = Image.open(BytesIO(image_data))
            st.image(image, caption=caption)
        elif src.startswith(("http://", "https://")):
            try:
                response = requests.get(src, timeout=5)
                response.raise_for_status()
                image = Image.open(BytesIO(response.content))
                st.image(image, caption=caption)
            except requests.exceptions.RequestException as e:
                st.error(f"Ошибка при загрузке изображения: {e}")
                st.code(src)
        else:
            st.text(f"Неподдерживаемая ссылка на изображение: {src}")

    elif image_segment["format"] == "data_url":
        src = image_segment["src"]
        b64_data = src.split(",")[1]
        image_data = base64.b64decode(b64_data)
        image = Image.open(BytesIO(image_data))
        st.image(image, caption=caption)
