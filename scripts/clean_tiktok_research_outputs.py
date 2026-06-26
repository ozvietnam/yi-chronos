#!/usr/bin/env python3
"""
Build reader-friendly research transcript files from extracted TikTok text.

This does deterministic cleanup only: it removes repeated technical metadata from
the combined file format, normalizes common TikTok caption casing errors, and
keeps one compact source line per video.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT_ROOT = ROOT / "data" / "research" / "tiktok_transcripts"


COMMON_WORD_FIXES = {
    "AI": "ai",
    "BA": "ba",
    "Cao": "cao",
    "Cho": "cho",
    "Ra": "ra",
    "SAO": "sao",
    "Sai": "sai",
    "Tay": "tay",
    "Theo": "theo",
    "Xu": "xu",
    "Xin": "xin",
}

PHRASE_FIXES = [
    (r"\btử VI\b", "tử vi"),
    (r"\bTử VI\b", "Tử vi"),
    (r"\btừ VI\b", "tử vi"),
    (r"\bTừ VI\b", "Tử vi"),
    (r"\btử bi\b", "tử vi"),
    (r"\bTử bi\b", "Tử vi"),
    (r"\btừ bi đẩu số\b", "tử vi đẩu số"),
    (r"\bTừ bi đẩu số\b", "Tử vi đẩu số"),
    (r"\btử vì\b", "tử vi"),
    (r"\bTử vì\b", "Tử vi"),
    (r"\btừ vi\b", "tử vi"),
    (r"\bTừ vi\b", "Tử vi"),
    (r"\bđầu số\b", "đẩu số"),
    (r"\bĐầu số\b", "Đẩu số"),
    (r"\blá số tử VI\b", "lá số tử vi"),
    (r"\blà số tử vi\b", "lá số tử vi"),
    (r"\blà số\b", "lá số"),
    (r"\blá số này\b", "lá số này"),
    (r"\blận giải\b", "luận giải"),
    (r"\blợn giải\b", "luận giải"),
    (r"\blận lá số\b", "luận lá số"),
    (r"\b7 bại\b", "thất bại"),
    (r"\b7 nghiệp\b", "thất nghiệp"),
    (r"\bnội 7\b", "nội thất"),
    (r"\b2 BA\b", "hai ba"),
    (r"\bthứ BA\b", "thứ ba"),
    (r"\bThứ BA\b", "Thứ ba"),
    (r"\btứ chủ 8 tự\b", "tứ trụ bát tự"),
    (r"\btứ châu 8 tự\b", "tứ trụ bát tự"),
    (r"\bcùng bài\b", "cúng bái"),
    (r"\btương Lai\b", "tương lai"),
    (r"\bTương Lai\b", "Tương lai"),
    (r"\bTai họa\b", "tai họa"),
    (r"\bcái Kim\b", "cái kim"),
    (r"\bVA chạm\b", "va chạm"),
    (r"\bchồng em chào anh nhá\b", "chồng em"),
    (r"\buống rượu thứ\b", "phương diện thứ"),
    (r"\bphương vị thứ\b", "phương diện thứ"),
    (r"\bbệnh sắp phá tham\b", "mệnh Sát Phá Tham"),
    (r"\bmệnh sắp phá tham\b", "mệnh Sát Phá Tham"),
    (r"\bsắp phá tham\b", "Sát Phá Tham"),
    (r"\bphàm quân\b", "Phá Quân"),
    (r"\btham Lam\b", "Tham Lang"),
    (r"\bTham Lam\b", "Tham Lang"),
    (r"\bcựu môn\b", "Cự Môn"),
    (r"\bngười đồng lương\b", "Cơ Nguyệt Đồng Lương"),
    (r"\bcơ người đồng lương\b", "Cơ Nguyệt Đồng Lương"),
    (r"\bcơ nguyện đồng lương\b", "Cơ Nguyệt Đồng Lương"),
    (r"\bcơ nguyệt đồng lương\b", "Cơ Nguyệt Đồng Lương"),
    (r"\bphá tan\b", "Phá Tham"),
    (r"\bphá tha\b", "Phá Tham"),
    (r"\bthiên hạ\b", "thiên hạ"),
    (r"\bkhông AI\b", "không ai"),
    (r"\bAI cũng\b", "ai cũng"),
    (r"\bAI là\b", "ai là"),
    (r"\bAI nhìn\b", "anh nhìn"),
    (r"\bchống tương lai\b", "chồng tương lai"),
    (r"\bchống sau\b", "chồng sau"),
    (r"\bđời chống\b", "đời chồng"),
    (r"\blấy chống\b", "lấy chồng"),
    (r"\blay chống\b", "lấy chồng"),
    (r"\bvợ chống\b", "vợ chồng"),
    (r"\bnảy\b", "này"),
    (r"\bbao lầu\b", "bao lâu"),
    (r"\bnến tảng\b", "nền tảng"),
    (r"\bhồn nhẫn\b", "hôn nhân"),
    (r"\bLuận sưỡng\b", "Luận sướng"),
    (r"\bkhö qUa\b", "khổ qua"),
    (r"\bPhu The\b", "Phu Thê"),
    (r"\bnghé\b", "nghề"),
    (r"\bnghể\b", "nghề"),
    (r"\bngäy\b", "ngày"),
    (r"\bkhong\b", "không"),
    (r"\bthong qua\b", "thông qua"),
    (r"\bthang sinh\b", "tháng sinh"),
    (r"\bvan han\b", "vận hạn"),
    (r"\bKham pha\b", "Khám phá"),
    (r"\bphan\b", "phận"),
    (r"\bphat đạt\b", "phát đạt"),
    (r"\bPhat\b", "Phật"),
    (r"\bPhật P\b", "Phật"),
    (r"\bAmlich\b", "Âm lịch"),
    (r"\bTac hai\b", "Tác hại"),
    (r"\bbổ me\b", "bố mẹ"),
    (r"\bgidu\b", "giàu"),
    (r"\bgiảu\b", "giàu"),
    (r"\btải lộc\b", "tài lộc"),
    (r"\bthì lam\b", "thì làm"),
    (r"\bgi\b", "gì"),
    (r"\bvỉ trí\b", "vị trí"),
    (r"\bVong Trưởng Sinh\b", "Vòng Trường Sinh"),
    (r"\bdo gid sinh\b", "đổi giờ sinh"),
    (r"\bthi cảng\b", "thì càng"),
    (r"\bdau rắc\b", "đâu rắc"),
    (r"\bSóng gid\b", "Sống nhờ"),
    (r"\bphủ đởi trai\b", "phụ đời trai"),
    (r"\bhồn nhần\b", "hôn nhân"),
    (r"\bhồn nhẫn\b", "hôn nhân"),
    (r"\bnhẫn duyên\b", "nhân duyên"),
    (r"\bNhẫn quả\b", "Nhân quả"),
    (r"\bdung cách\b", "đúng cách"),
    (r"\bhanh thông\b", "hanh thông"),
    (r"\bKhi Thiên Cơ\b", "Khi Thiên Cơ"),
    (r"\bthực sự nghi\b", "thực sự nghĩ"),
    (r"\bNgồi sao\b", "Ngôi sao"),
    (r"\blam an xa\b", "làm ăn xa"),
    (r"\bmay man\b", "may mắn"),
    (r"\bgap chong\b", "gặp chồng"),
    (r"\bVảo nam nao\b", "vào năm nào"),
    (r"\bthanh công\b", "thành công"),
    (r"\bNang khiéu bam sinh\b", "Năng khiếu bẩm sinh"),
    (r"\bcon cải\b", "con cái"),
    (r"\bĐồ tuổi\b", "Độ tuổi"),
    (r"\bChon chong\b", "Chọn chồng"),
    (r"\bnảo\b", "nào"),
    (r"\bco tam thức\b", "có tâm thức"),
    (r"\bSắt tỉnh\b", "Sát tinh"),
    (r"\bhang nhất\b", "hạng nhất"),
    (r"\bHôn phổi\b", "Hôn phối"),
    (r"\bTrồng sẽ\b", "Chồng sẽ"),
    (r"\bnhin của\b", "nhìn của"),
    (r"\bquan Giàu\b", "Quan giàu"),
    (r"\bPhu Thề\b", "Phu Thê"),
    (r"\blành dữ\b", "lành dữ"),
    (r"\bDung mạo\b", "Dung mạo"),
    (r"\bxinh xan\b", "xinh xắn"),
    (r"\bthưởng có\b", "thường có"),
    (r"\bquan trong\b", "quan trọng"),
    (r"\btỉnh duyén\b", "tình duyên"),
    (r"\bnam sau\b", "năm sau"),
    (r"\bTải Bạch\b", "Tài Bạch"),
    (r"\blay Mệnh\b", "lấy Mệnh"),
    (r"\bthi hon nhãn viên man\b", "thì hôn nhân viên mãn"),
    (r"\btiền đổ\b", "tiền đồ"),
    (r"\btiển đồ\b", "tiền đồ"),
    (r"\bbản thần\b", "bản thân"),
    (r"\bThién Di\b", "Thiên Di"),
    (r"\bLý do\b", "Lý do"),
    (r"\bxdu\b", "xấu"),
    (r"\bnhan sắc\b", "nhan sắc"),
    (r"\blay được\b", "lấy được"),
    (r"\bmat sẽ\b", "mặt sẽ"),
    (r"\bmất sẽ\b", "mặt sẽ"),
    (r"\bCoi số mệnh sau này mặt sẽ ra sao: an\b", "Coi số mệnh sau này mặt sẽ ra sao"),
    (r"\bCap đồi\b", "Cặp đôi"),
    (r"\bđồi oan gia\b", "đôi oan gia"),
    (r"\bj\.\b", "gì"),
    (r"\bhôn k nhãn\b", "hôn nhân"),
    (r"\bthần ông Huỳnh Để\b", "thần Ông Huỳnh Đế"),
    (r"\bconTrdihay / con\b", "con trai hay con"),
    (r"\bTử Tức\b", "Tử Tức"),
    (r"\bTu Tức\b", "Tử Tức"),
    (r"\bBại tỉnh\b", "Bại tinh"),
    (r"\bquý tử ey F\b", "quý tử"),
    (r"\bcốtcách\b", "cốt cách"),
    (r"\btình số\b", "tính số"),
    (r"\btinh số\b", "tính số"),
    (r"\bHén\b", "Hèn"),
    (r"\blận dan\b", "luận đoán"),
    (r"\bHầu vẫn\b", "Hậu vận"),
    (r"\bphan\b", "phận"),
    (r"\bNhãn duyên\b", "Nhân duyên"),
    (r"\bChính tỉnh\b", "Chính tinh"),
    (r"\btải chính\b", "tài chính"),
    (r"\bdé bi ban đởi phản bồi\b", "dễ bị bạn đời phản bội"),
    (r"\bdé lấy\b", "dễ lấy"),
    (r"\bgioi kiem tien\b", "giỏi kiếm tiền"),
    (r"\bGidu lam\b", "giàu lắm"),
    (r"\bChöng\b", "Chồng"),
    (r"\bnhan sắc\b", "nhan sắc"),
    (r"\bNhìn phat\b", "Nhìn phát"),
    (r"\blay chồng\b", "lấy chồng"),
    (r"\bsông không tho\b", "sống không thọ"),
    (r"\blấychồng\b", "lấy chồng"),
    (r"\bcangdechialy\b", "càng dễ chia ly"),
]

BOILERPLATE_PATTERNS = [
    r"\bHãy subscribe cho kênh La(?:\s+La)?\s+School\b",
    r"\bsubscribe cho kênh La(?:\s+La)?\s+School\b",
    r"\bHãy subscribe cho kênh lalaschool\b",
    r"\bHãy subscribe cho kênh Ghiền Mì Gõ\b",
    r"\bHãy subscribe cho kênh\b",
    r"\blalaschool\b",
    r"\bHãy đăng ký kênh để ủng hộ kênh mình nhé\b",
    r"\bHãy đăng ký kênh\b",
    r"\bđể ủng hộ kênh của mình nhé\b",
    r"\bĐể không bỏ lỡ những video hấp dẫn\b",
    r"\bCảm ơn (?:người nghe|các bạn) đã theo dõi(?: và hẹn gặp lại)?\b",
    r"\bHẹn gặp lại\b",
    r"\bngười nghe trong những video tiếp theo\b",
    r"\bmình nhé\b",
]

DOMAIN_TERMS = [
    "tử vi",
    "đẩu số",
    "lá số",
    "cung ",
    "sao ",
    "mệnh",
    "phu thê",
    "tử tức",
    "tài bạch",
    "quan lộc",
    "thiên ",
    "thái ",
    "vũ khúc",
    "cự môn",
    "tham lang",
    "phá quân",
    "liêm trinh",
    "thất sát",
    "hóa ",
    "tuần",
    "triệt",
]


def load_manifest(channel_dir: Path) -> list[dict[str, Any]]:
    manifest = channel_dir / "text_manifest.jsonl"
    return [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]


def format_date(upload_date: str | None) -> str:
    if not upload_date or len(upload_date) != 8:
        return upload_date or ""
    return f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}"


def topic_from_title(title: str, channel_name: str) -> str:
    topic = re.sub(r"\s+", " ", title or "").strip()
    topic = re.sub(r"^\s*Tử\s*Vi\s*Bôn\s*Ba\s*[:,-]?\s*", "", topic, flags=re.IGNORECASE)
    topic = re.sub(r"\s*\.\.\.$", "", topic).strip()
    if len(topic) > 120:
        topic = topic[:117].rstrip(" ,.;:-") + "..."
    return topic or channel_name


def extract_body(text_path: Path) -> str:
    text = text_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    start = 0
    for idx, line in enumerate(lines):
        if line.strip().startswith("Thời lượng:"):
            start = idx + 1
            break
    body = "\n".join(lines[start:]).strip()
    body = re.sub(r"\n?Nguồn lời thoại: Whisper local.*$", "", body, flags=re.S).strip()
    body = re.sub(r"\n?Nguồn lời thoại: OCR thumbnail/poster.*$", "", body, flags=re.S).strip()
    return body


def normalize_text(text: str, source: str = "") -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^[Ñï|_\\.,;: -]+", "", text).strip()
    for pattern in BOILERPLATE_PATTERNS:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)
    for _ in range(2):
        for pattern, replacement in PHRASE_FIXES:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE if pattern.islower() else 0)
    for wrong, right in COMMON_WORD_FIXES.items():
        text = re.sub(rf"\b{re.escape(wrong)}\b", right, text)
    text = re.sub(r"\b(à|ờ|ừ|ừm|ạ)\b\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(a|ơ)\s+(?=[a-zà-ỹ])", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(đúng không|em hiểu không|đấy|nhá|nha)\b[,.]?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(các bạn|anh em mình)\b", "người nghe", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(\d)\s+(\d{2})\b", r"\1\2", text)
    text = re.sub(r"\s+([,.?!:;])", r"\1", text)
    text = re.sub(r"([,.?!:;])([^\s])", r"\1 \2", text)
    text = re.sub(r"\s+", " ", text).strip()
    if source == "ocr_thumbnail":
        text = re.sub(r"[|_\\]+", " ", text)
        text = re.sub(r"\b(?:ey F|mực|ie|la|re 1|x1|lv|z1|A|Í|š|l|mo DĐ|mat at|eels|els|mm m|os m|HNMMWMAA|HNMWWMAA|TMMWWMAM|HN dV MẶ|HMWWEA|Ws|Vs|NÌ|NỈ|HP|Nee|Ne|NZ|NS|Nv|N|SỈ|NU|XÃ|eae|ae|th|ck a3|ad|ny|ial|ram rap|oe|DĐ)\b", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"^[0-9\s%+.,;:/()\-]+", "", text).strip()
        text = re.sub(r"\s+[0-9\s%+.,;:/()\-]+$", "", text).strip()
        text = re.sub(r"\s+\b(?:m|ae|th|ad|ay|ú|é|Ẳ|ủ|nl|NHI|mm|co|do|ra|bs|se|tn|ah|MM|MẶ|O|a3|P|È|y|x|ck|NLS|F|Ws|Vs)\b(?:\s+\b(?:m|ae|th|ad|ay|ú|é|Ẳ|ủ|nl|NHI|mm|co|do|ra|bs|se|tn|ah|MM|MẶ|O|a3|P|È|y|x|ck|NLS|F|Ws|Vs)\b)*\s*$", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"\s*[-–]\s*$", "", text).strip()
        text = re.sub(r"^[^A-Za-zÀ-ỹ0-9]+", "", text).strip()
        text = re.sub(r"\s+", " ", text).strip(" .,:;|-")
    text = re.sub(r"([.!?])\s+", r"\1\n\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def compact_text(text: str) -> str:
    return re.sub(r"\s*\n+\s*", " ", text).strip()


def has_research_content(text: str, source: str) -> bool:
    compact = compact_text(text)
    if source == "ocr_thumbnail":
        return len(compact) >= 8
    if len(compact) < 20:
        return False
    if source == "whisper_local":
        lowered = compact.lower()
        return len(compact) >= 100 and any(term in lowered for term in DOMAIN_TERMS)
    return True


def channel_name(rows: list[dict[str, Any]], fallback: str) -> str:
    for row in rows:
        if row.get("channel"):
            return str(row["channel"])
    return fallback


def build_clean_file(channel_slug: str, output_name: str | None = None) -> Path:
    channel_dir = TRANSCRIPT_ROOT / channel_slug
    final_dir = channel_dir / "final"
    final_dir.mkdir(exist_ok=True)
    rows = load_manifest(channel_dir)
    rows.sort(key=lambda row: (row.get("upload_date") or "", row.get("id") or ""))
    display_name = channel_name(rows, channel_slug)
    output_path = channel_dir / (output_name or f"{channel_slug}_research_clean.txt")

    parts = [
        f"# {display_name} - bản lời thoại sạch",
        "",
        f"Cập nhật bản sạch: {datetime.now(timezone.utc).isoformat()}",
        f"Tổng số video: {len(rows)}",
        "",
        "Ghi chú: bản này đã bỏ metadata kỹ thuật lặp, chuẩn hóa các lỗi caption phổ biến và giữ một dòng nguồn cho từng video.",
        "",
        "---",
        "",
    ]

    missing = 0
    video_records: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, start=1):
        text_path_value = row.get("text_path")
        text_path = ROOT / text_path_value if text_path_value else channel_dir / "text" / f"{row['id']}.txt"
        title = row.get("title") or row.get("description") or row["id"]
        topic = topic_from_title(title, display_name)
        date = format_date(row.get("upload_date"))
        duration = row.get("duration_string") or row.get("duration") or ""
        url = row.get("webpage_url") or row.get("url") or ""
        source = row.get("transcript_source") or ("subtitle" if row.get("subtitle_path") else "text")

        parts.append(f"## {idx:03d}. {date} - {topic}")
        parts.append("")
        parts.append(f"Nguồn: {url} | Thời lượng: {duration} | Transcript: {source}")
        parts.append("")
        clean_body = ""
        if text_path.exists():
            clean_body = normalize_text(extract_body(text_path), source)
            if has_research_content(clean_body, source):
                parts.append(clean_body)
            else:
                clean_body = ""
                parts.append("[Không nhận diện được lời thoại rõ ràng.]")
        else:
            missing += 1
            parts.append("[Chưa có lời thoại.]")
        video_records.append(
            {
                "idx": idx,
                "date": date,
                "title": topic,
                "video_id": row["id"],
                "url": url,
                "duration": duration,
                "has_transcript": bool(clean_body),
                "transcript_source": source,
                "chars": len(compact_text(clean_body)),
                "text": compact_text(clean_body),
            }
        )
        parts.append("")
        parts.append("---")
        parts.append("")

    output_path.write_text("\n".join(parts), encoding="utf-8")
    (channel_dir / "videos.json").write_text(json.dumps(video_records, ensure_ascii=False, indent=1), encoding="utf-8")
    (final_dir / "transcripts.txt").write_text("\n".join(parts), encoding="utf-8")
    (final_dir / "videos.json").write_text(json.dumps(video_records, ensure_ascii=False, indent=1), encoding="utf-8")

    index_lines = [
        f"# {display_name} - mục lục bản sạch",
        "",
        f"Tổng số video: {len(video_records)}",
        f"Có lời thoại: {sum(1 for record in video_records if record['has_transcript'])}",
        "",
    ]
    for record in video_records:
        index_lines.append(
            f"{record['idx']:03d}. {record['date']} | {record['duration']} | {record['title']} | {record['transcript_source']} | {record['video_id']}"
        )
    (final_dir / "index.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"Wrote {output_path} ({len(rows)} videos, missing text files: {missing})")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("channels", nargs="+", help="Channel folder slug(s), e.g. huytuantuvi")
    parser.add_argument("--output-name", default=None, help="Use only with one channel")
    args = parser.parse_args()
    if args.output_name and len(args.channels) != 1:
        parser.error("--output-name can only be used with one channel")
    for channel in args.channels:
        build_clean_file(channel, args.output_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
