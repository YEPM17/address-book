"""Burn captions into the recorded demo frames and encode an MP4.

Requires Pillow (bundled with the DSH runtime) and an ffmpeg binary with an
H.264 encoder. Usage:

    python scripts/build_demo_video.py <work-dir> <output.mp4>
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FFMPEG = r"C:\Program Files (x86)\Lenovo\LegionZone\2.0.23.3251\SEGamingAI\services\editor\ffmpeg.exe"
FONT = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
SERIF = r"C:\Windows\Fonts\georgia.ttf"
W, H = 1440, 960
INK = (19, 36, 32)
CREAM = (245, 240, 228)
MUTED = (154, 170, 162)
ACCENT = (79, 209, 197)
AMBER = (201, 138, 18)


def load_font(path: str, size: int):
    return ImageFont.truetype(path, size)


def quote(path: Path) -> str:
    return f"file '{Path(path).as_posix()}'"


def run(args: list[str], cwd: Path | None = None) -> None:
    result = subprocess.run([FFMPEG, *args], cwd=cwd, text=True)
    if result.returncode != 0:
        raise SystemExit(f"ffmpeg failed with {result.returncode}")


def caption_for(segments: list[dict], at: int) -> str:
    current = ""
    for segment in segments:
        if segment["at"] <= at:
            current = segment["caption"]
        else:
            break
    return current


def draw_caption(image: Image.Image, caption: str) -> None:
    if not caption:
        return
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    bar_top = H - 96
    draw.rectangle([0, bar_top, W, H], fill=(10, 21, 18, 216))
    draw.rectangle([0, bar_top, W, bar_top + 3], fill=(201, 138, 18, 255))
    font = load_font(FONT, 25)
    draw.text((44, bar_top + 48), caption, font=font, fill=(245, 240, 228, 255), anchor="lm")
    brand = load_font(FONT_BOLD, 15)
    draw.text((W - 44, bar_top + 48), "FOLIO", font=brand, fill=(126, 224, 213, 230), anchor="rm")
    composited = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    image.paste(composited, (0, 0))


def title_card() -> Image.Image:
    image = Image.new("RGB", (W, H), INK)
    draw = ImageDraw.Draw(image)
    # soft decorative circles
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.ellipse([W - 520, -260, W + 200, 460], fill=(26, 138, 127, 42))
    odraw.ellipse([-260, H - 420, 360, H + 120], fill=(201, 138, 18, 26))
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle([96, 92, 176, 172], radius=20, fill=(15, 118, 110))
    draw.text((136, 132), "F", font=load_font(SERIF, 52), fill=CREAM, anchor="mm")

    draw.text((96, 300), "Folio 通讯录", font=load_font(FONT_BOLD, 72), fill=CREAM)
    draw.text(
        (100, 410),
        "书签 · 多联系方式 · Excel 导入导出",
        font=load_font(FONT, 30),
        fill=MUTED,
    )
    draw.rectangle([100, 480, 260, 485], fill=AMBER)
    draw.text(
        (100, 540),
        "一个用 Flask + SQLite + 原生前端实现的通讯录",
        font=load_font(FONT, 24),
        fill=(190, 202, 196),
    )
    draw.text(
        (100, 590),
        "EE308FZ Software Engineering · 2601_FZU-MU_SE",
        font=load_font(FONT, 19),
        fill=(126, 145, 137),
    )
    return image


def outro_card() -> Image.Image:
    image = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle([96, 120, 176, 200], radius=20, fill=(15, 118, 110))
    draw.text((136, 160), "F", font=load_font(SERIF, 52), fill=CREAM, anchor="mm")
    draw.text((96, 300), "谢谢观看", font=load_font(FONT_BOLD, 64), fill=(27, 36, 34))
    lines = [
        "书签联系人 · 多种联系方式 · Excel 导入导出",
        "Python Flask · SQLite · openpyxl · 原生 JavaScript",
        "源代码、截图与演示数据见 GitHub 仓库",
    ]
    font = load_font(FONT, 24)
    for index, line in enumerate(lines):
        draw.text((100, 420 + index * 52), line, font=font, fill=(70, 83, 80))
    draw.rectangle([100, 600, 260, 605], fill=(15, 118, 110))
    draw.text(
        (100, 660),
        "Folio Address Book v1.0.0",
        font=load_font(FONT_BOLD, 20),
        fill=(123, 133, 128),
    )
    return image


def main() -> None:
    work = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    frames = json.loads((work / "frames.json").read_text(encoding="utf-8"))
    segments = json.loads((work / "segments.json").read_text(encoding="utf-8"))
    segments.sort(key=lambda item: item["at"])

    annotated = work / "annotated"
    annotated.mkdir(exist_ok=True)

    entries: list[tuple[int, Path, str]] = []
    for frame in frames:
        entries.append((frame["at"], work / "frames" / frame["file"], frame["file"]))

    # A duplicated frame at each segment start makes captions switch on time.
    for segment in segments:
        previous = [entry for entry in entries if entry[0] <= segment["at"]]
        if not previous:
            continue
        source = max(previous, key=lambda entry: entry[0])[1]
        name = f"caption-{segment['at']:05d}.jpg"
        entries.append((segment["at"], source, name))
    entries.sort(key=lambda entry: entry[0])

    concat_lines: list[str] = []
    for index, (at, source, name) in enumerate(entries):
        image = Image.open(source).convert("RGB")
        draw_caption(image, caption_for(segments, at))
        target = annotated / f"frame-{index:05d}.jpg"
        image.save(target, quality=90, subsampling=1)
        next_at = entries[index + 1][0] if index + 1 < len(entries) else at + 2000
        duration = min(4.0, max(0.05, (next_at - at) / 1000))
        concat_lines.append(f"file 'annotated/{target.name}'")
        concat_lines.append(f"duration {duration:.3f}")
    concat_lines.append(f"file 'annotated/{target.name}'")

    intro = work / "intro.jpg"
    outro = work / "outro.jpg"
    title_card().save(intro, quality=92)
    outro_card().save(outro, quality=92)

    (work / "main.txt").write_text("\n".join(concat_lines), encoding="utf-8")

    main_video = work / "main.mp4"
    intro_video = work / "intro.mp4"
    outro_video = work / "outro.mp4"
    run(
        [
            "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", "main.txt",
            "-vf", "fps=30,format=yuv420p",
            "-c:v", "h264_mf", "-b:v", "5M",
            str(main_video),
        ],
        cwd=work,
    )
    for image, seconds, target in ((intro, "2.6", intro_video), (outro, "2.8", outro_video)):
        run(
            [
                "-y", "-hide_banner", "-loglevel", "error",
                "-loop", "1", "-t", seconds, "-i", str(image),
                "-vf", "fps=30,format=yuv420p",
                "-c:v", "h264_mf", "-b:v", "5M",
                str(target),
            ],
            cwd=work,
        )

    combined = work / "combined.txt"
    combined.write_text(
        "\n".join(quote(path) for path in (intro_video, main_video, outro_video)),
        encoding="utf-8",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    run(
        [
            "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(combined),
            "-c", "copy", "-movflags", "+faststart", str(output),
        ],
        cwd=work,
    )
    print(f"wrote {output}")


if __name__ == "__main__":
    main()