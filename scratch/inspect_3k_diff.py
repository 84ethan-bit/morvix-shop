import re
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def inspect_3k_diff():
    with open("scratch/after_click.html", "r", encoding="utf-8") as f:
        html = f.read()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔍 [3.7KB 증가 DOM 레이어 속성 정밀 계측 리포트]")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # 1. body 직계 자식 노드 조사
    body_children = re.findall(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
    if body_children:
        tags = re.findall(r'<([a-zA-Z0-9-]+)[^>]*>', body_children[0])
        print(f"📌 [body 직계 자식 태그 목록] ({len(tags)}개): {tags[:15]}")

    # 2. role="dialog" 또는 aria-modal="true" 레이어 수색
    dialogs = re.findall(r'<[^>]*role="dialog"[^>]*>(.*?)</[^>]+>', html, re.DOTALL)
    modals = re.findall(r'<[^>]*aria-modal="true"[^>]*>(.*?)</[^>]+>', html, re.DOTALL)
    print(f"📌 [role='dialog'] 요소 개수: {len(dialogs)}개")
    print(f"📌 [aria-modal='true'] 요소 개수: {len(modals)}개")

    # 3. position:fixed / absolute 레이어 수색
    fixed_layers = re.findall(r'style="[^"]*position:\s*(?:fixed|absolute)[^"]*"', html, re.IGNORECASE)
    print(f"📌 [position: fixed/absolute] 레이어 개수: {len(fixed_layers)}개")

    # 4. display:none 이나 hidden 태그 수색
    hidden_tags = re.findall(r'(<[^>]*hidden[^>]*>|<[^>]*display:\s*none[^>]*>)', html, re.IGNORECASE)
    print(f"📌 [hidden / display:none] 요소 개수: {len(hidden_tags)}개")

    # 5. portal 키워드 및 radix UI 포털 레이어 수색
    radix_portals = re.findall(r'data-radix-[^=]+="[^"]*"', html)
    print(f"📌 [Radix UI / Portal 데이터 속성] 개수: {len(radix_portals)}개")

if __name__ == "__main__":
    inspect_3k_diff()
